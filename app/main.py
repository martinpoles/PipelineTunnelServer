import json
import re
import threading
import time
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from app.config import TARGET_TEAM_ID, CLIENT_STATE
from app.graph import get_token, get_channel_name, create_channels_subscription, init_graph
from app.pipeline import run_pipeline
from app.ngrok_util import start_ngrok
from app.logger import logger
from app.utils import sanitize_filename

app = FastAPI()

def route_event(event):
    resource = event.get("resource", "")
    change = event.get("changeType", "")

    if "channels" in resource and change == "created":
        return "channel_created"

    return None

def handle_channel_created(event):

    try:
        resource = event.get("resource", "")

        team_match = re.search(r"teams\('([^']+)'\)", resource)
        channel_match = re.search(r"channels\('([^']+)'\)", resource)

        if not team_match or not channel_match:
            print("❌ Cannot parse resource:", resource)
            logger.info(f"Cannot parse resource:{resource}")
            return

        team_id = team_match.group(1)
        channel_id = channel_match.group(1)

        # filtro team
        if team_id != TARGET_TEAM_ID:
            return

        token = get_token()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        channel_name = get_channel_name(
            team_id,
            channel_id,
            headers
        )

        print(f"\n🆕 NUOVO CANALE CREATO: {channel_name}")
        logger.info(f"\nNUOVO CANALE CREATO: {channel_name}")

        print("\n🚀 RUN PIPELINE")
        logger.info("\n RUN PIPELINE")

        safe_channel_name = sanitize_filename(channel_name)

        run_pipeline(safe_channel_name)

    except Exception as e:
        print("❌ CHANNEL HANDLER ERROR:", e)
        logger.exception(f"CHANNEL HANDLER ERROR:{e}", )

@app.post("/webhook")
async def webhook(request: Request):

    try:
        body = await request.body()

        text = body.decode("utf-8") if body else ""

        data = {}

        if text:
            try:
                data = json.loads(text)
            except Exception:
                data = {}

        # -------------------------
        # GRAPH VALIDATION HANDSHAKE
        # -------------------------

        validation_token = request.query_params.get("validationToken")

        if validation_token:
            return PlainTextResponse(
                validation_token,
                status_code=200
            )

        if "validationToken" in data:
            return PlainTextResponse(
                data["validationToken"],
                status_code=200
            )

        # -------------------------
        # EVENT PROCESSING
        # -------------------------

        if "value" not in data:
            return PlainTextResponse("ok", status_code=200)

        events = data.get("value", [])

        for event in events:

            if event.get("clientState") != CLIENT_STATE:
                logger.warning("Invalid clientState")
                return PlainTextResponse("invalid", status_code=403)

            print("\n📩 RAW EVENT")
            logger.info("\n RAW EVENT")
            print(event)
            logger.info(event)

            event_type = route_event(event)

            if event_type == "channel_created":

                threading.Thread(
                    target=handle_channel_created,
                    args=(event,)
                ).start()

            else:
                print("⚠️ Unknown event type")
                logger.info("Unknown event type")

            return PlainTextResponse("ok", status_code=200)

    except Exception as e:
        print("❌ WEBHOOK ERROR:", e)
        logger.exception(f"WEBHOOK ERROR:{e}")

        return PlainTextResponse("ok", status_code=200)

@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


def subscription_renewer(ngrok_url):

    while True:

        print("\n🔄 Checking subscriptions...")
        logger.info("\n Checking subscriptions...")

        try:
            create_channels_subscription(
            ngrok_url,
            TARGET_TEAM_ID
        )

        except Exception as e:
            print("❌ Renew error:", e)
            logger.exception(f"Renew error:{e}")

        time.sleep(60 * 20)

def start_server():

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="warning"
    )


def main():

    logger.info("Starting application")

    # 1. FASTAPI
    server_thread = threading.Thread(
        target=start_server,
        daemon=True
    )

    server_thread.start()

    # 2. aspetta server pronto
    time.sleep(2)

    # 3. NGROK
    ngrok_url = start_ngrok()

    logger.info(f"[MAIN] Ngrok ready: {ngrok_url}")

    # 4. GRAPH INIT
    init_graph(ngrok_url)

    # 5. SUBSCRIPTIONS
    threading.Thread(
        target=subscription_renewer,
        args=(ngrok_url,),
        daemon=True
    ).start()

    # 6. KEEP ALIVE
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()