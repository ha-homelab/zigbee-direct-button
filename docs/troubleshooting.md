# Troubleshooting

## Button LED is faint, device disappears, or OTA stops early

Check the correct battery size, charge, and contact pressure. A visible LED proves little about voltage under transmit load. The reference project encountered failures near 7% and 10%; success followed battery/contact work plus a ZHA reload, so the evidence does not isolate one cause. Avoid treating every stall as firmware corruption. Read the installed version before retrying.

## Update says “in progress” but no bytes arrive

First distinguish **stock Tuya conversion** from an update of the **converted upstream 1.1.3** battery firmware. Repeated short presses helped the stock conversion, but source inspection and host simulation showed that ordinary large-key presses in the converted firmware do not reopen fast polling: they can send Toggle/reports while the device remains on a 120-second long-poll interval.

The default startup window polls every 500 ms for ten seconds. In the observed HA/ZHA implementation, `update.install` waits for a Poll Control bind and writes a 30-second fast-poll timeout **before** `image_notify`. One attempt timed out there without sending image bytes. A responsive light switch and an `in_progress` flag therefore do not prove that an OTA notification or payload has reached the device.

Confirm the exact image type, model filters, offered version, and whether preparation or payload transfer is active. For the converted firmware, use the [guarded startup-window procedure](upgrade.md#start-within-the-startup-fast-poll-window): arm the example script, then perform the controlled five-second battery removal and immediate single working-key press **only after confirming that the previous install ended and no payload is transferring**. Never remove power during an active or ambiguously active install. A stalled percentage alone is not proof that power removal is safe.

The script listens for the press-action sensor state **`press`**, not `pressed`. If nothing starts, inspect its trace, the exact sensor entity/state, and its installed/latest-version and idle guards. A ten-minute wait timeout stops the script without starting an update. Cancel an abandoned waiting script so a later ordinary press cannot unexpectedly trigger it. The startup procedure is not a verified successful transfer by itself; require progress, completion, version readback, and physical tests.

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
