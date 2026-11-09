"""Arbitrary-N directional configuration classification."""

from collections.abc import Sequence

import pandas as pd


def classify_configuration(modes: Sequence[str], *, outer_scale_name: str = "outer",
                           expected_count: int | None = None) -> dict[str, object]:
    """Classify an ordered small-to-large mode vector without future data."""
    values = tuple(str(mode) for mode in modes)
    if expected_count is not None and len(values) != expected_count:
        raise ValueError(f"Expected exactly {expected_count} ordered modes.")
    if len(values) < 2:
        raise ValueError("At least two ordered modes are required.")

    boundary_count = sum(left != right for left, right in zip(values[:-1], values[1:], strict=True))
    outer_agreement_breadth = sum(mode == values[-1] for mode in values)
    small_coherence_depth = 1
    for mode in values[1:]:
        if mode != values[0]:
            break
        small_coherence_depth += 1

    if boundary_count == 0:
        hierarchy_shape = "broad_agreement"
        counter_depth: object = 0
    elif boundary_count == 1:
        counter_depth = small_coherence_depth
        hierarchy_shape = f"counter_depth_{counter_depth}"
    else:
        counter_depth = pd.NA
        hierarchy_shape = f"fragmented_{boundary_count}_boundaries"

    return {
        "configuration": "/".join(values),
        "hierarchy_shape": hierarchy_shape,
        "direction_boundaries": boundary_count,
        f"{outer_scale_name}_agreement_breadth": outer_agreement_breadth,
        "small_coherence_depth": small_coherence_depth,
        "counter_depth": counter_depth,
        "coherent_frontier": boundary_count <= 1,
    }
