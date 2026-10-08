# Troubleshooting

## Button LED is faint, device disappears, or OTA stops early

Check the correct battery size, charge, and contact pressure. A visible LED proves little about voltage under transmit load. The reference project encountered failures near 7% and 10%; success followed battery/contact work plus a ZHA reload, so the evidence does not isolate one cause. Avoid treating every stall as firmware corruption. Read the installed version before retrying.

## Update says “in progress” but no bytes arrive

The service may be waiting for the sleepy device. Briefly press the large working key with pauses, then watch actual image-block or percentage progress. Do not hold Reset/Pair. Confirm image type, model filters, and offered version. Stop repeated presses once transfer is continuous. A mismatched image will not become correct by repeatedly restarting the update.

## Update reached 100% but the UI still shows the old model

Allow restart, version query, and automatic interview to finish. The reference system briefly showed a cached stock identity while the new firmware was being discovered. Read actual firmware/identity and inspect interview status. Use Reconfigure after the active update completes if necessary. Do not remove/re-pair while flashing; it can destroy useful configuration without fixing a UI cache.

## ShortPressLongOff is missing, or selecting it has no effect

Check the loaded target-only quirk, duplicate registrations, installed firmware, and actual device attribute values. Reload through the supported HA lifecycle or restart if required. The quirk alone cannot add behavior to an upstream image. Only enable mode 4 on `0x11033001` or a later known-compatible build. Ensure the input is Momentary and duration is 1,000 ms.

## One press turns lights on and immediately off

The old HA event-to-Toggle automation may still be running alongside direct binding. Disable that specific automation and retry. Check for duplicate bindings or other automations as a separate step. One group Toggle is intended per short press.

## Some lamps respond and others do not

Check native group membership at each actual lamp endpoint, power, reachability, and replacement/re-pair history. An HA helper group member is not proof of native membership. A successful create-group API reply is not proof all Add Group operations succeeded. Group command delivery has no per-member application acknowledgment; physically inspect or query each lamp.

## The lamps are off, but HA still says on

Direct commands and state reporting are separate paths. Poll/read the On/Off attribute of each lamp when reachable and compare with physical observation. Group broadcasts can work even when a later unicast query times out. Do not “fix” a successful direct action by adding a second HA toggle that creates race conditions.

## A mixed group stays mixed after short press

Toggle inverts each lamp independently. Hold sends absolute Off and should align reachable members. A lamp that misses even that Off still needs radio/membership troubleshooting; idempotent commands are not guaranteed delivery.

## The button works nearby but not in its normal position

Investigate the parent/router, interference, obstacles, and powered router coverage. Distance through a ceiling or wall is not line-of-sight distance. Restore reliable mesh coverage before changing firmware. A sleepy device may need time or a short wake to rejoin after parent loss.

## A custom WebSocket script reports timeouts or id_reuse

HA requires strictly increasing request IDs on a connection. An `id_reuse` rejection means the operation was not accepted. In the observed HA version, ZHA Reconfigure emitted asynchronous progress instead of a normal RPC result; a generic client's timeout did not prove reconfiguration failed. Observe live state/events before retrying. Internal WebSocket behavior is version-dependent; prefer the supported UI/service path unless maintaining the client.

## Rollback or factory reset

First restore mode **PressStart / 1**, which changes behavior without another flash. See [recovery](recovery.md). Factory reset is not the normal fix for an OTA notification, cached UI, or weak battery. It removes useful state and requires recommissioning.
