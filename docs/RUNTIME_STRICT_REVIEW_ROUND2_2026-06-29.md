# Runtime Strict Review Round 2 — Architect + Critic Evaluation

Date: 2026-06-29  
Scope: second strict review after the stage adjustment commit `1d48ee6`.

This review evaluates whether the current Paper Production Graph Runtime has a sound flow of materials, stages, backflow, and delivery gates for a Codex-native paper-writing plugin.

Two independent read-only subagents reviewed the repository:

- `architect`: system-design review of topology, boundaries, stage responsibilities, and minimal runnable core.
- `critic`: adversarial review focused on failure modes, hidden non-runnability, context pollution, and false validation.

## Executive verdict

| Question | Verdict | Reason |
| --- | --- | --- |
| Has the design moved away from yxj-paper-os-style department self-loops? | Yes, architecturally | The controller/graph/validator/bus model correctly places the main agent in charge and treats subagents as bounded stage workers. |
| Are the adjusted stage flows reasonable as a taxonomy/view? | Yes | `S03 -> S04`, `S06 -> S08`, `S01/S04 -> S11`, `S09A -> S09B -> S10`, and `S14/S15 -> S09A/S09B` fix the previous worst stage-level ambiguities. |
| Is it a runnable runtime now? | No | It is still a stage taxonomy, visual roadmap, and protocol draft; it lacks executable versioned material graph semantics. |
| Can review backflow truly perform local reverse propagation? | Not yet | Current examples and validators do not prove `material@v2 --supersedes--> material@v1`, scoped stale propagation, or regenerated downstream packets/drafts. |
| Can real subagents safely execute from the current material packets? | Not yet | `WritingTaskPacket`, `BackflowTask`, `ReviewFinding`, `ReviewClosure`, and validator reports need hard schemas and Codex dispatch fields. |

**Combined judgment:** keep the stage graph, but demote it to a **view / transform taxonomy**. The next engineering phase must build the **executable material graph**: versioned material nodes, transforms, validator reports, stale propagation, backflow compiler, and Codex-ready task packets.

## Consensus from architect and critic

Both agents converged on the same central diagnosis:

```text
Current design = stage taxonomy + visual control block + minimal structural validator.
Required runtime = versioned Material@vN graph + TransformTask + ValidatorReport + BackflowTask + stale/supersedes semantics.
```

The stage graph is no longer the main risk. The main risk is mistaking that stage graph for the runtime graph.

## Stage topology evaluation

### Corrected flows that are now accepted

The following changes are judged correct at the stage/topology level:

1. **Contribution cannot skip claim gate**

   ```text
   S03 -> S04 -> S05
   ```

   Contribution options must be admitted by evidence-to-claim gating before shaping the reader spine.

2. **Figure planning consumes section/function budget**

   ```text
   S06 -> S08
   ```

   Figures, tables, algorithms, and formulas need argument/function placement, not only aesthetic planning.

3. **Figure production cannot invent data**

   ```text
   S01/S04 -> S11
   ```

   Source locators and claim/evidence result packages must feed figure/caption/formal production.

4. **S09 split is correct**

   ```text
   S09A Control-material selection -> S09B Per-unit task packet assembly -> S10 Production
   ```

   This is the right Codex-native decomposition: first select control material, then assemble a bounded task packet.

5. **Clean export and repair export are both allowed**

   ```text
   S12/S13/S15 -> S16
   ```

   A clean candidate should not be forced through fake repair, and a repaired package should be able to reach delivery.

6. **Review can regenerate writing control and packets**

   ```text
   S14 -> S09A
   S15 -> S09B
   ```

   Repair may require control reselection or packet regeneration before rewriting local text.

### Topology still missing executable semantics

The topology still needs machine-readable branching and gates:

1. **S13 needs typed pass/fail outputs**

   Current graph has both:

   ```text
   S13 -> S14
   S13 -> S16
   ```

   But it does not encode the condition.

   Required material split:

   ```text
   S13 -> ReviewFinding@v1 -> S14
   S13 -> ReviewClosure@v1 -> S16
   ```

2. **S16 needs a delivery gate, not ordinary incoming edges**

   Delivery should require one of these conditions:

   ```text
   clean_path = CleanFinalCandidate + ReviewClosure + RepositoryState
   repair_path = RepairCompletePackage + ReviewClosure + RepositoryState
   ```

   This should be encoded in a `ReviewClosure` / `DeliveryGate` schema.

3. **Figure/export/repository backflow is underrepresented**

   Blueprint mentions `L5_figure_data`, `L6_export_render`, `L7_repository_hygiene`, but the visible graph mostly routes backflow to S04/S07/S09A/S09B/S10/S12. Add profile-specific backflow targets:

   ```text
   S14/S15 -> S01  source locator or data trace repair
   S14/S15 -> S08  figure contract repair
   S14/S15 -> S11  figure/caption/formal artifact repair
   S14/S15 -> S16  export/repository hygiene repair
   ```

