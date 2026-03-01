"""
LogGrowthIntent

Slots:
  weight      – AMAZON.NUMBER  (optional)
  height      – AMAZON.NUMBER  (optional)
  head        – AMAZON.NUMBER  (optional)
  unit_system – custom: metric | imperial  (optional, default imperial)

Conversion (imperial → metric, always passed as metric to API):
  weight : lbs  → kg   (* 0.453592)
  height : in   → cm   (* 2.54)
  head   : in   → cm   (* 2.54)

Only parameters provided by the user are forwarded to the API call.
"""
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from huckleberry_client import get_client
from handlers.common import get_slot_value


def _to_float(raw):
    """Return float or None."""
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


class LogGrowthIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LogGrowthIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()

        weight_raw = get_slot_value(handler_input, "weight")
        height_raw = get_slot_value(handler_input, "height")
        head_raw   = get_slot_value(handler_input, "head")
        unit_system = (get_slot_value(handler_input, "unit_system") or "imperial").lower()

        weight = _to_float(weight_raw)
        height = _to_float(height_raw)
        head   = _to_float(head_raw)

        if weight is None and height is None and head is None:
            speech = "Please provide at least one measurement — weight, height, or head circumference."
            return handler_input.response_builder.speak(speech).response

        # Convert imperial → metric
        if unit_system == "imperial":
            if weight is not None:
                weight = round(weight * 0.453592, 4)
            if height is not None:
                height = round(height * 2.54, 4)
            if head is not None:
                head = round(head * 2.54, 4)

        # Build kwargs with only the provided measurements
        kwargs = {"units": "metric"}
        if weight is not None:
            kwargs["weight"] = weight
        if height is not None:
            kwargs["height"] = height
        if head is not None:
            kwargs["head"] = head

        api.log_growth(child_uid, **kwargs)

        return handler_input.response_builder.speak("Growth logged.").response
