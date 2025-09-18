# backend/app/utils/security.py
from datetime import datetime, timedelta, timezone
from jose import jwt
import os, hashlib, hmac
from typing import Tuple
from ..config import settings

# ===== JWT =====

def create_access_token(sub: str, expires_minutes: int | None = None) -> str:
    exp_minutes = expires_minutes or settings.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

# ===== Password Hash =====

_PBKDF2_ALG   = "sha256"
_PBKDF2_ITERS = 100_000
_SALT_BYTES   = 16

def _pbkdf2(plain: str, salt: bytes, iterations: int = _PBKDF2_ITERS) -> bytes:
    return hashlib.pbkdf2_hmac(_PBKDF2_ALG, plain.encode("utf-8"), salt, iterations)

def hash_password(plain_password: str) -> str:
    salt = os.urandom(_SALT_BYTES)
    dk = _pbkdf2(plain_password, salt, _PBKDF2_ITERS)
    return f"pbkdf2$sha256${_PBKDF2_ITERS}${salt.hex()}${dk.hex()}"

def _parse_stored(stored: str) -> Tuple[int, bytes, bytes]:
    try:
        scheme, alg, iters, salt_hex, hash_hex = stored.split("$", 4)
        if scheme != "pbkdf2" or alg != "sha256":
            raise ValueError("Unsupported hash format")
        return int(iters), bytes.fromhex(salt_hex), bytes.fromhex(hash_hex)
    except Exception as e:
        raise ValueError(f"Invalid stored hash: {e}")

def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        iters, salt, expected = _parse_stored(stored_hash)
        dk = _pbkdf2(plain_password, salt, iters)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False
