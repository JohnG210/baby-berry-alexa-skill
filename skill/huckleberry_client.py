"""
Thin authentication wrapper for huckleberry-api.

Re-authenticates on every call — Lambda is stateless and invocations may hit
fresh containers at any time.

Real API: HuckleberryAPI(email, password, timezone) then .authenticate()
"""
import os
import time
import uuid

from huckleberry_api import HuckleberryAPI


def get_client():
    """Return an authenticated (api, child_uid) tuple from env vars."""
    email = os.environ["HUCKLEBERRY_EMAIL"]
    password = os.environ["HUCKLEBERRY_PASSWORD"]
    child_uid = os.environ["HUCKLEBERRY_CHILD_UID"]
    timezone = os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC")

    api = HuckleberryAPI(email=email, password=password, timezone=timezone)
    api.authenticate()

    return api, child_uid


def log_bottle_at_time(api, child_uid, amount, bottle_type, units, start_timestamp):
    """
    Log a bottle feeding at a specific Unix timestamp.

    The huckleberry-api's log_bottle_feeding() always uses now — it has no
    timestamp parameter. This function writes the Firestore document directly,
    mirroring the exact structure the API uses, with a custom start time.
    """
    client = api._get_firestore_client()
    feed_ref = client.collection("feed").document(child_uid)

    now_time = time.time()
    # Use the target time for the interval ID so it sorts correctly in the app
    interval_id = f"{int(start_timestamp * 1000)}-{uuid.uuid4().hex[:20]}"
    offset = api._get_timezone_offset_minutes()

    bottle_entry = {
        "mode": "bottle",
        "start": start_timestamp,
        "lastUpdated": now_time,
        "bottleType": bottle_type,
        "amount": amount,
        "units": units,
        "offset": offset,
        "end_offset": offset,
    }

    feed_ref.collection("intervals").document(interval_id).set(bottle_entry)

    last_bottle_data = {
        "mode": "bottle",
        "start": start_timestamp,
        "bottleType": bottle_type,
        "bottleAmount": amount,
        "bottleUnits": units,
        "offset": offset,
    }

    feed_ref.set(
        {
            "prefs": {
                "lastBottle": last_bottle_data,
                "bottleType": bottle_type,
                "bottleAmount": amount,
                "bottleUnits": units,
                "timestamp": {"seconds": now_time},
                "local_timestamp": now_time,
            }
        },
        merge=True,
    )
