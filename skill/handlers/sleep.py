"""
Sleep intent handlers:
  StartSleepIntent    – api.start_sleep(child_uid)
  PauseSleepIntent    – api.pause_sleep(child_uid)
  ResumeSleepIntent   – api.resume_sleep(child_uid)
  CompleteSleepIntent – api.complete_sleep(child_uid)
  CancelSleepIntent   – api.cancel_sleep(child_uid)
"""
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from huckleberry_client import get_client


class StartSleepIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("StartSleepIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.start_sleep(child_uid)
        return handler_input.response_builder.speak("Sleep session started.").response


class PauseSleepIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("PauseSleepIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.pause_sleep(child_uid)
        return handler_input.response_builder.speak("Sleep paused.").response


class ResumeSleepIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ResumeSleepIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.resume_sleep(child_uid)
        return handler_input.response_builder.speak("Sleep resumed.").response


class CompleteSleepIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CompleteSleepIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.complete_sleep(child_uid)
        return handler_input.response_builder.speak("Sleep session saved.").response


class CancelSleepIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("CancelSleepIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()
        api.cancel_sleep(child_uid)
        return handler_input.response_builder.speak("Sleep session cancelled.").response
