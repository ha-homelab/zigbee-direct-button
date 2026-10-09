# Experimental normal-update image

This build targets only the already-converted `TS0041-TB` / `mrpevh8p` Telink battery EndDevice. It is not a stock Tuya conversion image.

Read the [upgrade runbook](../../docs/upgrade.md) and [validation record](../../docs/validation.md) before installation. The image has been compiled, structurally validated, installed on the reference button, and configured for a 1,000 ms hold using mode 4. The device reports `0x11033001`, and its settings were read back uncached. **Physical acceptance of short press and hold remains pending**; the earlier upstream Toggle test does not establish the new behavior. The successful normal OTA took about 29 minutes 52 seconds, compared with about eight and a half minutes for the earlier stock conversion. Use `metadata.json` and `SHA256SUMS` to verify your copy. `index.json` is a local-provider example whose image must remain in the same directory.

A post-update HA snapshot also confirms five registered native-group members, five lamp entities in the HA helper, and the old HA Toggle automation disabled. These are registration/state checks; they do not replace fresh radio acknowledgments or the pending physical acceptance tests.

The application source is MIT; compiled SDK components retain the [Telink SDK license](../../licenses/TELINK-APACHE-2.0.txt). See [third-party notices](../../THIRD_PARTY_NOTICES.md).
