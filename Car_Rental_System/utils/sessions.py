# utils/session.py
import secrets, time

class SessionManager:
    _sessions: dict[str, dict] = {}

    @classmethod
    def create(cls, user: dict, ttl_sec: int = 3600) -> str:
        """Create a short-lived session and return a token."""
        token = secrets.token_urlsafe(24)
        cls._sessions[token] = {"user": user, "exp": time.time() + ttl_sec}
        return token

    @classmethod
    def get_user(cls, token: str) -> dict | None:
        """Resolve token to user if not expired."""
        data = cls._sessions.get(token)
        if not data:
            return None
        if time.time() > data["exp"]:
            cls._sessions.pop(token, None)
            return None
        return data["user"]

    @classmethod
    def invalidate(cls, token: str) -> None:
        cls._sessions.pop(token, None)
