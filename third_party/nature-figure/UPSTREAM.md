# Vendored upstream: nature-figure

- Upstream repository: <https://github.com/Yuan1z0825/nature-skills>
- Upstream skill path: `skills/nature-figure`
- Upstream commit: `c91df241a7a963ea151687ac669c5534404f53e5`
- Observed skill version: `2.0.0`
- License: Apache-2.0, copied from upstream root `LICENSE`
- Vendored for: `yxj-paper-os` S11 `S11.nature_figure_production_pass`
- Local authority boundary: S11 remains graph authority; this vendored skill is a figure-production helper only.
- Local changes to upstream files: none expected for upstream files. yxj-paper-os integration lives outside this vendored subtree except this `UPSTREAM.md` and `PARITY_MANIFEST.json`.

## Capability parity policy

The vendored subtree keeps the upstream router/static/reference/assets/evals structure so S11 can call nature-figure without capability loss or runtime network dependence. `PARITY_MANIFEST.json` records the vendored file inventory and hashes used by the verifier.
