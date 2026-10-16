"""OTA links must remain on the repository's exact public GitHub origin."""
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "ota_index", Path(__file__).parents[1] / "helper_scripts/make_z2m_ota_index.py"
)
INDEX = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INDEX)


@pytest.mark.parametrize("remote", [
    "https://github.com/owner/repo.git", "http://github.com/owner/repo",
    "git@github.com:owner/repo.git", "ssh://git@github.com/owner/repo.git",
    "git://github.com/owner/repo.git", "gh:owner/repo",
])
def test_public_github_remote(remote):
    assert INDEX.raw_github_url(remote, "release/test") == (
        "https://github.com/owner/repo/raw/refs/heads/release/test"
    )


@pytest.mark.parametrize("remote", [
    "https://evil.invalid/git://github.com/owner/repo", "https://github.com.evil.invalid/owner/repo",
    "https://github.com@evil.invalid/owner/repo", "https://token@github.com/owner/repo",
    "https://github.com/owner/repo?token=private", "https://github.com/owner/repo#fragment",
    "https://github.com:444/owner/repo", "https://github.com/owner/../repo",
    "https://github.com/owner/repo%2fother", "file:///owner/repo",
    "\nhttps://github.com/owner/repo", "https://github.com/owner/repo\n",
])
def test_untrusted_or_ambiguous_remote_is_rejected(remote):
    with pytest.raises(ValueError):
        INDEX.raw_github_url(remote, "main")


def test_branch_cannot_inject_url_query():
    assert INDEX.raw_github_url("https://github.com/owner/repo", "topic?x=#y").endswith(
        "/topic%3Fx%3D%23y"
    )
