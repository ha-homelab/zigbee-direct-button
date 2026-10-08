# Validation record and acceptance checks

## Recorded evidence

As of 2026-10-08:

- The upstream EndDevice 1.1.3 image was installed on the exact reference hardware. The installed runtime identity and version were read back.
- Five Zigbee lamps acknowledged membership of a native group; the button acknowledged its On/Off group binding.
- The owner physically confirmed prompt group on and off with the old HA toggle automation disabled.
- The hold-to-off patch passed **243 host simulation tests**, including **12 new command-contract cases** across host normal and EndDevice variants. The Python 3.14 run emitted 11 upstream harness thread/output-capture warnings in the firmware run; there were no failing tests. The public repository also passes 19 artifact corruption/identity checks, for **262 tests total** (eight inherited output-capture warnings in that run).
- The new hold-to-off binary was compiled on Linux amd64 using the pinned source/SDK/compiler. Its 151,698-byte OTA file passed identity, length, embedded version, boot marker, CRC, and size-limit checks. Hardware installation and physical acceptance remain pending; do not infer these from the earlier upstream Toggle test.
- HA-stopped independence and actual battery-removal persistence have not yet been physically recorded.

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
