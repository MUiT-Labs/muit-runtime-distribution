# Verified network download

[简体中文](NETWORK.zh-CN.md) · [Full installation](INSTALL.en.md)

Fixed pre-release: 0.1.0-rc.8.2. Downloading requires an existing Python3.11+ and independently trusted OpenSSL3+. Running MUiT needs neither Python nor Node/npm. The downloader does not install dependencies, run downloaded code, enroll credentials/certificates, change services/databases, NetBird or firewall rules.

## 1. Confirm the external trust root

Confirm raw Ed25519 key ID `7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e` and SPKI SHA-256 `3cf6512c7065df33bb04deb30f8b4e565a7f37949754da705f296161b6965703` through an administrator or independent trusted channel. Public files keys/release-v1.json and keys/release-v1.pub can be saved as trust.json and trust.pub. Do not establish first trust solely from a fingerprint accompanying the same unverified download.

```sh
openssl pkey -pubin -in trust.pub -outform DER -out trust.der
openssl dgst -sha256 trust.der
```

Compare the result with the independently confirmed SPKI digest. Stop on any mismatch. The downloader also checks the raw public key's fingerprint in trust.json.

## 2. Verify the downloader itself

Obtain release.json, release.sig and download.py from the [fixed Release](https://github.com/MUiT-Labs/muit-runtime-distribution/releases/tag/v0.1.0-rc.8.2) into a new working directory. Linux commands follow. Windows users can save the same files through a browser, then perform the last two verification steps with trusted OpenSSL and Python.

```sh
base=https://github.com/MUiT-Labs/muit-runtime-distribution/releases/download/v0.1.0-rc.8.2
for name in release.json release.sig download.py; do curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.3 "$base/$name" --output "$name" || exit 1; done
openssl pkeyutl -verify -pubin -inkey trust.pub -rawin -in release.json -sigfile release.sig || exit 1
python3 -c 'import json,hashlib,pathlib; m=json.load(open("release.json")); a=next(x for x in m["bootstraps"] if x["file"]=="download.py"); p=pathlib.Path("download.py"); assert p.stat().st_size==a["size"] and hashlib.sha256(p.read_bytes()).hexdigest()==a["sha256"]' || exit 1
```

Use python instead of python3 on Windows. PowerShell 7+ supports `|| exit 1`; on older PowerShell run the last two checks separately and confirm each `$LASTEXITCODE` equals 0. Stop on either failure. Execute download.py only after both signature and hash checks pass. The helper is publicly readable; never pipe an unverified download into a shell.

## 3. Download selected components

```sh
python3 ./download.py --version 0.1.0-rc.8.2 --repository MUiT-Labs/muit-runtime-distribution --trust ./trust.json --key-id 7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e --component collector tools web --out ./verified-0.1.0-rc.8.2
```

Receiver devices use `--component receiver tools`. The current OS/amd64 is detected; prepare offline files for another supported device using --platform linux-amd64 or --platform windows-amd64. ARM64/other systems have no artifacts; renaming a file does not make it compatible.

Requests are anonymous and require no GitHub token. HTTPS/TLS1.3 and constrained GitHub redirect origins are enforced. The exact version, external signing identity, signature, size and SHA-256 are checked before native programs become available in a new output directory. Existing directories are never replaced. PASS in download-report.json means download/verification only; nothing has started. Failed files remain under .unverified-* for diagnosis; retry into a new output. --test-base-url is exclusively for loopback HTTP fault tests.

Follow INSTALL for stage/activate/init, certificates/configuration, checks and explicitly authorized service actions. Keep trust.json externally. Upgrades pin a new version and retain old packages/complete backups; never automatically track latest or bypass migration compatibility checks.
