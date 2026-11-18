# MUiT installation and recovery · English

[简体中文](INSTALL.zh-CN.md). Public pre-release 0.1.0-rc.8.2. Application source remains private; components, installation tools and guides are publicly downloadable. Real VPS/165H deployment, NetBird, boot/startup, 5Mbps capacity and a72-hour soak require device authorization and actual evidence.

## Components and bootstrap trust

Collector, Receiver, Web and Tools are separate archives. Candidate targets are Linux amd64 and Windows amd64; a build is not proof of every target's deployment support. Windows uses portable foreground execution; Linux/Debian VMs have systemd units. Receiver requires a separately provisioned PostgreSQL database. Complete backup/restore additionally requires compatible `pg_dump` and `pg_restore` clients. No CA private key, database engine, NetBird enrollment or device credential is bundled.

Linux amd64 requires Debian12+ and system glibc>=2.36; glibc is not bundled. Public exchange TLS on Linux also requires system ca-certificates and a correct clock; the MFP private CA is separate. Only local filesystem validation has evidence; network filesystems require separate tests.

The signed release manifest binds source Commit/dirty state/source digest, versions, migrations, every component and bootstrap executable's size/SHA-256. Obtain and pin trust.json/trust.pem independently from an authorized administrator. A key or checksum accompanying an untrusted download is insufficient. This release uses a separate publication identity with raw Ed25519 key ID 7644ee621f5fb4e9443c47bcb42ce7e9800826bbc015cc864667a8a9d84f759e. It is distinct from the Stage7 development key, device identity and mTLS CA.

Before executing a downloaded Linux bootstrap, use a trusted OpenSSL and Python 3.11+:

```sh
openssl pkeyutl -verify -pubin -inkey /secure/trust.pem -rawin -in release.json -sigfile release.sig
python3 -c 'import json,hashlib,pathlib; m=json.load(open("release.json")); a=next(x for x in m["bootstraps"] if x["os"]=="linux" and x["arch"]=="amd64"); p=pathlib.Path(a["file"]); assert p.stat().st_size==a["size"] and hashlib.file_digest(p.open("rb"),"sha256").hexdigest()==a["sha256"]'
chmod 755 ./muit-install_linux_amd64
./muit-install_linux_amd64 verify --manifest ./release.json --signature ./release.sig.json --public-key /secure/trust.json --components collector,web,tools
```

The running services need neither Python nor Node/npm. On Windows and Linux, follow NETWORK.en.md to verify the downloader itself, then download verified native bootstraps. Downloaded executables always require independent verification first. Never pipe an unverified download to a shell.

## Preflight and local installation

Run `muit-install preflight --root <existing-directory>` to record actual OS/arch/CPU/free space and UTC. Separately check target Debian/kernel, RAM/swap, disk/inodes/mounts, existing ports/services, SSH/rescue access, NTP, NetBird/DNS/routes/MTU, Receiver CA/enrollment and effective network capacity. Unknown values remain UNKNOWN. Management defaults to loopback; use only a verified NetBird address and matching SAN for remote access.

The following system-root commands are for explicitly authorized hosts. For development/Windows use an isolated root such as D:\MUiT-local. Example release 0.1.0-rc.8.2 must match the actual signed manifest.

```sh
./muit-install_linux_amd64 stage --root / --manifest ./release.json --signature ./release.sig.json --public-key /secure/trust.json --assets . --components collector,web,tools --apply
./muit-install_linux_amd64 activate --root / --release 0.1.0-rc.8.2 --components collector,web,tools --apply
./muit-install_linux_amd64 init --root / --components collector --apply
```

For a Receiver host select receiver,tools, then initialize receiver. Stage adds immutable releases, activate atomically changes code pointers, and init preserves existing configuration. `/opt/muit/releases/<release>/<component>` holds code; `/opt/muit/installed.json` holds active/previous pointers; `/etc/muit/{collector,receiver}` holds private configuration; `/var/lib/muit/{collector,receiver}` holds responsibility data. Program upgrades do not overwrite configuration or data. Collector's current implementation uses collector.db and Spool subdirectories at the same root; preserve this existing flat state layout.

## Provision before starting

- Use the installed collector/bin/muitctl `identity init` with a new node file, actual Asset ID and Root DID reference. Preserve the existing identity on upgrades.
- `muit-install cert --action csr --out-dir <private-tls-directory> --name server --common-name <name> --dns <management-dns> --ip 127.0.0.1` creates only an Ed25519 private key and CSR. Get the server chain signed through your controlled CA and save server.pem. Receiver additionally needs client-ca.pem. Never send keys through chat or public Git.
- `cert --action inspect --certificate ... --key ... --ca ... --usage server --server-name ...` verifies key pairing, trust, SAN, usage and expiry (24 hours remaining by default). For clients use `--usage client`. Validate replacement certificates before a controlled stop/replace/restart and update leaf-fingerprint enrollment; never disable verification.
- Empty Collector authorization is intentionally unusable. An initial administrator may explicitly issue `access --authorization <file> --credential-out <new-private-file> --role Owner --owner --kind session --ttl 1h`. Tokens are written only to a private file; authorization stores hashes. Other roles require a reviewed grants array; health automation uses a separate least-privilege bearer. Restart to load authorization changes; expiry is never extended automatically.
- Collector settings start with a 2GB quota, no Receiver and no acquisition lease. Add private endpoint references and client certificate/key/CA paths only after verification. Receiver grants bind leaf fingerprint, service identity, Node, Stream and Sink. A time-limited run_authorization epoch/expires_at is required for acquisition; apply it through the documented local settings/restart process.
- Replace Receiver pg_service.conf examples with a dedicated existing database/role and verified CA. Prefer a restricted passfile; keep passwords out of argv/logs. An authorized database operator explicitly runs `muit-receiver migrate` using private PGSERVICEFILE and MUIT_RECEIVER_DSN='service=muit_receiver', then checks it. The installer never automatically migrates a production database. The backup role needs dump/table-lock privileges; this must not grant the normal runtime role CREATE/DROP DATABASE.

