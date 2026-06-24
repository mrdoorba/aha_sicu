"""Scoring calculator package.

Exposes the production entry point ``calculate_score``. Internal helpers and
submodule symbols are imported directly from their submodules (e.g.
``from app.calculators.scoring.computations import _compute_g68``).
"""

from app.calculators.scoring._calculator import calculate_score  # noqa: F401
