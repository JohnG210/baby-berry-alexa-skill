"""
LogBottleFeedingIntent

Slots:
  amount      – AMAZON.NUMBER
  unit        – custom: oz | ounces | ml | milliliters
  feed_type   – custom: formula | breast milk | mixed  (optional, default "Formula")
  time        – AMAZON.TIME  (optional)

Notes:
  • Units are normalised: ounces→oz, milliliters→ml before passing to the API.
  • feed_type is title-cased: formula→"Formula", breast milk→"Breast Milk", mixed→"Mixed".
  • The huckleberry-api log_bottle_feeding() does not document a timestamp param.
    We attempt to pass `start=<unix_ts>` and silently fall back to current time
    if the API raises TypeError (unsupported kwarg).
"""
import datetime
import logging
import os

import pytz
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from huckleberry_client import get_client
from handlers.common import get_slot_value

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Normalisation maps
# ---------------------------------------------------------------------------

_UNIT_MAP = {
    "ounces": "oz",
    "oz": "oz",
    "milliliters": "ml",
    "ml": "ml",
}

_FEED_TYPE_MAP = {
    "formula": "Formula",
    "breast milk": "Breast Milk",
    "mixed": "Mixed",
}


def _parse_alexa_time(time_str):
    """
    Convert an AMAZON.TIME value (HH:MM, 24-hour) to a Unix timestamp in the
    skill's configured timezone.  Returns None for fuzzy values (MO/NI/AF/EV)
    or parse errors.
    """
    if not time_str or len(time_str) != 5 or ":" not in time_str:
        return None
    try:
        tz = pytz.timezone(os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC"))
        now = datetime.datetime.now(tz)
        hour, minute = map(int, time_str.split(":"))
        dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return int(dt.timestamp())
    except (ValueError, pytz.UnknownTimeZoneError):
        return None


class LogBottleFeedingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LogBottleFeedingIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()

        # --- slots ---
        amount_raw = get_slot_value(handler_input, "amount")
        unit_raw = (get_slot_value(handler_input, "unit") or "").lower()
        feed_type_raw = (get_slot_value(handler_input, "feed_type") or "formula").lower()
        time_raw = get_slot_value(handler_input, "time")

        if amount_raw is None:
            speech = "I didn't catch the amount. Please try again."
            return handler_input.response_builder.speak(speech).response

        try:
            amount = float(amount_raw)
        except ValueError:
            speech = "I couldn't understand the amount. Please try again."
            return handler_input.response_builder.speak(speech).response

        units = _UNIT_MAP.get(unit_raw, "oz")
        feed_type = _FEED_TYPE_MAP.get(feed_type_raw, "Formula")
        timestamp = _parse_alexa_time(time_raw)

        # Attempt to pass a start timestamp; fall back if API rejects the kwarg.
        time_caveat = ""
        if timestamp:
            try:
                api.log_bottle_feeding(
                    child_uid,
                    amount=amount,
                    bottle_type=feed_type,
                    units=units,
                    start=timestamp,
                )
            except TypeError:
                logger.warning(
                    "log_bottle_feeding does not accept 'start'; logging at current time."
                )
                api.log_bottle_feeding(
                    child_uid,
                    amount=amount,
                    bottle_type=feed_type,
                    units=units,
                )
                time_caveat = " Note: time override is not supported, logged at current time."
        else:
            api.log_bottle_feeding(
                child_uid,
                amount=amount,
                bottle_type=feed_type,
                units=units,
            )

        # Format amount: strip unnecessary decimal for whole numbers
        amount_str = str(int(amount)) if amount == int(amount) else str(amount)
        speech = f"Logged {amount_str} {units} {feed_type} bottle feeding.{time_caveat}"
        return handler_input.response_builder.speak(speech).response
