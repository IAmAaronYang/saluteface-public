"""Deterministic payload fuzzer.

The fuzzer turns a :class:`~schemapilot.contract.Contract` into a stream of
:class:`FuzzCase` objects. Generation is *deterministic*: the same contract
and seed always produce the same cases, which makes reports diffable and CI
reproducible.

Two families of cases are produced:

``valid``
    Payloads that satisfy every constraint. Useful as golden fixtures and to
    prove a downstream consumer accepts conforming data.

``adversarial``
    Payloads that violate exactly one constraint in a labelled way (wrong
    type, out-of-bounds, enum miss, pattern miss, missing-required, extra
    field, null-where-not-allowed, empty/oversized arrays). Each adversarial
    case records the *mutation* applied so validators and repair plans can be
    scored against a known ground truth.

The generator uses a small linear-congruential PRNG seeded from the contract
fingerprint plus the user seed, so it never touches the global ``random``
state and stays reproducible across processes and platforms.
