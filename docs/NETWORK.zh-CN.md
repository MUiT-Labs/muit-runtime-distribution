# 验签后网络下载

[English](NETWORK.en.md) · [完整安装](INSTALL.zh-CN.md)

固定版本：0.1.0-rc.8.2，预发布。下载需要现有Python3.11+及可信OpenSSL3+；运行MUiT服务不需要Python/Node/npm。下载器不会安装依赖、启动程序、登记证书/凭据、改服务、数据库、NetBird或防火墙。

## 1. 独立确认公钥

向管理员或独立可信渠道确认原始Ed25519指纹 `7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e`，以及SPKI SHA-256 `3cf6512c7065df33bb04deb30f8b4e565a7f37949754da705f296161b6965703`。公开公钥位于本库keys/release-v1.json和keys/release-v1.pub；分别保存为trust.json和trust.pub。不要仅根据同一份未验证下载提供的指纹建立首次信任。

```sh
openssl pkey -pubin -in trust.pub -outform DER -out trust.der
openssl dgst -sha256 trust.der
```

将最后结果与独立确认的SPKI摘要逐字比较，不一致即停止。下载器随后还会核对trust.json原始公钥的指纹。

## 2. 下载并验证下载器本身

从 [固定Release](https://github.com/MUiT-Labs/muit-runtime-distribution/releases/tag/v0.1.0-rc.8.2) 取得release.json、release.sig和download.py，保存到一个新工作目录。Linux可用以下命令；Windows可在浏览器保存相同文件，之后用可信OpenSSL和Python执行后两步。

```sh
base=https://github.com/MUiT-Labs/muit-runtime-distribution/releases/download/v0.1.0-rc.8.2
for name in release.json release.sig download.py; do curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.3 "$base/$name" --output "$name" || exit 1; done
openssl pkeyutl -verify -pubin -inkey trust.pub -rawin -in release.json -sigfile release.sig || exit 1
python3 -c 'import json,hashlib,pathlib; m=json.load(open("release.json")); a=next(x for x in m["bootstraps"] if x["file"]=="download.py"); p=pathlib.Path("download.py"); assert p.stat().st_size==a["size"] and hashlib.sha256(p.read_bytes()).hexdigest()==a["sha256"]' || exit 1
```

Windows 使用 python 代替 python3；PowerShell 7+ 支持上面的 `|| exit 1`，旧版 PowerShell 请分别运行后两项检查并确认每个 `$LASTEXITCODE` 为 0。任一失败就停止。验签与 Hash 检查都成功后，才执行 download.py。可以浏览公开脚本；不要将未验证脚本直接管道到 Shell。

## 3. 选择组件并下载

```sh
python3 ./download.py --version 0.1.0-rc.8.2 --repository MUiT-Labs/muit-runtime-distribution --trust ./trust.json --key-id 7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e --component collector tools web --out ./verified-0.1.0-rc.8.2
```

Receiver设备改为 `--component receiver tools`。默认识别当前OS/amd64；为另一台受支持设备准备离线包可显式用 `--platform linux-amd64` 或 `--platform windows-amd64`。ARM64及其他OS没有对应包，不能用改文件名方式安装。

下载全程匿名，不使用GitHub令牌。仅HTTPS/TLS1.3与受限GitHub重定向来源；验证精确版本、外部签名、公钥、文件大小/SHA-256后才将程序文件交付到新目录。已有目录会拒绝覆盖。download-report.json的PASS仅代表下载/校验成功；程序没有启动。不完整下载留在.unverified-*以便诊断，可选择新的空输出目录重试。--test-base-url仅供环回HTTP故障测试，正式下载不用它。

进入verified目录，再按INSTALL执行stage、activate、init、配置/证书登记、check和授权主机上的服务动作。外部trust.json继续单独保存；下载包不能替代该信任根。升级固定新版本并保留旧包/完整备份，不能自动跟随latest或不兼容迁移。
