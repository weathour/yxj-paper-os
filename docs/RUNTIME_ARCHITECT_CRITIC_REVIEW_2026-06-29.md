# PPG Runtime Architect/Critic Strict Review — 2026-06-29

This review consolidates two independent read-only subagent reviews:

- `architect`: system structure, stage boundaries, material contracts, validation/backflow feasibility.
- `critic`: adversarial review of over-design, hidden department recursion, material vagueness, execution risk.

## Executive judgment

The runtime direction is correct for a Codex-native paper production system:

```text
Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch
```

The model correctly rejects department self-loops. It gives the main agent runtime authority, treats subagents as bounded transforms, and routes review findings into local backflow instead of whole-paper rewrites.

However, the current repository is still a **stage taxonomy and visualization prototype**, not yet a runnable paper-production runtime. The main gap is that the claimed “explicit material graph” is not yet implemented at the level of versioned material nodes. Most current diagrams show stage nodes (`S00`-`S16`) rather than concrete material/version nodes such as `ClaimEvidenceMatrix@v1`, `WritingTaskPacket@v1`, `SectionDraft@v1`, `ReviewFinding@v1`, `BackflowTask@v1`, and repaired `@v2` materials.

## Consensus findings

### 1. Stage design is directionally sound

The stage taxonomy covers the full paper lifecycle:

```text
S00 Owner semantics
S01 Source/evidence inventory
S02 Research/template/SOTA
S03 Novelty/contribution options
S04 Evidence-to-claim gate
S05 Reader spine
S06 Object/granularity design
S07 Rhetoric/terminology/surface controls
S08 Figure/formal planning
S09 Text task packet compilation
S10 Text production
S11 Figure/caption/formal production
S12 Integration/consistency
S13 Adversarial review
S14 Backflow compilation
S15 Local repair/regeneration
S16 Export/handoff
G01 Runtime governance
G02 Post-paper derivatives
```

The most robust boundaries are:

- `S00` vs `S01`: owner intent is separated from available evidence.
- `S04`: evidence-to-claim admissibility is correctly placed before writing.
- `S08` vs `S11`: figure planning is separated from figure production.
- `S13` vs `S14` vs `S15`: review, repair planning, and repair execution are separated, preventing uncontrolled reviewer rewrites.
- `CTRL / GRAPH / VALIDATORS / BUS`: control-plane roles are conceptually useful.

### 2. The biggest structural failure is stage graph vs material graph

Current viewer/runtime data primarily encodes stage-to-stage flow. That is useful as an explanation view, but it is not the runtime graph itself.

A real runtime graph must make material objects first-class:

```text
OwnerIntent@v1
  -> EvidenceInventory@v1
  -> ClaimEvidenceMatrix@v1
  -> ReviewerQuestionMap@v1
  -> WritingTaskPacket[intro]@v1
  -> SectionDraft[intro]@v1
  -> FullManuscriptCandidate@v1
  -> ReviewFinding@v1
  -> BackflowTask@v1
  -> ClaimEvidenceMatrix@v2
  --supersedes--> ClaimEvidenceMatrix@v1
```

Stages should become metadata on transforms, not the only visible graph nodes.

### 3. Validation is specified but not yet authoritative

Documents state that subagents only return candidates and the main agent commits after validation. This is correct.

But the current validator is too weak to prove runtime correctness. It validates graph structure but does not yet enforce:

- material artifact existence;
- validator report existence;
- owner decision evidence;
- active version pointer updates;
- hard-dependency stale propagation;
- backflow producing a new version;
- `supersedes` edges;
- repair target uniqueness;
- downstream draft invalidation after upstream repair.

### 4. Backflow is conceptually right but not operational yet

The intended principle is good:

```text
review finding -> classify -> locate source material -> mark stale -> compile repair task -> regenerate affected downstream only
```

But examples still risk “repairing” old nodes instead of creating new versions. A valid backflow example must show:

```text
ReviewFinding@v1
  -> BackflowTask@v1
  -> ClaimBoundaryMap@v2
  --supersedes--> ClaimBoundaryMap@v1
  -> WritingTaskPacket@v2
  -> SectionDraft@v2
```

### 5. Writing input is still at risk of becoming a context dump

The project correctly accepts large structured bundles, but `S09/S10` are still underspecified.

The dangerous phrase is essentially:

```text
S09 consumes all L2-L3 control materials
```

This is acceptable only if the task packet compiler enforces layers such as:

- mission;
- authority limits;
- mandatory control materials;
- evidence anchors;
- local context;
- optional background;
- forbidden routes;
- validator references;
- exact output path/format.

Without this, the writing stage becomes a large undifferentiated prompt and will reproduce the previous yxj-paper-os failure mode.

### 6. Figure branch is still under-specified semantically

The viewer now exposes the visual flow:

```text
S05 -> S08 -> S11 -> S12
```

But the material semantics are incomplete. `S11` cannot rely only on `S08`. Figure production also needs hard evidence/data inputs:

