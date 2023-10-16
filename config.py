import dotenv
import os

dotenv.load_dotenv("local.env")

api_id = int(os.environ.get("API_ID") or 6)
api_hash = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RANDOM_NAME_TEXT_FILE = os.environ.get("RANDOM_NAME_TEXT_FILE_PATH") or "rndomname.txt"
IMG_PROFILE_PATH = os.environ.get("IMG_PROFILE_PATH") or "./profilepics/"
OWNER_ID = int(os.environ.get("OWNER_ID", 1))