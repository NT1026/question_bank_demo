from datetime import datetime
from fastapi import Request


def is_token_expired(unix_timestamp: int):
    if unix_timestamp is None:
        return True
    return datetime.now() > datetime.fromtimestamp(unix_timestamp)


def validate_session(request: Request):
    user_id = request.session.get("user_id")
    token_exp = request.session.get("token_expiry")

    # No user in session
    if not user_id:
        return False

    # Check if token is expired
    if not token_exp or is_token_expired(token_exp):
        return False

    # Valid session
    return True
