import jwt
import msal
import requests
from datetime import datetime, timedelta
from logger import logger
from config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, CLIENT_STATE, TARGET_TEAM_ID
from graph_store import upsert_subscription, get_valid_subscription, cleanup_expired

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

def get_token():

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

    token = app.acquire_token_for_client(
        scopes=SCOPE
    )

    return token["access_token"]

def build_headers(token):

    return {
        "Authorization": f"Bearer {token}"
    }

def create_graph_subscription(payload):

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://graph.microsoft.com/v1.0/subscriptions"

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print("SUB:", response.status_code, response.text)
    logger.info(f"SUB:{response.status_code}, {response.text}")

    if response.status_code not in [200, 201]:
        return None

    data = response.json()

    subscription = {
        "id": data.get("id"),
        "resource": payload["resource"],
        "expiration": data.get("expirationDateTime")
    }

    upsert_subscription(subscription)

    return data

def get_channel_name(team_id, channel_id, headers):

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"teams/{team_id}/channels/{channel_id}"
    )

    response = requests.get(
        url,
        headers=headers
    )

    if response.status_code != 200:
        print("[GRAPH] cannot fetch channel:", response.text)
        logger.info(f"[GRAPH] cannot fetch channel:{response.text}")
        return None

    return response.json().get("displayName")

def fetch_teams(headers):

    url = (
        "https://graph.microsoft.com/v1.0/groups"
        "?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')"
    )

    response = requests.get(
        url,
        headers=headers
    )

    print("[INIT] teams status:", response.status_code)
    logger.info(f"[INIT] teams status:{response.status_code}")

    if response.status_code != 200:
        print("[INIT][FATAL] cannot fetch teams")
        logger.info(f"[INIT][FATAL] cannot fetch teams")
        print(response.text)
        logger.info(f"{response.text}")
        return []

    groups = response.json().get("value", [])

    return [{"id": g["id"]} for g in groups]

def create_channels_subscription(webhook_url, team_id):

    resource = f"/teams/{team_id}/channels"

    existing = get_valid_subscription(resource)

    if existing:
        print("✅ Subscription already valid:", resource)
        logger.info(f"Subscription already valid:{resource}")
        return existing

    payload = {
        "changeType": "created",
        "notificationUrl": f"{webhook_url}/webhook",
        "resource": resource,
        "expirationDateTime": (
            datetime.utcnow() + timedelta(minutes=50)
        ).isoformat() + "Z",
        "clientState": CLIENT_STATE
    }

    print("⚡ Creating subscription:", resource)
    logger.info(f"Creating subscription:{resource}")

    return create_graph_subscription(payload)

def bootstrap(ngrok_url):

    print(
        f"[BOOTSTRAP] subscribing to team: "
        f"{TARGET_TEAM_ID}"
    )
    logger.info(
        f"[BOOTSTRAP] subscribing to team: "
        f"{TARGET_TEAM_ID}"
        )

    create_channels_subscription(
        ngrok_url,
        TARGET_TEAM_ID
    )

def print_architettura_channels(headers):

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"teams/{TARGET_TEAM_ID}/channels"
    )

    response = requests.get(
        url,
        headers=headers
    )

    print("\n====== CANALI ARCHITETTURA ======\n")
    logger.info("\n====== CANALI ARCHITETTURA ======\n")

    if response.status_code != 200:
        print("Errore:", response.text)
        logger.info(f"Errore:{response.text}")
        return

    channels = response.json().get("value", [])

    for channel in channels:
        print(" -", channel["displayName"])
        logger.info(f" -{channel['displayName']}")

def init_graph(ngrok_url):

    print("\n================ INIT GRAPH START ================\n")
    logger.info("\n================ INIT GRAPH START ================\n")
    print("[INIT] cleaning old subscriptions...")
    logger.info("[INIT] cleaning old subscriptions...")

    cleanup_expired()

    print("[INIT] getting access token...")
    logger.info("[INIT] getting access token...")

    try:

        token = get_token()

        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )

        print("[INIT] token roles:", decoded.get("roles", []))
        logger.info(f"[INIT] token roles: {decoded.get('roles', [])}")
        print("[INIT] token acquired ✔")
        logger.info("[INIT] token acquired ✔")

    except Exception as e:

        print("[INIT][ERROR] token failed:", e)
        logger.info(f"[INIT][ERROR] token failed:{e}")

        return

    headers = build_headers(token)

    print("[INIT] fetching teams...")
    logger.info("[INIT] fetching teams...")

    teams = fetch_teams(headers)

    if not teams:
        print("[INIT][FATAL] no teams found")
        logger.info("[INIT][FATAL] no teams found")
        return

    print(f"[INIT] found {len(teams)} teams")
    logger.info(f"[INIT] found {len(teams)} teams")

    print("[INIT] starting bootstrap...")
    logger.info("[INIT] starting bootstrap...")

    try:

        bootstrap(ngrok_url)

        print("[INIT] bootstrap completed ✔")
        logger.info("[INIT] bootstrap completed ✔")

    except Exception as e:

        print("[INIT][ERROR] bootstrap failed:", e)
        logger.info(f"[INIT][ERROR] bootstrap failed:{e}")

    print_architettura_channels(headers)

    print("\n================ INIT GRAPH END ================\n")
    logger.info("\n================ INIT GRAPH END ================\n")