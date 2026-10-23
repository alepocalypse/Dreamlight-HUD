"""Text of a rotating Dreamlight Duty or Mist Duty: slot_duty_text(duty_id, target, filter), slot_title(key).

The templates are the game's (slot_text.py); {TargetAmount} is the slot's target and {ItemName} the name of
the filter's item, a Villager for a Character one. Unknown ids answer 'Duty #id', unknown items 'Item #id'.
"""
import re

from .items import item_name
from .slot_text import SLOT_TEXT, SLOT_TITLES
from .villagers import VILLAGERS


def slot_title(key):
    return SLOT_TITLES.get(str(key), "Duties")


def slot_duty_text(duty_id, target, filter):
    template = SLOT_TEXT.get(duty_id)
    if template is None:
        return f"Duty #{duty_id}"
    item = filter.get("item")
    name = (VILLAGERS.get(item) or item_name(item)) if item else ""
    return re.sub(r"\{(\w+)\}", lambda m: str(target) if m[1].lower() == "targetamount" else name, template)


def names_a_zone(text):
    """True when the duty text sets a place ('in the Glittering Dunes', 'from the Forest of Valor') that the
    save's filter does not carry, so what counts is not fully known from the filter."""
    return bool(re.search(r"\b(?:in|from|at) the [A-Z]", text))
