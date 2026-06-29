# Related Frameworks — Pipeline, Graph Runtime, Asset Graph, and Agent Orchestration

This note records framework references for the Paper Production Graph Runtime (PPG Runtime).

## Core conclusion

No surveyed framework directly implements the full target model:

> explicit academic-paper material graph + local backpropagation + Codex main-agent dispatch + subagent/script task packets + front-end material-flow visualization.

However, several frameworks provide strong patterns to borrow:

- **OMX Pipeline**: stage sequencing, state persistence, resume, mode integration.
- **LangGraph**: stateful graph runtime where nodes do work and edges route state.
- **CrewAI Flows**: event-driven stateful flows with plot/visualization and task/crew integration.
- **Microsoft Agent Framework / AutoGen family**: production multi-agent workflow patterns, checkpointing, handoff, human-in-loop.
- **OpenAI Agents SDK**: handoffs, guardrails, tracing; useful for agent-to-agent delegation contracts.
- **Dagster software-defined assets**: material/asset-first graph, lineage, observability, freshness.
- **Apache Hamilton**: function-to-artifact DAG, readable code-to-data dependency mapping, visualization.
- **Kedro**: data catalog + modular reproducible pipelines.
- **Haystack Pipelines**: component graph orchestration for LLM/RAG apps.
- **Prefect**: durable workflow orchestration, scheduling, retries, observability.

The recommended architecture is therefore not to adopt one framework wholesale. Instead, implement a lightweight PPG graph core and borrow specific design patterns.

## Current OMX Pipeline

Local OMX `pipeline` skill describes a configurable stage orchestrator:

```ts
interface PipelineStage {
  readonly name: string;
  run(ctx: StageContext): Promise<StageResult>;
  canSkip?(ctx: StageContext): boolean;
}
```

Default Autopilot sequence:

```text
deep-interview -> ralplan -> ultragoal (+ team if needed) -> code-review -> ultraqa
```

It persists state at `.omx/state/pipeline-state.json` and resumes from the last incomplete stage.

### Fit for PPG Runtime

Useful as an **outer lifecycle shell**:

```text
design graph -> validate topology -> run material node -> review -> backflow -> export
```

Not enough as the inner model, because it is stage-oriented rather than material-node-oriented. It does not natively represent:

- explicit material dependencies;
- versioned material nodes;
- local stale propagation;
- review findings mapped to upstream nodes;
- front-end graph visualization contract.

## Framework comparison

| Framework | Closest useful concept | Strength for PPG | Limitation for PPG |
| --- | --- | --- | --- |
| OMX Pipeline | Sequential stages, state persistence, resume | good outer lifecycle wrapper | not a material graph runtime |
| LangGraph | state graph, nodes, edges, looping workflows | best agent-graph reference | graph state is app state, not necessarily versioned material artifacts |
| CrewAI Flows | event-driven workflows, state, plot visualization | good for flow visualization and structured event control | more agent/team oriented than artifact lineage oriented |
| Microsoft Agent Framework | production multi-agent workflows, graph patterns, checkpointing | useful for durable multi-agent architecture | heavier ecosystem; not paper-material specific |
| OpenAI Agents SDK | handoffs, guardrails, tracing | useful for delegation and validation contracts | not a graph/material runtime by itself |
| Dagster | software-defined assets and asset graph | strongest material/asset lineage analogy | data-pipeline oriented, not agent-writing oriented |
| Apache Hamilton | Python functions become dataflow DAG nodes | excellent function-to-artifact mapping | not an agent orchestration framework |
| Kedro | data catalog + modular pipelines | useful artifact storage/catalog pattern | pipeline-first, not dynamic backflow-first |
| Haystack | component graph orchestration | useful for LLM/RAG component pipelines | less material-version/backflow focused |
| Prefect | task orchestration, retries, scheduling | useful for robust execution later | not asset/material semantics first |

## Design patterns to borrow

### From OMX Pipeline

- stage interface;
- persisted state file;
- resume from incomplete stage;
- explicit skip conditions;
- verification gates between stages.

PPG adaptation:

```text
PipelineStage -> GraphPhase
StageResult.artifacts -> MaterialNode status transitions
canSkip -> node freshness / validator evidence
```

### From LangGraph

- nodes perform work;
- edges control routing;
- graph state is explicit;
- loops are normal;
- compile-time graph checks;
- state can be inspected and resumed.

PPG adaptation:

```text
LangGraph State -> PPG GraphState
LangGraph Node -> TransformTask / Validator / AgentRun
LangGraph Edge -> consumes / constrains / validates / repairs / supersedes
```

