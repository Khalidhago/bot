"""Tests for JWT security utilities."""

from __future__ import annotations

import pytest

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self) -> None:
        plain = "super_secret_password"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed)

    def test_wrong_password_fails(self) -> None:
        hashed = hash_password("correct_password")
        assert not verify_password("wrong_password", hashed)


class TestJWT:
    def test_access_token_round_trip(self) -> None:
        token = create_access_token("user-123", "engineer")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["role"] == "engineer"
        assert payload["type"] == "access"

    def test_refresh_token_round_trip(self) -> None:
        token = create_refresh_token("user-456")
        payload = decode_token(token)
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"

    def test_invalid_token_raises(self) -> None:
        with pytest.raises(UnauthorizedError):
            decode_token("not.a.valid.token")

    def test_tampered_token_raises(self) -> None:
        token = create_access_token("user-789", "viewer")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(UnauthorizedError):
            decode_token(tampered)
