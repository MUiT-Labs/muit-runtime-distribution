# Security, known limits and release withdrawal

应用源码、设备身份、授权文件、证书私钥、PG口令、数据库/Spool及原始运行日志不得提交到本公开库或公开Issue。Confidential reports must use the repository's private vulnerability reporting channel when enabled, or contact the maintainer privately through an already trusted channel; do not post secrets publicly. No unverified reporting address is supplied.

Known build-tool issue: [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf), picomatch ReDoS. At preparation time the upstream advisory has no patched release. Production npm dependencies do not include the affected build chain; actual audit counts are recorded in the version's validation.json. No forced dependency downgrade is claimed as a fix. Builds process only reviewed, locked maintainer source; no public development server or user-controlled build globs are accepted. Node/npm build tools are not installed on target devices. Residual toolchain risk remains until patched and retested.

Public Release assets are fixed per version; do not replace an asset in place. Withdraw a defective release by marking it withdrawn in versions/index.json and publishing a maintainer advisory with the version/key ID, scope and safe replacement. Existing downloads remain independently verifiable; withdrawal does not erase third-party copies. Do not automatically switch a running node to a different version or bypass signature checks.

Compromised signing keys require an independently authenticated revocation and a new reviewed trust root; a new key supplied by the compromised release is insufficient. Keep old known-good release files and complete private backups according to retention needs. See keys/README.md.

Real devices, boot, systemd enforcement, network conditions and long-duration operation require separate acceptance. A pre-release or successful download is not production acceptance. No default API credentials are distributed.
