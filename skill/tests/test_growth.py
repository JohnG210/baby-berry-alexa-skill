"""Tests for handlers/growth.py — LogGrowthIntent."""
import pytest

from handlers.growth import LogGrowthIntentHandler
from tests.conftest import CHILD_UID, make_intent_input, speech


@pytest.fixture
def mock_api(mock_client):
    return mock_client("growth")


HANDLER = LogGrowthIntentHandler()


# ── can_handle ───────────────────────────────────────────────────────────────

def test_can_handle():
    assert HANDLER.can_handle(make_intent_input("LogGrowthIntent")) is True

def test_cannot_handle_other():
    assert HANDLER.can_handle(make_intent_input("StartSleepIntent")) is False


# ── Imperial → metric conversion ─────────────────────────────────────────────

def test_imperial_weight_converted_to_kg(mock_api):
    hi = make_intent_input(
        "LogGrowthIntent", {"weight": "10", "unit_system": "imperial"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert abs(kwargs["weight"] - 4.53592) < 0.0001

def test_imperial_height_converted_to_cm(mock_api):
    hi = make_intent_input(
        "LogGrowthIntent", {"height": "22", "unit_system": "imperial"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert abs(kwargs["height"] - 55.88) < 0.01

def test_imperial_head_converted_to_cm(mock_api):
    hi = make_intent_input(
        "LogGrowthIntent", {"head": "15", "unit_system": "imperial"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert abs(kwargs["head"] - 38.1) < 0.01

def test_all_three_imperial_measurements(mock_api):
    hi = make_intent_input(
        "LogGrowthIntent",
        {"weight": "10", "height": "22", "head": "15", "unit_system": "imperial"},
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert "weight" in kwargs
    assert "height" in kwargs
    assert "head" in kwargs


# ── Units always sent as metric ───────────────────────────────────────────────

def test_units_always_metric_for_imperial_input(mock_api):
    hi = make_intent_input(
        "LogGrowthIntent", {"weight": "10", "unit_system": "imperial"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert kwargs["units"] == "metric"

def test_units_always_metric_for_metric_input(mock_api):
    hi = make_intent_input(
        "LogGrowthIntent", {"weight": "5", "unit_system": "metric"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert kwargs["units"] == "metric"


# ── Metric passthrough (no conversion) ───────────────────────────────────────

def test_metric_weight_not_converted(mock_api):
    hi = make_intent_input(
        "LogGrowthIntent", {"weight": "5", "unit_system": "metric"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert kwargs["weight"] == 5.0

def test_metric_height_not_converted(mock_api):
    hi = make_intent_input(
        "LogGrowthIntent", {"height": "60", "unit_system": "metric"}
    )
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert kwargs["height"] == 60.0


# ── None values not forwarded ─────────────────────────────────────────────────

def test_only_weight_provided_no_height_or_head_in_kwargs(mock_api):
    hi = make_intent_input("LogGrowthIntent", {"weight": "10"})
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert "weight" in kwargs
    assert "height" not in kwargs
    assert "head" not in kwargs

def test_only_height_provided(mock_api):
    hi = make_intent_input("LogGrowthIntent", {"height": "22"})
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    assert "height" in kwargs
    assert "weight" not in kwargs
    assert "head" not in kwargs


# ── No measurements → error ───────────────────────────────────────────────────

def test_no_measurements_returns_error(mock_api):
    hi = make_intent_input("LogGrowthIntent")
    resp = HANDLER.handle(hi)
    assert "at least one" in speech(resp).lower()
    mock_api.log_growth.assert_not_called()


# ── Confirmation speech ───────────────────────────────────────────────────────

def test_confirmation_speech(mock_api):
    hi = make_intent_input("LogGrowthIntent", {"weight": "10"})
    resp = HANDLER.handle(hi)
    assert "growth logged" in speech(resp).lower()


# ── Default unit_system is imperial ──────────────────────────────────────────

def test_default_unit_system_is_imperial(mock_api):
    """When unit_system slot is absent, treat as imperial and convert."""
    hi = make_intent_input("LogGrowthIntent", {"weight": "10"})
    HANDLER.handle(hi)
    _, kwargs = mock_api.log_growth.call_args
    # 10 lbs → ~4.54 kg (not 10.0) confirms imperial path was taken
    assert kwargs["weight"] < 5.0
