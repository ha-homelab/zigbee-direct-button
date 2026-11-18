# Documentation

Custom firmware for a battery Tuya Zigbee button that talks to Home Assistant
directly, with the build, upgrade and validation records for it.

## Understand it

- [Design and compatibility](design.md) — the supported board, its stock identity and the radio it uses.
- [License assessment and distribution scope](license-assessment.md) — what the upstream grant allows and what this distribution includes.
- [Quality and OpenSSF assessment boundaries](quality.md) — what the firmware, HAL code and helpers are checked against.

## Build and install

- [Build, inspect and trace an image](build.md) — the host simulation and the toolchain it needs.
- [Home Assistant / ZHA configuration](home-assistant.md) — example entities for the opt-in beta, with placeholders.
- [Backup and upgrade runbook](upgrade.md) — the two distinct transitions from stock and from an already-converted button.
- [ZG-1012S V2.0 / TS0044 commissioning](zg101zs-v2-bringup.md) — an experimental hardware investigation, not a supported target.

## Recover and verify

- [Recovery and rollback](recovery.md) — the cluster and attribute writes that restore momentary behaviour.
- [Troubleshooting](troubleshooting.md) — battery, contact pressure and why an LED proves little.
- [Validation record and acceptance checks](validation.md) — what was compiled and installed by 2026-10-08, and what was not.
