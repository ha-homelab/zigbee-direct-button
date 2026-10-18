"""Check real host NVM writes with permissive umask and hostile file types."""
import os
from pathlib import Path
import stat
import subprocess

import pytest


@pytest.fixture(scope="module")
def nvm_writer(tmp_path_factory):
    directory = tmp_path_factory.mktemp("nvm-writer")
    source = directory / "writer.c"
    source.write_text(
        '#include "hal/nvm.h"\n'
        'int main(void) { uint8_t data[] = {1, 2, 3}; '
        'return (int)hal_nvm_write(42, sizeof(data), data); }\n'
    )
    root = Path(__file__).resolve().parents[1]
    binary = directory / "writer"
    subprocess.run(
        ["clang", "-Wall", "-Wextra", "-Werror", "-I", str(root / "src"),
         str(source), str(root / "src/stub/hal/nvm.c"), "-o", str(binary)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return binary


def write(nvm_writer, tmp_path):
    return subprocess.run(
        [str(nvm_writer)], cwd=tmp_path, umask=0,
        capture_output=True, text=True, timeout=5,
    )


@pytest.mark.parametrize("existing", [False, True])
def test_nvm_file_is_private_even_with_permissive_umask(nvm_writer, tmp_path, existing):
    directory = tmp_path / "stub_nvm_data"
    item = directory / "item_2a.bin"
    if existing:
        directory.mkdir(mode=0o700)
        item.write_bytes(b"previous longer content")
        item.chmod(0o666)
    result = write(nvm_writer, tmp_path)
    assert result.returncode == 0, result.stderr
    assert stat.S_IMODE(item.stat().st_mode) == 0o600
    assert item.read_bytes() == bytes([1, 2, 3])


@pytest.mark.parametrize("kind", ["symlink", "fifo"])
def test_nvm_rejects_non_regular_destination(nvm_writer, tmp_path, kind):
    directory = tmp_path / "stub_nvm_data"
    directory.mkdir(mode=0o700)
    item = directory / "item_2a.bin"
    original = tmp_path / "original"
    original.write_bytes(b"unchanged")
    if kind == "symlink":
        item.symlink_to(original)
    else:
        os.mkfifo(item)
    result = write(nvm_writer, tmp_path)
    assert result.returncode == 2, result.stderr
    assert original.read_bytes() == b"unchanged"
