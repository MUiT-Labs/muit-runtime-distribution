# MUiT 安装与恢复手册 · 简体中文

[English](INSTALL.en.md)。公开预发布 0.1.0-rc.8.2。应用源码保持私有；本手册、安装工具和组件可从GitHub公开分发库浏览/下载。真实Tokyo VPS、165H、NetBird、系统开机自启、5Mbps和72小时负载需要对应设备授权及实际验收。

## 包和信任

候选按 collector / receiver / web / tools 分包，目标 linux/amd64 与 windows/amd64；其他平台不可由文件名推定支持。Windows 使用前台便携模式，Linux 原生或 Debian VM 提供 systemd 单元。Receiver 需要独立 PostgreSQL；备份/恢复还需与服务器主版本兼容的 `pg_dump`、`pg_restore`。不把数据库引擎、NetBird、证书或设备授权装进包。

Linux amd64要求Debian12或更新版本、系统glibc>=2.36；本包不复制glibc。Linux 外部公开行情 TLS 还需要系统 `ca-certificates` 与正确时钟；MFP 使用另行登记的私有 CA，两者不可混淆。只有本地文件系统上的安装/状态验证有证据，网络盘等文件系统需另测。

`release.json` 绑定来源 Commit、是否含未提交改动、源码树 SHA-256、协议/API/迁移和每个包/引导程序的大小及 SHA-256。`release.sig.json` 用于 Go 工具验证，`release.sig` 可由 OpenSSL 独立验证。公钥 `trust.json` / `trust.pem` 必须从管理员的独立可信渠道取得并核对指纹。包内附带的校验值或公钥自身不能建立信任。本版本使用独立发行身份，原始Ed25519公钥指纹为 7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e；与阶段7开发密钥、设备身份及mTLS CA均不同。

引导程序也必须先验证。Linux 可用系统 OpenSSL 与 Python 3：

```sh
openssl pkeyutl -verify -pubin -inkey /secure/trust.pem -rawin -in release.json -sigfile release.sig
python3 -c 'import json,hashlib,pathlib; m=json.load(open("release.json")); a=next(x for x in m["bootstraps"] if x["os"]=="linux" and x["arch"]=="amd64"); p=pathlib.Path(a["file"]); assert p.stat().st_size==a["size"] and hashlib.file_digest(p.open("rb"),"sha256").hexdigest()==a["sha256"]'
chmod 755 ./muit-install_linux_amd64
./muit-install_linux_amd64 verify --manifest ./release.json --signature ./release.sig.json --public-key /secure/trust.json --components collector,web,tools
```

Python 3.11+ 的引导辅助只用标准库；运行 MUiT 服务不需要 Python/Node/npm。在 Windows与Linux均可使用公开download.py按外部指纹验证并下载引导程序；下载器本身也须先按清单签名/Hash核验，具体见NETWORK.zh-CN.md。不要执行未验证的下载脚本或用下载包旁边的同一份 SHA256SUMS 作为唯一信任依据。

## 安装前记录

运行 `muit-install preflight --root <现有目录>` 保存本机 OS/arch、CPU、卷可用空间和 UTC。它不代替部署规格的完整现场检查：Debian/内核、RAM/swap、目录/inode/挂载、已有服务/端口、SSH/控制台退路、NTP、NetBird Peer/DNS/路由/MTU、Receiver 地址/CA/授权和真实吞吐都需核实。未知写 UNKNOWN。管理默认 `127.0.0.1`；需要远程管理时先核实 NetBird 的具体地址和受控 DNS/SAN，不监听公网。

后续系统服务命令仅供已获授权的目标主机执行。本阶段在本地隔离环境验证，不代表操作真实设备。

## 分步初装

下面以公开预发布 `0.1.0-rc.8.2` 为例；以实际签名清单中的版本为准。选择唯一明确的安装根目录：Linux 正式布局为 `/`；开发或 Windows 使用单独目录。stage 只新增版本目录，activate 只切换程序指针，init 不覆盖已存在的配置。

```sh
./muit-install_linux_amd64 stage --root / --manifest ./release.json --signature ./release.sig.json --public-key /secure/trust.json --assets . --components collector,web,tools --apply
./muit-install_linux_amd64 activate --root / --release 0.1.0-rc.8.2 --components collector,web,tools --apply
./muit-install_linux_amd64 init --root / --components collector --apply
```

Receiver 主机用 `--components receiver,tools` 分包和激活，再以 `--components receiver` 初始化。两组件可以独立部署，也可在同一系统中使用独立用户/配置/数据。不要与已有非 MUiT 数据目录混用。

目录：

