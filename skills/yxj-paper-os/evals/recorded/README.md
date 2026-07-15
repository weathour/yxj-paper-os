# Recorded behavior captures

`fixture-current/capture-20260710-template-analysis` is the reproducible offline
current-policy fixture. It contains 15 response records covering the twelve schema-0.3
behavior groups, with separate cases for each of the four owner gates. Its manifest
identifies `policy-fixture` / `offline-reproducible-fixture`; it is not represented as
a model execution. `assets/evals/behavior-responses.json` is the sole authoritative
good/bad fixture source; the local good/bad fixture files and current actions are exact
mirrors, not independent evidence.

Its `behavior-prompt/2.1` prompt embeds the complete current `SKILL.md` and
`references/lenses/venue-template.md`, each with a content hash, plus the response
vocabulary and schema. Every scenario is projected to exactly `id`, `situation`, and
`context`. Required/prohibited actions, dimensions, scopes, side effects, question
gates, update/readiness rules, and response limits remain verifier-only oracle data.
Acceptance requires exact response/update/readiness/question keys and types, closed
scenario allowances, canonical non-duplicated record identities, and exact rule-bound
structured values for operations, locators, pointers, grounding, epistemic state, and
readiness consequences. Rule and response cardinalities are exact, readiness scope
identities are unique, and raw/scenario/manifest JSON rejects duplicate keys; the raw
response is one sole finite-number JSON document. Valid scenario authority must first
produce a deterministic complete witness accepted by the shared runtime, including
negative rules, cross-field invariants, target/readiness scope equality, public-pointer
anchor binding, and global identity uniqueness. `reason`, controlled `design_payload`,
and live-model provenance labels must contain a Unicode-visible code point; prose
fields remain variable free text. The complete typed manifest binds all input/output
hashes.
Sentence-like controlled payload detection is a manual-review warning only and does
not prove or disprove prose quality.
The fixture covers detailed paragraph design, placeholder-controlled frames, routine
adaptation, four focused gates, the design-only firewall, semantic readiness without
analyzer output, bounded quantitative analysis, selective invalidation, 0.2
recompilation, 0.3 readiness restoration, dual-role identity, and metadata-only access.

`codex-current/capture-20260710-template-analysis` is a historical 20-scenario Codex
CLI capture from the pre-schema-0.3 behavior contract. It and the earlier
`codex-fresh/capture-20260710` and `codex-policy/capture-20260710` directories are
retained only as provenance. They must not be used as current-policy validation inputs
or silently relabeled as successful current model evidence.
