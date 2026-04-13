# The Archeia Ontology

> **Purpose.** This document grounds every term the Archeia Standard uses in established academic literature — cognitive science, multi-agent systems, temporal databases, knowledge representation — and in the recent (2023–2026) AI agent research that is shaping vocabulary in real time. It is the reference every other Archeia document cites when it needs to justify a term.
>
> The field is pre-paradigmatic. Garry Tan, Harrison Chase, Sarah Wooders, Michael Chomsky, Letta, Zep, Supermemory, Mem0, Anthropic, and a dozen academic groups are all using different words for overlapping concepts. Archeia's job is not to invent new words; it is to pick the canonical ones and say why.

---

## 1. How to read this document

Every concept appears as a **term** followed by its **canonical source**, a **one-line definition**, and the **Archeia role** it plays. When Archeia adopts a term as-is, we say so. When Archeia refines or narrows a term, we say how. When Archeia introduces a term that has no good academic equivalent, we flag it as coinage and justify the choice.

At the end of the document, a **vocabulary table** summarizes every term with its canonical citation.

Every claim in this document is anchored to one of three source types:

- **Classical academic** — peer-reviewed work from 1959–2021, verified against primary sources.
- **Recent AI research** — arXiv papers from 2023–2026, verified against the paper text where possible.
- **Industry coinage** — terms from Anthropic, Letta, Garry Tan, Harrison Chase, Sarah Wooders, or the broader agent-framework community that haven't yet crystallized in academia. Used sparingly and always flagged.

---

## 2. The three layers of agentic development

Before defining terms, we need to say where Archeia sits in the stack. Every discussion of "AI productivity" is happening on one of three layers, and conflating them is the largest source of confusion in the current debate.

```
+------------------------------------------------------+
|  KNOWLEDGE LAYER                                      |
|  Where project knowledge lives, who owns it, how it  |
|  evolves, how humans and agents coordinate on it.    |
|  <-- Archeia operates here.                           |
+------------------------------------------------------+
                         |
                         |  reads from / writes to
                         v
+------------------------------------------------------+
|  EXECUTION LAYER                                      |
|  The harness that loads skills, invokes the model,   |
|  manages context, and reads/writes artifacts.        |
|  Claude Code, Cursor, OpenCode, bespoke runtimes.    |
|  <-- Garry Tan's "thin harness, fat skills" operates  |
|      here. Harrison Chase's "your harness, your      |
|      memory" argument operates here. Sarah Wooders'  |
|      "memory isn't a plugin, it's the harness"       |
|      operates here.                                   |
+------------------------------------------------------+
                         |
                         |  runs
                         v
+------------------------------------------------------+
|  MODEL LAYER                                          |
|  The LLM itself — Claude, GPT, open-weight models.   |
|  Where latent reasoning happens.                     |
+------------------------------------------------------+
```

Archeia is the **knowledge layer contract**. It does not replace the execution layer and it does not compete with the model layer. A conforming implementation is any combination of (harness) + (model) that produces and consumes `.archeia/` trees according to the standard.

This three-layer framing is consistent with the architectural surveys in OpenDev (2026), Meta-Harness (Lee et al., 2026), and the Natural-Language Agent Harnesses paper (2026). All three treat the execution layer as a first-class concern distinct from the model below and the knowledge/artifact layer above. Archeia names the layer above.

---

## 3. Primitives

### 3.1 Cognitive Architecture

**Canonical source:** Allen Newell, *Unified Theories of Cognition* (Harvard University Press, 1990); John Anderson, *Rules of the Mind* (Lawrence Erlbaum, 1993) for ACT-R.

**Modern bridge to LLM agents:** Theodore Sumers, Shunyu Yao, Karthik Narasimhan, and Thomas L. Griffiths, "Cognitive Architectures for Language Agents" (**CoALA**), arXiv:2309.02427, 2023.

**Definition:** A cognitive architecture is a theoretical framework specifying the fixed structures and processes that implement cognition — memory systems, control processes, learning mechanisms — into which variable content (knowledge, skills, goals) is loaded.

**Archeia role:** Archeia **is a cognitive architecture for agentic development**. Not a wiki, not a database, not a memory service. It specifies fixed structures (domains, lifecycle shapes, ownership rules, operations) into which a specific project's variable content is loaded. This framing is load-bearing and should be used whenever Archeia is compared to other approaches.

CoALA is the paper that first applied the cognitive-architecture frame to LLM agents at the in-context execution layer. Archeia extends the same frame to the in-repo persistent knowledge layer. The relationship is direct: CoALA specifies the memory structures inside the agent's context window; Archeia specifies the memory structures outside the agent's context window, on disk, accessible to many agents and humans over time.

### 3.2 Memory taxonomy

**Canonical sources:**
- **Working memory:** Alan Baddeley & Graham Hitch, "Working Memory," in G. A. Bower (ed.), *The Psychology of Learning and Motivation*, vol. 8, pp. 47–89 (Academic Press, 1974).
- **Episodic vs semantic memory:** Endel Tulving, "Episodic and Semantic Memory," in E. Tulving & W. Donaldson (eds.), *Organization of Memory*, pp. 381–403 (Academic Press, 1972).
- **Declarative vs procedural memory:** Larry Squire's classification, developed across the early-to-mid 1980s; canonical synthesis in Squire & Zola-Morgan (1991), "The medial temporal lobe memory system," *Science* 253(5026):1380–1386.
- **Prospective memory:** Mark McDaniel & Gilles Einstein, *Prospective Memory: An Overview and Synthesis of an Emerging Field* (Sage, 2007).
- **LLM-agent adoption:** CoALA (Sumers et al. 2023) adopted this taxonomy for language agents.

**Definitions:**
- **Working memory** — the limited-capacity, actively-manipulated store of information currently in use.
- **Episodic memory** — memory for specific events, with spatio-temporal indexing ("I had this conversation yesterday").
- **Semantic memory** — general factual knowledge, decontextualized ("Python is interpreted").
- **Procedural memory** — knowledge of how to perform actions, typically implicit ("how to ride a bike").
- **Prospective memory** — memory for intentions to perform future actions ("I need to file taxes by April 15").

