# Real-device acceptance / 实机验收

Release 0.1.0-rc.8.2 / source 95aab60b7997e97593d9af2f31e44e6c67b9177f. This is an empty operator template, not a PASS report. Local container tests do not populate real-device results.

Record device/VM asset, OS/kernel/architecture, CPU/RAM/disk/filesystem, UTC/operator, release hashes/key ID, application versions, private configuration version, public certificate fingerprints and authorized network scope. Keep private keys/passwords, production addresses and raw data out of public reports.

| Check / 检查 | Expected evidence | Result |
| --- | --- | --- |
| Anonymous download, independent trust | Exact version, source/asset hashes, signature checks | NOT TESTED |
| Install and safe configuration | Separate identities/directories; existing config/data retained | NOT TESTED |
| mTLS/application authorization | Verified CA/SAN/expiry; authorized Node/Stream/Sink only | NOT TESTED |
| NetBird/MTU/actual5Mbps | Peer/DNS/route/TLS and measured throughput | NOT TESTED |
| Service boot/resource protection | Actual non-root boot, limits/namespace/write protections | NOT TESTED |
| Real Source to COMMITTED | Batch ID, compressed hash, PG commit, receipt, Cursor and independent counts | NOT TESTED |
| Network/ACK loss and replay | No duplicate records, retained original receipt, continuous Cursor | NOT TESTED |
| Hash conflict and persistence failure | ACK_CONFLICT isolation; no premature COMMITTED | NOT TESTED |
| Forced exit and full machine restart | WAL/Spool recovered; no silent committed loss | NOT TESTED |
| Multiple Sink isolation | Healthy target progresses while failed target retains responsibility | NOT TESTED |
| Spool pressure and sequence gaps | Bounded backpressure, visible quality gaps, no unsent overwrite | NOT TESTED |
| Certificate/configuration conflicts | Explicit refusal; valid state preserved | NOT TESTED |
| Complete backup/new-target restore | Payloads and original receipt/cursor reconciled | NOT TESTED |
| Upgrade/rollback/uninstall | Compatible code, retained state/config/backup; no data wipe | NOT TESTED |
| 72-hour observation | Actual CPU/RSS/IO/WAL/link/quality and end-to-end reconciliation | NOT TESTED |

Host/service/database/network changes require the corresponding device authorization. Record executed commands, actual output/evidence, failures and recovery, remaining risks and acceptance owner; leave every unexecuted item NOT TESTED.
