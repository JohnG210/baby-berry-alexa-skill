"""Tests for handlers/diaper.py — LogDiaperIntent."""
import pytest

from handlers.diaper import LogDiaperIntentHandler
from tests.conftest import CHILD_UID, make_intent_input, speech


@pytest.fixture
def mock_api(mock_client):
    return mock_client("diaper")


HANDLER = LogDiaperIntentHandler()


# ── can_handle ───────────────────────────────────────────────────────────────

def test_can_handle():
    assert HANDLER.can_handle(make_intent_input("LogDiaperIntent")) is True

def test_cannot_handle_other():
    assert HANDLER.can_handle(make_intent_input("StartSleepIntent")) is False


# ── Diaper-type mapping ───────────────────────────────────────────────────────

@pytest.mark.parametrize("spoken,expected_mode,expected_pee,expected_poo", [
    ("pee",   "pee",  True,  False),
    ("wet",   "pee",  True,  False),
    ("poo",   "poo",  False, True),
    ("poop",  "poo",  False, True),
    ("dirty", "poo",  False, True),
    ("both",  "both", True,  True),
    ("dry",   "dry",  False, False),
])
def test_diaper_type_mapping(mock_api, spoken, expected_mode, expected_pee, expected_poo):
    hi = make_intent_input("LogDiaperIntent", {"diaper_type": spoken})
    HANDLER.handle(hi)
    mock_api.log_diaper.assert_called_once()
    _, kwargs = mock_api.log_diaper.call_args
    assert kwargs["mode"] == expected_mode
    assert kwargs["pee"] is expected_pee
    assert kwargs["poo"] is expected_poo


# ── Optional slots ────────────────────────────────────────────────────────────

def test_color_passed_when_provided(mock_api):
    hi = make_intent_input("LogDiaperIntent", {"diaper_type": "poo", "color": "yellow"})
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_diaper.call_args
    assert kwargs["color"] == "yellow"

def test_color_absent_when_not_provided(mock_api):
    hi = make_intent_input("LogDiaperIntent", {"diaper_type": "pee"})
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_diaper.call_args
    assert "color" not in kwargs

def test_consistency_passed_when_provided(mock_api):
    hi = make_intent_input(
        "LogDiaperIntent", {"diaper_type": "poo", "consistency": "loose"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_diaper.call_args
    assert kwargs["consistency"] == "loose"

def test_consistency_absent_when_not_provided(mock_api):
    hi = make_intent_input("LogDiaperIntent", {"diaper_type": "poo"})
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_diaper.call_args
    assert "consistency" not in kwargs


# ── Diaper rash ───────────────────────────────────────────────────────────────

def test_rash_maps_to_true(mock_api):
    hi = make_intent_input(
        "LogDiaperIntent", {"diaper_type": "poo", "diaper_rash": "rash"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_diaper.call_args
    assert kwargs["diaper_rash"] is True

def test_no_rash_maps_to_false(mock_api):
    hi = make_intent_input(
        "LogDiaperIntent", {"diaper_type": "poo", "diaper_rash": "no rash"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_diaper.call_args
    assert kwargs["diaper_rash"] is False

def test_diaper_rash_absent_when_not_provided(mock_api):
    hi = make_intent_input("LogDiaperIntent", {"diaper_type": "pee"})
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_diaper.call_args
    assert "diaper_rash" not in kwargs


# ── Unknown type ──────────────────────────────────────────────────────────────

def test_unknown_diaper_type_returns_error(mock_api):
    hi = make_intent_input("LogDiaperIntent", {"diaper_type": "unknown"})
    resp = HANDLER.handle(hi)
    assert "didn't catch" in speech(resp).lower()
    mock_api.log_diaper.assert_not_called()

def test_missing_diaper_type_returns_error(mock_api):
    hi = make_intent_input("LogDiaperIntent")
    resp = HANDLER.handle(hi)
    assert "didn't catch" in speech(resp).lower()
    mock_api.log_diaper.assert_not_called()


# ── Confirmation speech ───────────────────────────────────────────────────────

def test_confirmation_includes_type(mock_api):
    hi = make_intent_input("LogDiaperIntent", {"diaper_type": "poo"})
    resp = HANDLER.handle(hi)
    assert "poo" in speech(resp).lower()
