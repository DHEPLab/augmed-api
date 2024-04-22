from enum import Enum


class BusinessExceptionEnum(Enum):
    UserPasswordInvalid = (
        "1001",
        (
            "Passwords must have at least 8 characters and contain at least a letter, "
            "a number and a symbol. Please try again."
        ),
    )
    UserNotInPilot = (
        "1002",
        "It seems that you are not invited to Pilot group. Please contact dhep.lab@gmail.com",
    )
    UserEmailIsAlreadySignup = ("1003", "Email is already sign up, please log in.")
    UserEmailIsNotSignup = ("1004", "Email hasn’t sign up, please sign up.")
    UserPasswordIncorrect = ("1005", "Incorrect password. Please try again.")
    ConfigFileIncorrect = (
        "1006",
        "Error while processing Excel file, please check again.",
    )
    InvalidFileExtension = (
        "1007",
        "Invalid file extension. Only .xlsx or .xls files are allowed."
    )
    NoFilePart = (
        "1008",
        "No file part in the request."
    )
    NoFileSelected = (
        "1009",
        "No file selected."
    )


    def __init__(self, code, message):
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message


class BusinessException(Exception):
    def __init__(self, businessExceptionEnum: BusinessExceptionEnum):
        self.error = businessExceptionEnum
