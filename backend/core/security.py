import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from backend.core.exceptions import AuthenticationError

AUTH_SECRET_ENV = "AUTH_SECRET"
AUTH_TOKEN_TTL_ENV = "AUTH_TOKEN_TTL_SECONDS"
DEFAULT_AUTH_TOKEN_TTL_SECONDS = 86_400
PASSWORD_HASH_ITERATIONS = 100_000


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def get_auth_secret() -> str:
    secret = os.getenv(AUTH_SECRET_ENV)
    if not secret:
        raise RuntimeError(f"{AUTH_SECRET_ENV} environment variable is required")
    return secret


def get_auth_token_ttl_seconds() -> int:
    return int(os.getenv(AUTH_TOKEN_TTL_ENV, str(DEFAULT_AUTH_TOKEN_TTL_SECONDS)))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return f"{PASSWORD_HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        iterations_str, salt_hex, digest_hex = password_hash.split("$", maxsplit=2)
        iterations = int(iterations_str)
    except ValueError as exc:
        raise AuthenticationError("Invalid password hash format") from exc

    computed_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        iterations,
    )
    return hmac.compare_digest(computed_digest.hex(), digest_hex)


def create_access_token(
    *,
    user_id: int,
    role: str,
    username: str,
) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "username": username,
        "exp": int(time.time()) + get_auth_token_ttl_seconds(),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded_payload = _b64url_encode(payload_bytes)
    signature = hmac.new(
        get_auth_secret().encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict:
    try:
        encoded_payload, encoded_signature = token.split(".", maxsplit=1)
    except ValueError as exc:
        raise AuthenticationError("Invalid authentication credentials") from exc

    expected_signature = hmac.new(
        get_auth_secret().encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(_b64url_encode(expected_signature), encoded_signature):
        raise AuthenticationError("Invalid authentication credentials")

    try:
        payload = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AuthenticationError("Invalid authentication credentials") from exc

    if int(payload.get("exp", 0)) <= int(time.time()):
        raise AuthenticationError("Token has expired")

    return payload
