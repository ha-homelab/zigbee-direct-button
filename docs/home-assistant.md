# Home Assistant / ZHA configuration

These examples contain placeholders. Use your own device/entity IDs locally. The reference integration was exercised with HA 2026.9.1; UI names and internal WebSocket operations can change between releases.

## Install the target-only quirk and OTA provider

Copy **`examples/home-assistant/tuya_direct_button.py`** into HA's `/config/custom_zha_quirks/`. It registers only `mrpevh8p` / `TS0041-TB` and adds the new enum choice. A quirk exposes controls; it does not install firmware or make an older image implement mode 4.

Do not also install `zha/switch_quirk.py`: that is the broad inherited development output. Avoid two quirks registering the same device; replace the matching old registration or remove that target from an existing broad custom quirk after backing it up.

Merge `examples/home-assistant/configuration.yaml` into your existing `zha:` configuration without duplicating that top-level key. Place the OTA image and generated index in `/config/ota/zigbee_direct_button/`. The file `path` in the local index is relative to that index directory.

Validate HA configuration. Restart HA if enabling the custom-quirk path/provider for the first time. For subsequent file changes, use the supported ZHA reload lifecycle if your installed version reloads both quirks and providers; otherwise restart HA. Verify the actual loaded quirk and offered version rather than assuming a reload worked. Do not reload during an update.

Generate the index with an actual trusted artifact URL; the local provider reads the sibling file:

```sh
python3 scripts/make_ota_index.py output/ts0041-hold-off-1.1.3.1.zigbee   --url https://example.invalid/replace-with-your-trusted-artifact-url \
  --output output/index.json
```

Replace the example URL before deploying. The tool validates image identity, integrity fields, and version, calculates SHA-512/size, and narrows matching to this converted model. It does not publish an artifact or access HA.

## Create the native Zigbee group

In ZHA's groups management, create a dedicated native group and add every intended lamp's actual On/Off endpoint. For example, use group `0x1234` if free. The reference CREE Connected A-19 bulbs use endpoint 10; other bulbs may use a different endpoint. Inspect, do not assume.

Check that each requested lamp has acknowledged membership and appears in the resulting group. API success may mean the group object was created even if one member operation failed. Fix missing members before proceeding. Keep an HA helper group if useful for dashboards, but it is not a substitute for this group.

## Bind the button to the group

On the converted button, bind endpoint **1**, output/client **On/Off cluster `0x0006`**, to the native group using ZHA's group binding controls. Wake it with a short working-key press if needed.

Verify a successful **device Bind response**, not only an accepted API request. During the reference commissioning, the group-bind API could return success while an individual radio operation failed. Briefly enable targeted Zigbee/ZDO debug logging if necessary, capture the actual result privately, then restore the previous level. Logs may expose network/device identifiers.

For hold-to-off, no Level Control binding is required. Avoid changing unrelated bindings. Some older firmware also uses Level Control for long presses; this new mode intentionally suppresses that dimming path.

## Configure only after installing the patched image

Verify runtime version **`0x11033001`** first. On endpoint 1, input/server On/Off Configuration cluster **`0x0007`**, set:

- `switch_mode`, attribute **`0xff00`**: **Momentary / 1**.
- `switch_actions`, attribute **`0x0010`**: **ToggleSimple / 2**.
- `binded_mode`, attribute **`0xff05`**: **ShortPressLongOff / 4**.
- `long_press_duration`, attribute **`0xff03`**: **1000 ms**.

The runtime quirk creates select/number controls for these values. Existing entity IDs can retain historical names, including a number called “long press mode” that actually controls duration. Use the actual entities in your installation, and confirm attributes read back from the physical device without relying only on a UI's optimistic/cache value.

`examples/home-assistant/actions.yaml` demonstrates the four actions with placeholder entity IDs. They configure the device; they are not the light-control automation. Keep any old event-to-Toggle automation disabled or one press can toggle twice.

## OTA service example

HA exposes the firmware as an update entity. Select only the exact button:

```yaml
action: update.install
target:
  entity_id: update.example_button_firmware
data:
  version: "0x11033001"
```

Use the exact version string offered by your HA version. Check live update state before retrying, and confirm the installed version afterward. Do not create a service loop that repeatedly starts updates.

## References

- [HA ZHA: groups and binding](https://www.home-assistant.io/integrations/zha/#zigbee-groups-and-binding-devices)
- [Upstream custom firmware](https://github.com/romasku/tuya-zigbee-switch)
- [Silicon Labs: binding concepts](https://docs.silabs.com/zigbee/9.1.0/zigbee-concepts-network/binding)
