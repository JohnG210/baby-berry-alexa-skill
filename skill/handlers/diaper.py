"""
LogDiaperIntent

Slots:
  diaper_type   – custom: pee | wet | poo | poop | dirty | both | dry
  color         – custom: yellow | green | brown | black | red       (optional)
  consistency   – custom: solid | loose | runny | mucousy | hard | pebbles | diarrhea  (optional)
  diaper_rash   – custom: rash | no rash                             (optional)

API call: log_diaper(child_uid, mode, pee_amount=None, poo_amount=None,
                     color=None, consistency=None, diaper_rash=False)
  mode alone distinguishes pee/poo/both/dry — no separate pee/poo booleans.
  pee_amount / poo_amount ('little'|'medium'|'big') are not exposed via voice.
"""
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from huckleberry_client import get_client
from handlers.common import get_slot_value

_DIAPER_MAP = {
    "pee":   "pee",
    "wet":   "pee",
    "poo":   "poo",
    "poop":  "poo",
    "dirty": "poo",
    "both":  "both",
    "dry":   "dry",
}


class LogDiaperIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LogDiaperIntent")(handler_input)

    def handle(self, handler_input):
        api, child_uid = get_client()

        diaper_type_raw = (get_slot_value(handler_input, "diaper_type") or "").lower()
        color = get_slot_value(handler_input, "color")
        consistency = get_slot_value(handler_input, "consistency")
        diaper_rash_raw = get_slot_value(handler_input, "diaper_rash")

        mode = _DIAPER_MAP.get(diaper_type_raw)
        if not mode:
            speech = "I didn't catch the diaper type. Please say pee, poo, both, or dry."
            return handler_input.response_builder.speak(speech).response

        kwargs = {"mode": mode}
        if color:
            kwargs["color"] = color
        if consistency:
            kwargs["consistency"] = consistency
        if diaper_rash_raw is not None:
            kwargs["diaper_rash"] = (diaper_rash_raw.lower() == "rash")

        api.log_diaper(child_uid, **kwargs)

        label = diaper_type_raw if diaper_type_raw != "wet" else "pee"
        return handler_input.response_builder.speak(f"Logged {label} diaper.").response
