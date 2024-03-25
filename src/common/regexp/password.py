import re

special_letter_pattern = r"[!@#$%^&*()\-_+=.<>/?[\]{}\\\'\"]"

""" Password:
        - length must within [8,128]
        - at lease one upper-case letter
        - at lease onne lower-case letter
        - at lease one digit
        - at lease one special characher.
"""
password_pattern = re.compile(
    r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[{0}])[A-Za-z\d{0}]{{8,128}}$".format(
        re.escape(special_letter_pattern)
    )
)


def validate_password(password):
    if re.match(password_pattern, password):
        return True
    else:
        return False
