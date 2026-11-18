#!/usr/bin/env python3
"""Download one fixed MUiT release anonymously; verify before exposing executables.

Requires Python 3.11+ and an independently installed OpenSSL 3+. Does not execute
downloaded programs, extract archives, change services or provision credentials.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?$')
SAFE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,178}$')
SHA = re.compile(r'^[a-f0-9]{64}$')
HOSTS = {'github.com', 'api.github.com', 'raw.githubusercontent.com',
         'release-assets.githubusercontent.com', 'objects.githubusercontent.com',
         'objects-origin.githubusercontent.com', 'github-releases.githubusercontent.com',
         'github-cloud.s3.amazonaws.com'}
COMPONENTS = ('collector', 'receiver', 'tools', 'web')
MAX_ASSET = 512 * 1024 * 1024


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON property')
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object)


def trust_key(file, expected):
    if not SHA.fullmatch(expected) or file.is_symlink() or not file.is_file() or file.stat().st_size > 4096:
        raise ValueError('supply a bounded external public key and independently confirmed SHA-256 key ID')
    key = decode(file.read_bytes())
    if set(key) != {'algorithm', 'key_id', 'public_key'} or key['algorithm'] != 'ed25519':
        raise ValueError('unsupported external public key')
    public = base64.b64decode(key['public_key'], validate=True)
    if len(public) != 32 or hashlib.sha256(public).hexdigest() != expected or key['key_id'] != expected:
        raise ValueError('external trust fingerprint mismatch')
    return public


def openssl_path(option=None):
    executable = option or shutil.which('openssl')
    if not executable and sys.platform == 'win32':
        candidate = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/usr/bin/openssl.exe'
        if candidate.is_file():
            executable = str(candidate)
    if not executable:
        raise ValueError('install OpenSSL 3+ independently; no downloaded bootstrap has been executed')
    run = subprocess.run([executable, 'version'], capture_output=True, timeout=15)
    if run.returncode or not re.match(rb'OpenSSL ([3-9]|[1-9][0-9])\.', run.stdout):
        raise ValueError('OpenSSL 3+ is required')
    return executable


def verify_signature(directory, public, executable):
    # RFC 8410 Ed25519 SubjectPublicKeyInfo; no custom signature implementation.
    der = bytes.fromhex('302a300506032b6570032100') + public
    pem = b'-----BEGIN PUBLIC KEY-----\n' + base64.b64encode(der) + b'\n-----END PUBLIC KEY-----\n'
    with tempfile.TemporaryDirectory(prefix='muit-public-trust-') as scratch:
        key = Path(scratch) / 'external-trust.pem'
        key.write_bytes(pem)
        run = subprocess.run([executable, 'pkeyutl', '-verify', '-pubin', '-inkey', str(key),
                              '-rawin', '-in', str(directory / 'release.json'),
                              '-sigfile', str(directory / 'release.sig')], capture_output=True, timeout=20)
    if run.returncode:
        raise ValueError('release signature verification failed')


def validate_url(url, loopback=None):
    parsed = urllib.parse.urlsplit(url)
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError('credentials/fragments in download URL are forbidden')
    if loopback is not None:
        test = urllib.parse.urlsplit(loopback)
        if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', '::1', 'localhost') or (parsed.hostname, parsed.port) != (test.hostname, test.port):
            raise ValueError('test transport is loopback-only and cannot redirect outside its origin')
    elif parsed.scheme != 'https' or parsed.hostname not in HOSTS or parsed.port not in (None, 443):
        raise ValueError('only approved GitHub HTTPS download origins are permitted')


class CheckedRedirect(urllib.request.HTTPRedirectHandler):
    max_redirections = 5

    def __init__(self, loopback):
        self.loopback = loopback

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl, self.loopback)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(opener, url, target, maximum, deadline, loopback=None, size=None, sha=None):
    validate_url(url, loopback)
    request = urllib.request.Request(url, headers={'User-Agent': 'MUiT-release-download/0.1', 'Accept': 'application/octet-stream'})
    digest = hashlib.sha256()
    count = 0
    try:
        with opener.open(request, timeout=30) as response, target.open('xb') as output:
            if response.status != 200:
                raise ValueError('download did not return HTTP 200')
            header = response.headers.get('Content-Length')
            if header is not None and (int(header) > maximum or (size is not None and int(header) != size)):
                raise ValueError('download Content-Length rejected')
            while True:
                if time.monotonic() > deadline:
                    raise ValueError('download time budget exceeded')
                block = response.read(min(65536, maximum - count + 1))
                if not block:
                    break
                count += len(block)
                if count > maximum:
                    raise ValueError('download size limit exceeded')
                digest.update(block)
                output.write(block)
            output.flush()
            os.fsync(output.fileno())
    except urllib.error.HTTPError as error:
        raise ValueError('download HTTP error ' + str(error.code)) from None
    except urllib.error.URLError:
        raise ValueError('download transport/TLS failed; existing releases were not modified') from None
    if (size is not None and count != size) or (sha is not None and digest.hexdigest() != sha):
        raise ValueError('download differs from the signed size or SHA-256')
    return count


def select_assets(manifest, version, components, operating_system, architecture):
    if manifest.get('format') != 1 or manifest.get('release') != version or manifest.get('protocol') != 'muit.feed.v1' or manifest.get('api') != '/api/v1' or manifest.get('source_dirty') is not False or not re.fullmatch(r'0\.1\.(0|[1-9][0-9]*)', manifest.get('runtime', '')):
        raise ValueError('release version, clean provenance or compatibility rejected')
    assets, bootstraps = manifest.get('assets'), manifest.get('bootstraps')
    if not isinstance(assets, list) or not 1 <= len(assets) <= 32 or not isinstance(bootstraps, list) or not 1 <= len(bootstraps) <= 8:
        raise ValueError('invalid bounded asset lists')
    seen = set()
    for asset in assets + bootstraps:
        if not isinstance(asset, dict) or set(asset) != {'component', 'os', 'arch', 'file', 'size', 'sha256'} or asset['component'] not in COMPONENTS or asset['os'] not in ('linux', 'windows', 'any') or asset['arch'] not in ('amd64', 'arm64', 'any') or not isinstance(asset['file'], str) or not SAFE.fullmatch(asset['file']) or asset['file'].lower() in seen or type(asset['size']) is not int or not 0 < asset['size'] <= MAX_ASSET or not isinstance(asset['sha256'], str) or not SHA.fullmatch(asset['sha256']):
            raise ValueError('invalid, unsafe or duplicate signed asset')
        seen.add(asset['file'].lower())
    chosen = []
    for component in dict.fromkeys(components):
        matches = [a for a in assets if a['component'] == component and a['os'] in (operating_system, 'any') and a['arch'] in (architecture, 'any')]
        if len(matches) != 1:
            raise ValueError('no unique tested package for ' + component + '/' + operating_system + '/' + architecture)
        chosen += matches
    matches = [a for a in bootstraps if a['component'] == 'tools' and a['os'] == operating_system and a['arch'] == architecture]
    if len(matches) != 1:
        raise ValueError('no unique bootstrap for requested platform')
    chosen += matches
    if sum(a['size'] for a in chosen) > 1536 * 1024 * 1024:
        raise ValueError('total download budget exceeded')
    return chosen


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--repository', default='MUiT-Labs/muit-runtime-distribution')
    parser.add_argument('--trust', required=True, type=Path)
    parser.add_argument('--key-id', required=True)
    parser.add_argument('--component', nargs='+', choices=COMPONENTS, default=['collector', 'tools', 'web'])
    parser.add_argument('--platform', choices=['linux-amd64', 'windows-amd64'])
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--openssl')
    parser.add_argument('--test-base-url', help='fault-test only: HTTP loopback origin; signature requirements still apply')
    args = parser.parse_args(argv)
    if not VERSION.fullmatch(args.version) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', args.repository):
        raise ValueError('unsafe fixed version or repository')
    public = trust_key(args.trust, args.key_id)
    executable = openssl_path(args.openssl)
    if args.platform:
        operating_system, architecture = args.platform.split('-')
    else:
        operating_system = 'windows' if sys.platform == 'win32' else sys.platform
        architecture = {'x86_64': 'amd64', 'amd64': 'amd64', 'aarch64': 'arm64'}.get(platform.machine().lower(), platform.machine().lower())
    if args.test_base_url:
        validate_url(args.test_base_url, args.test_base_url)
        base = args.test_base_url.rstrip('/')
    else:
        base = 'https://github.com/' + args.repository + '/releases/download/v' + args.version
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    opener = urllib.request.build_opener(CheckedRedirect(args.test_base_url), urllib.request.HTTPSHandler(context=context))
    # Refuse links in every existing ancestor and require a completely new output.
    output = args.out.absolute()
    if any(p.is_symlink() for p in [output, *output.parents]):
        raise ValueError('linked output path rejected')
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    staging = Path(tempfile.mkdtemp(prefix='.unverified-', dir=output))
    deadline = time.monotonic() + 900
    report = {'result': 'FAIL', 'version': args.version, 'credentials_used': False, 'downloaded_programs_executed': False}
    try:
        for name, limit in [('release.json', 2 * 1024 * 1024), ('release.sig', 64), ('release.sig.json', 4096)]:
            fetch(opener, base + '/' + name, staging / name, limit, deadline, args.test_base_url)
        if (staging / 'release.sig').stat().st_size != 64:
            raise ValueError('invalid Ed25519 signature length')
        verify_signature(staging, public, executable)
        envelope = decode((staging / 'release.sig.json').read_bytes())
        if set(envelope) != {'algorithm', 'key_id', 'signature'} or envelope['algorithm'] != 'ed25519' or envelope['key_id'] != args.key_id or base64.b64decode(envelope['signature'], validate=True) != (staging / 'release.sig').read_bytes():
            raise ValueError('signature envelope mismatch')
        manifest = decode((staging / 'release.json').read_bytes())
        chosen = select_assets(manifest, args.version, args.component, operating_system, architecture)
        if shutil.disk_usage(output).free < 2 * sum(a['size'] for a in chosen) + 16 * 1024 * 1024:
            raise ValueError('insufficient free disk space for this selection')
        for asset in chosen:
            fetch(opener, base + '/' + asset['file'], staging / asset['file'], asset['size'], deadline, args.test_base_url, asset['size'], asset['sha256'])
        for name in ['release.json', 'release.sig', 'release.sig.json'] + [a['file'] for a in chosen]:
            # Output is new/private; never replace an existing release or asset.
            destination = output / name
            with destination.open('xb') as stream, (staging / name).open('rb') as source:
                shutil.copyfileobj(source, stream, length=65536)
                stream.flush()
                os.fsync(stream.fileno())
        report.update(result='PASS', platform=operating_system + '-' + architecture, key_id=args.key_id,
                      source_commit=manifest.get('source_commit'), files=chosen)
        print('Verified ' + str(len(chosen)) + ' files. Follow INSTALL to stage/configure; nothing has been started.')
        return 0
    finally:
        # Failed unverified files remain isolated for diagnosis, never executed.
        (output / 'download-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print('Download refused: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
    except (KeyError, TypeError, AttributeError):
        print('Download refused: malformed signed metadata', file=sys.stderr)
        raise SystemExit(1)