**Archeia role:** Archeia's artifact shapes map 1:1 onto Tulving's taxonomy, extending the CoALA framework to the persistent-knowledge layer:

| Tulving / Squire / Baddeley term | Archeia artifact shape | Examples |
|---|---|---|
| **Working memory** (Baddeley 1974) | (not in `.archeia/`; lives in the harness context window) | active session, current context window |
| **Semantic memory** (Tulving 1972) | **Living documents** | `product/product.md`, `codebase/architecture/*`, `business/vision/vision.md` |
| **Episodic memory** (Tulving 1972) | **Accumulating records** | `product/decisions/*.md`, `execution/retros/*.md`, `business/landscape/*.md` |
| **Procedural memory** (Squire) | **Skills** (not in `.archeia/` but in `skills/`) | `archeia:work`, `archeia:consolidate`, `archeia:clarify-idea` |
| **Prospective memory** (McDaniel & Einstein) | **Transient artifacts** in `future` status | `execution/tasks/` with `status: todo`, `business/drafts/*.md` |

This mapping is why Archeia's three lifecycle shapes aren't arbitrary: they correspond to cognitive-science memory categories that have 50 years of empirical grounding, and CoALA already established the bridge from these categories to LLM agent systems. Archeia applies the same taxonomy one layer outward.

### 3.3 Memory consolidation

**Canonical sources:**
- Georg Elias Müller & Alfons Pilzecker, *Experimentelle Beiträge zur Lehre vom Gedächtnis* (Leipzig, 1900) — the original experimental work establishing memory consolidation and coining the German term *Konsolidierung*.
- Larry Squire & Pablo Alvarez, "Retrograde amnesia and memory consolidation: a neurobiological perspective," *Current Opinion in Neurobiology* 5:169–177, 1995 — modern systems consolidation theory.
- **Modern LLM-agent adoption:** MemoryAgentBench (Hu, Wang & McAuley, arXiv:2507.05257, 2025) and the Agent-Memory Survey use "knowledge consolidation" as the canonical term for converting episodic traces into structured semantic artifacts.

**Definition:** The process by which labile, detail-rich memories (episodic) are transformed into stable, structured, generalized knowledge (semantic) through re-examination, pattern extraction, and integration with prior knowledge.

**Archeia role:** The Archeia kernel operation `consolidate` (see §4.6) names this process in the agent context. When an agent reads multiple source artifacts and produces a structured target artifact with citations, it is performing consolidation. This replaces Garry Tan's informal "diarize" term from "Thin Harness, Fat Skills" (which was a misapplied metaphor from speech processing) with the cognitive-science term for exactly this operation.

### 3.4 Temporal modeling (bi-temporal)

**Canonical sources:**
- Richard T. Snodgrass & Ilsoo Ahn, "Temporal Databases," *IEEE Computer* 19(9):35–42, **1986** (not 1988; the 1988 Stam & Snodgrass paper is a bibliography). Introduces the valid-time vs transaction-time distinction.
- Christian S. Jensen et al., "A Glossary of Temporal Database Concepts," *ACM SIGMOD Record* 21(3):35–43, 1992 — consensus vocabulary for temporal databases.
- **SQL:2011** — the first SQL standard to include bi-temporal features (system-versioned temporal tables, application-time periods). Formally standardized the vocabulary.
- **Modern LLM-agent adoption:** Rasmussen et al., "Zep: A Temporal Knowledge Graph Architecture for Agent Memory," arXiv:2501.13956, 2025. Applies bi-temporal modeling to agent memory via the Graphiti engine.

**Definition:** A **bi-temporal** data model tracks two independent time dimensions:
- **Transaction time (TT)** — when the system recorded the fact.
- **Valid time (VT)** — when the fact was, is, or will be true in the real world.

A fact can have a transaction time of "March 15" and a valid time of "Q2 2025 through Q1 2026." Knowing when it was recorded is not the same as knowing when it's true.

**Archeia role:** Archeia is currently **only transaction-time aware** (via git). Zep's and Michael Chomsky's critique — that git knows when a file changed but not whether it's still true — is a real gap. The Archeia schemas for living documents and accumulating records now support an optional `last_verified` frontmatter field (the nearest practical proxy for valid time) so that staleness is detectable.

A future Archeia extension may adopt fuller bi-temporal support — `valid_from` / `valid_until` on accumulating records, periodic re-verification of living documents — but even the minimal `last_verified` addition materially improves selective forgetting, which is one of the four canonical memory competencies MemoryAgentBench uses to score memory systems (see §6).

### 3.5 Agent

**Canonical sources:**
- Michael Wooldridge & Nicholas Jennings, "Intelligent Agents: Theory and Practice," *The Knowledge Engineering Review* 10(2):115–152, 1995. The foundational definition for intelligent agents.
- Anand Rao & Michael Georgeff, "Modelling Rational Agents within a BDI-Architecture," *Principles of Knowledge Representation and Reasoning*, 1991. The BDI (Belief-Desire-Intention) model.
- Stuart Russell & Peter Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020. "An agent is anything that can perceive its environment through sensors and act upon that environment through actuators."

**Definition:** A system that perceives its environment and acts upon it to achieve goals. In LLM practice, "agent" usually means an LLM wrapped in a tool-calling loop, which is a narrower case of the classical definition.

**Archeia role:** Archeia is agent-framework-agnostic. A conforming writer is any producer that obeys the domain schemas and ownership rules — it may be a BDI agent, an LLM-with-tools, a deterministic script, a CI pipeline, or a human editing in VS Code. The `agents/` folder in the reference implementation contains Claude Code subagents specifically, but these are one distribution's choice, not a kernel requirement.

### 3.6 Ontology

**Canonical source:** Thomas R. Gruber, "A Translation Approach to Portable Ontology Specifications," *Knowledge Acquisition* 5(2):199–220, 1993. DOI: 10.1006/knac.1993.1008.

**Exact quote (page 199):** "An ontology is an explicit specification of a conceptualization."

**Archeia role:** This document (the Archeia Ontology) is such an explicit specification. It conceptualizes the entities and operations of agentic project knowledge so that conforming tools, writers, and readers share a common vocabulary. Gruber's definition is 30+ years old and remains the most-cited in computer science (21,000+ Google Scholar citations as of 2024).

---

