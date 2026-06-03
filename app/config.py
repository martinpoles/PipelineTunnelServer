import os
import platform
import sys
from dotenv import load_dotenv
from app.logger import logger

load_dotenv()

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_nas_root():

    system = platform.system()

    if system == "Windows":
        return os.getenv("NAS_ROOT_WINDOWS")

    elif system == "Darwin":
        return os.getenv("NAS_ROOT_MAC")

    elif system == "Linux":
        return os.getenv("NAS_ROOT_LINUX")

    else:
        logger.exception(f"Unsupported OS: {system}")
        raise Exception(f"Unsupported OS: {system}")

NAS_ROOT = get_nas_root()

NAS_STORAGE = os.path.join(
    NAS_ROOT,
    os.getenv("NAS_PROJECTS_FOLDER", "01_PROGETTI")
)

TEMPLATE_PATH = os.path.join(
    NAS_ROOT,
    os.getenv("NAS_TEMPLATE_PATH", "00_BASE/BAS_A_Cartella Base")
)


CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
CLICKUP_FOLDER_ID = os.getenv("CLICKUP_FOLDER_ID")
CLICKUP_TEMPLATE_ID = os.getenv("CLICKUP_TEMPLATE_ID")

PORT = int(os.getenv("PORT", 8080))

CLIENT_STATE = os.getenv("CLIENT_STATE")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
TARGET_TEAM_ID = os.getenv("TARGET_TEAM_ID")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

NGROK_PATH = "/usr/local/bin/ngrok"