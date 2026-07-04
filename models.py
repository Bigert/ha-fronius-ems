from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExportLimits:
    """Current export limit configuration."""

    soft_limit: int
    hard_limit: int
    network_mode: str