## Checks and services

`muit-install check --root <root> --components collector` validates configuration and the existing ledger without a listener/acquisition/migration. Receiver check includes its actual database. `run` starts the corresponding foreground process. A default template is a pending configuration, not a successfully running installation.

On an authorized Linux host only, `service --component collector --action prepare --apply` creates the dedicated user and reviewed unit/bootstrap files but does not enable/start it. Use separate enable/start/stop/disable actions. Receiver uses component receiver and its independent account. Differing existing service/bootstrap files are refused for manual review. Windows has no claimed Windows Service auto-start support; use foreground mode and Ctrl+C.

systemd runs as muit/muit-receiver with restricted write paths, no new privileges, process/file limits and memory/CPU budgets. Collector's defaults are GOMEMLIMIT=600MiB, MemoryHigh=800M, MemoryMax=900M and CPUQuota=150%; measure on the target. JSON logs use the isolated MUiT journal namespace (128M persistent/32M runtime/7 days), leaving global journal limits unchanged. Inspect with `journalctl --namespace=muit -u muit-collector.service` and systemctl show.

The muit-runtime group grants traversal of shared 0750 parent directories only; component subdirectories/keys have separate dedicated groups. Ordinary interactive/root accounts are refused as service identities. Endpoint/CA changes use a new endpoint reference while retaining the old binding/trust for outstanding delivery responsibilities.

Health uses verified TLS 1.3: `muit-install health --url https://127.0.0.1:8444/api/v1/health --ca <management-ca> --bearer-file <private-getHealth-token>`. Receiver /healthz additionally needs enrolled mTLS client-cert/client-key. HTTP 200, success=true and code=OK are all required. Health alone does not prove Source data, durable commits or Cursor reconciliation.

## Backup, upgrade, rollback and recovery

Verify/stage the new release before downtime. Stop/drain affected services, record active/previous versions and take a complete snapshot using the running version's muitctl:

```sh
muitctl state backup --state-dir <collector-state> --backup-dir <new-private-snapshot> --apply
muitctl receiver backup --state-dir <receiver-archive> --backup-dir <new-private-snapshot> --pg-service-file <private-service-file> --pg-service <source-service> --pg-bin <client-bin-directory> --apply
```

Collector holds the process lock, captures SQLite WAL using Backup API and copies pending/inflight/sent/quarantine/groups. Receiver holds its archive lock and metadata SHARE locks for a consistent PostgreSQL custom dump plus Parquet; any missing committed file rejects a complete backup. pg_dump/restore read private service files, never passwords in child argv. Snapshots contain private business data and need restricted storage plus an external encrypted copy/snapshot. Same-disk backups do not cover disk loss.

Separately back up configuration JSON, node identity, version manifests and audit handoff privately. Data snapshots do not include TLS keys, database passwords or external credentials. Encrypt production configuration backups and provision secrets/certificate enrollment again through controlled channels after recovery.

Activate only compatible protocol/migration lineage, then check/start/health and verify actual Source state, pending delivery, COMMITTED receipts, Cursors and counts. Acquisition needs explicit restart. If validation fails, stop the new service, preserve evidence/new data and use `rollback --root <root> --components collector,web,tools --apply`, followed by checks and reconciliation. Rollback changes code pointers; it never restores an old DB or deletes Spool. Changed/unknown migrations require a separate ADR and migration/recovery plan.

Installer format 1 accepts the compatible 0.1.x runtime family with the same MFP/API and identical migration history; 0.2.x/new migrations are refused. Staging is atomic per component: after partial failure, verify completed components and stage only missing ones before activation. Windows publication retries transient sharing/access conflicts for about one second without changing ACLs or replacement rules. A persistent error leaves the original backup/package intact; release the handle and use a new restore target. Snapshot inventory is bounded to 100,000 files/32MiB metadata; larger archives require a separately planned volume/segmented backup, never silently omitted files.

```sh
muitctl state restore --backup-dir <complete-snapshot> --state-dir <new-nonexistent-state-directory> --apply
muitctl receiver restore --backup-dir <complete-snapshot> --state-dir <new-nonexistent-archive-directory> --pg-service-file <private-service-file> --pg-service <new-empty-target-database-service> --apply
```

Receiver restore performs no DROP/CLEAN/CREATE DATABASE and uses one pg_restore transaction. New archive files remain for inspection on failure. Rebind private paths/secrets and verify original Batch replay returns the original Receipt/Commit ID without duplicate business rows and with the expected continuous Cursor. Do not overwrite existing directories as a recovery method. Uninstall by stopping/disabling services and removing only reviewed program/service files; keep configuration, state, backups and quarantine by default.

## Acceptance

Record actual platform, Commit/asset Hash, UTC/operator, NetBird, certificate fingerprints, configuration versions, resource/link measurements, Batch ID/compressed Hash/Receiver Commit ID/Cursor and independent counts. Exercise acquisition, restart/boot, outage/replay, lost ACK, persistence failure, multi-Sink isolation, pressure and restore; run the planned 72-hour observation. Templates, budgets and container results never become real-device PASS.
