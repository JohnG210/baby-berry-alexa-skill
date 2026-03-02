"""
Shared fixtures and builder helpers for the baby-tracker skill test suite.

Run from the skill/ directory:
    pytest

Or from the repo root:
    pytest skill/tests/
"""
import os
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import (
    Application,
    Intent,
    IntentRequest,
    LaunchRequest,
    RequestEnvelope,
    Session,
    SessionEndedRequest,
    Slot,
    User,
)

# Allow `import handlers.*` and `import huckleberry_client` when pytest is
# invoked from the repo root (e.g. `pytest skill/tests/`).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Constants ────────────────────────────────────────────────────────────────

CHILD_UID = "test_child_uid"

# ── Request envelope builders ────────────────────────────────────────────────

def _session():
    return Session(
        session_id="s-test",
        application=Application(application_id="app-test"),
        user=User(user_id="user-test"),
        new=False,
    )


def _handler_input(request):
    return HandlerInput(
        request_envelope=RequestEnvelope(
            version="1.0",
            session=_session(),
            request=request,
        ),
    )


def make_intent_input(intent_name, slots=None):
    """
    Build a HandlerInput for an IntentRequest.

    `slots` is a plain dict of {slot_name: value_string | None}.
    """
    slot_map = {}
    if slots:
        for name, value in slots.items():
            slot_map[name] = Slot(name=name, value=value)
    return _handler_input(
        IntentRequest(
            request_id="req-test",
            timestamp=datetime.now(timezone.utc),
            intent=Intent(name=intent_name, slots=slot_map),
        )
    )


def make_launch_input():
    return _handler_input(
        LaunchRequest(request_id="req-test", timestamp=datetime.now(timezone.utc))
    )


def make_session_ended_input():
    return _handler_input(
        SessionEndedRequest(request_id="req-test", timestamp=datetime.now(timezone.utc))
    )


# ── Response helper ──────────────────────────────────────────────────────────

def speech(response):
    """Strip SSML tags: '<speak>Hello.</speak>' → 'Hello.'"""
    ssml = response.output_speech.ssml
    return ssml.replace("<speak>", "").replace("</speak>", "")


# ── Shared fixture ───────────────────────────────────────────────────────────

@pytest.fixture
def mock_client(mocker):
    """
    Factory fixture.  Patch get_client in a specific handlers submodule.

    Usage in a test file:
        @pytest.fixture
        def mock_api(mock_client):
            return mock_client("sleep")
    """
    def _patch(module_name):
        api = MagicMock()
        mocker.patch(
            f"handlers.{module_name}.get_client",
            return_value=(api, CHILD_UID),
        )
        return api

    return _patch
