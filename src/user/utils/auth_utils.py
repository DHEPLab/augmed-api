from datetime import datetime, timedelta, timezone
from functools import wraps

from flask_jwt_extended import (create_access_token, get_jwt, get_jwt_identity,
                                verify_jwt_in_request)
from werkzeug.exceptions import Unauthorized

from src import db
from user.repository.user_repository import UserRepository

user_repository = UserRepository(db.session)


def validate_jwt_and_refresh():
    verify_jwt_in_request()
    jwt_claims = get_jwt()

    user_email = get_jwt_identity()
    user = user_repository.get_user_by_email(user_email)
    if not user:
        raise Unauthorized("User not found, please login.")

    now = datetime.now(timezone.utc)
    jwt_expiry = datetime.fromtimestamp(jwt_claims["exp"], timezone.utc)
    last_login_time = datetime.fromisoformat(jwt_claims.get("last_login_time"))
    if jwt_expiry <= now:
        if now - last_login_time > timedelta(days=3):
            raise Unauthorized("Session expired, please login again.")
        else:
            new_access_token = create_access_token(
                identity=user_email,
                additional_claims={"last_login_time": last_login_time.isoformat()},
            )
            return new_access_token
    return None


def jwt_validation_required():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            new_token = validate_jwt_and_refresh()
            response = fn(*args, **kwargs)
            if new_token:
                response.headers["Authorization"] = f"Bearer {new_token}"
            return response

        return wrapper

    return decorator
