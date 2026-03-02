"""Tests for handlers/bottle_feeding.py — LogBottleFeedingIntent."""
import os
import pytest
from unittest.mock import call

from handlers.bottle_feeding import LogBottleFeedingIntentHandler
from tests.conftest import CHILD_UID, make_intent_input, speech


@pytest.fixture
def mock_api(mock_client):
    return mock_client("bottle_feeding")


HANDLER = LogBottleFeedingIntentHandler()


# ── can_handle ───────────────────────────────────────────────────────────────

def test_can_handle():
    assert HANDLER.can_handle(make_intent_input("LogBottleFeedingIntent")) is True

def test_cannot_handle_other():
    assert HANDLER.can_handle(make_intent_input("StartSleepIntent")) is False


# ── Happy path ───────────────────────────────────────────────────────────────

def test_4oz_formula(mock_api):
    hi = make_intent_input("LogBottleFeedingIntent", {"amount": "4", "unit": "oz"})
    resp = HANDLER.handle(hi)
    mock_api.log_bottle_feeding.assert_called_once_with(
        CHILD_UID, amount=4.0, bottle_type="Formula", units="oz"
    )
    assert "4 oz Formula bottle feeding" in speech(resp)

def test_120ml_breast_milk(mock_api):
    hi = make_intent_input(
        "LogBottleFeedingIntent",
        {"amount": "120", "unit": "ml", "feed_type": "breast milk"},
    )
    resp = HANDLER.handle(hi)
    mock_api.log_bottle_feeding.assert_called_once_with(
        CHILD_UID, amount=120.0, bottle_type="Breast Milk", units="ml"
    )
    assert "120 ml Breast Milk" in speech(resp)

def test_mixed_bottle(mock_api):
    hi = make_intent_input(
        "LogBottleFeedingIntent",
        {"amount": "3", "unit": "oz", "feed_type": "mixed"},
    )
    HANDLER.handle(hi)
    mock_api.log_bottle_feeding.assert_called_once_with(
        CHILD_UID, amount=3.0, bottle_type="Mixed", units="oz"
    )


# ── Unit normalisation ───────────────────────────────────────────────────────

@pytest.mark.parametrize("spoken,expected", [
    ("oz", "oz"),
    ("ounces", "oz"),
    ("ml", "ml"),
    ("milliliters", "ml"),
])
def test_unit_normalisation(mock_api, spoken, expected):
    hi = make_intent_input("LogBottleFeedingIntent", {"amount": "4", "unit": spoken})
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_bottle_feeding.call_args
    assert kwargs["units"] == expected


# ── Feed-type mapping ────────────────────────────────────────────────────────

@pytest.mark.parametrize("spoken,expected", [
    ("formula",     "Formula"),
    ("breast milk", "Breast Milk"),
    ("mixed",       "Mixed"),
    (None,          "Formula"),   # default when slot absent
])
def test_feed_type_mapping(mock_api, spoken, expected):
    slots = {"amount": "4", "unit": "oz"}
    if spoken is not None:
        slots["feed_type"] = spoken
    hi = make_intent_input("LogBottleFeedingIntent", slots)
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_bottle_feeding.call_args
    assert kwargs["bottle_type"] == expected


# ── Whole-number formatting ───────────────────────────────────────────────────

def test_whole_number_displayed_without_decimal(mock_api):
    hi = make_intent_input("LogBottleFeedingIntent", {"amount": "4.0", "unit": "oz"})
    resp = HANDLER.handle(hi)
    # "4" not "4.0"
    assert "4 oz" in speech(resp)
    assert "4.0" not in speech(resp)


# ── Missing / invalid amount ─────────────────────────────────────────────────

def test_missing_amount_returns_error(mock_api):
    hi = make_intent_input("LogBottleFeedingIntent", {"unit": "oz"})
    resp = HANDLER.handle(hi)
    assert "didn't catch the amount" in speech(resp).lower()
    mock_api.log_bottle_feeding.assert_not_called()

def test_invalid_amount_returns_error(mock_api):
    hi = make_intent_input(
        "LogBottleFeedingIntent", {"amount": "four", "unit": "oz"}
    )
    resp = HANDLER.handle(hi)
    assert "couldn't understand" in speech(resp).lower()
    mock_api.log_bottle_feeding.assert_not_called()


# ── Time slot — routes to log_bottle_at_time ─────────────────────────────────

def test_time_slot_calls_log_bottle_at_time_not_api(mock_api, mocker):
    """When time slot is present, log_bottle_at_time() is used instead of the API method."""
    mock_at_time = mocker.patch("handlers.bottle_feeding.log_bottle_at_time")
    hi = make_intent_input(
        "LogBottleFeedingIntent",
        {"amount": "4", "unit": "oz", "time": "14:30"},
    )
    HANDLER.handle(hi)
    mock_at_time.assert_called_once()
    mock_api.log_bottle_feeding.assert_not_called()

def test_time_slot_passes_correct_timestamp(mock_api, mocker):
    """The Unix timestamp passed to log_bottle_at_time reflects the requested time."""
    import datetime, pytz
    mock_at_time = mocker.patch("handlers.bottle_feeding.log_bottle_at_time")
    hi = make_intent_input(
        "LogBottleFeedingIntent",
        {"amount": "60", "unit": "ml", "time": "19:07"},
    )
    HANDLER.handle(hi)
    _, kwargs = mock_at_time.call_args
    ts = kwargs.get("start_timestamp") or mock_at_time.call_args[0][5]
    tz = pytz.timezone(os.environ.get("HUCKLEBERRY_TIMEZONE", "UTC"))
    dt = datetime.datetime.fromtimestamp(ts, tz=tz)
    assert dt.hour == 19
    assert dt.minute == 7

def test_no_time_slot_calls_api_once_without_start(mock_api):
    hi = make_intent_input("LogBottleFeedingIntent", {"amount": "4", "unit": "oz"})
    HANDLER.handle(hi)
    mock_api.log_bottle_feeding.assert_called_once()
    _, kwargs = mock_api.log_bottle_feeding.call_args
    assert "start" not in kwargs
