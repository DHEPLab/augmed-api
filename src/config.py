import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


def days_to_seconds(days: int):
    seconds_in_a_day = 24 * 60 * 60
    return days * seconds_in_a_day


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", days_to_seconds(3))
    )  # Defaults to 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRES", days_to_seconds(3))
    )  # Defaults to 3 days
