"""Tests for handlers/nursing.py — all nursing/breastfeeding intents."""
import pytest

from handlers.nursing import (
    CancelFeedingIntentHandler,
    CompleteFeedingIntentHandler,
    PauseFeedingIntentHandler,
    ResumeFeedingIntentHandler,
    StartFeedingIntentHandler,
    SwitchFeedingSideIntentHandler,
)
from tests.conftest import CHILD_UID, make_intent_input, speech


@pytest.fixture
def mock_api(mock_client):
    return mock_client("nursing")


# ── StartFeedingIntent ───────────────────────────────────────────────────────

class TestStartFeedingIntent:
    def test_can_handle(self):
        assert StartFeedingIntentHandler().can_handle(
            make_intent_input("StartFeedingIntent")
        ) is True

    def test_cannot_handle_other(self):
        assert StartFeedingIntentHandler().can_handle(
            make_intent_input("PauseFeedingIntent")
        ) is False

    def test_left_side(self, mock_api):
        hi = make_intent_input("StartFeedingIntent", {"side": "left"})
        resp = StartFeedingIntentHandler().handle(hi)
        mock_api.start_feeding.assert_called_once_with(CHILD_UID, side="left")
        assert "left" in speech(resp)

    def test_right_side(self, mock_api):
        hi = make_intent_input("StartFeedingIntent", {"side": "right"})
        resp = StartFeedingIntentHandler().handle(hi)
        mock_api.start_feeding.assert_called_once_with(CHILD_UID, side="right")
        assert "right" in speech(resp)

    def test_defaults_to_left_when_side_absent(self, mock_api):
        hi = make_intent_input("StartFeedingIntent")
        resp = StartFeedingIntentHandler().handle(hi)
        mock_api.start_feeding.assert_called_once_with(CHILD_UID, side="left")
        assert "left" in speech(resp)


# ── PauseFeedingIntent ───────────────────────────────────────────────────────

class TestPauseFeedingIntent:
    def test_can_handle(self):
        assert PauseFeedingIntentHandler().can_handle(
            make_intent_input("PauseFeedingIntent")
        ) is True

    def test_calls_api_and_confirms(self, mock_api):
        hi = make_intent_input("PauseFeedingIntent")
        resp = PauseFeedingIntentHandler().handle(hi)
        mock_api.pause_feeding.assert_called_once_with(CHILD_UID)
        assert "paused" in speech(resp).lower()


# ── ResumeFeedingIntent — no side argument ───────────────────────────────────

class TestResumeFeedingIntent:
    def test_can_handle(self):
        assert ResumeFeedingIntentHandler().can_handle(
            make_intent_input("ResumeFeedingIntent")
        ) is True

    def test_calls_api_without_side_arg(self, mock_api):
        hi = make_intent_input("ResumeFeedingIntent")
        ResumeFeedingIntentHandler().handle(hi)
        # Must be called with ONLY child_uid — no side kwarg
        mock_api.resume_feeding.assert_called_once_with(CHILD_UID)
        call_kwargs = mock_api.resume_feeding.call_args[1]
        assert "side" not in call_kwargs

    def test_confirms_resumed(self, mock_api):
        hi = make_intent_input("ResumeFeedingIntent")
        resp = ResumeFeedingIntentHandler().handle(hi)
        assert "resumed" in speech(resp).lower()


# ── SwitchFeedingSideIntent ──────────────────────────────────────────────────

class TestSwitchFeedingSideIntent:
    def test_can_handle(self):
        assert SwitchFeedingSideIntentHandler().can_handle(
            make_intent_input("SwitchFeedingSideIntent")
        ) is True

    def test_calls_api_and_confirms(self, mock_api):
        hi = make_intent_input("SwitchFeedingSideIntent")
        resp = SwitchFeedingSideIntentHandler().handle(hi)
        mock_api.switch_feeding_side.assert_called_once_with(CHILD_UID)
        assert "switched" in speech(resp).lower()


# ── CompleteFeedingIntent ────────────────────────────────────────────────────

class TestCompleteFeedingIntent:
    def test_can_handle(self):
        assert CompleteFeedingIntentHandler().can_handle(
            make_intent_input("CompleteFeedingIntent")
        ) is True

    def test_calls_api_and_confirms(self, mock_api):
        hi = make_intent_input("CompleteFeedingIntent")
        resp = CompleteFeedingIntentHandler().handle(hi)
        mock_api.complete_feeding.assert_called_once_with(CHILD_UID)
        assert "saved" in speech(resp).lower()


# ── CancelFeedingIntent ──────────────────────────────────────────────────────

class TestCancelFeedingIntent:
    def test_can_handle(self):
        assert CancelFeedingIntentHandler().can_handle(
            make_intent_input("CancelFeedingIntent")
        ) is True

    def test_calls_api_and_confirms(self, mock_api):
        hi = make_intent_input("CancelFeedingIntent")
        resp = CancelFeedingIntentHandler().handle(hi)
        mock_api.cancel_feeding.assert_called_once_with(CHILD_UID)
        assert "cancelled" in speech(resp).lower()
