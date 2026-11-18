# MUiT Connection Runtime 0.1.0-rc.8.2

Public pre-release / 公开预发布。Application source is private; original works
retain all rights with free official download, installation and use under LICENSE.txt.

Collector, Receiver and installation tools: Linux amd64 (Debian 12+, system
glibc >= 2.36) and portable Windows amd64; Web: compiled bilingual English/简体中文 UI.
The public repository's automatic source archives contain installation materials only.

Verified locally: actual signed package lifecycle on Windows and non-root Debian,
backup/restore, compatible code-pointer upgrade/rollback, PostgreSQL/Parquet durable
commit and live public market delivery, plus bounded downloader fault tests.
See versions/0.1.0-rc.8.2/validation.json and compatibility.json for exact scope.

Known limitation: development-toolchain npm audit has
7 high findings;
production npm audit has 0.
Only trusted locked build inputs are used; Node/npm/development servers are not shipped.
Real VPS/165H installation, system boot, active systemd protections, NetBird/5Mbps,
72-hour soak, ARM64 and Windows Service remain NOT TESTED. This is not production acceptance.

Start with README.md / README.zh-CN.md and docs/NETWORK.en.md / NETWORK.zh-CN.md.
Verify the independently supplied signing fingerprint, manifest signature and hashes
before executing any downloaded helper or binary. Downloading does not configure devices.

固定版本、签名和 Hash 校验后安装；应用层证书与授权需单独登记。
实机、VM 自启和目标网络仍须逐项验收，未执行项不计通过。
