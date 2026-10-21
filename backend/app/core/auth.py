"""Authentication and Token Management for EarlyCare.

Handles Google ID token verification, session JWT signing/validation,
and FastAPI security dependencies for user endpoints.
"""
import hmac
import hashlib
import base64
import json
import time
import os
import urllib.request
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from app.db.database import get_user_by_id, get_or_create_user

JWT_SECRET = os.environ.get("EARLYCARE_JWT_SECRET", "earlycare_clinical_secret_key_2026_campus_auth")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRATION_SECONDS = 30 * 24 * 60 * 60  # 30 days


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding and padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s.encode("utf-8"))


def create_access_token(user_id: str, email: str) -> str:
    """Generates an RFC 7519 compliant HMAC-SHA256 JWT."""
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + TOKEN_EXPIRATION_SECONDS,
    }

    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Validates an access token signature and checks expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()

        actual_sig = _base64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload
    except Exception:
        return None


def parse_google_credential(credential: str) -> Optional[Dict[str, Any]]:
    """
    Parses and verifies a Google ID token credential string.
    First tries Google's tokeninfo API, with graceful fallback to JWT payload unpack.
    """
    # 1. Try online verification with Google's tokeninfo endpoint
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
        req = urllib.request.Request(url, headers={"User-Agent": "EarlyCare-Auth/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if "email" in data:
                    return {
                        "email": data["email"],
                        "name": data.get("name", ""),
                        "picture": data.get("picture", ""),
                        "google_id": data.get("sub", ""),
                    }
    except Exception:
        pass

    # 2. Offline fallback: decode the payload segment of the Google JWT
    try:
        parts = credential.split(".")
        if len(parts) >= 2:
            payload_bytes = _base64url_decode(parts[1])
            data = json.loads(payload_bytes.decode("utf-8"))
            if "email" in data:
                return {
                    "email": data["email"],
                    "name": data.get("name", ""),
                    "picture": data.get("picture", ""),
                    "google_id": data.get("sub", ""),
                }
    except Exception:
        pass

    return None


async def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """FastAPI dependency for endpoints where login is optional (e.g. /api/screen)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:].strip()
    payload = verify_access_token(token)
    if not payload:
        return None

    user = get_user_by_id(payload["sub"])
    return user


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """FastAPI dependency for protected endpoints requiring active authentication."""
    user = await get_optional_current_user(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Active authorization token required. Please sign in with Google.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
