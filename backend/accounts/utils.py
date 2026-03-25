import re
import secrets

import bcrypt
from rest_framework.exceptions import ValidationError


PASSWORD_UPPER_RE = re.compile(r"[A-Z]")
PASSWORD_NUMBER_RE = re.compile(r"\d")
PASSWORD_SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")


def validate_password_strength(password: str) -> None:
    if password is None:
        raise ValidationError("Password is required.")

    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    if not PASSWORD_UPPER_RE.search(password):
        raise ValidationError("Password must contain at least 1 uppercase letter.")

    if not PASSWORD_NUMBER_RE.search(password):
        raise ValidationError("Password must contain at least 1 number.")

    if not PASSWORD_SPECIAL_RE.search(password):
        raise ValidationError("Password must contain at least 1 special character.")


def hash_password_bcrypt(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def check_password_bcrypt(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def generate_reset_token() -> str:
    # URL-safe token to embed in reset links (or demo responses).
    return secrets.token_urlsafe(32)