```text
S01/S04 -> S11
S06 -> S08
S08 -> S11
S11 -> S12
```

Otherwise figure/caption agents may invent source data or treat captions as self-generated claims.

### 7. Clean export path is missing

If review passes cleanly, the graph should allow export without forcing `S15` repair.

Needed edges:

```text
S12 -> S16   final candidate
S13 -> S16   review closure
S15 -> S16   repair-complete candidate only when repairs occurred
```

Current simplified path over-emphasizes `S15 -> S16`.

### 8. Department self-loop residue still needs hard isolation

Historical yxj-paper-os department concepts remain in inventory/layer documents and sidecar governance materials. They are acceptable only as inert metadata.

Required invariant:

```text
department-* artifacts may label responsibilities, but must not create frontier nodes,
must not commit graph state, must not dispatch subagents, and must not close findings.
```

`G01` must be governance/permission metadata only, not a paper cognition producer.

## P0 corrections

These are required before claiming the system is a runtime.

1. **Separate stage view from material graph.**
   - Keep `S00`-`S16` as stage taxonomy and visualization overlay.
   - Create a true material graph example with versioned materials and transforms.
   - Update viewer or add a second mode that shows material/version nodes.

2. **Implement real version/backflow example.**
   - Backflow must create `@v2` materials.
   - Old versions must be preserved.
   - `supersedes` edges must be explicit.
   - Downstream stale nodes must be marked.

3. **Strengthen validators.**
   - Extend `scripts/validate_graph.py`.
   - Add validators for material envelope, task packet, review finding, and backflow task.
   - Enforce artifact paths, validator reports, owner evidence, hard dependencies, stale reasons, and supersedes chains.

4. **Fix critical graph edges.**
   - Add `S06 -> S08` for section/function budget.
   - Add `S01/S04 -> S11` for source data and evidence.
   - Add `S12 -> S16` and `S13 -> S16` for clean export.
   - Add `S14/S15 -> S09` when repair requires regenerated task packets.
   - Resolve `S03 -> S04` vs `S03 -> S05` inconsistency.

5. **Make owner gating operational.**
   - Add `OwnerDecisionQueue` and `OwnerDecisionRecord` to runtime protocol.
   - Any backflow to `OwnerIntent` or core `PaperSpine` must produce owner-facing options and consequences.

## P1 corrections

These are needed before letting Codex subagents run real writing tasks.

1. **Define a small set of strong material schemas first.**
   Start with:
   - `OwnerIntent`
   - `EvidenceInventory`
   - `ClaimEvidenceMatrix` / `ClaimEvidenceVisibilityMap`
   - `ReviewerQuestionMap`
   - `TerminologyRegister`
   - `WritingTaskPacket`
   - `ReviewFinding`
   - `BackflowTask`

2. **Unify task packet contract.**
   Replace the reduced `TaskContextBundle` with the richer structured-bundle fields from ADR-0003.

3. **Add Codex dispatch contract fields.**
   Each task packet should specify:
   - `agent_type`
   - working directory
   - allowed read/write paths
   - allowed tools
   - output artifact path
   - completion forbidden
   - no recursive orchestration
   - lock consumption
   - timeout/budget
   - failure report format

4. **Split or constrain S09.**
   Prefer:
   - `S09a` control-material selection;
   - `S09b` per-unit task packet assembly.

5. **Make Stage Activation Policy machine-readable.**
   The 17 stages are a taxonomy, not a default linear execution chain.

6. **Extend backflow levels.**
   Current levels cover text/claim/spine, but must also cover:
   - figure/data trace failures;
   - citation rendering failures;
   - export/render failures;
   - repository hygiene failures.

## P2 corrections

1. Generalize Nature-specific material names into venue/profile-specific names.
2. Add `S04E` empirical/computational profile checks: reproducibility, metric consistency, ablation/baseline, figure-data trace.
3. Mark `G01/G02` as sidecar-only and default read-only.
4. Improve viewer defaults so dispatch/validation edges are not hidden when auditing runtime control.
5. Normalize claim material names: `ClaimCitationCapsule`, `ClaimEvidenceMatrix`, `ClaimBoundaryMap`, and `ClaimEvidenceVisibilityMap` currently overlap.

## Recommended next implementation order

Do not continue polishing the stage visualization first. The next useful work is a core vertical slice:

```text
1. material graph schema
2. minimal versioned example
3. graph validator upgrade
4. stale propagation
5. backflow compiler
6. task packet schema
7. viewer material-graph mode
```

The acceptance test should be an overclaim repair scenario:

```text
OwnerIntent@v1
EvidenceInventory@v1
ClaimEvidenceMatrix@v1
WritingTaskPacket@v1
SectionDraft@v1
ReviewFinding(overclaim)@v1
BackflowTask@v1
ClaimEvidenceMatrix@v2 --supersedes--> ClaimEvidenceMatrix@v1
WritingTaskPacket@v2
SectionDraft@v2
validator reports all linked
```

Only after that loop passes should the runtime be connected to real Codex subagent writing.
