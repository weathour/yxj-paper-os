---
name: yxj-paper-ppg-runtime
description: "Design and operate the Paper Production Graph Runtime: explicit material graph, local backpropagation, and main-agent dispatch for Codex-native academic paper production. Current repository is planning-first and not live-installed by default."
---

# yxj-paper-ppg-runtime

Use this skill for planning or operating a Codex-native paper production graph runtime.

## Core model

The runtime is:

> Explicit Material Graph + Local Backpropagation + Main-Agent Dispatch

The main agent controls a versioned graph of materials, task packets, validators, review findings, and backflow tasks. Specialist agents return candidates; scripts validate deterministic invariants; the main agent commits graph state.

## Current repository status

This repository is a development scaffold. Do not mutate existing `yxj-paper-os`, install this plugin, publish it, or register it in a marketplace unless explicitly authorized.

## First documents to read

1. `README.md`
2. `docs/PLAN.md`
3. `docs/TOPOLOGY.md`
4. `docs/VISUALIZATION_CONTRACT.md`
5. `docs/MATERIAL_SCHEMA.md`
6. `docs/RUNTIME_PROTOCOL.md`
7. `docs/BACKFLOW_PROTOCOL.md`
8. `docs/VALIDATION_AND_TESTING.md`

## Completion rule

A paper-production node is not complete because an agent produced text. It is complete only when the graph records candidate output, validator evidence, committed state, and scoped stale/backflow status.

