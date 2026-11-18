# Release signing trust / 发行签名信任

Identity: MUiT-Labs release-v1, Ed25519. Raw key ID: `7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e`.
SPKI SHA-256: `3cf6512c7065df33bb04deb30f8b4e565a7f37949754da705f296161b6965703`.

release-v1.json contains the public key in the installer's trust format. release-v1.pub is PEM SubjectPublicKeyInfo for independent OpenSSL verification. Both are public; neither contains a private key. They are separate from device identities and mTLS CA keys.

首次信任必须从管理员或独立可信渠道确认上述指纹；不能仅因公钥与安装包同时下载就信任。下载器要求显式 --trust 和 --key-id，并拒绝不匹配身份。Follow NETWORK before executing even the public download helper: the helper's hash is itself included in the signed release manifest.

Keep the release private key in restricted signing storage with an encrypted offline backup under the maintainer's control. Never place it in Git, CI artifacts, a device installer, chat or a public repository. The source repository does not contain the private key. Test suites use separate disposable signing identities and must not receive the release private key.

Routine rotation: create a new identity in private signing storage, verify it independently, publish its public key/fingerprint and transition notice, then explicitly enroll it on clients. Keep old keys/releases for checking retained versions; do not silently trust a replacement downloaded with a new release. If an old key is compromised, use an independently authenticated revocation route; an old-key signature alone is insufficient.

撤回/轮换不自动删除设备上的旧包、Spool或备份，不重签同版本资产。新版本保持独立清单和迁移兼容审查。Release元数据可用于发现版本，真正下载必须固定 --version。
