from __future__ import annotations

from core.security import hash_password, verify_password


def test_hash_and_verify_round_trip() -> None:
    h = hash_password("secret-password")
    assert verify_password("secret-password", h)
    assert not verify_password("wrong", h)
