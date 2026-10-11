# Async validation sketch

Today `schemapilot validate` walks a fixture set synchronously.
A future path could yield `(fixture, result)` as they complete while keeping
the same report schema and the same determinism guarantees per fixture.

Open questions: ordering of the streamed report, and how failures surface
mid-stream. Both are solvable without changes to the schema format.
