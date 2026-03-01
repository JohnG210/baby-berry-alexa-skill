"""Tests for handlers/common.py — shared utilities and lifecycle handlers."""
from unittest.mock import MagicMock

import pytest
from ask_sdk_model import Slot

from handlers.common import (
    CancelOrStopIntentHandler,
    CatchAllExceptionHandler,
    HelpIntentHandler,
    LaunchRequestHandler,
    SessionEndedRequestHandler,
    get_slot_value,
)
from tests.conftest import (
    CHILD_UID,
    make_intent_input,
    make_launch_input,
    make_session_ended_input,
    speech,
)


# ── get_slot_value ───────────────────────────────────────────────────────────

class TestGetSlotValue:
    def test_returns_none_when_slots_absent(self):
        hi = make_launch_input()  # LaunchRequest has no slots
        # Simulate missing slots dict on intent
        hi.request_envelope.request.intent = None  # type: ignore[attr-defined]
        # Just call with a launch input — it has no intent, so slots is None
        # We test via intent input instead
        hi2 = make_intent_input("Foo", slots=None)
        hi2.request_envelope.request.intent.slots = None
        assert get_slot_value(hi2, "amount") is None

    def test_returns_none_when_slot_value_is_none(self):
        hi = make_intent_input("Foo", slots={"amount": None})
        assert get_slot_value(hi, "amount") is None

    def test_returns_raw_value_when_no_resolution(self):
        hi = make_intent_input("Foo", slots={"unit": "oz"})
        assert get_slot_value(hi, "unit") == "oz"

    def test_returns_none_for_missing_slot_name(self):
        hi = make_intent_input("Foo", slots={"unit": "oz"})
        assert get_slot_value(hi, "nonexistent") is None

    def test_prefers_entity_resolution_canonical_value(self):
        """ER_SUCCESS_MATCH should win over the raw spoken value."""
        hi = make_intent_input("Foo", slots={"unit": "ounces"})
        # Manually attach a resolution result
        from ask_sdk_model.slu.entityresolution import (
            Resolution,
            Resolutions,
            Status,
            ValueWrapper,
            Value,
            StatusCode,
        )
        resolution = Resolution(
            status=Status(code=StatusCode.ER_SUCCESS_MATCH),
            values=[ValueWrapper(value=Value(id="oz", name="oz"))],
        )
        slot = hi.request_envelope.request.intent.slots["unit"]
        slot.resolutions = Resolutions(resolutions_per_authority=[resolution])
        assert get_slot_value(hi, "unit") == "oz"


# ── LaunchRequestHandler ─────────────────────────────────────────────────────

class TestLaunchRequestHandler:
    def test_can_handle_launch(self):
        handler = LaunchRequestHandler()
        assert handler.can_handle(make_launch_input()) is True

    def test_cannot_handle_intent(self):
        handler = LaunchRequestHandler()
        assert handler.can_handle(make_intent_input("StartSleepIntent")) is False

    def test_response_mentions_key_features(self):
        handler = LaunchRequestHandler()
        resp = handler.handle(make_launch_input())
        text = speech(resp).lower()
        assert "baby tracker" in text
        assert "bottles" in text
        assert "nursing" in text
        assert "sleep" in text


# ── HelpIntentHandler ────────────────────────────────────────────────────────

class TestHelpIntentHandler:
    def test_can_handle(self):
        assert HelpIntentHandler().can_handle(
            make_intent_input("AMAZON.HelpIntent")
        ) is True

    def test_cannot_handle_other(self):
        assert HelpIntentHandler().can_handle(
            make_intent_input("StartSleepIntent")
        ) is False

    def test_response_covers_all_categories(self):
        resp = HelpIntentHandler().handle(make_intent_input("AMAZON.HelpIntent"))
        text = speech(resp).lower()
        for keyword in ("bottle", "nursing", "sleep", "diaper", "growth"):
            assert keyword in text, f"Help text missing category: {keyword}"


# ── CancelOrStopIntentHandler ────────────────────────────────────────────────

class TestCancelOrStopIntentHandler:
    def test_can_handle_cancel(self):
        assert CancelOrStopIntentHandler().can_handle(
            make_intent_input("AMAZON.CancelIntent")
        ) is True

    def test_can_handle_stop(self):
        assert CancelOrStopIntentHandler().can_handle(
            make_intent_input("AMAZON.StopIntent")
        ) is True

    def test_cannot_handle_other(self):
        assert CancelOrStopIntentHandler().can_handle(
            make_intent_input("StartSleepIntent")
        ) is False

    def test_response_is_goodbye(self):
        resp = CancelOrStopIntentHandler().handle(
            make_intent_input("AMAZON.CancelIntent")
        )
        assert "goodbye" in speech(resp).lower()


# ── SessionEndedRequestHandler ───────────────────────────────────────────────

class TestSessionEndedRequestHandler:
    def test_can_handle(self):
        assert SessionEndedRequestHandler().can_handle(
            make_session_ended_input()
        ) is True

    def test_returns_empty_response(self):
        resp = SessionEndedRequestHandler().handle(make_session_ended_input())
        assert resp.output_speech is None


# ── CatchAllExceptionHandler ─────────────────────────────────────────────────

class TestCatchAllExceptionHandler:
    def test_can_handle_any_exception(self):
        handler = CatchAllExceptionHandler()
        hi = make_launch_input()
        assert handler.can_handle(hi, Exception("boom")) is True
        assert handler.can_handle(hi, ValueError("bad")) is True

    def test_response_is_sorry(self):
        handler = CatchAllExceptionHandler()
        hi = make_launch_input()
        resp = handler.handle(hi, Exception("boom"))
        assert "something went wrong" in speech(resp).lower()
