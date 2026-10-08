# Design and compatibility

## Exact build target

The supported board is the battery Tuya TS0041 identified by stock manufacturer `_TZ3000_mrpevh8p`, using a Telink TLSR8258. The custom identity is `mrpevh8p` / `TS0041-TB`. The build is **EndDevice**, not Router, with this upstream pin configuration:

```text
mrpevh8p;TS0041-TB;BB4d;SB5u;ID2;BTB5;M;
```

Other hardware support inherited in the source tree does not mean this project's binary has been tested or is suitable for it. Verify model, manufacturer, radio chip, and pin configuration before selecting any firmware.

## Command behavior

The implementation is in `src/zigbee/switch_cluster.c` and `src/zigbee/consts.h`. New binding mode **4**, exposed as `ShortPressLongOff`, uses the existing nonvolatile setting and does not change its storage layout.

For a Momentary input in mode 4:

1. Press start records the input normally but sends no bound action.
2. Release before the long threshold invokes the existing short-action handler. With ToggleSimple, it sends On/Off cluster `0x0006`, command `0x02` (Toggle).
3. Reaching the long threshold sends cluster `0x0006`, command `0x00` (Off), through the same binding destination.
4. Continuing to hold sends no repeat, and release after a hold sends no Toggle or Level Stop.

The normal long-press telemetry event remains available to HA. Other binding modes keep their upstream behavior. The feature is for the momentary button flow; configuring a maintained/toggle switch instead changes input semantics.

## Where the state lives

- **Button flash:** Zigbee network identity, binding entries, and persistent settings. The binding selects a group as the destination of On/Off commands.
- **Each lamp:** membership of the native Zigbee group, normally persistent in the lamp's own nonvolatile memory.
- **Coordinator / ZHA:** network administration, its database, the commissioned device model, and a management view of groups and bindings.
- **HA light-group helper:** a separate dashboard/automation convenience. It does not create a native radio group by itself.

Normal battery replacement or removing and reinstalling a bulb should preserve persistent state. The button setting persistence has a host simulation test; physical persistence for the custom image must be recorded separately. A factory reset, flash erase, incompatible migration, storage corruption, or writing another device's dump can remove or invalidate state. A replacement bulb needs joining and group membership even if it uses the same HA entity name.

## What independence means

HA does not translate button events into light service calls. A radio command can reach its bound group without an HA automation or internet. This removes that event-processing delay and dependency.

The button is still a sleepy Zigbee EndDevice and relies on a parent in a functioning Zigbee network. Stopping HA software is not the same experiment as unplugging the coordinator, powering down routers, or removing the button's parent. Do not promise success under every network outage. Group delivery has no per-lamp application acknowledgment: physically verify every intended lamp.

This mechanism applies to Zigbee endpoints accepting the On/Off cluster. Matter uses a different application protocol; a Matter-only lamp cannot join this Zigbee group. A bridge or automation would be a different design.

## Toggle versus absolute Off

Toggle inverts each lamp's current state, so a previously mixed group can remain mixed. Absolute Off is idempotent: repeating it asks every recipient to become off. It helps recover consistent state after missed Toggles but cannot fix a lamp that is unreachable or has lost group membership.

The 1,000 ms hold threshold is a deployment choice, not hard-coded timing. Endpoint 1 input cluster `0x0007` stores it in attribute `0xff03`; mode lives in `0xff05`. Only configure mode 4 after installing the patched firmware. Before downgrading to upstream, restore mode 1 so the older implementation sees a value it understands.
