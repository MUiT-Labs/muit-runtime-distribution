# MUiT Connection Runtime 安装分发

[English](README.md)

当前版本 **0.1.0-rc.8.2，公开预发布**。MUiT Collector Node负责采集、持久缓冲和可靠交付；独立Feed Receiver负责认证、校验、幂等提交与回执。应用Go/Vue源码在私有库维护。本公开库只保存安装材料，其自动生成的源码归档只包含这些公开安装材料。

从 [Releases下载固定版本](https://github.com/MUiT-Labs/muit-runtime-distribution/releases/tag/v0.1.0-rc.8.2)。设备安装无需私有源码库权限或GitHub访问令牌。

| 从这里开始 | 用途 |
| --- | --- |
| [验签网络下载](docs/NETWORK.zh-CN.md) | 确认外部公钥指纹，先验证下载器，再获取所需组件 |
| [安装与恢复](docs/INSTALL.zh-CN.md) | 身份、证书、配置、服务准备、健康检查、升级回退和完整恢复 |
| [兼容矩阵](versions/0.1.0-rc.8.2/compatibility.json) | 平台基线、MFP/API与迁移兼容规则 |
| [实际本地验证](versions/0.1.0-rc.8.2/validation.json) | 已执行检查及明确未测环境 |
| [实机验收模板](docs/ACCEPTANCE.md) | 实体机/VM安装、真实数据对账；初始均为NOT TESTED |
| [签名身份维护](keys/README.md) | 外部信任、轮换、撤销和恢复 |
| [安全与已知限制](SECURITY.md) | 依赖公告范围、版本撤回及保密反馈 |

Collector设备通常选择Collector + Tools + Web；接收设备选择Receiver + Tools，并准备独立PostgreSQL17服务及兼容备份客户端。Linux amd64基线为Debian12+、系统glibc>=2.36及ca-certificates，包内不复制glibc。Windows amd64提供便携前台模式。Web含简体中文/English和亮暗主题，由Collector HTTPS托管，设备无需Node/npm。

真实VPS/165H安装、整机启动、systemd动态保护、NetBird/5Mbps、72小时运行、Windows Service及其他架构均为NOT TESTED。预算与容器结果不等于实机性能。下载公开包不会自动登记Node、签发mTLS证书或授予API权限。

原始Ed25519公钥指纹：`7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e`。公钥SPKI SHA-256：`3cf6512c7065df33bb04deb30f8b4e565a7f37949754da705f296161b6965703`。首次使用须经独立可信渠道确认。Release签名覆盖组件、原生引导程序和下载脚本；发行身份与设备/mTLS身份分离。源码来源提交：`95aab60b7997e97593d9af2f31e44e6c67b9177f`。

原创内容适用 [分发条款](LICENSE.txt)，各包内保留第三方许可证及适用运行库例外。公开下载不代表应用源码开源。
