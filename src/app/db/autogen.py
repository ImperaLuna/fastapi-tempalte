"""Shared Alembic autogenerate configuration (used by migrations/env.py and tests)."""

from typing import Any


def include_object(
    obj: Any, name: str | None, type_: str, reflected: bool, compare_to: Any
) -> bool:
    """Exclude CHECK constraints from autogenerate comparison.

    Enum(create_constraint=True) resolves its constraint name at DDL-compile
    time, so Alembic's comparer (which requires named metadata constraints)
    can't pair it with the reflected one and emits a false `remove_constraint`.
    Excluding CHECKs restores pre-Alembic-1.19 behavior; the constraints
    themselves are guarded by behavioral tests instead.
    """
    return type_ != "check_constraint"
