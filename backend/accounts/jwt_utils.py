from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone


def generate_jwt(*, user_id: int, email: str, role: str) -> str:
    """
    Create JWT with required claims:
    - userId
    - email
    - role
    """
    now = timezone.now()
    exp = now + timedelta(hours=settings.JWT_EXP_HOURS)
    payload = {
        "userId": user_id,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    # PyJWT returns str in recent versions, but normalize anyway.
    return token if isinstance(token, str) else token.decode("utf-8")


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

