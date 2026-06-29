# Validation and Testing Plan

## Validator categories

### Graph validators

- all edge endpoints exist;
- node ids are unique;
- committed manuscript artifacts have writing task packets;
- review findings have backflow targets;
- stale nodes list a stale reason;
- owner intent changes have owner evidence.

### Material validators

- envelope fields present;
- typed payload required fields present;
- source inputs exist;
- validators are declared;
- invalidation policy exists.

### Manuscript validators

- no internal code leakage in main prose;
- no raw snake_case constraints;
- no bare citation keys in rendered output;
- claims obey evidence visibility limits;
- section units answer declared reader questions;
- terminology register is consumed.

### Backflow validators

- every finding has a failure type;
- every backflow task has a target node;
- stale propagation is scoped;
- unrelated downstream nodes remain unchanged;
- repaired nodes create new versions.

## Test levels

### Level 1 — Structural graph test

Run:

```bash
python3 scripts/validate_graph.py examples/minimal-paper-production-graph.json
```

### Level 2 — Single-node fixture test

Use a small material fixture and verify schema/envelope.

Examples:

- `ReviewerQuestionMap` fixture;
- `TerminologyRegister` fixture;
- `WritingTaskPacket` fixture.

### Level 3 — Local backflow fixture

Simulate:

```text
finding: claim overreach in Introduction paragraph
```

Expected:

- classify as `L3_claim_evidence`;
- target `ClaimEvidenceVisibilityMap` or `ClaimEvidenceMatrix`;
- mark affected introduction draft stale;
- do not mark unrelated related-work draft stale.

### Level 4 — Mock paper closed loop

Run a toy graph:

```text
intent -> analysis -> control materials -> writing task -> draft -> review -> backflow -> revised draft
```

### Level 5 — Real-paper single-section pilot

Apply the runtime to one section only, ideally Introduction contribution paragraph or one result interpretation paragraph.

Exit gate:

- graph shows all materials and affected dependencies;
- draft is produced from task packet;
- review finding triggers local backflow;
- unrelated nodes are not rewritten.