| 位置 | 用途 |
| --- | --- |
| `/opt/muit/releases/<release>/<component>` | 不覆盖的程序/静态文件/工具版本 |
| `/opt/muit/installed.json` | 原子切换的 active/previous 指针 |
| `/opt/muit/bin/muit-install` | 注册 systemd 时从已验包复制的稳定引导 |
| `/etc/muit/collector`、`/etc/muit/receiver` | 独立配置、授权、证书引用；init 不覆盖 |
| `/var/lib/muit/collector`、`/var/lib/muit/receiver` | SQLite/Spool、Receiver Parquet；升级不覆盖 |
| `/var/log/muit/<component>` | 预留独立日志目录；服务 JSON 输出由 MUiT journal namespace 限额保存 |
| `/var/lib/muit/backups` | 运维选择的私有备份位置；外部加密副本/快照需另外配置 |

Collector 目录是当前实现的扁平 Spool 根（`collector.db` 与 pending/inflight/sent/quarantine/groups 同级）；沿用已有扁平布局，不额外迁移旧路径。

## 身份、证书和配置

1. 使用该版本 collector/bin/muitctl 的 `identity init --file /etc/muit/collector/node.json --asset-id <资产编号> --name <名称> --root-did <实际Root-DID引用>` 建立新节点。原有 Node 不能随升级重新生成。
2. `muit-install cert --action csr --out-dir /etc/muit/collector/tls --name server --common-name <名称> --dns <管理DNS> --ip 127.0.0.1` 只生成私钥/CSR。交由受控 CA 签发，将完整服务端链保存为 server.pem。Receiver 同样建立 server.pem/server.key，并设置 client-ca.pem。私钥不经聊天或公开仓库传递。
3. `muit-install cert --action inspect --certificate ... --key ... --ca ... --usage server --server-name <实际SAN>` 验证匹配、链、用途、有效期，默认要求还剩 24 小时；客户端用途用 `--usage client`。换证先在新位置验证，再在停服/Drain 的窗口原子替换和重启；登记新的叶证书指纹。不能因换证移除 CA 校验或放宽授权。
4. Collector 初始 authorization.json 没有有效凭据，必须显式登记。初始 Owner 可运行 `muit-install access --authorization /etc/muit/collector/authorization.json --credential-out /secure/owner-session.txt --role Owner --owner --kind session --ttl 1h`。凭据原文只写新私有文件，授权库只存 SHA-256。非 Owner 需审阅的 `--grants` 数组，角色不能替代对象授权。健康检查另发 `--kind bearer` 的最小 getHealth 权限身份。文件改动后按当前运行时流程重启使其载入；到期不自动续权。
5. settings.json 默认 2GB Spool、无 Receiver、无运行许可。显式填写私网 Endpoint 引用、TLS 客户端证书/私钥/CA 路径；Receiver 按证书指纹、Node/Stream/Sink 登记。需要采集时再登记有期限的 `run_authorization`（epoch/expires_at）并重启；不得用无限租约或默认通配 Receiver 授权替代。
6. Receiver 的 pg_service.conf 仅为示例，替换 host/dbname/user/CA，优先使用私有 passfile；不要把口令放入命令参数。预先由数据库管理员创建专用数据库/角色。以受控 `PGSERVICEFILE` 和 `MUIT_RECEIVER_DSN='service=muit_receiver'` 执行 `muit-receiver migrate`，随后 check；安装器不会自动迁移生产库。备份角色需有 dump 和冻结表写入所需权限，不能让运行角色因此获得数据库创建/删除权限。

CSR 文件不等于证书，网络连通不等于 mTLS/Node/Stream/Sink 授权成功。默认模板是安全的待配置状态，不能将未配置、未检查写成安装成功并运行。

## 检查和服务

```sh
./muit-install_linux_amd64 check --root / --components collector
./muit-install_linux_amd64 run --root / --components collector
# 仅授权 Linux 主机：独立系统用户和服务文件；prepare 不启用、不启动。
./muit-install_linux_amd64 service --component collector --action prepare --apply
./muit-install_linux_amd64 service --component collector --action enable --apply
./muit-install_linux_amd64 service --component collector --action start --apply
```

Receiver 将 collector 替换为 receiver。服务以 `muit` / `muit-receiver` 运行。资源值是预算：Collector GOMEMLIMIT 600MiB、MemoryHigh 800M、MemoryMax 900M、CPUQuota 150%、TasksMax 128；Receiver 单独配置。按目标盘/RAM实测审查，不当成性能结果。若既有 service/bootstrap 文件不同，prepare 拒绝覆盖，先备份、对比后人工审查替换。

两个服务通过仅用于父目录遍历的 `muit-runtime` 组访问 0750 的 `/etc/muit`、`/var/lib/muit`。子目录和私钥分别归各自专用组，Receiver 不因此取得 Collector 的密钥权限。拒绝将普通交互用户或 root 当成专用服务账户。改变 Endpoint 或 CA 时使用新 Endpoint 引用，保留旧引用/信任用于处理原待送责任，不覆盖持久化绑定。

`check` 不监听或启动采集，不应用迁移；Receiver 检查实际数据库，Collector 检查已存在的迁移账本。systemd ExecStartPre 同样执行 check，停止时转发退出信号并等待排空；超时留待 Spool 恢复。journal namespace 仅配置 MUiT 日志（128M 持久、32M 运行时、7 天），不更改全局日志配额。可用 `journalctl --namespace=muit -u muit-collector.service` 和 `systemctl show` 查看实际行为。

