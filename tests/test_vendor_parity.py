from pathlib import Path

import pytest


SOURCE_ROOT = Path(r"D:\projects\quant-studies\signalfoundry")
LOCAL_ROOT = Path("dc_basics")
PAIRS = {
    SOURCE_ROOT / "features/src/okmich_quant_features/directional_change/_parser.py": LOCAL_ROOT / "core/_parser.py",
    SOURCE_ROOT / "features/src/okmich_quant_features/directional_change/_features.py": LOCAL_ROOT / "core/_features.py",
    SOURCE_ROOT / "features/src/okmich_quant_features/directional_change/_tsfdc_features.py": (
        LOCAL_ROOT / "core/_tsfdc_features.py"
    ),
    SOURCE_ROOT / "ml/src/okmich_quant_ml/hmm/util.py": LOCAL_ROOT / "hmm/util.py",
    SOURCE_ROOT / "ml/src/okmich_quant_ml/hmm/pomegranate.py": LOCAL_ROOT / "hmm/pomegranate.py",
    SOURCE_ROOT / "ml/src/okmich_quant_ml/hmm/base_pomegranate.py": LOCAL_ROOT / "hmm/base_pomegranate.py",
    SOURCE_ROOT / "ml/src/okmich_quant_ml/hmm/distribution/_lambda.py": LOCAL_ROOT / "hmm/distribution/_lambda.py",
    SOURCE_ROOT / "ml/src/okmich_quant_ml/hmm/distribution/__init__.py": (
        LOCAL_ROOT / "hmm/distribution/__init__.py"
    ),
}


@pytest.mark.parametrize(("source", "local"), PAIRS.items())
def test_vendored_module_matches_pinned_checkout(source: Path, local: Path) -> None:
    if not source.exists():
        pytest.skip("The original signalfoundry checkout is not available.")
    source_text = source.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip("\n")
    local_text = local.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip("\n")
    assert local_text == source_text
