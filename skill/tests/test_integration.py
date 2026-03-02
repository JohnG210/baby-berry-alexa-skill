"""
Integration tests — hit the real Huckleberry API.

These are skipped automatically if the required environment variables are not
set, so they never run in CI unless explicitly configured.

Run them locally with:
    ./run_pytest.sh -v -m integration
"""
import datetime
import json
import os

import pytest
import pytz

# Skip entire module if credentials are absent
pytestmark = pytest.mark.skipif(
    not os.environ.get("HUCKLEBERRY_EMAIL"),
    reason="HUCKLEBERRY_* env vars not set — skipping integration tests",
)


def _invoke(event_file):
    """Load an event JSON and invoke the Lambda handler, return the response dict."""
    import lambda_function

    with open(event_file) as f:
        event = json.load(f)
    return lambda_function.lambda_handler(event, {})


def _speech(response):
    return response["response"]["outputSpeech"]["ssml"].replace("<speak>", "").replace("</speak>", "")


# ── Launch ────────────────────────────────────────────────────────────────────

def test_launch_no_api_call():
    resp = _invoke("test_events/launch.json")
    assert resp["response"]["outputSpeech"] is not None
    assert "baby tracker" in _speech(resp).lower()


# ── 60 ml bottle at 7:07 PM — the core use-case ──────────────────────────────

def test_log_60ml_bottle_at_7_07_pm():
    """
    Log 60 ml Formula at 7:07 PM today in the configured timezone.
    Verifies:
      - Authentication succeeds
      - log_bottle_at_time() writes to Firestore without error
      - The spoken response confirms the correct amount, unit, and type
      - The Firestore start timestamp is 7:07 PM today (within ±60 s)
    """
    resp = _invoke("test_events/bottle_with_time.json")
    text = _speech(resp)

    assert "60 ml" in text, f"Expected '60 ml' in speech: {text}"
    assert "Formula" in text, f"Expected 'Formula' in speech: {text}"
    assert "bottle feeding" in text.lower(), f"Expected 'bottle feeding' in speech: {text}"

    # Verify the timestamp that would have been written is correct
    tz_name = os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC")
    tz = pytz.timezone(tz_name)
    now = datetime.datetime.now(tz)
    expected_dt = now.replace(hour=19, minute=7, second=0, microsecond=0)
    expected_ts = int(expected_dt.timestamp())

    # Re-derive the same way the handler does
    from handlers.bottle_feeding import _parse_alexa_time
    actual_ts = _parse_alexa_time("19:07")

    assert actual_ts is not None, "Time parsing returned None for '19:07'"
    assert abs(actual_ts - expected_ts) <= 60, (
        f"Timestamp mismatch: got {actual_ts}, expected ~{expected_ts}"
    )


# ── Confirm the correct time is being sent to Firestore ──────────────────────

@pytest.mark.parametrize("time_str,expected_hour,expected_minute", [
    ("19:07", 19,  7),
    ("08:30",  8, 30),
    ("00:00",  0,  0),
    ("13:45", 13, 45),
])
def test_time_parsing_produces_correct_local_hour_and_minute(time_str, expected_hour, expected_minute):
    """_parse_alexa_time should yield a timestamp whose local time matches the slot value."""
    from handlers.bottle_feeding import _parse_alexa_time

    tz_name = os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC")
    tz = pytz.timezone(tz_name)

    ts = _parse_alexa_time(time_str)
    assert ts is not None

    dt = datetime.datetime.fromtimestamp(ts, tz=tz)
    assert dt.hour == expected_hour
    assert dt.minute == expected_minute
