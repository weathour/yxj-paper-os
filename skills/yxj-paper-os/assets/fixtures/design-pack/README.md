# Design-pack characterization fixtures

- legacy-section-ready-0.2/ is a sanitized, self-contained structural derivative
  of the read-only current-paper workspace named in the schema-0.3 PRD. It preserves
  only the legacy writer-ready/section-level condition; no scientific content is
  copied and tests do not access the external paper.
- detailed-ready-minimal-0.3/ starts from the six shipped public template identities
  and fills the smallest detailed contract: one scope, one section, two paragraphs,
  one important paragraph with frames, seven coverage rows, and grounded template
  handling not_applicable. It intentionally contains no dossier or analyzer output.

These directories are test data, not additional public workspace templates. Source
hashes captured during WP0 are in .omx/ultragoal/wp0/.
