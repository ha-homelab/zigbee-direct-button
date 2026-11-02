"""Keep direct tooling inputs aligned with the verified installation lock."""
import pytest
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def exact_pins(text):
    return {name.lower().replace("_", "-"): version for name, version in
            re.findall(r"^([A-Za-z0-9_.-]+)==([^ ;\\\n]+)", text, re.MULTILINE)}


@pytest.mark.parametrize("source,lock", [("requirements.txt", "requirements.lock"),
                                        ("requirements-build.in", "requirements-build.lock")])
def test_direct_dependency_versions_match_hashed_lock(source, lock):
    direct = exact_pins((ROOT / source).read_text())
    locked = exact_pins((ROOT / lock).read_text())
    assert direct
    assert {name: locked.get(name) for name in direct} == direct


@pytest.mark.parametrize("lock", ["requirements.lock", "requirements-build.lock"])
def test_installation_lock_has_hashes_for_every_entry(lock):
    locked = (ROOT / lock).read_text()
    entries = re.split(r"(?m)(?=^[A-Za-z0-9_.-]+==)", locked)[1:]
    assert entries
    assert all("--hash=sha256:" in entry for entry in entries)
