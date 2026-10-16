"""Exercise real shared C firmware with endpoint and component boundary inputs."""
from pathlib import Path
import subprocess

import pytest

from client import StubProc
from conftest import Device, MINIMUM_SWITCH_TIME_MS


def test_tenth_endpoint_remains_addressable_and_readers_finish():
    config = "X;Y;SA0u;SA1u;SA2u;SA3u;RB0;RB1;RB2;RB3;CC0C1;CC2C3;"
    proc = StubProc(device_config=config)
    with proc:
        device = Device(proc)
        device.step_time(MINIMUM_SWITCH_TIME_MS)
        device.zcl_cover_open(10)
        assert device.get_gpio("C2", refresh=True)
        assert not device.get_gpio("C3", refresh=True)
    assert not proc._reader_thread.is_alive()
    assert not proc._stderr_forward_thread.is_alive()


@pytest.mark.parametrize("entries", [
    "SA0u;" * 5, "RA0;" * 5, "XA0A1u;" * 4, "CA0A1;" * 4,
    "LA0;" * 6, "BA0u;" * 12,
    "SA0u;" * 4 + "RA1;" * 4 + "XA2A3u;" * 3,
])
def test_excess_configuration_resets_without_out_of_bounds_write(entries, tmp_path):
    binary = Path("build/stub/stub_device").resolve()
    result = subprocess.run(
        [str(binary), "--device-config", "X;Y;" + entries],
        cwd=tmp_path, capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert "Configuration capacity exceeded" in result.stdout
    assert "AddressSanitizer" not in result.stderr
    assert "runtime error:" not in result.stderr


@pytest.mark.parametrize("binary_name", ["stub_device", "stub_end_device"])
@pytest.mark.parametrize("battery", ["", "BTD0;"])
@pytest.mark.parametrize("entries", [
    "SA0u;SA1u;SA2u;SA3u;RB0;RB1;RB2;RB3;XC0C1u;XC2C3u;",
    "SA0u;SA1u;SA2u;SA3u;RB0;RB1;RB2;XC0C1u;XC2C3u;XC4C5u;",
    "SA0u;SA1u;SA2u;SA3u;RB0;RB1;RB2;RB3;CC0C1;CC2C3;",
])
def test_full_endpoint_cluster_budget(binary_name, battery, entries, tmp_path):
    binary = Path("build/stub", binary_name).resolve()
    result = subprocess.run(
        [str(binary), "--device-config", "X;Y;" + battery + entries],
        input="q\n", cwd=tmp_path, capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert "Config parsed successfully" in result.stdout
    assert "AddressSanitizer" not in result.stderr
    assert "runtime error:" not in result.stderr
