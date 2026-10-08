# Backup and upgrade runbook

Read [compatibility](design.md) first. There are two distinct transitions: stock Tuya to upstream custom firmware, and an already-converted button to this hold-to-off build. They use different OTA image types.

## 1. Capture a private recovery point

Before either transition:

1. Create and download a fresh **ZHA network backup**, and verify it is complete. It contains network keys; store it in a private encrypted location.
2. Back up HA configuration, relevant custom quirks/OTA provider files, device/entity registries, and the affected automations. Use HA's supported backup process or a consistent SQLite backup for a live Zigbee database; copying the database without its WAL is not a reliable live backup.
3. Privately record the device IEEE address, manufacturer/model, installed firmware, endpoint list, settings, group IDs/members, and verified bindings.
4. Preserve hashes and an offline copy of the known-good firmware. A coordinator network backup is **not** a dump of the button firmware, its flash, or all per-device binding tables.
5. Keep a working HA/dashboard or physical control path for the lights during commissioning. Disable the old button-triggered HA toggle automation before enabling direct control, to avoid duplicate commands.

No backup files, IEEE addresses, keys, live registries, credentials, or raw debug captures should be committed to this public repository.

## 2. Prepare power and radio

Use the battery size specified by the actual holder. The reference unit contained **CR2450** even though an upstream database entry mentions CR2430. Both are nominal 3 V, but a CR2430 is thinner; a lit LED is not proof of stable contact under OTA load. Prefer the correct battery and secure contacts.

Place the button near the coordinator or a known reliable router, ideally in the same room. A meter through a floor is not equivalent to an unobstructed meter. Keep the Zigbee network and HA stable while updating. How the device wakes depends on its currently installed firmware. The stock conversion and the already-converted firmware need different preparation; see the relevant section below.

## 3A. Only if still on stock Tuya firmware

The pinned upstream release provides a separate **`-from_tuya.zigbee`** conversion image for the exact board. Its OTA header uses manufacturer **4417**, image type **54179**, and version **`0xffffffff`** as a conversion marker. The converted runtime uses image type **45636**, identity `TS0041-TB` / `mrpevh8p`, and upstream version **`0x11033000`**.

