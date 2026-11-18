# MUiT Connection Runtime

[简体中文](README.zh-CN.md)

Public installation materials for **0.1.0-rc.8.2 (pre-release)**: Collector Node, independent Feed Receiver, Web control center and installation tools. Application Go/Vue source is maintained privately. This repository contains installation materials only; its automatically generated source archives do not contain the application source.

Download fixed-version components from [Releases](https://github.com/MUiT-Labs/muit-runtime-distribution/releases/tag/v0.1.0-rc.8.2). Device installation does not require access to the private application repository or a GitHub token.

| Start here | Purpose |
| --- | --- |
| [Verified network download](docs/NETWORK.en.md) | Pin the external signing identity, verify the downloader and obtain selected components |
| [Network troubleshooting](docs/NETWORK-TROUBLESHOOTING.en.md) | Main-site/proxy failures, the official public API fallback and transfer between devices |
| [Installation and recovery](docs/INSTALL.en.md) | Identity, TLS/mTLS, configuration, service preparation, checks, upgrade, rollback and complete restore |
| [Compatibility](versions/0.1.0-rc.8.2/compatibility.json) | Platform baseline, MFP/API and migration limits |
| [Actual local validation](versions/0.1.0-rc.8.2/validation.json) | Executed checks and explicitly untested environments |
| [Real-device acceptance](docs/ACCEPTANCE.md) | Record physical/VM installation and data reconciliation; initially NOT TESTED |
| [Signing key lifecycle](keys/README.md) | External trust, rotation, revocation and recovery |
| [Security and known limits](SECURITY.md) | Advisory exposure, release withdrawal and confidential reporting |

Collector hosts normally use Collector + Tools + Web. Receiver hosts use Receiver + Tools plus a separately provisioned PostgreSQL17 service and compatible backup clients. Linux amd64 baseline: Debian12+, system glibc>=2.36 and ca-certificates; glibc is not bundled. Windows amd64 uses portable foreground mode. The bilingual Web UI is served by Collector HTTPS; device-side Node/npm is unnecessary.

Real VPS/165H installation, boot, active systemd enforcement, NetBird/5Mbps WAN,72-hour operation, Windows Service and other architectures remain NOT TESTED. Budget limits and container results are not physical-device measurements. Public downloads do not enroll a Node or grant MFP/API access.

Raw Ed25519 key ID: `7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e`. Public SPKI SHA-256: `3cf6512c7065df33bb04deb30f8b4e565a7f37949754da705f296161b6965703`. Confirm these through an independent trusted channel before first use. The Release signs each component, native bootstrap and network helper. The signing key is separate from device/mTLS identities. Source commit: `95aab60b7997e97593d9af2f31e44e6c67b9177f`.

Original works: [distribution terms](LICENSE.txt). Third-party licenses and applicable runtime exceptions are retained in each component archive. Public availability does not open-source the application.

Post-publication anonymous download and installation evidence: [remote acceptance](versions/0.1.0-rc.8.2/remote-validation.json).
