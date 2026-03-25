from dataclasses import dataclass

import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from .jwt_utils import decode_jwt


@dataclass
class JWTUser:
    user_id: int
    email: str
    role: str

    @property
    def is_authenticated(self) -> bool:
        return True


class JWTAuthentication(BaseAuthentication):
    """
    Reads Authorization: Bearer <jwt> and returns a lightweight user object.
    """

    keyword = "Bearer"

    def authenticate(self, request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            # Allow public endpoints (DRF will treat as unauthenticated).
            return None

        if not auth_header.startswith(f"{self.keyword} "):
            raise AuthenticationFailed("Invalid authorization header format.")

        token = auth_header.split(" ", 1)[1].strip()
        try:
            claims = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")

        user_id = claims.get("userId")
        email = claims.get("email")
        role = claims.get("role")
        if not user_id or not email or not role:
            raise AuthenticationFailed("Invalid token payload.")

        return JWTUser(user_id=int(user_id), email=email, role=str(role)), None

