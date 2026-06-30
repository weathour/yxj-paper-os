# Legacy yxj-paper-os Design Archive Manifest

Date: 2026-06-30

This archive preserves historical yxj-paper-os analysis material as provenance only. These files are not the active operating spine for `yxj-paper-ppg-runtime` Phase9.

Active spine replacement model:

```text
Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch
```

## Exact allowlist

| Original path | Archive path | Reason | Active replacement | Provenance status |
| --- | --- | --- | --- | --- |
| `docs/YXJ_PAPER_OS_PROCESS_INVENTORY.md` | `archive/legacy-yxj-paper-os-design-20260630/docs/YXJ_PAPER_OS_PROCESS_INVENTORY.md` | Historical yxj-paper-os process inventory; useful provenance but not current runtime spine. | `docs/SUBAGENT_STAGE_BLUEPRINT.md`, `runtime/stage_registry.json` | archived-provenance |
| `docs/YXJ_PAPER_OS_NEURAL_LAYER_MAP.md` | `archive/legacy-yxj-paper-os-design-20260630/docs/YXJ_PAPER_OS_NEURAL_LAYER_MAP.md` | Historical neural-layer reorganization; useful provenance but not current runtime spine. | `docs/PPG_RUNTIME_CONTROL_BLOCK.md`, `docs/runtime-viewer/index.html`, `runtime/stage_registry.json` | archived-provenance |
| `docs/data/yxj-paper-os-layer-map.json` | `archive/legacy-yxj-paper-os-design-20260630/docs/data/yxj-paper-os-layer-map.json` | Historical machine-readable yxj-paper-os layer map. | `runtime/stage_registry.json`, `examples/stage-contracts/` | archived-provenance |
| `docs/diagrams/yxj-paper-os-neural-layer-map.drawio` | `archive/legacy-yxj-paper-os-design-20260630/docs/diagrams/yxj-paper-os-neural-layer-map.drawio` | Historical yxj-paper-os diagram source. | `docs/diagrams/ppg-runtime-control-block.drawio`, `docs/runtime-viewer/index.html` | archived-provenance |
| `docs/diagrams/yxj-paper-os-neural-layer-map.drawio.png` | `archive/legacy-yxj-paper-os-design-20260630/docs/diagrams/yxj-paper-os-neural-layer-map.drawio.png` | Historical yxj-paper-os diagram export. | `docs/diagrams/ppg-runtime-control-block.drawio.png`, `docs/runtime-viewer/index.html` | archived-provenance |
| `docs/diagrams/yxj-paper-os-neural-layer-map.png` | `archive/legacy-yxj-paper-os-design-20260630/docs/diagrams/yxj-paper-os-neural-layer-map.png` | Historical yxj-paper-os diagram preview. | `docs/diagrams/ppg-runtime-control-block.png`, `docs/runtime-viewer/index.html` | archived-provenance |
| `docs/diagrams/yxj-paper-os-neural-layer-map.svg` | `archive/legacy-yxj-paper-os-design-20260630/docs/diagrams/yxj-paper-os-neural-layer-map.svg` | Historical yxj-paper-os diagram SVG. | `docs/diagrams/ppg-runtime-control-block.svg`, `docs/runtime-viewer/index.html` | archived-provenance |

## Explicit exclusions

The following review/protocol documents remain in active docs because current runtime and viewer surfaces still reference them as provenance or current review evidence:

- `docs/RUNTIME_ARCHITECT_CRITIC_REVIEW_2026-06-29.md`
- `docs/RUNTIME_STRICT_REVIEW_ROUND2_2026-06-29.md`
- `docs/PPG_RUNTIME_MACRO_EXECUTION_PLAN_2026-06-29.md`
- `docs/PPG_RUNTIME_EIGHT_PHASE_AUTOPILOT_PLAN_2026-06-29.md`

Expanding the archive scope requires a new exact allowlist in ralplan.
