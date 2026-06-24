# Migration notes

The previous `/home/weathour/plugins/yxj-paper-os` implementation was archived before this local install. The installed `yxj-paper-os` source does not delete the archive, publish marketplace updates beyond the existing personal-local entry, or remove old project artifacts.

Archive locator:

```text
/home/weathour/plugins/.backups/yxj-paper-os-before-v2-install-20260622T121414Z
```

## Suggested future migration stages

1. Inventory old yxj-paper-os profiles, state files, and task packets by locator only.
2. Classify each artifact as preserve, adapt, replace, or discard.
3. Map old native-subagent-job packets to current task packets with explicit `agent_type`, collection path, state ledger path, and `validator_refs`.
4. Run current validators against migrated fixtures.
5. Ask for explicit confirmation before old-plugin archive removal, production publication, or destructive migration.


## V1-to-v2 governance migration

V1 paper-control fixtures and old project ledgers remain readable, but v2 tasks
must add governance fields before they can be considered managed by the new
system:

| V1 artifact/field | V2 target |
| --- | --- |
| `owner_lane` only | `owner_department` + `owner_lane` derived from `agent-lane-registry.yaml` |
| `expected_output_artifacts` | `expected_output_artifacts` plus `expected_output_materials` |
| generic context paths | typed `input_materials` with artifact ids/types/paths |
| narrative notes in prose | `ReaderSpineBrief` and `ObjectRepresentationMatrix` refs |
| exemplar/template notes in prose | `TemplateQuantProfile`, `SectionFunctionBudget`, and visual/formal budget refs |
| review findings as comments | `ReaderExperienceReviewReport` and `NarrativeBackflowTask` |
| validator report only | validator report plus fixture-matrix and mirror-sync evidence |

Migration is source-only unless the paper owner explicitly authorizes live
install, publish, old-plugin removal, external submission/upload, destructive
changes, credentialed services, or private/raw material copying. A migrated task
is not complete until the v2 material outputs are collected, validators pass,
state is ingested, and the state transition is explicit.

## Manager authority migration

Older ledgers may contain manager-authored prose, validator summaries, or closure
claims without actor provenance. When migrating such records, do not preserve the
old `complete` claim blindly. Reclassify manager-authored department work as a
`ManagerDirectIntervention` candidate, add provenance where available, derive
paper/state sensitivity from materials and state transitions, and require
independent review before promoting the migrated task to `complete`.

If provenance cannot be reconstructed, keep the migrated record as
`candidate`/`validated` with residual self-certification risk instead of
inventing an independent reviewer.