## Node responsibility evaluation

| Node/group | Assessment | Remaining risk | Required hardening |
| --- | --- | --- | --- |
| `CTRL / GRAPH / VALIDATORS / BUS` | Conceptually correct control plane. | Still visual/protocol-level; not enough runtime authority. | Implement store, validator registry, frontier selection, commit protocol. |
| `S00` Owner semantic contract | Correctly separates human intent from evidence. | Owner gate is a concept, not a queue/record. | Add `OwnerDecisionQueue` and `OwnerDecisionRecord`. |
| `S01` Inventory | Correct foundation for evidence boundaries. | Artifact paths and source locators not checked. | Validate file existence, citation/source locator schema. |
| `S02/S03` Research/contribution | Useful optional branch. | Standard routes may skip S03 while S04 consumes contribution options. | Define stable-contribution fallback material. |
| `S04` Claim/evidence gate | Central and necessary. | Overloaded for empirical/computational validation. | Add optional `S04E` empirical checks: reproducibility, metrics, baselines, figure-data trace. |
| `S05/S06/S07` Paper design controls | Good separation of spine, granularity, surface. | Materials may become vague long documents. | Make reader spine, section budget, terminology, and surface rules schema-backed. |
| `S08/S11` Figure branch | Planning/production split is correct. | Caption semantics are blurred; S11 both consumes and produces caption brief. | S08/S07 produce caption constraints; S11 produces caption draft/export bundle only. |
| `S09A/S09B` Writing packet branch | Correct and important split. | Still no algorithm/schema preventing all-context dump. | Add `SelectedControlBundle` and `WritingTaskPacket` schemas with size/role/priority checks. |
| `S10` Main text production | Correctly candidate-only. | Without packet schema it may still overclaim or write outside scope. | Require evidence anchors, output path, completion forbidden, no recursive orchestration. |
| `S12` Integration | Necessary cross-module consistency gate. | Cannot prove clean candidate without structured findings. | Produce `CleanFinalCandidate` or `ConsistencyFinding` material. |
| `S13` Review | Correctly separated from rewriting. | Too many report types; could become universal reviewer blob. | Normalize into `ReviewFinding[]`, `ValidatorReport[]`, `ReviewClosure`. |
| `S14` Backflow compiler | Correct role: map findings to nearest responsibility. | Overloaded unless each finding has one primary target and downstream set. | Add `BackflowTask` schema and classifier tests. |
| `S15` Repair execution | Necessary local regeneration stage. | Could become general rewrite agent. | Add `repair_kind`, `target_material_type`, `allowed_write_scope`, `stale_downstream_set`. |
| `S16` Delivery | Correct final packaging role. | Clean export may bypass open findings. | Add `ReviewClosure` and `DeliveryGate` checks. |
| `G01/G02` Sidecars | Properly marked sidecar. | Metadata/patent/Nature/presentation can leak into writing cognition. | Add lint/schema forbidding sidecar materials in paper-facing input bundles unless explicitly authorized. |

## Material semantics evaluation

Current material names are good for discussion, but too abstract for execution. These must become typed, versioned, schema-validated material families.

### P0 material schemas

- `ppg-material.schema.json`
- `ppg-transform-task.schema.json`
- `ppg-validator-report.schema.json`
- `ppg-review-finding.schema.json`
- `ppg-backflow-task.schema.json`
- `ppg-review-closure.schema.json`
- `ppg-delivery-gate.schema.json`

### P1 paper-production schemas

- `ppg-owner-intent.schema.json`
- `ppg-owner-decision.schema.json`
- `ppg-evidence-inventory.schema.json`
- `ppg-claim-boundary-map.schema.json`
- `ppg-claim-evidence-visibility-map.schema.json`
- `ppg-reader-spine.schema.json`
- `ppg-terminology-register.schema.json`
- `ppg-selected-control-bundle.schema.json`
- `ppg-writing-task-packet.schema.json`
- `ppg-section-draft.schema.json`
- `ppg-figure-contract.schema.json`
- `ppg-panel-evidence-map.schema.json`
- `ppg-figure-export-bundle.schema.json`

### Codex-ready `WritingTaskPacket` must include

At minimum:

```yaml
packet_id:
schema_version:
target_material_id:
target_section_or_unit:
agent_type:
mission:
input_materials:
mandatory_controls:
evidence_anchors:
forbidden_routes:
allowed_read_paths:
allowed_write_paths:
allowed_tools:
output_artifact_path:
validators:
return_format:
single_writer_lock:
timeout_or_budget:
failure_report_format:
completion_forbidden: true
no_recursive_orchestration: true
```

