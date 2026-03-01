"""Tests for handlers/bottle_feeding.py — LogBottleFeedingIntent."""
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


# ── Time slot — start kwarg probe ────────────────────────────────────────────

def test_time_slot_passes_start_kwarg_when_supported(mock_api):
    """When time slot is present and API accepts start=, log with timestamp."""
    hi = make_intent_input(
        "LogBottleFeedingIntent",
        {"amount": "4", "unit": "oz", "time": "14:30"},
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_bottle_feeding.call_args
    assert "start" in kwargs
    assert isinstance(kwargs["start"], int)

def test_time_slot_falls_back_when_start_not_supported(mock_api):
    """TypeError on start= → retry without it and add spoken caveat."""
    mock_api.log_bottle_feeding.side_effect = [TypeError("unexpected keyword"), None]
    hi = make_intent_input(
        "LogBottleFeedingIntent",
        {"amount": "4", "unit": "oz", "time": "14:30"},
    )
    resp = HANDLER.handle(hi)
    # Called twice: once with start=, once without
    assert mock_api.log_bottle_feeding.call_count == 2
    second_call_kwargs = mock_api.log_bottle_feeding.call_args_list[1][1]
    assert "start" not in second_call_kwargs
    assert "current time" in speech(resp).lower()

def test_no_time_slot_calls_api_once_without_start(mock_api):
    hi = make_intent_input("LogBottleFeedingIntent", {"amount": "4", "unit": "oz"})
    HANDLER.handle(hi)
    mock_api.log_bottle_feeding.assert_called_once()
    _, kwargs = mock_api.log_bottle_feeding.call_args
    assert "start" not in kwargs
