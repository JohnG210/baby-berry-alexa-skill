"""Tests for handlers/status.py — status query intents."""
import time

import pytest

from handlers.status import (
    LastDiaperStatusIntentHandler,
    LastFeedingStatusIntentHandler,
    LastSleepStatusIntentHandler,
    StatusSummaryIntentHandler,
    _time_since_speech,
)
from tests.conftest import CHILD_UID, make_intent_input, speech


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_api(mock_client):
    return mock_client("status")


# ── _time_since_speech helper ─────────────────────────────────────────────────

@pytest.mark.parametrize("seconds,expected", [
    (30,     "less than a minute"),
    (60,     "1 minute"),
    (120,    "2 minutes"),
    (3600,   "1 hour"),
    (7200,   "2 hours"),
    (3660,   "1 hour and 1 minute"),
    (7320,   "2 hours and 2 minutes"),
    (5400,   "1 hour and 30 minutes"),
])
def test_time_since_speech(seconds, expected):
    assert _time_since_speech(seconds) == expected


# ── can_handle ────────────────────────────────────────────────────────────────

def test_feeding_can_handle():
    assert LastFeedingStatusIntentHandler().can_handle(
        make_intent_input("LastFeedingStatusIntent")
    ) is True

def test_diaper_can_handle():
    assert LastDiaperStatusIntentHandler().can_handle(
        make_intent_input("LastDiaperStatusIntent")
    ) is True

def test_sleep_can_handle():
    assert LastSleepStatusIntentHandler().can_handle(
        make_intent_input("LastSleepStatusIntent")
    ) is True

def test_summary_can_handle():
    assert StatusSummaryIntentHandler().can_handle(
        make_intent_input("StatusSummaryIntent")
    ) is True


# ── LastFeedingStatusIntent ───────────────────────────────────────────────────

def test_feeding_reports_elapsed(mock_api):
    two_hours_ago = int(time.time()) - 7200
    mock_api.get_feed_intervals.return_value = [{"start": two_hours_ago}]
    hi = make_intent_input("LastFeedingStatusIntent")
    resp = LastFeedingStatusIntentHandler().handle(hi)
    assert "2 hours" in speech(resp)
    assert "feeding" in speech(resp).lower()

def test_feeding_no_results(mock_api):
    mock_api.get_feed_intervals.return_value = []
    hi = make_intent_input("LastFeedingStatusIntent")
    resp = LastFeedingStatusIntentHandler().handle(hi)
    assert "couldn't find" in speech(resp).lower()

def test_feeding_picks_most_recent(mock_api):
    now = int(time.time())
    mock_api.get_feed_intervals.return_value = [
        {"start": now - 7200},
        {"start": now - 3600},  # most recent
    ]
    hi = make_intent_input("LastFeedingStatusIntent")
    resp = LastFeedingStatusIntentHandler().handle(hi)
    assert "1 hour" in speech(resp)


# ── LastDiaperStatusIntent ────────────────────────────────────────────────────

def test_diaper_reports_elapsed(mock_api):
    ninety_min_ago = int(time.time()) - 5400
    mock_api.get_diaper_intervals.return_value = [
        {"start": ninety_min_ago, "mode": "pee"}
    ]
    hi = make_intent_input("LastDiaperStatusIntent")
    resp = LastDiaperStatusIntentHandler().handle(hi)
    assert "1 hour and 30 minutes" in speech(resp)
    assert "diaper" in speech(resp).lower()

def test_diaper_no_results(mock_api):
    mock_api.get_diaper_intervals.return_value = []
    hi = make_intent_input("LastDiaperStatusIntent")
    resp = LastDiaperStatusIntentHandler().handle(hi)
    assert "couldn't find" in speech(resp).lower()


# ── LastSleepStatusIntent ─────────────────────────────────────────────────────

def test_sleep_uses_end_time(mock_api):
    now = int(time.time())
    # Sleep started 3 h ago, lasted 1 h → ended 2 h ago
    mock_api.get_sleep_intervals.return_value = [
        {"start": now - 10800, "duration": 3600}
    ]
    hi = make_intent_input("LastSleepStatusIntent")
    resp = LastSleepStatusIntentHandler().handle(hi)
    assert "2 hours" in speech(resp)
    assert "sleep" in speech(resp).lower()

def test_sleep_in_progress(mock_api):
    now = int(time.time())
    # Sleep started 30 min ago, duration 0 → still sleeping
    mock_api.get_sleep_intervals.return_value = [
        {"start": now - 1800, "duration": 0}
    ]
    hi = make_intent_input("LastSleepStatusIntent")
    resp = LastSleepStatusIntentHandler().handle(hi)
    assert "sleeping" in speech(resp).lower()
    assert "30 minutes" in speech(resp)

def test_sleep_no_results(mock_api):
    mock_api.get_sleep_intervals.return_value = []
    hi = make_intent_input("LastSleepStatusIntent")
    resp = LastSleepStatusIntentHandler().handle(hi)
    assert "couldn't find" in speech(resp).lower()


# ── StatusSummaryIntent ───────────────────────────────────────────────────────

def test_summary_includes_all_three(mock_api):
    now = int(time.time())
    mock_api.get_feed_intervals.return_value = [{"start": now - 3600}]
    mock_api.get_diaper_intervals.return_value = [{"start": now - 7200, "mode": "pee"}]
    mock_api.get_sleep_intervals.return_value = [{"start": now - 10800, "duration": 3600}]

    hi = make_intent_input("StatusSummaryIntent")
    resp = StatusSummaryIntentHandler().handle(hi)
    text = speech(resp).lower()

    assert "feeding" in text
    assert "diaper" in text
    assert "sleep" in text

def test_summary_handles_missing_data(mock_api):
    mock_api.get_feed_intervals.return_value = []
    mock_api.get_diaper_intervals.return_value = []
    mock_api.get_sleep_intervals.return_value = []

    hi = make_intent_input("StatusSummaryIntent")
    resp = StatusSummaryIntentHandler().handle(hi)
    text = speech(resp).lower()

    assert "no recent feeding" in text
    assert "no recent diaper" in text
    assert "no recent sleep" in text