Without these fields, subagents will still infer boundaries from prose and produce imprecise work.

## Backflow evaluation

Current backflow is conceptually local, but not yet executable.

### Required executable pattern

```text
ReviewFinding@v1
-> BackflowTask@v1
-> ClaimBoundaryMap@v2
--supersedes--> ClaimBoundaryMap@v1
-> WritingTaskPacket[intro]@v2
-> SectionDraft[intro]@v2
```

And simultaneously:

```text
ClaimBoundaryMap@v1 -> stale
WritingTaskPacket[intro]@v1 -> stale
SectionDraft[intro]@v1 -> stale
UnrelatedSectionDraft@v1 -> remains valid
```

### Current failure mode

If a backflow edge merely says:

```text
BackflowTask -> ClaimBoundaryMap@v1 repairs
```

then it does not prove a new version, does not prove `supersedes`, does not mark downstream stale, and does not prevent “just rewrite from scratch.”

## P0/P1/P2 action list

### P0 — must fix before claiming runnable runtime

1. **Split stage view from executable material graph.**
   - Stage view: `S00-S16` transform taxonomy.
   - Runtime graph: `Material@version + TransformTask + ValidatorReport + BackflowTask`.

2. **Implement version/supersedes/stale invariants.**
   - Repair creates new material version.
   - Old version is retained.
   - Active pointer moves only after validators pass.
   - Downstream stale scope is explicit.

3. **Make S13/S16 gates machine-readable.**
   - `ReviewFinding` vs `ReviewClosure`.
   - `DeliveryGate` prevents export with open P0/P1 findings.

4. **Strengthen validator.**
   - Check artifact existence.
   - Check payload schema.
   - Check validator report links.
   - Check supersedes chain.
   - Check stale propagation.
   - Check backflow primary target uniqueness.

5. **Add owner decision mechanism.**
   - `OwnerDecisionQueue`.
   - `OwnerDecisionRecord`.
   - Required for semantic reset or core claim changes.

### P1 — needed for reliable Codex subagent execution

1. Define `WritingTaskPacket`, `SelectedControlBundle`, `BackflowTask`, `ReviewFinding` schemas.
2. Add machine-readable stage activation/frontier policy.
3. Add figure/data/export/repository backflow targets and fixtures.
4. Add `S04E` empirical/computational profile checks.
5. Rename Nature-specific materials into venue/profile-specific materials.

### P2 — quality and UX improvements

1. Add frontend material-graph mode beside stage roadmap.
2. Add sidecar-pollution lint for `G01/G02` materials.
3. Add owner decision UI/diff queue later, after core runtime invariants pass.

## Minimal runnable runtime slice

Do not implement all `S00-S16` first. The minimum proof should be one overclaim repair loop:

```text
OwnerIntent@v1
-> EvidenceInventory@v1
-> ClaimBoundaryMap@v1
-> ClaimEvidenceVisibilityMap@v1
-> ReaderSpine@v1
-> TerminologyRegister@v1
-> SelectedControlBundle@v1
-> WritingTaskPacket[intro]@v1
-> SectionDraft[intro]@v1
-> ReviewFinding(overclaim)@v1
-> BackflowTask@v1
-> ClaimBoundaryMap@v2 --supersedes--> ClaimBoundaryMap@v1
-> WritingTaskPacket[intro]@v2
-> SectionDraft[intro]@v2
-> ReviewClosure@v1
-> DeliveryGate@pass
```

### Minimal program components

1. `ppg_store.py`
   - load/save graph
   - resolve active material version
   - upstream/downstream traversal
   - commit candidate material

2. Enhanced `validate_graph.py`
   - artifact existence
   - typed payload schema
   - supersedes invariant
   - stale invariant
   - review/backflow/delivery gates

3. `propagate_stale.py`
   - hard dependency invalidation
   - scoped stale sets
   - unrelated material preservation test

4. `compile_task_packet.py`
   - from selected controls + evidence anchors to Codex-ready `WritingTaskPacket`

5. `compile_backflow.py`
   - from `ReviewFinding` to one primary target plus affected downstream set

6. Fixture/mock closed loop
   - no real subagent needed at first
   - prove graph semantics before adding expensive agent execution

## Final synthesis

The current stage design is now good enough as a **human-understandable control map**. Further rearranging S-nodes has diminishing returns.

The next correct move is not another stage taxonomy pass. It is to implement a tiny executable material graph that proves:

```text
versioned material -> bounded task packet -> candidate output -> review finding -> local backflow -> new version -> scoped stale clearing -> clean delivery gate
```

Until that exists, the system remains vulnerable to the same failure mode as yxj-paper-os: impressive orchestration language without enforceable material state.
