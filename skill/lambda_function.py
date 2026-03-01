"""
Entry point for the Baby Tracker Alexa skill.
Invocation name: "baby tracker"

Lambda handler: lambda_function.lambda_handler
"""
import logging

from ask_sdk_core.skill_builder import SkillBuilder

from handlers.bottle_feeding import LogBottleFeedingIntentHandler
from handlers.common import (
    CancelOrStopIntentHandler,
    CatchAllExceptionHandler,
    HelpIntentHandler,
    LaunchRequestHandler,
    SessionEndedRequestHandler,
)
from handlers.diaper import LogDiaperIntentHandler
from handlers.growth import LogGrowthIntentHandler
from handlers.nursing import (
    CancelFeedingIntentHandler,
    CompleteFeedingIntentHandler,
    PauseFeedingIntentHandler,
    ResumeFeedingIntentHandler,
    StartFeedingIntentHandler,
    SwitchFeedingSideIntentHandler,
)
from handlers.sleep import (
    CancelSleepIntentHandler,
    CompleteSleepIntentHandler,
    PauseSleepIntentHandler,
    ResumeSleepIntentHandler,
    StartSleepIntentHandler,
)

logging.basicConfig(level=logging.INFO)

sb = SkillBuilder()

# Built-in / lifecycle handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Bottle feeding
sb.add_request_handler(LogBottleFeedingIntentHandler())

# Nursing
sb.add_request_handler(StartFeedingIntentHandler())
sb.add_request_handler(PauseFeedingIntentHandler())
sb.add_request_handler(ResumeFeedingIntentHandler())
sb.add_request_handler(SwitchFeedingSideIntentHandler())
sb.add_request_handler(CompleteFeedingIntentHandler())
sb.add_request_handler(CancelFeedingIntentHandler())

# Sleep
sb.add_request_handler(StartSleepIntentHandler())
sb.add_request_handler(PauseSleepIntentHandler())
sb.add_request_handler(ResumeSleepIntentHandler())
sb.add_request_handler(CompleteSleepIntentHandler())
sb.add_request_handler(CancelSleepIntentHandler())

# Diaper & growth
sb.add_request_handler(LogDiaperIntentHandler())
sb.add_request_handler(LogGrowthIntentHandler())

# Exception handler must be last
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
