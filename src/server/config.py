import os
from dotenv import load_dotenv


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PWD")
DB_HOST = os.getenv("DB_HOST")

DB_ROOT = os.getenv("DB_ROOT")
DB_APP = os.getenv("DB_APP")
DB_TEST = os.getenv("DB_TEST")

DB_APP_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PWD}@{DB_HOST}/{DB_APP}"
DB_TEST_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PWD}@{DB_HOST}/{DB_TEST}"

USER_NAME = os.getenv("USER_NAME")
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")

SECRET_KEY = os.getenv("SECRET_KEY")

SENTRY_DSN = os.getenv("SENTRY_DSN")
