# Maintenance roadmap

Priorities for October 2026 through October 2027:

- Preserve exact-board compatibility and the distinction between simulated command behavior, installed-version evidence and physical acceptance.
- Fix memory-safety findings in the shared firmware and maintain normal plus AddressSanitizer/UndefinedBehaviorSanitizer host tests; extend analysis to platform-specific HAL and linked SDK components.
- Review the complete Zigbee commissioning, key lifecycle and OTA trust boundary. Existing protocol compatibility does not establish a complete cryptographic qualification.
- Resolve the redistribution and corresponding-source status of linked prebuilt SDK libraries; retain original upstream and SDK notices.
- Keep Python tooling, build inputs and source/download provenance current, and add malformed-input regressions for real findings.
- Establish an actual backup maintainer and access-recovery process before claiming continuity.

These are priorities, not promised delivery dates. Other boards, physical household acceptance and new vendor protocols require separate evidence.
