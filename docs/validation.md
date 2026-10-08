# Validation record and acceptance checks

## Recorded evidence

As of 2026-10-08, the hold-to-off image is **compiled, installed, and configured** on the reference button. **Physical acceptance is pending.**

### Earlier upstream baseline

Before the hold-to-off update, the upstream EndDevice 1.1.3 image was installed on the exact reference hardware and its identity/version were read back. Five Zigbee lamps acknowledged native group membership, the button acknowledged its On/Off group binding, and the owner physically confirmed prompt group on/off with the old HA toggle automation disabled. These are historical baseline results, not a physical test of the newly installed hold-to-off image.

### Build and host tests

The hold-to-off patch passed **243 host simulation tests**, including **12 new command-contract cases** across host normal and EndDevice variants. The Python 3.14 firmware run emitted 11 upstream harness thread/output-capture warnings; there were no failing tests. The public repository also passes 19 artifact corruption/identity checks, for **262 tests total**. The later full run with pytest 9.0.3 passed all 262 tests with ten inherited output-capture warnings.

The image was compiled on Linux amd64 using the pinned source/SDK/compiler. Its 151,698-byte OTA file passed identity, length, embedded version, boot marker, CRC, and size-limit checks.

### Installed firmware and device configuration

The third normal-update attempt succeeded after a controlled five-second battery removal, reinsertion, and immediate large-key press to start within the startup fast-poll window. The [upgrade runbook](upgrade.md#start-within-the-startup-fast-poll-window) explains this procedure and why it must only be used when no previous install or payload transfer is active.

Actual transfer was observed from **22:31:00.642890 to 23:00:52.336563 UTC on 2026-10-08**, approximately **29 minutes 52 seconds**. HA's installation service completed successfully. This normal OTA took longer than the earlier stock-to-custom conversion, which took about eight and a half minutes. Neither observation is an expected timeout: monitor actual progress and completion rather than treating elapsed time alone as failure.

After the update, the device's OTA current-file-version attribute returned **285421569 / `0x11033001`**. Uncached reads of endpoint 1, input cluster `0x0007`, confirmed:

- `switch_mode` (`0xff00`): **Momentary / 1**.
- `switch_actions` (`0x0010`): **ToggleSimple / 2**.
- `binded_mode` (`0xff05`): **ShortPressLongOff / 4**.
- `long_press_duration` (`0xff03`): **1,000 ms**.

These readings establish installation and stored configuration. They do not establish that every lamp received an actual short-press or hold command. Fresh group/binding verification and the physical checks below remain to be recorded. HA-stopped independence and battery-removal persistence **after the new installation** have not been tested; the pre-update battery restart is not a persistence test of the new image.

## Before declaring a deployment successful

Record these locally, without uploading identifiers or private logs:

1. Build metadata/hash matches the artifact served by HA.
2. Runtime version is `0x11033001`; identity and loaded target quirk are correct.
3. Native group contains every intended lamp and source binding has a successful device acknowledgment.
4. Device reads back Momentary, ToggleSimple, mode 4, and 1,000 ms.
5. With all lights off, a short press switches them on **only on release**.
6. With all on, hold beyond one second: all turn off; continued hold and release do nothing further.
7. Hold again while all are off: no initial flash, no turn-on on release.
8. Create mixed lamp states using HA, then hold: every reachable group member becomes off.
9. Subsequent short presses still toggle normally. No duplicate HA button automation runs.
10. Check physical light state separately from HA state; delayed or missing reports can leave the UI stale after a successful group command.

## Separate resilience tests

Once baseline behavior is confirmed, plan these one at a time:

- **HA software stopped:** stop only the HA application while preserving coordinator/radio and network power; test the button, then restore HA. This checks application independence, not all possible Zigbee outages.
- **Button battery replacement:** remove/reinsert the proper battery, allow rejoin, then confirm settings/binding and action. Avoid reset/pair presses.
- **One lamp power cycle:** remove power once, restore it, allow startup/rejoin, then hold Off and confirm membership still works. Some lamps intentionally power on at full brightness after power restoration.
- **Range and parent recovery:** test the normal location after commissioning close to the radio. A reliable near-radio test does not establish whole-house range.

Do not combine all outages in one experiment; otherwise failures cannot be assigned to firmware, network, power, or reporting. Record partial results as partial results.

## Published build

The normal-update image and [metadata](../firmware/1.1.3-holdoff1/metadata.json) are in `firmware/1.1.3-holdoff1/`. OTA SHA-256:

```text
de84c34f5d0f9a15d8f3bf47323958121eb3e2b599f19c2e4ca389bec046e59d
```

The build's preprocessed SDK acceptance limit is 208 KiB; the inspector applies that limit to the full OTA file. The binary has no deployment credentials or live network configuration: it initializes identity and keys on the device, rather than embedding a private network backup.
