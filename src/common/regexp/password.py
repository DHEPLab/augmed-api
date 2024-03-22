import re

""" Password:
        - length must within [8,128]
        - at lease one upper-case letter
        - at lease onne lower-case letter
        - at lease one digit
        - at lease one special characher.
"""
password_pattern = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[_@$!%*?&])[A-Za-z\d_@$!%*?&]{8,128}$"
)


def validate_password(password):
    if re.match(password_pattern, password):
        return True
    else:
        return False
