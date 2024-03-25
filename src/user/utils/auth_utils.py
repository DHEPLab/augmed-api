from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import make_response, request
from flask_jwt_extended import (create_access_token, get_jwt, get_jwt_identity,
                                verify_jwt_in_request)
from werkzeug.exceptions import Unauthorized


def validate_jwt_and_refresh():
    verify_jwt_in_request()
    jwt_claims = get_jwt()

    user_email = get_jwt_identity()

    now = datetime.now(timezone.utc)
    jwt_expiry = datetime.fromtimestamp(jwt_claims["exp"], timezone.utc)
    additional_claims = jwt_claims.get("additional_claims", {})
    last_login_time = additional_claims.get("last_login_time")
    if last_login_time:
        last_login_time = datetime.fromisoformat(last_login_time)

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
            result = fn(*args, **kwargs)

            if isinstance(result, tuple):
                response, status = result
                response = make_response(response, status)
            else:
                response = result

            jwt_to_set = (
                new_token
                if new_token
                else request.headers.get("Authorization", "").split(" ")[-1]
            )
            if jwt_to_set:
                response.headers["Authorization"] = f"Bearer {jwt_to_set}"

            return response

        return wrapper

    return decorator
