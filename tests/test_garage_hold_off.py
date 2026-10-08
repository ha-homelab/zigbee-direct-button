"""Wire-command contract for the opt-in battery-remote hold-to-off mode."""
import pytest

from client import StubProc
from conftest import Device

CONFIG = "mrpevh8p;TS0041-TB;BB4d;SB5u;ID2;BTB5;M;"
EP, ONOFF, LEVEL, CONFIG_CLUSTER = 1, 0x0006, 0x0008, 0x0007
MODE_ATTR, HOLD_ATTR = 0xFF05, 0xFF03
HOLD_OFF_MODE = 4


@pytest.fixture(params=["stub_device", "stub_end_device"])
def binary(request):
    return "./build/stub/" + request.param


def configure(d):
    d.zcl_switch_mode_set(EP, 1)
    d.zcl_switch_actions_set(EP, 2)
    d.zcl_switch_binding_mode_set(EP, HOLD_OFF_MODE)
    d.write_zigbee_attr(EP, CONFIG_CLUSTER, HOLD_ATTR, 1000)
    d.clear_events()


def commands(d):
    # Fence the stub event stream after the preceding simulated-time step.
    d.status()
    return [(c.cluster, c.cmd, c.data) for c in d.zcl_list_cmds()
            if c.cluster in (ONOFF, LEVEL)]


@pytest.fixture
def remote(binary):
    with StubProc(cmd=[binary], device_config=CONFIG) as p:
        d = Device(p)
        configure(d)
        yield d


def test_short_press_only_toggles_on_release(remote):
    remote.press_button("B5")
    remote.step_time(300)
    assert commands(remote) == []
    remote.release_button("B5")
    assert commands(remote) == [(ONOFF, 2, b"")]


def test_hold_sends_one_absolute_off_without_flash_or_dimming(remote):
    remote.press_button("B5")
    remote.step_time(900)  # 960 ms including the debounce helper: still below 1s.
    assert commands(remote) == []
    remote.step_time(100)
    assert commands(remote) == [(ONOFF, 0, b"")]
    remote.step_time(5000)
    remote.release_button("B5")
    assert commands(remote) == [(ONOFF, 0, b"")]


def test_repeated_hold_stays_off_then_short_press_still_toggles(remote):
    for _ in range(2):
        remote.long_click_button("B5", duration_ms=1200)
        remote.step_time(1000)
    remote.click_button("B5")
    assert commands(remote) == [(ONOFF, 0, b""), (ONOFF, 0, b""), (ONOFF, 2, b"")]


def test_hold_mode_and_threshold_survive_power_cycle(binary):
    with StubProc(cmd=[binary], device_config=CONFIG) as p:
        configure(Device(p))
    with StubProc(cmd=[binary], device_config=CONFIG) as p:
        d = Device(p)
        assert int(d.read_zigbee_attr(EP, CONFIG_CLUSTER, MODE_ATTR)) == HOLD_OFF_MODE
        assert int(d.read_zigbee_attr(EP, CONFIG_CLUSTER, HOLD_ATTR)) == 1000
        d.clear_events()
        d.long_click_button("B5", duration_ms=1200)
        assert commands(d) == [(ONOFF, 0, b"")]


def test_unjoined_remote_does_not_send_hold_command(binary):
    with StubProc(cmd=[binary], device_config=CONFIG, joined=False) as p:
        d = Device(p)
        configure(d)
        d.long_click_button("B5", duration_ms=1200)
        assert commands(d) == []


def test_release_of_key_held_at_boot_does_not_toggle(binary):
    with StubProc(cmd=[binary], device_config=CONFIG) as p:
        configure(Device(p))
    # A floating stub input starts low without changing active-low polarity,
    # modeling an already-held key. Production hardware keeps its pull-up.
    with StubProc(cmd=[binary], device_config=CONFIG.replace("SB5u", "SB5f")) as p:
        d = Device(p)
        d.clear_events()
        d.step_time(1500)
        d.release_button("B5")
        assert commands(d) == []
        d.click_button("B5")
        assert commands(d) == [(ONOFF, 2, b"")]