### From CrewAI Flows

- event-driven methods;
- stateful workflow instance;
- `@start` / `@listen` style dependencies;
- `plot()` as an early visualization primitive;
- persistence for restart/fork.

PPG adaptation:

```text
@listen(material_node) -> run transform when material validates
flow.plot() -> read-only material graph viewer MVP
```

### From Dagster

- assets are first-class outputs;
- asset graph shows lineage;
- freshness/up-to-date status matters;
- observability is tied to artifacts, not only tasks.

PPG adaptation:

```text
Software-defined asset -> PaperMaterialNode
asset freshness -> material stale/validated/committed state
asset lineage -> paper dependency graph
```

### From Hamilton

- function names map to produced artifacts;
- function parameters define dependencies;
- DAG can be visualized;
- code and data lineage stay readable.

PPG adaptation:

```python
def claim_boundary_map(evidence_inventory, owner_intent): ...
def writing_packet_intro(claim_boundary_map, reviewer_question_map): ...
```

This is a good pattern for deterministic/script-generated and hybrid materials.

### From OpenAI Agents SDK

- handoff contracts;
- guardrails;
- structured outputs;
- traces of LLM calls, tool calls, and handoffs.

PPG adaptation:

```text
Subagent run -> candidate material + trace + guardrail result
handoff -> TaskContextBundle
trace -> AgentRunNode provenance
```

## Recommended PPG architecture

### Do not adopt one framework wholesale in M1

For M1/M2, build a small local graph core:

```text
ppg-graph JSON
  + Python structural validators
  + stale propagation rules
  + minimal read-only front-end contract
```

Reason: adopting LangGraph/Dagster/CrewAI too early would force their runtime semantics before the paper-material semantics are stable.

### Adopt framework ideas by layer

| PPG layer | Best reference |
| --- | --- |
| material graph semantics | Dagster assets + Hamilton DAG |
| agent/subagent routing | LangGraph + OpenAI Agents SDK |
| workflow persistence | OMX Pipeline + CrewAI Flow persistence |
| visualization MVP | CrewAI plot + Dagster/Hamilton graph UI ideas |
| validator and observability | Dagster + OpenAI Agents tracing |

### Later integration options

1. **Lightweight internal runtime**: keep everything as JSON/YAML + Python scripts + Codex subagents.
2. **LangGraph-backed runtime**: compile PPG graph to LangGraph when agent control flow becomes complex.
3. **Dagster/Hamilton-backed material compiler**: use their asset/DAG concepts for deterministic material generation.
4. **OpenAI Agents SDK bridge**: use structured handoffs/guardrails/tracing for subagent execution outside Codex.

## Immediate next design implication

The PPG core schema should stay framework-neutral but include fields that map cleanly to these ecosystems:

```yaml
node:
  node_type:
  material_type:
  status:
  version:
  artifact_path:
  generator:
    method: agent_generated | script_generated | hybrid_generated | manual_owner_decision
    framework_hint: codex_subagent | python_script | langgraph_node | dagster_asset | hamilton_function | openai_agent
  validators:
  provenance:
  visualization:
```

This lets the plugin start simple and later compile selected nodes into external runtimes without redesigning the material graph.

## Source links

- OMX local pipeline skill: `/home/weathour/.codex/plugins/cache/oh-my-codex-local/oh-my-codex/0.18.15/skills/pipeline/SKILL.md`
- LangGraph docs: https://docs.langchain.com/oss/python/langgraph/graph-api
- LangGraph GitHub: https://github.com/langchain-ai/langgraph
- CrewAI Flows docs: https://docs.crewai.com/en/concepts/flows
- Microsoft Agent Framework GitHub: https://github.com/microsoft/agent-framework
- AutoGen docs: https://microsoft.github.io/autogen/stable/
- OpenAI Agents SDK GitHub: https://github.com/openai/openai-agents-python
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- OpenAI Codex with Agents SDK: https://developers.openai.com/codex/guides/agents-sdk
- Dagster GitHub: https://github.com/dagster-io/dagster
- Dagster software-defined assets blog: https://dagster.io/blog/software-defined-assets
- Apache Hamilton GitHub: https://github.com/apache/hamilton
- Hamilton nodes/dataflow docs: https://hamilton.apache.org/concepts/node/
- Kedro GitHub: https://github.com/kedro-org/kedro
- Prefect GitHub: https://github.com/PrefectHQ/prefect
- Haystack pipeline base: https://github.com/deepset-ai/haystack/blob/main/haystack/core/pipeline/base.py
