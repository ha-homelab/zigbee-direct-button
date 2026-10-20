# Changelog

## 1.1.3-holdoff.2-beta.1 — 2026-10-20

### Firmware identity

- Build fresh TS0041-TB firmware from the reviewed current sources as `1.1.3-holdoff2` / `0x11033002`. The inspector and local index reject the previous image as this candidate.
- Preserve the opt-in binding mode, target pin map and NVM schema. Existing holdoff1 binaries and deployment records remain historical.

### Security

- Restrict host-simulator NVM files to owner read/write permissions independently of umask, tighten existing files before replacing data, and reject symlinks or special files. This affects host simulation storage, not device flash.

- Bound one-based Zigbee endpoint maps, including valid endpoint 10, and reject configurations that exceed component, endpoint or cluster capacity before writing beyond their arrays. The issue was reproduced by AddressSanitizer/UndefinedBehaviorSanitizer in the shared firmware; no CVE is assigned.
- Match callback definitions to their actual scheduler/button/relay function-pointer types, eliminating undefined calls reported by Linux UBSan without changing event timing or state transitions.
- Validate stored and remotely written configuration lengths before reading strings or adding a terminator; keep token parsing inside the original terminator.
- Parse GitHub remote URLs before constructing inherited OTA index URLs, rejecting misleading hosts, credentials, fragments and unexpected paths. Explicit operator-selected `--base-url` remains a separate input.
- Verify the Telink SDK archive against the SHA-256 already recorded with the published reference build before extraction.

### Validation and documentation

- Add instrumented host simulation, C/Python/Actions static analysis and Python common-error checks. Drain host-test output threads before completing cleanup.
- Document maintenance, private reporting, licensing and complete-system assessment limits. The candidate rebuilds target firmware with OTA identity `0x11033002`; no physical acceptance or device deployment is implied.

## 1.1.3-holdoff.1

The experimental derivative adds opt-in short-release Toggle and absolute Off on hold for the exact documented TS0041/TLSR8258 EndDevice target. The repository retains source, a normal OTA image, build metadata and corruption/identity checks. Installation/configuration evidence and still-pending physical behavior acceptance are recorded separately in [validation](docs/validation.md).