## 4. The three shapes and the six kernel operations

The full specification is in [`TEMPORAL_MODEL.md`](TEMPORAL_MODEL.md). This section maps each concept to its canonical source and notes what Archeia adopts vs refines.

### 4.1 Living documents

**Archeia's term.** No single canonical academic equivalent, but the closest framing is **"semantic memory expressed as evolving canonical documents,"** which combines Tulving's semantic memory (1972) with the Docs-as-Code movement (GitHub Docs, Docusaurus, arc42). The living-document shape formalizes what operators have been doing in practice for a decade: one canonical file per concept, edited in place, history preserved by version control.

**Cognitive role:** semantic memory. Generalized, decontextualized knowledge about the world that evolves as understanding improves.

**History mechanism:** git (transaction time).

### 4.2 Accumulating records

**Archeia's term.** The academic equivalent is **"episodic memory store"** (Tulving 1972, CoALA 2023). The specific software-engineering precedent is **ADR (Architecture Decision Records)**, first formalized by Michael Nygard, "Documenting Architecture Decisions," 2011 (personal blog; widely cited).

**Cognitive role:** episodic memory. Discrete events authored at specific times, each with its own identity, referenced by later work.

**History mechanism:** on-disk forever. The records are their own history.

**The single permitted frontmatter mutation** (updating `status` from `active` to `superseded` when a successor is written) is analogous to the standard ADR practice described by Nygard and elaborated in *Building Evolutionary Architectures* (Ford, Parsons, Kua, O'Reilly 2017).

### 4.3 Transient artifacts

**Archeia's term.** The academic equivalent is **"prospective memory"** (McDaniel & Einstein 2007) plus **"operational working memory"** (Baddeley 1974) once the artifact is being actively worked on. Transient artifacts implement both: they begin as intentions (future), become active working state (present), and are archived after completion (past) with bounded retention.

**Cognitive role:** prospective memory + operational working memory.

**History mechanism:** on-disk during retention, git afterwards.

**Retention as a mechanism** is consistent with the biological forgetting literature (Hardt, Nader & Nadel, "Decay happens: the role of active forgetting in memory," *Trends in Cognitive Sciences* 17(3):111–120, 2013). Active forgetting is not a defect — it is a necessary cognitive mechanism for maintaining signal-to-noise ratio. Archeia's pruning is the computational analogue: a ceremony that prevents working-memory space from filling with yesterday's completed work.

### 4.4 `advance` operation

**Archeia's term.** The operation name is idiomatic software-engineering vocabulary ("advance a task from todo to active"). No canonical academic origin. The underlying concept is **state transition** in a finite state machine, which is standard computer science.

### 4.5 `complete` operation

**Archeia's term.** Same as `advance` — idiomatic software vocabulary. The transition from "in progress" to "done" with a recorded timestamp.

### 4.6 `consolidate` operation (formerly "diarize")

**Canonical source:** memory consolidation (Müller & Pilzecker 1900; Squire & Alvarez 1995). Modern LLM-agent adoption as "knowledge consolidation" in MemoryAgentBench (Hu et al. 2025) and the Agent-Memory Survey.

**Definition:** Read a set of source artifacts and produce or update a target artifact that integrates their content with cited evidence. The target is typically a living document (e.g., `architecture.md` consolidating source files, scan reports, and git history) or an accumulating record (e.g., a retrospective consolidating session traces).

**Why this replaces "diarize":** The term "diarize" in Garry Tan's "Thin Harness, Fat Skills" (X post, April 10, 2026) is a metaphor stretched from **speaker diarization** (Tranter & Reynolds, "An overview of automatic speaker diarization systems," *IEEE TASLP* 14(5):1557–1565, 2006), which means "determining who spoke when" in an audio recording. This is a completely different operation — it's speaker identification, not synthesis from multiple sources. Using "diarize" to mean "synthesize structured judgment from many documents" is a category error that would fail peer review.

**Consolidation is the right term** because it is:
- The biological process that takes fragmented experience and produces structured long-term memory (exact match to the operation)
- Already in use in the agent-memory literature (MemoryAgentBench, Agent-Memory Survey) for this purpose
- Non-invented and uncontroversial

**Contract (formally specified):**
- **Inputs:** a set of source artifacts (files, git history, external data, prior `.archeia/` artifacts) and a target artifact path.
- **Effect:** produce or update the target. The target must be either a living document or an accumulating record (consolidation produces durable, structured knowledge — never transient).
- **Evidence rule:** every claim in the target must cite a source from the inputs. Claims that cannot be evidenced must be flagged in the target with `<!-- INSUFFICIENT EVIDENCE -->` rather than fabricated.
- **Idempotence:** semantically idempotent. Two runs over the same inputs produce semantically equivalent outputs; exact text may differ.

Most of what `archeia:write-tech-docs` actually does is consolidation (read source files, produce `codebase/architecture/architecture.md`). Most of what `archeia:scan-git` does is consolidation (read git history, produce `codebase/git-report.md`). We have been hand-waving this operation. Naming it makes the kernel honest.

### 4.7 `prune` operation

**Archeia's term.** The operation name is idiomatic (pruning a tree, pruning dead branches). The underlying concept is **retention-based active forgetting** (Hardt et al. 2013). Git preserves the pruned content.

### 4.8 `supersede` operation

**Archeia's term.** The operation name is standard ADR vocabulary (Nygard 2011). The operation implements the append-only-with-status-update pattern canonical to accumulating records.

### 4.9 `evolve` operation

**Archeia's term.** The operation is the generic "show me how this thing changed" query, implemented differently per shape (git log for living, `supersedes` chain for accumulating, on-disk + git for transient). No academic equivalent — this is Archeia's naming of a workflow pattern.

---

## 5. Coordination primitives

Archeia's coordination model is grounded in three bodies of classical academic work that predate LLMs by decades.

### 5.1 Blackboard architecture

**Canonical sources:**
- Barbara Hayes-Roth, "A Blackboard Architecture for Control," *Artificial Intelligence* 26(3):251–321, 1985. The foundational BB1 paper.
- Robert Engelmore & Tony Morgan (eds.), *Blackboard Systems* (Addison-Wesley, 1988). The canonical edited volume.

**Definition:** A coordination architecture where multiple independent knowledge sources (specialized agents) contribute to a shared workspace (the "blackboard"). Each knowledge source monitors the blackboard and contributes when its expertise is relevant. Classical blackboard systems used control rules to arbitrate contention.

**Archeia role:** Archeia's ownership-per-domain model is **a disciplined blackboard architecture where ownership prevents contention**. Classical blackboards had to deal with multiple writers potentially overwriting each other; Archeia sidesteps this by assigning each domain to exactly one writer family. The rest of the blackboard pattern — independent knowledge sources, shared workspace, readers monitoring for relevant writes — transfers directly.

Recent work has re-derived this pattern without necessarily knowing Hayes-Roth. **BIGMAS** (Brain-Inspired Graph Multi-Agent Systems, arXiv:2603.15371, 2026) explicitly grounds its multi-agent coordination in **Global Workspace Theory** (Baars 1988), which is the neuroscience analogue of blackboard architecture. The convergence is telling: when multi-agent systems need a coordination primitive, they reach for a shared workspace, and the shared workspace needs ownership discipline to scale. Archeia is the in-repo version of this pattern.

### 5.2 Stigmergy

**Canonical sources:**
- Pierre-Paul Grassé's work on termite behavior in the 1950s; term coined in his 1959 paper on termite nest construction.
- Guy Theraulaz & Eric Bonabeau, "A Brief History of Stigmergy," *Artificial Life* 5(2):97–116, 1999. The foundational formalization for multi-agent systems.
- Michael Elliott, "Stigmergic Collaboration: The Evolution of Group Work," *M/C Journal* 9(5), 2006. The canonical application to wikis and open-source collaboration.

**Definition:** Indirect coordination among agents via modification of a shared environment. Agents leave traces in the environment; other agents read those traces and act accordingly. No direct agent-to-agent messaging; coordination emerges from the environment itself.

**Archeia role:** Archeia's Truth #6 ("agents compose via files, not APIs") is **literally stigmergy** — the in-repo filesystem is the shared environment, the artifacts are the traces, agents read them and act without direct messaging. Truth #6 should cite Theraulaz & Bonabeau and Elliott directly; the pattern is 70 years old in biology and 25 years old in multi-agent systems literature.

The stigmergic framing has a practical consequence: **agent composition is free at the protocol level.** Agents from different frameworks, in different languages, with different model providers, can all participate in the same coordination as long as they read and write conforming artifacts. This is the direct analogue of ants not needing a shared language to build a mound together — the environment carries the coordination.

### 5.3 Distributed cognition

**Canonical source:** Edwin Hutchins, *Cognition in the Wild* (MIT Press, 1995). The foundational book.

**Definition:** Cognitive processes are distributed across individuals, artifacts, and the environment — not localized inside any single head. Hutchins' classic case study is ship navigation, where the "cognitive system" is the crew plus charts plus instruments plus the ship, all operating together.

**Archeia role:** Archeia's overall frame — that the project's mind lives in a shared substrate accessible to both humans and agents — is **an instance of distributed cognition.** Hutchins' 10,000+ citations establish that cognition-as-distributed is not a fringe view; it's the standard frame in cognitive science for understanding how complex collaborative work actually happens.

When Archeia says "the `.archeia/` tree is the project's mind," we are not speaking loosely. We are making the Hutchins claim: the project's cognition is literally constituted by the operator + the agents + the filesystem + the tools they use to interact with it. The tree is not passive storage; it is part of the cognitive system.

---

## 6. The four memory competencies

Michael Chomsky's analysis essay (X, April 11, 2026) identified "four memory jobs" but did not cite their source. The source is:

**Canonical source:** Yifan Hu, Yining Wang & Julian McAuley, "Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions" (**MemoryAgentBench**), arXiv:2507.05257, 2025.

MemoryAgentBench proposes four canonical competencies for evaluating agent memory systems, explicitly grounded in cognitive science:

1. **Accurate retrieval** — find the right memory when it is needed.
2. **Test-time learning** — update what the agent knows from new information as it arrives.
3. **Long-range understanding** — connect information across sessions separated in time.
4. **Selective forgetting** — recognize when a memory is stale and stop relying on it.

These four are the canonical framing of what a memory system must do to be useful. Any agentic-memory claim should be audited against all four.

**Archeia's honest self-assessment** against the MemoryAgentBench framework is documented separately in [`../docs/memory-vs-knowledge.md`](../docs/memory-vs-knowledge.md). The short version: Archeia is strong on #1 (path-based retrieval), partial on #2 and #3, and weak on #4. We are not claiming to solve memory; we are claiming to solve the **structural substrate** that makes memory solutions tractable. The four memory jobs remain open problems in the field and no current system is strong on all four.

---

## 7. The harness

**Canonical sources (recent, emerging):**
- Lee, Nair, Zhang, Lee, Khattab & Finn, "Meta-Harness: End-to-End Optimization of Model Harnesses," arXiv:2603.28052, 2026. Defines harness as "code implementing LLM application logic" including context management, tool selection, and control flow.
- "Natural-Language Agent Harnesses" (NLAHs), arXiv:2603.25723, 2026. Expresses harness behavior in editable natural language, decoupling harness design from runtime conventions.
- Lou et al., "AutoHarness: improving LLM agents by automatically synthesizing a code harness," arXiv:2603.03329, 2026.
- OpenDev, "Building Effective AI Coding Agents for the Terminal: Scaffolding, Harness, Context Engineering," arXiv:2603.05344, 2026. Treats the harness as the control-logic and scaffolding layer around the model.

**Definition:** The **harness** is the orchestration layer that loads skills/tools, invokes the model in a loop, manages context, enforces safety, and reads/writes artifacts. It is distinct from the model (which does the reasoning) and distinct from the artifact layer (which stores the work). Every LLM-agent system has a harness whether it names it or not.

**Academic standing:** As of 2026 "harness" has crossed from industry coinage into academic literature. Meta-Harness, NLAHs, AutoHarness, and OpenDev all use the term formally. It is no longer acceptable to claim the term is informal.

**Archeia role:** Archeia does not specify the harness. It specifies the contract for what the harness produces and consumes. A conforming harness is any runtime that:
- Reads artifacts from `.archeia/` according to the schemas in [`contracts/`](contracts/)
- Writes artifacts back to `.archeia/` according to the ownership rules in [`SCHEMA.md`](SCHEMA.md)
- Guarantees that writes are flushed to disk before compaction may discard in-context state

The third point is Archeia's one hard requirement on harnesses: **compaction must not lose pending writes.** If a harness summarizes context and drops an in-flight write to `.archeia/product/product.md`, that's a harness bug, not an Archeia problem. Compaction policy is harness business; persistence guarantees are contract business.

---

## 8. Skills

**Canonical sources (recent, emerging):**
- Ma, Liu, Yang et al., "Scaling Coding Agents via Atomic Skills," arXiv:2604.05013, 2026. Formalizes five atomic coding skills and trains via joint RL.
- Liu, Ji, An, Jaakkola, Zhang & Chang, "How Well Do Agentic Skills Work in the Wild: Benchmarking LLM Skill Usage in Realistic Settings," arXiv:2604.04323, 2026. First large-scale study (34K skill library) of skill selection under realistic retrieval conditions.
- "SkillNet: Create, Evaluate, and Connect AI Skills," arXiv:2603.04448, 2026. 200K-skill ontology with multi-dimensional evaluation (Safety, Completeness, Executability, Maintainability, Cost-awareness).
- Anthropic Claude Code Skills documentation, [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills). Canonical specification of `SKILL.md` format.

**Cognitive precedent:** Skills correspond to **procedural memory** in the Squire/CoALA taxonomy — "how to do things" knowledge, packaged for reuse.

**Definition:** A **skill** is a reusable, parameterizable procedure — typically a Markdown document with YAML frontmatter — that teaches a model how to execute a specific workflow. Skills encode process, not content. The same skill invoked with different parameters produces different outcomes.

**"Fat skills, thin harness"** (Garry Tan's framing in "Thin Harness, Fat Skills," X, April 10, 2026) means: put the reusable procedural knowledge in skill files, keep the runtime that executes them as small as possible. This is consistent with Anderson's production-system architecture in ACT-R (1993): knowledge lives in productions (condition-action rules), and the runtime is a simple matcher-executor. Tan's own reference implementation is **gstack** ([github.com/garrytan/gstack](https://github.com/garrytan/gstack)) — 23 Claude Code skills organized as a "virtual engineering organization" (CEO, designer, QA, security, release engineer roles). It is the working proof-of-concept for the thin-harness / fat-skills architecture.

**Archeia role:** Skills live outside `.archeia/` — they are writers, not artifacts. The `skills/` folder at the repo root is where the reference implementation keeps them. A conforming distribution may organize skills differently; what matters is that skills produce and consume artifacts conforming to the schemas.

### The parameterized-skill refinement

Garry Tan's sharpest contribution on skills is that **they are method calls with parameters, not undifferentiated prompts**. The same `/investigate` skill with `(TARGET=<medical>, QUESTION=<safety>, DATASET=<discovery-emails>)` produces a medical research analyst; with different parameters it produces a forensic investigator. The procedure is the same; the parameters are the world.

Archeia should adopt this refinement explicitly in the skill format spec. Current `SKILL.md` frontmatter is:

```yaml
---
name: review-draft
description: ...
---
```

The refinement adds:

```yaml
---
name: review-draft
description: ...
parameters:
  - name: draft_path
    type: file
    required: true
  - name: codebase_context
    type: directory
    default: .archeia/codebase/architecture/
---
```

This is consistent with how Claude Code's skill description field already functions as an implicit parameter-matcher (via the resolver pattern Garry Tan describes), but making it explicit lets harnesses validate inputs at invocation time.

This refinement is a planned Phase-C update to [`KERNEL.md`](KERNEL.md), not yet shipped.

---

## 9. Latent vs deterministic

**Canonical source:** Garry Tan, "Thin Harness, Fat Skills" (X post, April 10, 2026). No classical academic source for this specific framing, but the underlying distinction is **exact computation vs approximate computation** from numerical analysis, and **declarative vs procedural reasoning** from cognitive architectures (Anderson 1993, ACT-R).

**Definition:** Work that requires judgment, synthesis, or pattern recognition belongs in **latent space** (the model does it). Work that requires exact reproducibility belongs in **deterministic code** (compiled programs, SQL queries, scripts, validators). Putting deterministic work in latent space is the most common failure mode in agent design.

**Archeia role:** This is a foundational principle that Archeia adopts as **Truth #7** in [`PRINCIPLES.md`](PRINCIPLES.md). Archeia's `consolidate` operation is latent (a model reads and synthesizes); Archeia's `validate` operation is deterministic (a schema validator checks conformance). Distributions must declare which of their artifacts and operations are latent and which are deterministic.

The principle is load-bearing because it tells you where to spend LLM budget. Consolidating architecture docs is worth the tokens. Validating frontmatter against a schema is not — run the deterministic validator.

---

## 10. Canonical vocabulary table

The authoritative mapping of Archeia terms to their academic or industry canonical sources. This table is the single source of truth for terminology; every other Archeia document cites this.

| Archeia term | Canonical source | Year | Type | Archeia role |
|---|---|---|---|---|
| Cognitive architecture | Newell 1990; Anderson 1993 | 1990, 1993 | Classical | Archeia is a cognitive architecture for agentic development |
| CoALA framework | Sumers, Yao, Narasimhan & Griffiths (arXiv:2309.02427) | 2023 | Recent AI | Applies Tulving memory taxonomy to LLM agents; Archeia extends this to in-repo persistent knowledge |
| Working memory | Baddeley & Hitch 1974 | 1974 | Classical | The LLM context window; harness-owned, not in `.archeia/` |
| Semantic memory | Tulving 1972 | 1972 | Classical | Living documents |
| Episodic memory | Tulving 1972 | 1972 | Classical | Accumulating records |
| Procedural memory | Squire 1982 | 1982 | Classical | Skills (in `skills/`, not in `.archeia/`) |
| Prospective memory | McDaniel & Einstein 2007 | 2007 | Classical | Transient artifacts in `future` status |
| Memory consolidation | Müller & Pilzecker 1900; Squire & Alvarez 1995 | 1900, 1995 | Classical | The biological process the `consolidate` operation implements |
| Knowledge consolidation | MemoryAgentBench (arXiv:2507.05257); Agent-Memory Survey | 2025 | Recent AI | Modern agent-literature term for the consolidate operation |
| Active forgetting | Hardt, Nader & Nadel, *Trends in Cognitive Sciences* 17(3):111–120 | 2013 | Classical | The cognitive basis for the `prune` operation and retention windows |
| Bi-temporal data | Snodgrass & Ahn, *IEEE Computer* 19(9):35–42 | 1986 | Classical | Transaction time (when recorded) vs valid time (when true) |
| Temporal database glossary | Jensen et al., *ACM SIGMOD Record* 21(3) | 1992 | Classical | Consensus vocabulary |
| Temporal knowledge graph | Zep (arXiv:2501.13956) | 2025 | Recent AI | Bi-temporal modeling applied to agent memory |
| Blackboard architecture | Hayes-Roth, *Artificial Intelligence* 26(3) | 1985 | Classical | Archeia's ownership-per-domain is a disciplined blackboard |
| Global Workspace Theory | Baars 1988; BIGMAS (arXiv:2603.15371) | 1988, 2026 | Classical + Recent AI | Neuroscience analogue of blackboard; used in BIGMAS |
| Stigmergy | Grassé 1959; Theraulaz & Bonabeau, *Artificial Life* 5(2) | 1959, 1999 | Classical | Truth #6: files as the message bus |
| Stigmergy in collaborative software | Elliott, *M/C Journal* 9(5) | 2006 | Classical | Wiki/OSS precedent for Archeia's composition model |
| Distributed cognition | Hutchins, *Cognition in the Wild* (MIT Press) | 1995 | Classical | Overall frame: `.archeia/` is part of the cognitive system |
| Intelligent agent | Wooldridge & Jennings, *Knowledge Engineering Review* 10(2) | 1995 | Classical | Foundational definition |
| BDI model | Rao & Georgeff, *KR-91* | 1991 | Classical | One of several agent architectures Archeia is agnostic to |
| Agent (modern) | Russell & Norvig, *AIMA* 4th ed. | 2020 | Classical | "Anything that can perceive its environment through sensors and act upon that environment through actuators" |
| Ontology (concept) | Gruber, *Knowledge Acquisition* 5(2):199–220 | 1993 | Classical | "An explicit specification of a conceptualization" |
| Knowledge graph | Hogan et al., *ACM Computing Surveys* 54(4) | 2021 | Classical | Relevant prior art Archeia deliberately does not adopt in full |
| Memory hierarchy | MemGPT / Letta (arXiv:2310.08560) | 2023 | Recent AI | Main context, external context, core memory, peripheral memory |
| Four memory competencies | MemoryAgentBench (arXiv:2507.05257) | 2025 | Recent AI | Accurate retrieval, test-time learning, long-range understanding, selective forgetting |
| Atomic skills | Ma et al. (arXiv:2604.05013) | 2026 | Recent AI | Foundational coding skill decomposition; precedent for Archeia's skill library |
| Skill retrieval bottleneck | Liu et al. (arXiv:2604.04323) | 2026 | Recent AI | 34K-skill-library study; the problem is selection, not execution |
| Skill ontology | SkillNet (arXiv:2603.04448) | 2026 | Recent AI | 200K-skill structured repository |
| Harness | Meta-Harness (arXiv:2603.28052); NLAHs (arXiv:2603.25723); OpenDev (arXiv:2603.05344) | 2026 | Recent AI | The runtime layer Archeia does not specify but assumes |
| Single-agent vs multi-agent | arXiv:2604.02460 (Stanford 2026) | 2026 | Recent AI | Information-theoretic bound; informs the delegation model |
| Reliability limits of delegation | arXiv:2603.26993 (MIT 2026) | 2026 | Recent AI | Formal proof that delegated networks cannot exceed centralized Bayes under same info |
| Self-organizing agents | arXiv:2603.28990 | 2026 | Recent AI | 25K-task empirical study; hybrid protocols beat both centralized and full autonomy |
| Explicit memory primitives | LightThinker++ (arXiv:2604.03679) | 2026 | Recent AI | Commit/Expand/Fold; intra-context analogues of Archeia's persistence operations |
| ADR (Architecture Decision Record) | Nygard 2011; Ford, Parsons & Kua 2017 | 2011, 2017 | Classical | Direct precedent for accumulating records in `product/decisions/` |

---

## 11. Archeia coinage and why

Terms Archeia uses that have no canonical academic precedent, and why they exist:

| Term | Status | Justification |
|---|---|---|
| **Living document** | Archeia coinage | Closest academic framing is "semantic memory as canonical evolving document." Full academic version is too long for a term used throughout the standard. |
| **Accumulating record** | Archeia coinage | Closest academic framings are "episodic memory store" and "append-only record." Archeia uses a compact term that combines both. |
| **Transient artifact** | Archeia coinage | Closest academic framings are "prospective memory" + "operational working memory," which don't compose naturally. "Transient" captures the bounded-retention property. |
| **Three lifecycle shapes** | Archeia coinage | Maps directly to Tulving taxonomy (see §3.2) but the specific triplet (living / accumulating / transient) is Archeia's organization. |
| **Forward flow** (business → product → execution → codebase) | Archeia coinage | The causal direction of work in software projects. No single academic source; the closest is the product-engineering handoff literature (Cagan, *Inspired*, 2008), which is non-academic. |
| **Read flow** (everyone reads codebase and product) | Archeia coinage | Complement to forward flow. Context-fetching pattern. No academic source. |
| **Codebase is a witness, not a planner** | Archeia coinage | Named principle unique to the standard. |

All other Archeia terms should be replaceable with or glossed by their canonical equivalents per the table in §10.

---

## 12. Unverified and flagged claims

Claims we have not been able to verify against primary sources, even with web search of recent literature:

1. **Sarah Wooders — "Why memory isn't a plugin (it's the harness)."** *(Previously unverified; now verified.)* X thread, April 4, 2026. Verified quote: **"Asking to plug memory into an agent harness is like asking to plug driving into a car."** Earlier drafts of this document paraphrased the concept as "memory is context management, not a retrieval problem" while noting the exact quote could not be located. The correct exact quote has now been located; Archeia cites Wooders' verified wording going forward. The concept — that managing context (and therefore memory) is a core responsibility of the harness itself, not a plugin — is identical to what Archeia had been attributing to her in paraphrased form.

2. **McDaniel & Einstein "canonical year"** for prospective memory. No single founding paper; the 2007 Sage book *Prospective Memory: An Overview and Synthesis of an Emerging Field* is the most-cited synthesis and what Archeia cites.

3. **"Consolidation"** in cognitive science vs **"knowledge consolidation"** in agent literature. Both are in use. Archeia uses the verb `consolidate` for the operation (shorter, stands alone) but glosses it as "knowledge consolidation" in formal definitions to match the MemoryAgentBench vocabulary.

4. **Anthropic-internal vocabulary** (skills, subagents, compaction, MEMORY.md). These are documented in `code.claude.com/docs/` but the formal specification evolves continuously. Archeia pins to specific doc URLs and cites them as industry references.

---

## 13. How this document evolves

The ontology is itself a living document (Archeia's own shape #1). It is edited in place as the canonical terms shift. Every edit is a git commit; previous versions are accessible via `git log standard/ONTOLOGY.md`.

**Additions** are straightforward — add a new primitive, add a new source citation, add to the vocabulary table.

**Corrections** are committed with a clear rationale in the commit message (e.g., "Snodgrass is 1986 not 1988; 1988 was a bibliography").

**Deletions** are avoided. If a term is deprecated, the table entry is marked `deprecated` with a pointer to the replacement. The old term and its justification stay, so the audit trail is preserved.

**Versioning:** this document is versioned with the standard (`standard/VERSION`). Breaking changes to terminology — renaming a kernel operation, changing a shape — require a major version bump in the standard.

---

## 14. References

Papers cited in this document, grouped by category.

### Classical cognitive science and memory
- Baddeley, A. & Hitch, G. (1974). Working memory. In G. A. Bower (ed.), *The Psychology of Learning and Motivation*, vol. 8, pp. 47–89. Academic Press.
- Hardt, O., Nader, K. & Nadel, L. (2013). Decay happens: the role of active forgetting in memory. *Trends in Cognitive Sciences* 17(3):111–120.
- McDaniel, M. A. & Einstein, G. O. (2007). *Prospective Memory: An Overview and Synthesis of an Emerging Field*. Sage Publications.
- Müller, G. E. & Pilzecker, A. (1900). *Experimentelle Beiträge zur Lehre vom Gedächtnis*. Leipzig: Barth.
- Squire, L. R. & Alvarez, P. (1995). Retrograde amnesia and memory consolidation: a neurobiological perspective. *Current Opinion in Neurobiology* 5:169–177.
- Squire, L. R. & Zola-Morgan, S. (1991). The medial temporal lobe memory system. *Science* 253(5026):1380–1386.
- Tulving, E. (1972). Episodic and semantic memory. In E. Tulving & W. Donaldson (eds.), *Organization of Memory*, pp. 381–403. Academic Press.

### Classical cognitive architecture
- Anderson, J. R. (1993). *Rules of the Mind*. Lawrence Erlbaum Associates.
- Newell, A. (1990). *Unified Theories of Cognition*. Harvard University Press (The William James Lectures).

### Classical multi-agent systems and coordination
- Baars, B. J. (1988). *A Cognitive Theory of Consciousness*. Cambridge University Press. (Global Workspace Theory)
- Elliott, M. (2006). Stigmergic collaboration: The evolution of group work. *M/C Journal* 9(5).
- Engelmore, R. & Morgan, T. (eds.) (1988). *Blackboard Systems*. Addison-Wesley.
- Grassé, P.-P. (1959). La reconstruction du nid et les coordinations inter-individuelles. *Insectes Sociaux* 6:41–81.
- Hayes-Roth, B. (1985). A blackboard architecture for control. *Artificial Intelligence* 26(3):251–321.
- Hutchins, E. (1995). *Cognition in the Wild*. MIT Press.
- Rao, A. S. & Georgeff, M. P. (1991). Modeling rational agents within a BDI-architecture. *Principles of Knowledge Representation and Reasoning* (KR-91).
- Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach*, 4th ed. Pearson.
- Theraulaz, G. & Bonabeau, E. (1999). A brief history of stigmergy. *Artificial Life* 5(2):97–116.
- Wooldridge, M. & Jennings, N. R. (1995). Intelligent agents: Theory and practice. *The Knowledge Engineering Review* 10(2):115–152.

### Classical knowledge representation and temporal data
- Gruber, T. R. (1993). A translation approach to portable ontology specifications. *Knowledge Acquisition* 5(2):199–220.
- Hogan, A., Blomqvist, E., Cochez, M., et al. (2021). Knowledge graphs. *ACM Computing Surveys* 54(4):71.
- Jensen, C. S., Clifford, J., Gadia, S. K., Segev, A. & Snodgrass, R. T. (1992). A glossary of temporal database concepts. *ACM SIGMOD Record* 21(3):35–43.
- Snodgrass, R. T. & Ahn, I. (1986). Temporal databases. *IEEE Computer* 19(9):35–42.

### Software engineering precedents
- Ford, N., Parsons, R. & Kua, P. (2017). *Building Evolutionary Architectures*. O'Reilly Media.
- Nygard, M. (2011). Documenting Architecture Decisions. [cognitect.com/blog](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- Tranter, S. E. & Reynolds, D. A. (2006). An overview of automatic speaker diarization systems. *IEEE Transactions on Audio, Speech, and Language Processing* 14(5):1557–1565.

### Industry essays and primary sources (April 2026)
- Chase, H. (2026). Your harness, your memory. *LangChain Blog, In the Loop Series*, April 11, 2026. https://blog.langchain.com/your-harness-your-memory/
- Chomsky, M. (2026). [Analysis of Garry Tan and Harrison Chase on harness + memory]. X, April 11, 2026. https://x.com/michael_chomsky/status/2043369126631207096
- Tan, G. (2026). Thin Harness, Fat Skills. X, April 10, 2026. https://x.com/garrytan/status/2042925773300908103
- Tan, G. (2026). gbrain — personal knowledge management with git-backed markdown + Postgres/pgvector retrieval. https://github.com/garrytan/gbrain
- Tan, G. (2026). gstack — 23 Claude Code skills organized as a virtual engineering organization. https://github.com/garrytan/gstack
- Wooders, S. (2026). Why memory isn't a plugin (it's the harness). X thread, April 4, 2026. https://x.com/sarahwooders/status/2040121230473457921

### Recent AI research (2023–2026)
- Hu, Y., Wang, Y. & McAuley, J. (2025). Evaluating memory in LLM agents via incremental multi-turn interactions (MemoryAgentBench). arXiv:2507.05257.
- Lee, Y., Nair, R., Zhang, Q., Lee, K., Khattab, O. & Finn, C. (2026). Meta-Harness: End-to-end optimization of model harnesses. arXiv:2603.28052.
- Liu, Y., Ji, J., An, L., Jaakkola, T., Zhang, Y. & Chang, S. (2026). How well do agentic skills work in the wild. arXiv:2604.04323.
- Lou, X., et al. (2026). AutoHarness: improving LLM agents by automatically synthesizing a code harness. arXiv:2603.03329.
- Ma, Y., Liu, Y., Yang, X., et al. (2026). Scaling coding agents via atomic skills. arXiv:2604.05013.
- Natural-Language Agent Harnesses (2026). arXiv:2603.25723.
- OpenDev (2026). Building effective AI coding agents for the terminal. arXiv:2603.05344.
- Packer, C., Fang, S., Patil, S. G., Wooders, S., Lin, K. & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as operating systems. arXiv:2310.08560.
- Rasmussen, P., et al. (2025). Zep: A temporal knowledge graph architecture for agent memory. arXiv:2501.13956.
- Single-Agent LLMs vs. Multi-Agent Systems (2026). arXiv:2604.02460.
- SkillNet (2026). Create, evaluate, and connect AI skills. arXiv:2603.04448.
- Sumers, T., Yao, S., Narasimhan, K. & Griffiths, T. L. (2023). Cognitive architectures for language agents (CoALA). arXiv:2309.02427.
- Wu, X., et al. (2024). LongMemEval: Benchmarking chat assistants on long-term interactive memory. arXiv:2410.10813.
- Zhang, N., et al. (2026). LightThinker++: From reasoning compression to memory management. arXiv:2604.03679.

---

## 15. Acknowledgments

The research underlying this ontology draws on four specific pieces of prior work from April 2026 that reshaped earlier Archeia drafts:

- **Garry Tan, "Thin Harness, Fat Skills"** (X, [April 10, 2026](https://x.com/garrytan/status/2042925773300908103)). Introduced the thin-harness / fat-skills framing, the latent-vs-deterministic distinction, and the parameterized-skill view. Archeia's Truth #7 and the skill format spec in [`KERNEL.md`](KERNEL.md#10-skill-format-parameterized-procedures) both follow from this reading. Tan's own reference implementations are [gstack](https://github.com/garrytan/gstack) (23 Claude Code skills as a "virtual engineering organization") and [gbrain](https://github.com/garrytan/gbrain) (personal knowledge management).

- **Sarah Wooders, "Why memory isn't a plugin (it's the harness)"** (X thread, [April 4, 2026](https://x.com/sarahwooders/status/2040121230473457921)). Sarah is CTO of [Letta](https://letta.com) (formerly MemGPT). The verified exact quote: *"Asking to plug memory into an agent harness is like asking to plug driving into a car. Managing context, and therefore memory, is a core capability and responsibility of the agent harness."* This framing is the source of Archeia's harness-boundary section in [`KERNEL.md`](KERNEL.md#9-where-the-harness-fits) — the claim that compaction policy is harness business, but persistence guarantees are contract business.

- **Harrison Chase, "Your harness, your memory"** (LangChain Blog, [April 11, 2026](https://blog.langchain.com/your-harness-your-memory/)). Harrison is CEO of LangChain. His essay argues that agent harnesses and agent memory are inseparable, that closed harnesses create memory lock-in ("if you use a closed harness, especially if its behind an API, you don't own your memory"), and that open harnesses (like LangChain's Deep Agents) are the right response. Archeia's kernel-and-distribution framing is aligned with this claim: the Archeia Standard is an open contract at the knowledge layer, and any conforming harness — Claude Code, Cursor, Deep Agents, OpenCode, bespoke — can participate.

- **Michael Chomsky, analysis essay** (X, [April 11, 2026](https://x.com/michael_chomsky/status/2043369126631207096)). Chomsky analyzed both Garry Tan and Harrison Chase and argued that *both* oversimplify memory — Garry by trusting markdown files alone, Harrison by making memory sound tractable. His essay introduced the four memory competencies as the audit framework (sourced from MemoryAgentBench, Hu et al. 2025). Archeia's [`docs/memory-vs-knowledge.md`](../docs/memory-vs-knowledge.md) audit is a direct response to Chomsky's critique. Chomsky also points out that Garry Tan's own `gbrain` project uses Postgres + pgvector underneath the markdown interface — evidence that even the strongest file-based-memory advocate needed a real database to make it work.

The error of using "diarize" for the knowledge-consolidation operation (inherited from Garry Tan's "Thin Harness, Fat Skills") is acknowledged as Archeia's own false start in earlier drafts. The correction to `consolidate` is documented in this file as the canonical term.

### Earlier attribution error (now corrected)

Earlier drafts of Archeia's documentation incorrectly credited **Steve Yegge** with authorship of "The Harness Is The Product" / "Thin Harness, Fat Skills." Yegge is a name that appears in Garry Tan's essay (quoted for the "10x to 100x productivity" claim), not the author. The correct author is Garry Tan, YC president. This ontology document — along with [`PRINCIPLES.md`](PRINCIPLES.md), [`KERNEL.md`](KERNEL.md), and [`../docs/memory-vs-knowledge.md`](../docs/memory-vs-knowledge.md) — was corrected to reflect the actual authorship in kernel version 0.2.1.

---

*This document is `standard/ONTOLOGY.md` in the Archeia repository. It is a living document per Archeia's own shape-1 convention: edited in place, history preserved in git, no superseded versions cluttering the directory.*