Use the EndDevice image from the pinned [upstream release artifact directory](https://github.com/romasku/tuya-zigbee-switch/tree/37f72be3501cc5f691f857dfa6dc6e52a7c39e51/bin/end_device/REMOTE_TUYA_BUTTON_TS0041_END_DEVICE), not a Router or another TS0041 build. The provenance manifest records reference hashes. Follow the [upstream flashing guidance](https://github.com/romasku/tuya-zigbee-switch/tree/ec57f81b89e7755c4a8833cc6cb081ba3cdda227/docs/flashing) and verify actual image metadata before serving it.

Do not feed the hold-to-off normal-update image to a stock device or modify its header to pretend it is a conversion image. Conversion changes identity and OTA layout; it is not just a version bump.

After conversion completes, allow the automatic interview/rejoin to finish. Confirm the new identity, installed version, custom quirk, and endpoints. Reconfigure/re-interview before considering removal and re-pairing. UI identity may briefly remain cached. Never remove, reset, or re-interview a device during an active transfer.

## 3B. Upgrade an already-converted button

1. Build or obtain the trusted **hold-to-off** image and validate its hash and metadata using [the build guide](build.md).
2. Install `examples/home-assistant/tuya_direct_button.py` and the local OTA provider configuration from [the ZHA guide](home-assistant.md). Keep only one custom quirk registering this target; replace or narrow an old broad quirk rather than stacking conflicting registrations.
3. Generate a local index for the image. Confirm the exact button's update entity offers **`0x11033001`**, currently reports the expected older version, and is not already updating.
4. For the converted upstream **1.1.3 / `0x11033000`** battery firmware, prepare the guarded update-after-wake script and use the controlled startup procedure below. Repeated working-key presses alone do not reopen its fast-poll window. Do not touch the reset/pair key.
5. Watch actual byte/percentage progress and completion. `in_progress: true` without any progress means HA may only be waiting; it does not prove firmware bytes were transferred. Do not start a second updater after a disconnected browser or SSH session: read the live state first.
6. After 100%, wait for the device to restart and HA to query/re-interview it. Read the installed firmware from the device: **`0x11033001`**, `TS0041-TB` / `mrpevh8p`. A successful service call or a downloaded file is insufficient.
7. Only then configure mode 4 and the 1,000 ms threshold, read them back uncached, and execute [the physical checks](validation.md).

The original reference conversion took about eight and a half minutes. OTA duration depends on block size, radio conditions, retries, and sleep behavior; that timing is not a deadline for this image.

### Why an ordinary press may not wake the updater

In the converted upstream battery firmware, the default startup fast-poll window lasts **10 seconds**, polling every **500 ms**. It then returns to a **120-second** long-poll interval. These are firmware defaults; previously stored Poll Control settings can change them. Source inspection and host simulation confirmed that an ordinary large-key press sends its bound Toggle and reports but **does not itself re-enter fast polling**. A working light switch therefore does not prove that the button is promptly receiving coordinator requests.

In the observed HA/ZHA version, `update.install` first waits for a Poll Control bind and writes a **30-second** fast-poll timeout before sending `image_notify`. An update attempt timed out during this preparation without transferring image bytes, despite successful ordinary key presses. The short-press technique that helped the earlier **stock Tuya conversion** is not sufficient evidence that the converted firmware is ready for a subsequent OTA.

### Start within the startup fast-poll window

Use [the example HA script](../examples/home-assistant/update-after-wake.yaml) to remove the delay between a physical wake and starting the service. It uses no credentials or additional Python packages.

1. **First prove the previous install has finished or failed and no image payload is transferring.** Check the live update state, completion/error, and progress. If an install is still active, its status is ambiguous, or image blocks are moving, do not remove the battery. A lack of visible percentage by itself is not permission to interrupt it.
2. Replace both example entity IDs throughout the script with the exact button's firmware-update and press-action sensor entities. Add the entry to the HA script configuration and reload scripts while no update is active. Keep the existing direct binding and leave the old HA Toggle automation disabled.
3. Confirm installed version `0x11033000`, offered version `0x11033001`, and `in_progress: false`. Start the script and confirm its trace is **waiting for a trigger**. The script checks those guards before waiting and again immediately before calling `update.install`; a failed guard stops it. `mode: single` prevents overlapping runs of this script, but do not start another updater separately.
4. With the update confirmed idle, remove the button battery for **five seconds**, reinsert it, and immediately press the large working key **once**. Do not hold the key during battery insertion, and do not press Reset/Pair. Aim to start the service within the default ten-second startup window. This ordinary key press may toggle the bound lights, which is expected with the existing mode.
5. The script waits for the exact press-action sensor state **`press`**, not `pressed`, for up to ten minutes. It then rechecks the version/idle guards and requests only version `0x11033001` for that button. A timeout stops the script; it does not force an install. The script cannot distinguish an ordinary later press from a startup press, so cancel it if abandoning the prepared startup attempt.
6. Watch for actual image-block or percentage progress. Once transfer begins, leave the battery, coordinator, and HA running. If preparation fails again with no payload, let that install end, inspect the error, and re-establish the idle state before considering another controlled attempt. Do not power-cycle in response to a slow active transfer.

This startup-window procedure addresses the observed pre-transfer failure. It is a commissioning method, not a claim that a subsequent transfer or physical hold-to-off test has succeeded. Continue through version readback and the acceptance checks above.

## 4. Close out

Keep only the intended normal-update provider entry active. Remove temporary force/conversion entries after their job is complete. Close permit-join when finished. Restore temporary debug logging. Save the installed version, hashes, settings, bind acknowledgment, group membership, and physical test results in a private deployment record. The public validation record should contain only sanitized results.
