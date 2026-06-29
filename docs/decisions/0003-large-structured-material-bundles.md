# ADR-0003 — Use large structured material bundles, not lossy pre-compression

## Status

Accepted.

## Context

PPG Runtime dispatches Codex subagents using task packets plus consumed material bundles. Since Codex subagents can receive substantial context, it is tempting to avoid aggressive compression and pass larger input bundles directly.

The risk is not only context-window size. The bigger risks are attention misallocation, unclear authority, weak traceability, and unverifiable outputs.

## Decision

Use **large structured material bundles** rather than lossy pre-compression.

Do not aggressively summarize away upstream materials before a subagent sees them. Instead, each task packet must organize inputs into clear strata:

```yaml
TaskPacket:
  mission:
  success_criteria:
  completion_forbidden: true
  required_output_schema:
  authority_limits:
  mandatory_control_materials:
  evidence_and_source_materials:
  local_context_materials:
  optional_background_materials:
  forbidden_routes_and_terms:
  validator_refs:
  return_format:
```

The subagent may reason over a larger bundle, but the bundle must still tell it:

1. what decision or output it owns;
2. which materials are authoritative;
3. which materials are background only;
4. what it must not change;
5. how its output will be validated.

## Consequences

Positive:

- preserves semantic richness;
- reduces over-compression artifacts;
- lets capable subagents discover cross-material relations;
- avoids premature information loss.

Costs:

- higher token use;
- requires strict task focus and ordering;
- validators must catch ignored constraints;
- main agent must still curate scope to avoid unrelated paper-wide dumps.

## Rule of thumb

The bundle can be large, but it must not be undifferentiated.

```text
bad: all known materials -> writer
better: large but layered bundle -> bounded task packet -> writer
```

## Input ordering

Recommended order:

1. mission and exact output contract;
2. hard constraints / forbidden routes;
3. mandatory control materials;
4. evidence anchors and allowed/forbidden wording;
5. local manuscript context;
6. optional background materials;
7. validator checklist and return format.

## PPG implication

The `WritingTaskPacket` compiler should not act primarily as a summarizer. It should act as a **material-bundle organizer**:

- include enough upstream materials for robust reasoning;
- classify each material's role;
- preserve exact anchors and paths;
- mark background vs authority;
- keep completion authority with the main agent and validators.
