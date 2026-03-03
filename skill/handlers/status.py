"""
Status query intent handlers — "how long since last X?"

Intents:
  LastFeedingStatusIntent  – how long since the last feeding (nursing or bottle)
  LastDiaperStatusIntent   – how long since the last diaper change
  LastSleepStatusIntent    – how long since the last sleep session ended
  StatusSummaryIntent      – all three at once
"""
import time
import logging

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from huckleberry_client import get_client

logger = logging.getLogger(__name__)

# How far back to search (seconds). 48 h covers all realistic gaps.
_LOOKBACK = 48 * 3600


def _time_since_speech(elapsed_seconds):
    """
    Convert a number of elapsed seconds into a natural-language phrase like
    '2 hours and 15 minutes' or '45 minutes' or 'less than a minute'.
    """
    if elapsed_seconds < 60:
        return "less than a minute"

    hours = int(elapsed_seconds // 3600)
    minutes = int((elapsed_seconds % 3600) // 60)

    if hours == 0:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    if minutes == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    return (
        f"{hours} hour{'s' if hours != 1 else ''} "
        f"and {minutes} minute{'s' if minutes != 1 else ''}"
    )


def _last_feeding_phrase(api, child_uid):
    """
    Return a speech phrase for the last feeding, e.g.
    'Last feeding was 2 hours and 10 minutes ago.'
    Returns None if no recent feeding is found.
    """
    now = int(time.time())
    intervals = api.get_feed_intervals(child_uid, now - _LOOKBACK, now)
    if not intervals:
        return None
    last = max(intervals, key=lambda e: e["start"])
    elapsed = now - last["start"]
    return f"Last feeding was {_time_since_speech(elapsed)} ago."


def _last_diaper_phrase(api, child_uid):
    """
    Return a speech phrase for the last diaper change.
    Returns None if no recent change is found.
    """
    now = int(time.time())
    intervals = api.get_diaper_intervals(child_uid, now - _LOOKBACK, now)
    if not intervals:
        return None
    last = max(intervals, key=lambda e: e["start"])
    elapsed = now - last["start"]
    return f"Last diaper change was {_time_since_speech(elapsed)} ago."


def _last_sleep_phrase(api, child_uid):
    """
    Return a speech phrase for the last sleep session.
    Uses the end of the session (start + duration) when available so the
    elapsed time reflects how long the baby has been awake.
    Returns None if no recent sleep is found.
    """
    now = int(time.time())
    intervals = api.get_sleep_intervals(child_uid, now - _LOOKBACK, now)
    if not intervals:
        return None
    last = max(intervals, key=lambda e: e["start"])
    duration = last.get("duration", 0)
    if not duration:
        # Session is still in progress (no duration recorded yet)
        elapsed = now - last["start"]
        return f"Baby has been sleeping for {_time_since_speech(elapsed)}."
    elapsed = now - (last["start"] + duration)
    return f"Last sleep ended {_time_since_speech(elapsed)} ago."


# ---------------------------------------------------------------------------
# LastFeedingStatusIntent
# ---------------------------------------------------------------------------

class LastFeedingStatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LastFeedingStatusIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        phrase = _last_feeding_phrase(api, child_uid)
        speech = phrase or "I couldn't find a recent feeding in the last 48 hours."
        return handler_input.response_builder.speak(speech).response


# ---------------------------------------------------------------------------
# LastDiaperStatusIntent
# ---------------------------------------------------------------------------

class LastDiaperStatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LastDiaperStatusIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        phrase = _last_diaper_phrase(api, child_uid)
        speech = phrase or "I couldn't find a recent diaper change in the last 48 hours."
        return handler_input.response_builder.speak(speech).response


# ---------------------------------------------------------------------------
# LastSleepStatusIntent
# ---------------------------------------------------------------------------

class LastSleepStatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LastSleepStatusIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        phrase = _last_sleep_phrase(api, child_uid)
        speech = phrase or "I couldn't find a recent sleep session in the last 48 hours."
        return handler_input.response_builder.speak(speech).response


# ---------------------------------------------------------------------------
# StatusSummaryIntent
# ---------------------------------------------------------------------------

class StatusSummaryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("StatusSummaryIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()

        feeding = _last_feeding_phrase(api, child_uid) or "No recent feeding found."
        diaper = _last_diaper_phrase(api, child_uid) or "No recent diaper change found."
        sleep = _last_sleep_phrase(api, child_uid) or "No recent sleep found."

        speech = f"{feeding} {diaper} {sleep}"
        return handler_input.response_builder.speak(speech).response
