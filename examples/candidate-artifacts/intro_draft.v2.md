---
schema_version: ppg-section-draft/v0.1
draft_id: intro_draft_v2
status: candidate
section_id: intro
packet_id: intro_writing_packet_v2
source_materials:
  - evidence_inventory_v1
  - claim_boundary_map_v2
  - reader_spine_v1
evidence_anchors:
  - examples/materials/evidence_inventory.v1.yaml
  - examples/materials/claim_boundary_map.v2.yaml
  - examples/materials/reader_spine.v1.yaml
graph_completion_claimed: false
recursive_dispatch_requested: false
---
# Introduction

When fresh V2X authority loses force, the controller should not treat suspicious messages as repaired truth. The active evidence supports a bounded authority-allocation claim: fresh V2X, trusted short memory, local sensing, and physical dynamics each retain only the control authority justified by the current evidence inventory.

This candidate introduction therefore frames the paper around graceful authority degradation rather than a universal safety promise. It remains a draft artifact until the main runtime validates and ingests it.
