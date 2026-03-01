"""Tests for handlers/sleep.py — all sleep intents."""
import pytest

from handlers.sleep import (
    CancelSleepIntentHandler,
    CompleteSleepIntentHandler,
    PauseSleepIntentHandler,
    ResumeSleepIntentHandler,
    StartSleepIntentHandler,
)
from tests.conftest import CHILD_UID, make_intent_input, speech


@pytest.fixture
def mock_api(mock_client):
    return mock_client("sleep")


@pytest.mark.parametrize("intent,handler_cls,api_method,expected_phrase", [
    ("StartSleepIntent",    StartSleepIntentHandler,    "start_sleep",    "started"),
    ("PauseSleepIntent",    PauseSleepIntentHandler,    "pause_sleep",    "paused"),
    ("ResumeSleepIntent",   ResumeSleepIntentHandler,   "resume_sleep",   "resumed"),
    ("CompleteSleepIntent", CompleteSleepIntentHandler, "complete_sleep", "saved"),
    ("CancelSleepIntent",   CancelSleepIntentHandler,   "cancel_sleep",   "cancelled"),
])
class TestSleepHandlers:
    def test_can_handle(self, mock_api, intent, handler_cls, api_method, expected_phrase):
        assert handler_cls().can_handle(make_intent_input(intent)) is True

    def test_cannot_handle_other(self, mock_api, intent, handler_cls, api_method, expected_phrase):
        assert handler_cls().can_handle(make_intent_input("LogDiaperIntent")) is False

    def test_calls_correct_api_method(self, mock_api, intent, handler_cls, api_method, expected_phrase):
        hi = make_intent_input(intent)
        handler_cls().handle(hi)
        getattr(mock_api, api_method).assert_called_once_with(CHILD_UID)

    def test_confirmation_speech(self, mock_api, intent, handler_cls, api_method, expected_phrase):
        hi = make_intent_input(intent)
        resp = handler_cls().handle(hi)
        assert expected_phrase in speech(resp).lower()
