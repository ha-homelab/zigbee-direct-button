# Changelog

## Unreleased

### Security

- Bound one-based Zigbee endpoint maps, including valid endpoint 10, and reject configurations that exceed component, endpoint or cluster capacity before writing beyond their arrays. The issue was reproduced by AddressSanitizer/UndefinedBehaviorSanitizer in the shared firmware; no CVE is assigned.
- Parse GitHub remote URLs before constructing inherited OTA index URLs, rejecting misleading hosts, credentials, fragments and unexpected paths. Explicit operator-selected `--base-url` remains a separate input.
- Verify the Telink SDK archive against the SHA-256 already recorded with the published reference build before extraction.

### Validation and documentation

- Add instrumented host simulation, C/Python/Actions static analysis and Python common-error checks. Drain host-test output threads before completing cleanup.
- Document maintenance, private reporting, licensing and complete-system assessment limits. No new target firmware, physical acceptance or device deployment is implied.

## 1.1.3-holdoff.1

The experimental derivative adds opt-in short-release Toggle and absolute Off on hold for the exact documented TS0041/TLSR8258 EndDevice target. The repository retains source, a normal OTA image, build metadata and corruption/identity checks. Installation/configuration evidence and still-pending physical behavior acceptance are recorded separately in [validation](docs/validation.md).
