from dotenv import load_dotenv
import os

OVERRIDES = {"dm          *spotify": "spotify"}
EXCLUDES = ["pagamentos validos normais"]

load_dotenv()

NEXTCLOUD_USERNAME = os.getenv("NEXTCLOUD_USERNAME")
NEXTCLOUD_PASSWORD = os.getenv("NEXTCLOUD_PASSWORD")
NEXTCLOUD_DAV_ENDPOINT = os.getenv("NEXTCLOUD_DAV_ENDPOINT")
NEXTCLOUD_FOLDER = os.getenv("NEXTCLOUD_FOLDER")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
