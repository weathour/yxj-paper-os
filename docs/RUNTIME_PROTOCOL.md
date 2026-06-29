# Runtime Protocol — Main-Agent Control

## Main-agent identity

The main agent is the **Paper Production Graph Runtime Controller**. It owns process control, not department self-management.

## Runtime loop

```text
observe graph
  -> select next frontier node
  -> compile task packet
  -> dispatch specialist or run script
  -> collect candidate output
  -> validate
  -> commit / mark stale / create backflow
  -> repeat
```

## Graph state summary

The main agent maintains:

```yaml
GraphState:
  active_target:
  current_gate:
  committed_materials:
  candidate_materials:
  stale_materials:
  blocked_materials:
  owner_gated_materials:
  open_review_findings:
  next_frontier:
```

## Frontier queue priority

Default priority:

```text
owner_gated root decision
> stale upstream control material
> blocked validator/material prerequisite
> missing task packet for active manuscript unit
> candidate output awaiting validation
> review finding awaiting classification
> export/rendering blocker
> optional improvement
```

## Task context bundle

Subagents receive bounded context only:

```yaml
TaskContextBundle:
  task_id:
  mission:
  input_materials:
  relevant_artifacts:
  forbidden_routes:
  expected_output_schema:
  validators:
  return_format:
  completion_forbidden: true
```

The subagent returns a candidate artifact and evidence. It does not mark completion.

## Dispatch policy

Use scripts for deterministic tasks:

- schema validation;
- graph consistency;
- stale propagation;
- artifact indexing;
- internal-code scanning;
- rendered text scanning;
- hash/manifest generation.

Use subagents for semantic tasks:

- reader question design;
- contribution and claim boundary analysis;
- writing task packet drafting;
- section/caption drafting;
- adversarial review;
- reader experience review.

Use hybrid mode for:

- claim-evidence matrix;
- terminology register;
- main text construction matrix;
- review finding classification;
- backflow task compilation.

## Commit protocol

```text
candidate exists
  -> validators pass
  -> provenance recorded
  -> stale impact checked
  -> graph status updated
  -> active version pointer updated
```

Only after this can a node become `committed`.

## Authority boundaries

- Owner intent changes require human decision evidence.
- Subagents cannot commit or close graph nodes.
- Reviewers produce findings, not direct whole-paper edits.
- Main agent can repair locally only inside existing owner-approved semantics.

