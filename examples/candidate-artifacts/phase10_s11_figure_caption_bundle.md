# Candidate S11 figure/caption artifact bundle

Status: candidate, selected-backend render-plan only. This bundle maps the S11 `nature_figure_production_pass` direct-call slot onto the vendored `third_party/nature-figure` capability while keeping S11 as the authority boundary.

The selected backend is Python (`python3`), fixed before worker execution. The worker must not ask to switch backend, must not use cross-backend rendering, and must not use mock empirical data for an evidential figure. The planned editable source is `figures/src/phase10_s11_authority_loss_reconfiguration.py`; planned candidate outputs are SVG/PDF under `figures/generated/`, but final human-readable PDF/export readiness remains S16-owned.

Caption candidate: Authority-loss reconfiguration as a bounded explanatory mechanism. Panel A indicates degradation of the authority path; Panel B indicates the constrained reconfiguration response. The schematic is explanatory and does not serve as empirical performance evidence.

Exemplar/design-transfer boundary: reference-style learning, if later enabled, may transfer only abstract design principles such as visual hierarchy and label clarity; exact layout, distinctive palette, panel geometry, and typographic signature copying are forbidden and must pass similarity-risk review.
