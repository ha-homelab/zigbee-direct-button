# Recovery and rollback

## Restore the former short-press behavior without flashing

Set endpoint 1 cluster `0x0007`, attribute `0xff05`, to **PressStart / 1**, then read it back. Keep Momentary and ToggleSimple. This returns to the former press-start Toggle path using the current firmware. Existing native group membership and binding do not need to be recreated just to change this setting.

Do not turn the old HA Toggle automation back on while direct Toggle remains bound; that can produce two commands per press.

## Return to the known-good upstream custom firmware

1. Back up current state privately.
2. **Set mode 1 before downgrade.** The upstream `0x11033000` implementation does not understand the new value 4.
3. Obtain the exact matching upstream EndDevice normal-update image, validate its identity/hash, and preserve your current artifact as well.
4. Use the explicitly supported downgrade/force mechanism for the installed ZHA/OTA stack. The normal OTA version check will not offer an older file automatically. Do not casually rewrite image headers or keep a force provider active indefinitely.
5. Keep power stable, wait for completion and re-interview, then read back firmware, settings, group membership, and binding. Repeat physical tests.
6. Remove temporary force entries and restore routine logging/permit-join state.

This repository intentionally does not provide a one-click force-flash script. Downgrade selection and safeguards vary by HA/zigpy version, and a forced header alone does not establish a safe image.

## Factory firmware is a different recovery operation

A ZHA backup restores network/coordinator information; it is not the button's original firmware. An upstream factory reference dump is not this device's full private flash backup. Writing another unit's MAC/network/calibration data indiscriminately can damage identity or radio behavior.

Returning to factory firmware may require opening the device, a Telink-compatible programmer, the correct pinout/voltage, and an appropriate original dump. Read the pinned upstream hardware/flashing documentation and make a complete private readout before a wired erase/write. USB-to-serial access to a coordinator does not automatically provide programming access to the button's Telink flash.

## Reset behavior and accidental resets

The pinned custom firmware supports reset through the dedicated pairing/reset input and through a rapid multiple-press sequence; the reference configuration uses a roughly two-second dedicated reset hold and ten rapid working-key presses. Treat these as destructive commissioning controls, not ways to keep an OTA awake. Do not use them during a transfer.

A single ordinary battery replacement or bulb power cycle is not a factory reset. Repeated timed power cycles can be the reset command for some lamps. For the reference CREE Connected A-19 lamps, consult the [manufacturer FAQ](https://cms.creelighting.com/app/uploads/dlm_uploads/2021/09/faq-connected-oct26_1.pdf) before cycling power: its reset procedure intentionally repeats a timed on/off sequence.

After a deliberate factory reset, expect to join the device again and recreate/verify groups, binding, and settings. HA may retain a friendly name, but that does not prove the physical device still holds its previous membership.
