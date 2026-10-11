# ZG-1012S V2.0 / TS0044 commissioning

This is an experimental hardware investigation, not an additional supported
firmware target. The working TS0041 image must not be installed on this remote.

## Stock device evidence — 2026-10-10

The owner reports a four-key board marked `ZG-1012S V2.0` and two CR2032 cells.
The printed name may resemble `ZG-101ZS`; keep that ambiguity until the board
photograph establishes it.

Pairing with the existing CC2652 coordinator through ZHA succeeded. The device
reports:

- model `TS0044`, manufacturer `_TZ3000_wkai4ga5`;
- application version 131, hardware version 1, software build `0122052017`;
- four endpoints, with the `TuyaSmartRemote0044TO` quirk;
- manufacturer-specific press events through On/Off cluster `0x0006`;
- Time and OTA output clusters on endpoint 1, with no standard On/Off or
  Level Control output clusters.

One physical short press from each of the four keys was received as a distinct
`remote_button_short_press` event. ZHA also declares double-press and long-press
triggers for all four keys; those gestures have not yet been physically tested.
Stock firmware is therefore usable through HA automations. Standard direct
lamp binding is not provided by the observed stock endpoints and commands.

## Confirmed processor, unverified pin map

The owner read `TLSR8258` on the physical chip. This establishes the Telink
family for this specimen; it does not establish its GPIO map or prove that all
boards sold under the same name use that processor.

The inherited `REMOTE_TUYA_TS0044` entry uses the same manufacturer/model but
describes a ZS3L / EFR32MG21 board powered by CR2430. The separate
`REMOTE_HOBEIAN_TS0044` entry describes Telink TLSR8253 hardware with a different
manufacturer string. Neither identity match alone proves that its binary or
GPIO map fits this board.

The diagnostic profile has no assigned GPIOs while the key/LED pin map remains
unknown. The upstream parser supports a clean
device with only Basic, OTA and Poll Control services, allowing subsequent
configuration over Zigbee. Such a profile is for commissioning, not normal
battery operation.

## Prepared diagnostic image

`scripts/build_zg101zs_probe.sh` builds an EndDevice with the configuration
`wkai4ga5;TS0044-ZG101-PROBE;`. It intentionally assigns no keys, LEDs, relays or
battery ADC. The image is temporary: without a battery input the current
firmware uses a faster polling policy, so this is not a finished battery device.

The Linux amd64 build, all 262 host tests and the Telink OTA structure/CRC
validation succeeded. The probe quirk imported successfully against the
installed HA dependencies and retained standard Basic attributes:

- runtime version `0x11033002`, image type `0xF100`, manufacturer `0x1141`;
- normal OTA image size: 151,682 bytes;
- normal OTA SHA-256:
  `0860e01571061c1cde0f7d3e064dc30160f684c66abcdb258863fab6e3604f43`.

This normal-update image is **not** a stock-conversion image. No compatibility
claim follows from a successful build, and it has not been offered to stock
firmware.

## OTA check: stock firmware explicitly rejects the request

The initial attempt failed with `NWK_NO_ROUTE`. After the owner resumed the
test near the coordinator, short-press events from all four endpoints arrived;
the capture also contained double-press events from endpoint 1. Battery reports
and prompt replies established two-way radio communication.

Four `image_notify` requests on endpoint 1, output cluster `0x0019`, received
`DefaultResponse(command_id=0, status=0x81 / UNSUP_CLUSTER_COMMAND)`. Reads of
current file version (`0x0002`), manufacturer (`0x0007`) and image type (`0x0008`)
each received `0x86 / UNSUPPORTED_ATTRIBUTE`. These are explicit replies from
the remote, not sleep-related timeouts. The HA update entity still has no
installed or available OTA version.

The standard OTA path is therefore unavailable in the observed stock state.
An advertised OTA cluster alone does not establish implemented OTA support.
No image, conversion entry or probe quirk was installed in HA, no update was
started, and no firmware bytes were transferred. Temporary debug logging and
the wake-and-notify listener were stopped. The stock remote remains paired.

## Next step: identify a wired read/write setup

The owner deferred wired flashing and chose to use the existing paired stock
remote for now. No firmware, button assignments or direct bindings were changed.
Short-press events from all four keys are verified; ZHA also exposes double and
long presses. Double-press events were observed on endpoint 1, while deliberate
long-press acceptance remains untested. Stock events can drive HA automations
once the owner chooses the button assignments. The hardware work below is a
deferred continuation, not an active flashing operation.

The next commissioning step is to identify the actual board's SWS, ground,
power and optional reset pads, then read its own factory flash before erasing
or writing anything. Do not copy the V3.2 board's GPIO or header layout to V2.0.
There was no attached USB serial programmer on the workstation or build host
at this checkpoint; the adapter model and board photographs are still needed.

Select tooling after identifying the adapter. The upstream TX-only web writer
is not a flash-backup tool. `TLSR825xComFlasher.py` supports reads as well as
writes, but its author documents adapter restrictions, including FTDI and
adapters with LEDs on RX. `TlsrPgm.py` is a different protocol requiring a
programmer running TLSRPGM firmware, not just an arbitrary USB serial adapter.
Use the appropriate documented wiring and verify repeatable full reads before
choosing erase ranges or a board configuration.

## Recovery and scope

A fresh, complete ZHA network backup and a consistent SQLite backup were
captured privately, along with HA configuration, registries, quirks and OTA
files. They are outside this public repository on an encrypted workstation.
They do not constitute a dump of this remote's factory flash.

The owner authorized experimental conversion of one remote and accepts the
possibility of losing it. No other remote or existing light binding is part of
that experiment. No image has been offered or transferred to this target yet.

Record the verified processor, image hashes, exact GPIO profile, OTA result and
post-conversion physical tests here before describing the board as supported.

## References

- [Inherited device database](../device_db.yaml)
- [Upstream TS0044 investigation](https://github.com/romasku/tuya-zigbee-switch/issues/171)
- [Upstream HOBEIAN investigation](https://github.com/romasku/tuya-zigbee-switch/issues/237)
- [Pinned upstream Telink wired guide](https://github.com/romasku/tuya-zigbee-switch/blob/ec57f81b89e7755c4a8833cc6cb081ba3cdda227/docs/flashing/telink.md)
- [UART SWire reader/writer and adapter restrictions](https://github.com/pvvx/TlsrComSwireWriter)
- [TLSRPGM programmer hardware and read/write commands](https://github.com/pvvx/TLSRPGM)
- [Backup and upgrade procedure](upgrade.md)
