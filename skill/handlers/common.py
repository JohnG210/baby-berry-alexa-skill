"""
Shared utilities and non-domain intent handlers:
  LaunchRequest, AMAZON.HelpIntent, AMAZON.CancelIntent,
  AMAZON.StopIntent, SessionEndedRequest, CatchAllExceptionHandler.
"""
import logging

from ask_sdk_core.dispatch_components import (
    AbstractExceptionHandler,
    AbstractRequestHandler,
)
from ask_sdk_core.utils import is_intent_name, is_request_type

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Slot helper
# ---------------------------------------------------------------------------

def get_slot_value(handler_input, slot_name):
    """
    Return the resolved canonical value for a slot, or the raw spoken value
    if no entity resolution match exists, or None if the slot is absent/empty.
    """
    slots = handler_input.request_envelope.request.intent.slots
    if not slots or slot_name not in slots:
        return None
    slot = slots[slot_name]
    if not slot or slot.value is None:
        return None

    # Prefer entity-resolution canonical name (ER_SUCCESS_MATCH)
    resolutions = slot.resolutions
    if resolutions and resolutions.resolutions_per_authority:
        for resolution in resolutions.resolutions_per_authority:
            if resolution.status.code.value == "ER_SUCCESS_MATCH":
                return resolution.values[0].value.name

    return slot.value


# ---------------------------------------------------------------------------
# LaunchRequestHandler
# ---------------------------------------------------------------------------

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech = (
            "Baby tracker ready. "
            "You can log bottles, nursing, diapers, sleep, and growth."
        )
        return handler_input.response_builder.speak(speech).response


# ---------------------------------------------------------------------------
# HelpIntentHandler
# ---------------------------------------------------------------------------

HELP_TEXT = (
    "Here's what you can say. "
    "For bottles: log 4 ounces bottle, or log 120 milliliters breast milk bottle. "
    "For nursing: start nursing, start left side, pause feeding, resume feeding, "
    "switch side, stop feeding, cancel feeding. "
    "For sleep: baby is sleeping, pause sleep, resume sleep, baby woke up, cancel sleep. "
    "For diapers: log a pee diaper, log a dirty diaper, log a poo diaper with a rash. "
    "For growth: log weight 10 pounds, log height 22 inches, log head circumference 15. "
    "For status: when was the last feeding, how long since last diaper, "
    "how long since last sleep, or give me a status update for all three."
)


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.speak(HELP_TEXT).response


# ---------------------------------------------------------------------------
# CancelOrStopIntentHandler
# ---------------------------------------------------------------------------

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or \
               is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.speak("Goodbye.").response


# ---------------------------------------------------------------------------
# SessionEndedRequestHandler
# ---------------------------------------------------------------------------

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


# ---------------------------------------------------------------------------
# CatchAllExceptionHandler
# ---------------------------------------------------------------------------

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.exception("Unhandled exception: %s", exception)
        speech = "Sorry, something went wrong. Please try again."
        return handler_input.response_builder.speak(speech).response
