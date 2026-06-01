import json
import os
import sys
from app.logger import logger

from datetime import datetime, timedelta

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

FILE = os.path.join(BASE_DIR, "subscriptions.json")


def load_subscriptions():

    if not os.path.exists(FILE):
        return []

    with open(FILE, "r") as f:
        return json.load(f)

def save_all(subscriptions):

    with open(FILE, "w") as f:
        json.dump(
            subscriptions,
            f,
            indent=2
        )

def is_subscription_valid(
    subscription,
    buffer_minutes=2
):

    expiration = subscription.get("expiration")

    if not expiration:
        return False

    expiration_dt = datetime.fromisoformat(
        expiration.replace("Z", "")
    )

    return (
        expiration_dt >
        datetime.utcnow() + timedelta(minutes=buffer_minutes)
    )

def upsert_subscription(subscription):

    data = load_subscriptions()

    # remove same resource
    data = [
        s for s in data
        if s["resource"] != subscription["resource"]
    ]

    data.append(subscription)

    save_all(data)

def get_valid_subscription(resource):

    data = load_subscriptions()

    for subscription in data:

        if (
            subscription["resource"] == resource
            and
            is_subscription_valid(subscription)
        ):
            return subscription

    return None

def cleanup_expired():

    data = load_subscriptions()

    valid = [
        subscription
        for subscription in data
        if is_subscription_valid(
            subscription,
            buffer_minutes=0
        )
    ]

    removed = len(data) - len(valid)

    if removed > 0:
        print(
            f"[GRAPH] Cleanup: "
            f"removed {removed} expired subscriptions"
        )
        logger.info(
            f"[GRAPH] Cleanup: "
            f"removed {removed} expired subscriptions")

    save_all(valid)