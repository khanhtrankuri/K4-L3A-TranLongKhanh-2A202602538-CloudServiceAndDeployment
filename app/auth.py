"""CP3 — Xác thực bằng API key."""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings

ANONYMOUS_USER = "anonymous"


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    """Kiểm tra header X-API-Key; trả về user_id nếu hợp lệ."""

    # 1. API key đúng lấy từ environment/config
    expected_api_key = get_settings().agent_api_key

    # 2 + 3. Thiếu hoặc sai API key → 401
    if x_api_key is None or not secrets.compare_digest(
        x_api_key,
        expected_api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
        )

    # 4. API key hợp lệ → xác định user
    return x_user_id if x_user_id is not None else ANONYMOUS_USER