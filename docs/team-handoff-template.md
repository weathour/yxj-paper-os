# Team handoff template

Use only after explicit Team approval.

## Context

- Ultragoal plan: `.omx/ultragoal/goals.json`
- Active goal id: `<Gxxx>`
- Installed plugin source: `/home/weathour/plugins/yxj-paper-os/`
- Installed plugin cache: `/home/weathour/.codex/plugins/cache/personal-local/yxj-paper-os/<version>/`

## Lanes

- Architect: workspace/state/runtime contracts.
- Executor A: skills.
- Executor B: templates/references.
- Test-engineer: validators/fixtures.
- Writer: docs/migration/operation guide.
- Verifier/Critic: false-completion and gate audit.

## Return evidence

Changed files, validator outputs, fixture pass/fail summary, unresolved risks, gate compliance, and recommendation for Ultragoal checkpoint.

For expression-design work, also report whether paper-facing tasks have additive
`expression_design_object_refs`, whether `reader_load_status` and
`expression_design_status` appear in handoff output, whether any
`ExpressionDesignBundle` is only a manifest, and whether export-facing claims
inspected rendered output rather than source markdown alone.

## Manager authority handoff for workers

Workers must report whether the leader/manager directly edited or certified any
owned material in their slice. If so, return the proposed
`ManagerDirectIntervention` id, provenance artifact path, reviewer identity,
final certifier identity, and the YAML `authority_role_separation` block needed
for the leader checkpoint. Workers do not checkpoint Ultragoal state themselves.
