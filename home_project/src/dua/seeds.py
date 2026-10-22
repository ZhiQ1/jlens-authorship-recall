"""Seeding.

Every stochastic step in this repository draws from a seed that comes from
``config.yaml``. There is no bare ``42`` anywhere else in the package, and no
call to ``random.sample`` / ``DataFrame.sample`` / ``train_test_split`` that
omits an explicit seed.

Call :func:`set_all_seeds` once at the top of any entry point.
"""

from __future__ import annotations

import os
import random

import numpy as np


def set_all_seeds(seed: int) -> int:
    """Seed ``random``, ``numpy``, and ``PYTHONHASHSEED``. Returns the seed.

    ``PYTHONHASHSEED`` is set for child processes only; it cannot affect the
    already-running interpreter, so nothing in this package may depend on
    ``hash()`` ordering. Set it in the shell if you need that guarantee.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    try:  # torch is an optional dependency, only needed for Section 7
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
    return seed


def rng(seed: int, *salt: str | int) -> np.random.Generator:
    """A named, independent generator derived from the global seed.

    Two analyses that both need randomness get independent streams without
    interfering, and each stream is reproducible on its own:

        >>> a = rng(42, "distractors", "medicine")
        >>> b = rng(42, "bootstrap")

    ``salt`` is hashed stably (SHA-256, not ``hash()``), so the stream does not
    depend on interpreter start-up state.
    """
    import hashlib

    if not salt:
        return np.random.default_rng(seed)
    key = "|".join(str(s) for s in salt).encode("utf-8")
    digest = hashlib.sha256(key).digest()[:8]
    return np.random.default_rng(seed ^ int.from_bytes(digest, "big"))
