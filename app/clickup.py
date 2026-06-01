import requests
from app.config import CLICKUP_API_KEY, CLICKUP_FOLDER_ID, CLICKUP_TEMPLATE_ID
from app.logger import logger


BASE_URL = "https://api.clickup.com/api/v2"

HEADERS = {
    "Authorization": CLICKUP_API_KEY,
    "Content-Type": "application/json"
}

def create_list_from_template(list_name, template_id, options=None):
   
    url = f"{BASE_URL}/folder/{CLICKUP_FOLDER_ID}/list_template/{CLICKUP_TEMPLATE_ID}"

    payload = {
        "name": list_name
    }

    if options:
        payload["options"] = options

    print(f"[CLICKUP] Creating list from template: {list_name} (template: {template_id})")
    logger.info(f"[CLICKUP] Creating list from template: {list_name} (template: {template_id})")



    r = requests.post(url, json=payload, headers=HEADERS, timeout=15)

    if r.status_code != 200:
        logger.exception(f"ClickUp error: {r.text}")
        raise Exception(f"ClickUp error: {r.text}")

    data = r.json()

    # ClickUp può restituire id o list_id a seconda della risposta
    return data.get("id") or data.get("list_id")