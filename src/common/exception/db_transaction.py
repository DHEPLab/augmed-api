from functools import wraps

from src import db


def db_transaction(throw=True):
    def transaction(func):
        @wraps(func)
        def handle(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                print(f"Transaction rollback: {e}")
                db.session.rollback()
                if throw:
                    raise e
            else:
                return ret

        return handle

    return transaction
