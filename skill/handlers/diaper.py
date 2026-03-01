"""
LogDiaperIntent

Slots:
  diaper_type   – custom: pee | wet | poo | poop | dirty | both | dry
  color         – custom: yellow | green | brown | black | red       (optional)
  consistency   – custom: solid | loose | runny | mucousy | hard | pebbles | diarrhea  (optional)
  diaper_rash   – custom: rash | no rash                             (optional)

Mapping:
  pee / wet          → mode="pee",  pee=True,  poo=False
  poo / poop / dirty → mode="poo",  pee=False, poo=True
  both               → mode="both", pee=True,  poo=True
  dry                → mode="dry",  pee=False, poo=False
"""
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

from huckleberry_client import get_client
from handlers.common import get_slot_value

_DIAPER_MAP = {
    "pee":   ("pee",  True,  False),
    "wet":   ("pee",  True,  False),
    "poo":   ("poo",  False, True),
    "poop":  ("poo",  False, True),
    "dirty": ("poo",  False, True),
    "both":  ("both", True,  True),
    "dry":   ("dry",  False, False),
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

        if diaper_type_raw not in _DIAPER_MAP:
            speech = "I didn't catch the diaper type. Please say pee, poo, both, or dry."
            return handler_input.response_builder.speak(speech).response

        mode, pee, poo = _DIAPER_MAP[diaper_type_raw]

        kwargs = {"mode": mode, "pee": pee, "poo": poo}
        if color:
            kwargs["color"] = color
        if consistency:
            kwargs["consistency"] = consistency
        if diaper_rash_raw is not None:
            kwargs["diaper_rash"] = (diaper_rash_raw.lower() == "rash")

        api.log_diaper(child_uid, **kwargs)

        label = diaper_type_raw if diaper_type_raw != "wet" else "pee"
        return handler_input.response_builder.speak(f"Logged {label} diaper.").response
