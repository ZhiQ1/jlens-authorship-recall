"""Configuration loading.

Everything tunable lives in ``config/config.yaml``. Nothing else in this
package hardcodes a path, a seed, a bin edge, or a field name. Resolution
order, last wins:

1. ``config/config.yaml``
2. ``config/config.local.yaml`` (gitignored, for machine-specific paths)
3. ``DUA_*`` environment variables, for the handful of large inputs that
   differ per machine: ``DUA_CORPUS``, ``DUA_OAG_POOL``, ``DUA_FASTTEXT_LID``,
   ``DUA_DATA``, ``DUA_RESULTS``.
"""

from __future__ import annotations

import copy
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"

_ENV_PATH_OVERRIDES = {
    "corpus": "DUA_CORPUS",
    "oag_pool": "DUA_OAG_POOL",
    "fasttext_lid": "DUA_FASTTEXT_LID",
    "data": "DUA_DATA",
    "results": "DUA_RESULTS",
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


@dataclass(frozen=True)
class CitationBin:
    """One of the thirteen exponentially spaced citation bins."""

    label: str
    lo: int
    hi: int | None  # None means open-ended (the 4097+ bin)

    def contains(self, citations: int) -> bool:
        if citations < self.lo:
            return False
        return self.hi is None or citations <= self.hi


class Config:
    """Read-only view over the merged configuration."""

    def __init__(self, raw: dict[str, Any]):
        self._raw = raw

    # -- raw access ------------------------------------------------------
    def __getitem__(self, key: str) -> Any:
        return self._raw[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._raw.get(key, default)

    @property
    def raw(self) -> dict[str, Any]:
        return copy.deepcopy(self._raw)

    # -- the values used everywhere --------------------------------------
    @property
    def seed(self) -> int:
        return int(self._raw["seed"])

    def path(self, name: str) -> Path:
        """Resolve a named path from ``paths:``, against the repo root."""
        env = _ENV_PATH_OVERRIDES.get(name)
        if env and os.environ.get(env):
            return Path(os.environ[env]).expanduser().resolve()
        value = Path(self._raw["paths"][name]).expanduser()
        return value if value.is_absolute() else (REPO_ROOT / value).resolve()

    @property
    def fields(self) -> dict[str, str]:
        """Canonical field key -> display label, in paper order."""
        return dict(self._raw["fields"])

    @property
    def field_keys(self) -> list[str]:
        return list(self._raw["fields"].keys())

    @property
    def citation_bins(self) -> list[CitationBin]:
        return [CitationBin(b["label"], int(b["lo"]), b["hi"]) for b in self._raw["citation_bins"]]

    @property
    def bin_labels(self) -> list[str]:
        return [b["label"] for b in self._raw["citation_bins"]]

    # -- companion files --------------------------------------------------
    @property
    def models(self) -> dict[str, Any]:
        return load_models()

    def prompt(self, filename: str) -> str:
        """Read a prompt template from ``config/prompts/``."""
        return (CONFIG_DIR / "prompts" / filename).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def load_config() -> Config:
    raw = yaml.safe_load((CONFIG_DIR / "config.yaml").read_text(encoding="utf-8"))
    local = CONFIG_DIR / "config.local.yaml"
    if local.exists():
        raw = _deep_merge(raw, yaml.safe_load(local.read_text(encoding="utf-8")) or {})
    return Config(raw)


@lru_cache(maxsize=1)
def load_models() -> dict[str, Any]:
    return yaml.safe_load((CONFIG_DIR / "models.yaml").read_text(encoding="utf-8"))
