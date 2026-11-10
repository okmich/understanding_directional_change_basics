"""Vendored modules must stay byte-identical to the pinned signalfoundry commit.

Two independent checks:

1. Every vendored file matches a SHA-256 recorded here when it was vendored.
   This always runs, so a local edit to a vendored file fails the suite even
   on machines without the source repository.
2. When a signalfoundry checkout is available, every vendored file matches
   ``git show <pinned commit>:<path>`` -- the pinned commit, not whatever the
   checkout's working tree currently holds.

The checkout location defaults to a sibling ``signalfoundry`` directory and can
be overridden with the ``SIGNALFOUNDRY_ROOT`` environment variable.
"""

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PINNED_COMMIT = "e297846e1bc0cb3f564ef94dcddaa72b01fa201b"
SOURCE_ROOT = Path(os.environ.get("SIGNALFOUNDRY_ROOT", REPOSITORY_ROOT.parent / "signalfoundry"))

# local path -> (path inside signalfoundry, SHA-256 of the LF-normalised text without trailing newlines)
VENDORED = {
    "dc_basics/core/_parser.py": (
        "features/src/okmich_quant_features/directional_change/_parser.py",
        "5d0c79fdbe78c5e75b4b197127f1e7f1f951f5dd83852cc64177b5e5f2ff0ca3",
    ),
    "dc_basics/core/_features.py": (
        "features/src/okmich_quant_features/directional_change/_features.py",
        "ea912034b198bf73c1d11aa93de7ea90f12b0244d551e4be6af6233b8ed37fc2",
    ),
    "dc_basics/core/_tsfdc_features.py": (
        "features/src/okmich_quant_features/directional_change/_tsfdc_features.py",
        "17e9d2184562f93f470175df15d110394d2ac81b1090401008e6a0f5f9dd6ff3",
    ),
    "dc_basics/hmm/util.py": (
        "ml/src/okmich_quant_ml/hmm/util.py",
        "d97d8b5d3636c39a390b5cf296dc8b5e99212afad622b552e4e199469ae63ba4",
    ),
    "dc_basics/hmm/pomegranate.py": (
        "ml/src/okmich_quant_ml/hmm/pomegranate.py",
        "a0d2aa15b55fa1c685888646052f152154ced55d1cdb1366b29b8c6d4850bc19",
    ),
    "dc_basics/hmm/base_pomegranate.py": (
        "ml/src/okmich_quant_ml/hmm/base_pomegranate.py",
        "d7800e54548555e7215337c4797d3a16b3bcde6b5b43bfc5f6fd9d71ea1e5dbc",
    ),
    "dc_basics/hmm/distribution/_lambda.py": (
        "ml/src/okmich_quant_ml/hmm/distribution/_lambda.py",
        "860d2cc27246e205175f4aee98329196646db3a66a1c7ef2245d8395acc0bd15",
    ),
    "dc_basics/hmm/distribution/__init__.py": (
        "ml/src/okmich_quant_ml/hmm/distribution/__init__.py",
        "2c448bf4682e3d411990af24d2263ec9c25638a035eefcfbaa52f7c89aed2b47",
    ),
}


def _normalise(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip("\n")


def _local_text(local: str) -> str:
    return _normalise((REPOSITORY_ROOT / local).read_text(encoding="utf-8"))


@pytest.mark.parametrize("local", VENDORED)
def test_vendored_module_matches_recorded_hash(local: str) -> None:
    _, expected_sha256 = VENDORED[local]
    actual_sha256 = hashlib.sha256(_local_text(local).encode("utf-8")).hexdigest()
    assert actual_sha256 == expected_sha256, (
        f"{local} differs from the version vendored at {PINNED_COMMIT[:7]}. "
        "Put local behaviour in a non-vendored module, or re-vendor and update dc_basics/VENDORED_FROM.md."
    )


@pytest.mark.parametrize("local", VENDORED)
def test_vendored_module_matches_pinned_commit(local: str) -> None:
    source_path, _ = VENDORED[local]
    if not (SOURCE_ROOT / ".git").exists():
        pytest.skip(f"No signalfoundry git checkout at {SOURCE_ROOT}; set SIGNALFOUNDRY_ROOT to enable.")
    result = subprocess.run(
        ["git", "-C", str(SOURCE_ROOT), "show", f"{PINNED_COMMIT}:{source_path}"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"Pinned commit {PINNED_COMMIT[:7]} is not available in {SOURCE_ROOT}.")
    assert _local_text(local) == _normalise(result.stdout.decode("utf-8"))
