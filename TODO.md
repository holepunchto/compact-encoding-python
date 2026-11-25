# TODO

Agent task tracking for this repo. One entry per line:

```markdown
- [ ] **Title** `[role]` - one sentence saying what the work is. (origin)
```

`[role]` is one of `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Sub-items and findings go in indented bullets beneath an entry. The PR that finishes an entry deletes it; git history is the record of what shipped.

GitHub Issues are the surface for external contributors. A conformance run that finds the corpus wrong rather than this port goes to `compact-encoding-test`, not here.

- [ ] **Decide what `json` is** `[needs-info]` - `json` writes Python's serialisation rather than the reference's bytes, so it is not interchangeable, and no corpus case can catch it. (conformance run, 2026-11-25)
  - An integral float keeps its `.0`: `{"a": 1.0}` writes `{"a":1.0}` where the reference writes `{"a":1}`, and the length prefix moves with it.
  - `inf` and `nan` write `Infinity` and `NaN`, which are not JSON at all and which a strict decoder in another language rejects; the reference writes `null`.
  - An integer-like key sorts first in the reference's object order, where Python keeps insertion order: `{"b": 1, "1": 2}` writes the pairs the other way round.
  - `compact-encoding-test` excludes `json` deliberately, as JavaScript's semantics behind a length prefix, so the harness reports this port conformant while `json` is not.
  - Three ways out, in rising cost: drop the codec, document it as this port's own format rather than a portable one, or match `JSON.stringify` closely enough to be byte-compatible.
