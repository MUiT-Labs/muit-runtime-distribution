# 下载通路排查与官方 API 备用入口

[English](NETWORK-TROUBLESHOOTING.en.md) · [签名验证流程](NETWORK.zh-CN.md)

固定版本 0.1.0-rc.8.2。公开附件不需要 GitHub 账户或令牌。主站、API、附件 CDN 和 codeload 是不同入口；一个入口可达不代表其它入口可达。下载失败应保留错误并换新目录重试，不能降低 TLS 或跳过签名。任何文件下载成功都不表示设备已经安装或获得 MFP/API 权限。

本阶段开发网络的 Windows 主站直连出现连接重置，自动采用的本地代理也出现停滞。干净 Debian 客户端使用 GitHub 官方公开附件 API 作独立验证；精确验证范围见版本验收摘要。该结果不能代替目标 VPS/165H 的网络验收。Windows 自带的部分 Schannel curl 无法启用 TLS1.3；可使用独立可信的 Python/OpenSSL，或在 Debian/VM 下载对应 Windows 包再传到目标机核验。

## Linux / Debian VM：发现官方附件地址

先在新目录取得元数据，列出需要的文件和各自 API URL。元数据用于发现地址，不能替代外部公钥与签名信任。

```sh
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.3 \
  https://api.github.com/repos/MUiT-Labs/muit-runtime-distribution/releases/tags/v0.1.0-rc.8.2 \
  --output release-metadata.json || exit 1
python3 -c 'import json; m=json.load(open("release-metadata.json")); [print(a["name"],a["url"]) for a in m["assets"]]'
```

选择需要的 release.json、release.sig、release.sig.json、对应 OS 的原生 muit-install，以及组件包。用表中该文件的精确 URL 和文件名替换下面两项占位值；不能直接运行占位命令。

```sh
curl --fail --location --proto '=https' --proto-redir '=https' --tlsv1.3 \
  --header 'Accept: application/octet-stream' \
  'EXACT_OFFICIAL_ASSET_API_URL' --output 'EXACT_FILENAME' || exit 1
```

直接在浏览器打开 API URL 通常显示 JSON；原始二进制需要上述 Accept 请求头。按 NETWORK 的外部公钥、原始 Ed25519 清单签名、原生引导程序 Hash 检查顺序，再进入 INSTALL。组件内第三方通知和原创分发条款继续保留。

代理异常时，可为这一次 curl 请求加 `--noproxy '*'` 选择直连。Python 验证进程可临时设置 NO_PROXY=*；这会忽略该进程的代理，不修改系统配置。需要代理的网络应由管理员提供可用通路。不要把代理密码或 GitHub 令牌写入下载材料。

传到另一台设备后重新核对同一个签名/Hash，再做 stage/check。保留旧可信版本和完整备份；不可用的网络通路标为失败或未测，不能从另一条通路的成功推断它已通过。
