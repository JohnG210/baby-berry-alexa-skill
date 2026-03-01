"""
Nursing / breastfeeding intent handlers:
  StartFeedingIntent      – api.start_feeding(child_uid, side=side)
  PauseFeedingIntent      – api.pause_feeding(child_uid)
  ResumeFeedingIntent     – api.resume_feeding(child_uid)   ← no side arg
  SwitchFeedingSideIntent – api.switch_feeding_side(child_uid)
  CompleteFeedingIntent   – api.complete_feeding(child_uid)
  CancelFeedingIntent     – api.cancel_feeding(child_uid)
"""
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from huckleberry_client import get_client
from handlers.common import get_slot_value


class StartFeedingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("StartFeedingIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        side = (get_slot_value(handler_input, "side") or "left").lower()
        api.start_feeding(child_uid, side=side)
        return handler_input.response_builder.speak(
            f"Nursing started on the {side}."
        ).response


class PauseFeedingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("PauseFeedingIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.pause_feeding(child_uid)
        return handler_input.response_builder.speak("Feeding paused.").response


class ResumeFeedingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ResumeFeedingIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        # resume_feeding takes no side argument
        api.resume_feeding(child_uid)
        return handler_input.response_builder.speak("Feeding resumed.").response


class SwitchFeedingSideIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SwitchFeedingSideIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.switch_feeding_side(child_uid)
        return handler_input.response_builder.speak("Switched feeding side.").response


class CompleteFeedingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CompleteFeedingIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.complete_feeding(child_uid)
        return handler_input.response_builder.speak("Nursing session saved.").response


class CancelFeedingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CancelFeedingIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.cancel_feeding(child_uid)
        return handler_input.response_builder.speak("Feeding session cancelled.").response
