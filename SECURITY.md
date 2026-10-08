# Security and privacy

This is a public source repository. Building it requires internet access for public dependencies but no HA token, network key, private address, or physical device identifier.

Keep these outside Git, build artifacts, screenshots, issues, and CI logs:

- ZHA network backups, network/link keys, coordinator dumps, and raw device flash readouts.
- HA access tokens, secrets/configuration containing credentials, `.env` files, private keys, and Terraform state.
- Live device/entity registries, IEEE/MAC identifiers, private network addresses/hostnames, and raw diagnostic logs.
- Personal location, room occupancy history, and account identifiers.

The `.gitignore` is a convenience, not a secrecy guarantee. Inspect staged changes before each public push and scan release bundles. Firmware source contains generic hardware names and pin maps; those are intentional and do not identify a particular household.

Use placeholders in reports. Include the exact public firmware version/hash, hardware manufacturer/model, sanitized symptom, and whether failure occurred before transfer, during transfer, after boot, or during group control. Share sensitive evidence only through a maintainer-provided private channel. Never post a network backup to a public issue to demonstrate a bug.

Experimental firmware can leave a device needing wired recovery. Match the exact board and image type, keep a recovery record, and verify artifact integrity before flashing. Do not distribute downloaded SDK/compiler files as if the project's license covers them; their own licenses apply.
