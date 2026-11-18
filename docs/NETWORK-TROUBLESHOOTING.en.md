# Download routes and the official API fallback

[简体中文](NETWORK-TROUBLESHOOTING.zh-CN.md) · [Signature verification](NETWORK.en.md)

Fixed version 0.1.0-rc.8.2. Public assets need no GitHub account or token. The main site, API, asset CDN and codeload are separate routes. Retain failures and retry in a new directory; never weaken TLS or skip signatures. A successful download does not install a device or enroll MFP/API permissions.

The development network produced a connection reset on the Windows main-site route and a stall through an automatically selected local proxy. A clean Debian client independently checks the official public asset API; see version acceptance evidence for exact scope. This is not a VPS/165H network acceptance claim. Some Windows Schannel curl builds cannot enable TLS1.3. Use independently trusted Python/OpenSSL or prepare the Windows packages on Debian/a VM, transfer them and verify again on the destination.

## Linux / Debian VM: discover official asset URLs

In a new directory, obtain metadata and list exact filenames and API URLs. This metadata discovers addresses; it does not establish signing trust.

```sh
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.3 \
  https://api.github.com/repos/MUiT-Labs/muit-runtime-distribution/releases/tags/v0.1.0-rc.8.2 \
  --output release-metadata.json || exit 1
python3 -c 'import json; m=json.load(open("release-metadata.json")); [print(a["name"],a["url"]) for a in m["assets"]]'
```

Select release.json, release.sig, release.sig.json, the target OS's native muit-install and the desired component archives. Replace both placeholders below with the exact official URL and filename from the list; do not run the placeholders.

```sh
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.3 \
  --header 'Accept: application/octet-stream' \
  'EXACT_OFFICIAL_ASSET_API_URL' --output 'EXACT_FILENAME' || exit 1
```

Opening an API URL in a browser generally returns JSON. The Accept header requests raw bytes. Follow NETWORK's external fingerprint, raw Ed25519 manifest signature and native bootstrap hash checks before INSTALL. Retain the third-party notices and original distribution terms.

For a broken proxy, `--noproxy '*'` selects direct access for that curl invocation. A temporary NO_PROXY=* selects direct access for a Python verification process without changing system settings. Networks requiring a proxy need an administrator-provided working route. Never place proxy passwords or GitHub tokens in installation materials.

After transfer, verify the same signature/hashes on the destination before stage/check. Retain the previous trusted release and complete backups. Record failed/untested routes independently of a successful alternate route.