Go 健康检查不跳过 TLS：`muit-install health --url https://127.0.0.1:8444/api/v1/health --ca <管理CA> --bearer-file <私有getHealth凭据>`。Receiver `/healthz` 需相应 mTLS 与登记，追加 `--client-cert` / `--client-key`。只有 HTTP200、success=true、code=OK 才报告 healthy；Source、Batch、Receipt 和 Cursor 仍须另行核对。

Windows 在独立根目录使用同样的 stage/activate/init/check/run 命令，例如 `--root D:\MUiT-local`。不要执行 Linux service 子命令；当前没有宣称支持 Windows Service 自启。便携前台服务用 Ctrl+C 关闭；强杀按 Spool 恢复处理。

## 备份、升级、回退与恢复

升级先 stage/verify 新包；停止并 Drain 受影响服务，再保存当前指针/版本和完整数据快照。使用运行版本中的 muitctl：

```sh
muitctl state backup --state-dir /var/lib/muit/collector --backup-dir /var/lib/muit/backups/collector-<唯一UTC编号> --apply
muitctl receiver backup --state-dir /var/lib/muit/receiver --backup-dir /var/lib/muit/backups/receiver-<唯一UTC编号> --pg-service-file /etc/muit/receiver/pg_service.conf --pg-service muit_receiver --apply
```

备份目录必须不存在。Receiver 可用 `--pg-bin <客户端目录>`；pg_dump/pg_restore 必须已安装并兼容服务器主版本。工具从私有 service file 读取连接，口令不进入子进程参数或日志。Collector 同进程锁 + SQLite Backup API 捕获 WAL 与所有 Spool 文件；Receiver 同归档锁 + SHARE 表锁覆盖一致 dump/Parquet，缺少任何已提交文件会拒绝备份。备份携带私有业务数据，保存到 0700/受限 ACL 的目录，并另行加密或做受控盘快照；不上传公共仓库。

另行私有备份 `/etc/muit/<component>` 的 JSON 配置、Node 身份、版本清单和审计交接。默认数据快照不含证书私钥、PG 口令或外部密钥；生产配置备份必须加密并限制访问。证书签发元数据可留存，私钥恢复/重新签发使用受控渠道。先检查空闲空间、外部副本和恢复密钥，单机磁盘损坏不能靠同盘备份解决。

同迁移/协议谱系的新版本可 activate，随后 check/start/health，并核对真实 Source、待送批次、COMMITTED、Receipt、Cursor 和计数；采集默认需重新显式启动。失败时停止新服务，保留故障证据和新产生数据，`rollback --root / --components collector,web,tools --apply` 切回记录的 previous；再 check/start/对账。回退不恢复旧数据库、不删除待送/隔离文件。未知或变化的迁移会拒绝切换，需单独 ADR 和迁移/恢复方案。

当前安装格式接受 0.1.x 补丁系列、相同 muit.feed.v1/API 和完全一致的迁移谱系；新协议/迁移或 0.2.x 不自动通过。stage 以组件为单位原子发布；若中途失败，已发布的组件保持不变，仅核对并补 stage 缺失组件，再整体 activate。Windows 临时访问/共享冲突最多重试约 1 秒；仍失败时保留原包/备份、关闭占用后换新恢复目录重试，不删除已有目标。快照清单有 100,000 文件/32MiB 的有界限制，超出须另订卷快照/分段备份方案，不能省略文件后称完整。

数据恢复只能进入新的目录/空数据库：

```sh
muitctl state restore --backup-dir <完整Collector快照> --state-dir <不存在的新状态目录> --apply
muitctl receiver restore --backup-dir <完整Receiver快照> --state-dir <不存在的新归档目录> --pg-service-file <私有连接文件> --pg-service <已创建的空目标库服务名> --apply
```

Receiver restore 不执行 DROP/CLEAN/CREATE DATABASE，使用单事务 pg_restore；新归档先保留，失败不会回删责任数据。恢复后按新环境重新配置秘密与路径，并验证原 Batch 重放返回原 Receipt/Commit ID、无重复业务记录和连续 Cursor。配置/数据切换需要人工审核，不能用覆盖目录作为恢复方法。回滚包与完整备份至少保留到验收通过和保留期限届满；卸载先停服/禁用，只移除获准的程序和服务，默认保留配置、数据、备份及隔离区，不提供一键清空。

## 实机验收

用公开ACCEPTANCE模板记录 OS/架构、Commit/制品 Hash、时间、操作者、NetBird、证书指纹、配置版本、实际资源/带宽、Batch ID、压缩 Hash、Receiver Commit ID、Cursor 及双方计数。完成真实采集、断网补传、重复/ACK 丢失、持久化失败、多 Sink、压力、重启自启和备份恢复，建议连续 72 小时。预算、设计、容器结果不能填写为实机 PASS。
