"""Minimal repair engine.

Given a contract and an invalid payload, :func:`repair_payload` computes a
:class:`RepairPlan`: an ordered list of concrete edits that would make the
payload conform, plus the repaired payload itself. The engine favours the
*smallest* change that resolves each violation:

- ``MISSING_REQUIRED`` -> insert the field's ``default`` when present, else a
  type-appropriate zero value.
- ``UNEXPECTED_FIELD``  -> drop the field.
- ``NULL_NOT_ALLOWED``  -> replace null with ``default`` or a zero value.
- ``TYPE_MISMATCH``     -> coerce when safely possible (e.g. ``"12"`` -> 12),
  otherwise substitute a zero value.
- ``ENUM_VIOLATION``    -> snap to the first enum member.
- ``BELOW_MIN``/``ABOVE_MAX`` -> clamp to the nearest bound.
- ``TOO_SHORT``/``TOO_LONG``  -> pad or truncate the string.
- ``TOO_FEW_ITEMS``/``TOO_MANY_ITEMS`` -> pad or trim the array.

Each repair is described by an :class:`Edit` so callers can present a diff and
