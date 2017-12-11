"""Payload validator.

The validator checks a payload against a :class:`~schemapilot.contract.Contract`
and emits a structured :class:`ValidationResult`. Every failure becomes a
:class:`Violation` carrying a stable ``code``, the offending field path, a
human message, and (where relevant) the observed and expected values.

Violation codes
---------------
=====================  ==============================================
Code                   Meaning
=====================  ==============================================
``MISSING_REQUIRED``   a required field is absent
``UNEXPECTED_FIELD``   a field not present in the contract
``TYPE_MISMATCH``      value type does not match the spec
``NULL_NOT_ALLOWED``   explicit null on a non-nullable field
