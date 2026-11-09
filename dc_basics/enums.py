"""Shared directional-change values whose meaning is invariant across scales."""

from enum import StrEnum


class DcMode(StrEnum):
    UP = "up"
    DOWN = "down"


class AttemptOutcome(StrEnum):
    PROPAGATED = "propagated"
    REJECTED = "rejected"
    AMBIGUOUS = "ambiguous_same_bar"
    UNRESOLVED = "unresolved_at_sample_end"
