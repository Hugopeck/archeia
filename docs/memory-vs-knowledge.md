# Memory vs Knowledge: What Archeia Solves and What It Doesn't

> **This document is the honest audit.** It separates what the Archeia Standard actually solves from what it doesn't, evaluated against the four canonical memory competencies from MemoryAgentBench (Hu, Wang & McAuley, arXiv:2507.05257, 2025). Archeia is described as *partial*, with some jobs deferred to future work and some jobs deferred to a different layer of the stack entirely.
>
> Published under Hugo's explicit direction that credibility comes from saying what doesn't work, not from pretending everything does.

---

## 1. Why this document exists

In April 2026, four essays appeared within a week of each other, all arguing about the same underlying question: what is the right architecture for agent memory, and who gets to own it?

- **Sarah Wooders, "Why memory isn't a plugin (it's the harness)"** ([X thread, April 4, 2026](https://x.com/sarahwooders/status/2040121230473457921)) — argued that memory is not a separate service that plugs into an agent; it is what the harness *is*. Verified exact quote: *"Asking to plug memory into an agent harness is like asking to plug driving into a car. Managing context, and therefore memory, is a core capability and responsibility of the agent harness."*

- **Garry Tan, "Thin Harness, Fat Skills"** ([X, April 10, 2026](https://x.com/garrytan/status/2042925773300908103)) — argued that AI agent productivity comes from the thin-harness + fat-skills architecture, with specific contributions on latent-vs-deterministic work allocation and skill-as-method-call semantics. Tan's reference implementations are [gstack](https://github.com/garrytan/gstack) (23 Claude Code skills as a "virtual engineering organization") and [gbrain](https://github.com/garrytan/gbrain) (personal knowledge management).

- **Harrison Chase, "Your harness, your memory"** ([LangChain Blog, April 11, 2026](https://blog.langchain.com/your-harness-your-memory/)) — argued that agent harnesses and agent memory are inseparable, that closed harnesses create memory lock-in, and that open harnesses (like LangChain's Deep Agents) are the necessary response. Key claim: *"If you use a closed harness, especially if its behind an API, you don't own your memory."*

- **Michael Chomsky, analysis essay** ([X, April 11, 2026](https://x.com/michael_chomsky/status/2043369126631207096)) — analyzed Garry Tan's and Harrison Chase's positions and argued that *both* oversimplify memory. Garry by trusting markdown files alone (Chomsky's key counterpoint: Garry's own `gbrain` project uses Postgres + pgvector underneath the markdown interface — evidence that even the strongest file-based-memory advocate needed a real database to make it work). Harrison by making memory sound tractable. Chomsky's essay introduced the **four memory competencies** from MemoryAgentBench as the audit framework any memory claim should face, and his summary — *"nobody has memory right"* — is the most credible framing in the current debate.

Chomsky's critique lands hardest on Archeia. Archeia has been marketed primarily as a **storage and structure** proposition, and for the central cases that's correct and useful. But Chomsky's honest summary is what makes his essay the most credible voice in the conversation. Archeia should match that honesty rather than overclaim.

This document is the match. It audits Archeia against the four canonical memory competencies from the academic literature, says where Archeia is strong, where it's partial, where it's weak, and where it explicitly defers to a different layer of the stack.

### Earlier attribution error (now corrected)

Earlier drafts of this document incorrectly credited **Steve Yegge** with authorship of "The Harness Is The Product" / "Thin Harness, Fat Skills." Yegge appears in Garry Tan's essay only as a quoted source for the "10x to 100x as productive" claim; the essay itself is Tan's. Earlier drafts also conflated **Harrison Chase's** "Your harness, your memory" argument with **Michael Chomsky's** four-memory-competencies critique — these are two different essays by two different authors with overlapping but distinct claims. Both errors were corrected in kernel version 0.2.1.

---

## 2. The canonical framing: four memory competencies

The most rigorous academic framing of what an agent memory system must do is **MemoryAgentBench** (Hu, Wang & McAuley, "Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions," arXiv:2507.05257, 2025). The paper proposes four core competencies, explicitly grounded in cognitive science:

1. **Accurate retrieval** — find the right memory when it is needed.
2. **Test-time learning** — update what the agent knows from new information as it arrives.
3. **Long-range understanding** — connect information across sessions separated in time.
4. **Selective forgetting** — recognize when a memory is stale and stop relying on it.

Michael Chomsky's "four jobs" framing in his April 11, 2026 analysis is a paraphrase of these four canonical competencies. The framing is canonical and any agent-memory claim should be audited against all four.

---

## 3. Archeia's score, honestly

### 3.1 Competency #1: Accurate retrieval — STRONG

**Claim**: path-based lookup is the strongest retrieval primitive available for project knowledge.

**Why it works**: when an agent needs to know the current product specification, it reads `.archeia/product/product.md`. There is no query, no ranking, no top-k, no relevance threshold, no embedding drift, no hallucinated near-match. The file exists at a known path or it doesn't. This is Archeia's central advantage over vector-DB-backed memory systems for well-structured project knowledge.

**Supporting literature**: Cao et al., "Coding Agents are Effective Long-Context Processors" (arXiv:2603.20432, 2026) — demonstrated that agents navigating text corpora as navigable file systems outperform state-of-the-art long-context attention methods by 17.3% on average across benchmarks spanning up to three trillion tokens. The empirical case for path-based retrieval at scale is strong.

**Where it stops working**: when the agent doesn't know what to look for. See §3.5 on the proactive injection problem.

**Competency score: STRONG for central cases, WEAK for peripheral cases.**

### 3.2 Competency #2: Test-time learning — PARTIAL

**Claim**: writing a new artifact to `.archeia/` and committing is real-time learning at the filesystem layer.

**What works**: when `archeia:review-draft` reads a business draft and produces an update to `product/product.md` plus a new entry in `product/decisions/`, that is real-time learning. The new knowledge is immediately available to the next session. Git commits are the learning events. No retraining, no vector index rebuild, no embedding regeneration — the filesystem already gives us real-time persistence.

**What doesn't work yet**: Archeia has no principle for **when** a living document should be updated. Does an agent edit `architecture.md` after every session? After significant code changes? On a schedule? On demand? The standard is silent. Without a rule, living documents either drift (too-infrequent updates → staleness) or churn (too-frequent updates → noise in git history).

This gap is real. The solution — some form of trigger-based re-consolidation policy, probably per-artifact — is future work. Recent research suggests the answer involves something like **Saguaro** (Mesa, 2025) — a separate review agent that runs after every turn and decides whether any living document needs re-consolidation. Or something like **A-MemGuard** (arXiv:2510.02373, 2025) — a proactive defense framework that monitors for context-triggered stale-memory injection. Archeia has neither mechanism yet.

**Supporting literature**: MemGPT (Packer et al., arXiv:2310.08560, 2023) addresses a different layer — in-context self-editing memory — and does it well. That approach is compatible with Archeia; a distribution could use MemGPT's self-editing patterns at the harness layer while persisting outputs to Archeia's filesystem layer.

**Competency score: PARTIAL.** The substrate supports real-time learning; the policy for when to re-consolidate is missing.

### 3.3 Competency #3: Long-range understanding — PARTIAL

**Claim**: accumulating records preserve long-range episodic facts; living documents preserve long-range semantic facts.

**What works**: ADRs in `product/decisions/` and retros in `execution/retros/` stay on disk forever. An agent working on a task today can read a decision from 18 months ago and understand why the system is shaped the way it is. This is long-range episodic memory and Archeia gets it right by default.

**What doesn't work**: Archeia has **no graph over artifacts**. There is no way to answer questions like:
- "Which decisions affected which features, which are implemented by which tasks, which touched which files?"
- "Which retros identified concerns that were later addressed by which decisions?"
- "What's the chain from the original vision in Q1 2025 to the current product.md spec?"

The cross-domain contracts in Archeia are **static schemas** (this frontmatter field exists) not **navigable relationships** (this artifact points at that one). Frontmatter fields like `supersedes:`, `source_draft:`, and `implements:` already sketch a lightweight graph, but nothing walks it.

**This is where graph-based memory systems (Zep/Graphiti, Supermemory, Mem0) genuinely do more than Archeia.** They build explicit edges between entities and support traversal queries. Archeia currently supports such queries only if a human or an agent reads many files and synthesizes manually — which is expensive.

**A future extension**: the planned `evolve` operation currently only walks history for a single artifact (git log for living docs, supersession chain for accumulating records). A future version could walk cross-artifact relationships via frontmatter links. This is tracked as a Phase-D improvement, not shipped in 0.2.0.

**Supporting literature**: Rasmussen et al., "Zep: A Temporal Knowledge Graph Architecture for Agent Memory" (arXiv:2501.13956, 2025) is the current state of the art in graph-based long-range understanding. Archeia is explicitly simpler and gives up some of Zep's capabilities in exchange for filesystem-native simplicity.

**Competency score: PARTIAL.** Episodic long-range memory works; graph traversal over the episodic + semantic stores does not.

### 3.4 Competency #4: Selective forgetting — WEAK

**Claim**: Archeia's retention windows handle selective forgetting for transient artifacts.

**What works**: a done task that enters its 14-day retention window and is then pruned is a form of selective forgetting. The task is gone from disk; git preserves the history; the agent's working context stays clean. For operational state this is exactly what you want.

**What doesn't work**: for **living documents** and **accumulating records**, Archeia has almost no forgetting mechanism. `architecture.md` can be stale — the code changed but nobody re-ran the consolidator — and nothing flags it. An ADR from 18 months ago can record a decision that was quietly abandoned — the team stopped following it — and nothing flags that either.

**The minimal bi-temporal support** added in 0.2.0 (the `last_verified` frontmatter field on living documents and accumulating records) is a *staleness signal* but not active forgetting. A reader who sees `last_verified: 2025-08-15` on today's architecture doc can infer that the doc is probably stale. Archeia does not currently have a skill that reviews these timestamps and prunes, re-verifies, or flags stale artifacts.

**This is the weakest of Archeia's four competencies.** Chomsky's critique is exactly right on this point: git preserves history perfectly but nothing in git tells you whether a file's contents are still *true*. Bi-temporal databases solve this by tracking valid time as a first-class field; Archeia currently only proxies it via `last_verified`, and we have no tooling to enforce re-verification cadence.

A future `archeia:verify-stale` skill (not yet shipped) would walk living documents and accumulating records, compare `last_verified` against distribution-defined staleness thresholds, and produce a "stale knowledge report" that distributions could surface to the operator. This is documented as Phase-D work.

**Supporting literature**:
- Snodgrass & Ahn, "Temporal Databases" (*IEEE Computer* 19(9), **1986**) — the foundational bi-temporal modeling paper.
- Rasmussen et al., "Zep" (arXiv:2501.13956, 2025) — applies bi-temporal modeling to agent memory with validity intervals on every fact. The current gold standard for selective forgetting at the memory-system layer.
- Hu, Wang & McAuley, "MemoryAgentBench" (arXiv:2507.05257, 2025) — explicitly tests selective forgetting as one of the four canonical competencies.

**Competency score: WEAK.** Retention windows for transient artifacts work; staleness detection for living and accumulating content is tracked only by advisory frontmatter and has no enforcement tooling.

### 3.5 The proactive injection problem — DISSOLVED FOR CENTRAL CASES, UNSOLVED FOR PERIPHERAL CASES

**Chomsky's proactive injection problem**: how do you get the right memory into context when the agent doesn't know it should be searching?

His example: "A coding agent drifts off-track and violates a pattern your team agreed on three months ago. The memory exists. The agent didn't search for it because it didn't know it was relevant."

**Archeia's answer for central cases**: the agent doesn't need to search. Path-based lookup means the agent working on a task reads `.archeia/execution/tasks/<id>.md`, `.archeia/product/product.md`, `.archeia/codebase/standards/standards.md`, and `.archeia/codebase/guide.md` at well-known paths because the skill specifies them. No search, no hit-or-miss retrieval, no embedding-ranking. This **dissolves the injection problem** for the central facts that every session needs.

**Archeia's honest limit for peripheral cases**: when the relevant knowledge is not on a standard path — an ADR from 18 months ago that mentions a pattern the current task accidentally violates, a past growth experiment whose learning applies to the current channel decision — Archeia is in the same situation as every other in-repo knowledge system. The agent won't find it unless something triggers the search, and Archeia does not have a good trigger.

Recent research is working on this. A-MemGuard (arXiv:2510.02373, 2025) proposes consensus-based validation for memory injection resistance. PRIME distills multi-turn trajectories into structured experiences that surface when contextually relevant. MemGuide ranks candidate memories by "marginal slot-completion gain" — asking whether injecting a candidate memory would fill a gap the agent needs. None of these are production-ready for synchronous agent loops where an extra inference round costs real latency.

Archeia has no current answer for the peripheral case. The honest position is: **the well-structured project knowledge that lives at known paths is handled by path-based lookup; the loosely-structured accumulated knowledge that might be relevant is an open research problem, and Archeia does not claim to solve it.**

---

## 4. The division of labor

Archeia is not a full memory system. It is a **cognitive architecture for structured project knowledge**, specifically:

- The **storage substrate** that makes memory tractable (files + ownership + shapes)
- The **structural conventions** that let agents find central facts at known paths (dissolving injection for central cases)
- The **human-agent shared canvas** that lets humans edit the same tree agents edit (Truth #2)
- The **coordination primitive** that lets multiple agents coexist without collisions (ownership + delegation)
- The **basic temporal hygiene** for operational artifacts (retention windows + pruning)

Archeia is NOT:

- A dynamic memory system with bi-temporal validity tracking (→ Zep/Graphiti does this better)
- A graph traversal engine over relationships between artifacts (→ Letta, Supermemory, Mem0 do this better)
- A selective forgetting mechanism for living documents (→ unsolved problem; A-MemGuard / PRIME are research)
- A proactive injection system for peripheral knowledge (→ unsolved problem)
- A replacement for the harness's in-context memory management (→ that's MemGPT/Letta/Claude Code's job)

The honest framing is that **Archeia is the knowledge layer; a full memory solution also needs a dynamic memory layer**. They compose. A distribution could plug a Zep/Graphiti-style memory engine into the harness layer while persisting durable outputs to an Archeia tree at the knowledge layer. Neither replaces the other.

### The gbrain data point — what Garry Tan's own practice reveals

Michael Chomsky's analysis essay surfaced a load-bearing observation that deserves its own section: Garry Tan's own **gbrain** project, the canonical reference implementation of the "markdown is memory" philosophy, **uses Postgres and pgvector underneath the markdown interface** for actual retrieval. The README is explicit about the three-layer architecture:

1. **Brain Repo (git):** markdown as source of truth — the layer users see and edit
2. **GBrain (retrieval):** Postgres with pgvector for hybrid search — the layer that actually answers queries
3. **AI Agent layer:** read/write interface over the other two

The point is not that gbrain is wrong. gbrain is *correct* — at scale, markdown files alone cannot serve search queries efficiently, and a real database is required. The point is that **even the strongest public advocate of "markdown is sufficient" built a database underneath when he had to ship a working system**. This is evidence for Chomsky's case that file-based memory is the right *starting* posture but not the end state, and it is evidence against any reading of Archeia that claims the filesystem alone replaces all database infrastructure.

**What this means for Archeia's positioning**: Archeia provides the structural and human-readable layer (equivalent to gbrain's "Brain Repo" layer). A production distribution that scales beyond single-operator projects will eventually need something like gbrain's middle layer — a real database for efficient retrieval, search, and graph queries — layered on top of the Archeia tree. This is not a failure of Archeia; it is a correct division of labor. Archeia specifies the canonical persistent substrate that humans and agents can both read and edit; downstream tooling can index and serve that substrate however it needs to. gbrain itself is a proof-of-concept that this division works in practice.

Archeia should explicitly welcome downstream retrieval layers rather than claim the filesystem alone is sufficient for every scale. Adding the gbrain architecture pattern as a recommended companion approach — Archeia tree as the source-of-truth, Postgres+pgvector (or equivalent) as the retrieval and query engine — is on the roadmap for Phase D, alongside the formal integration spec for dynamic memory systems (§6.5 below).

This is the right frame. Claiming "Archeia solves memory" would be overclaiming and Chomsky would be right to call it out. Claiming "Archeia is the structural substrate that makes memory solutions tractable, and it composes cleanly with dynamic memory engines above it" is accurate and defensible. It also aligns directly with Harrison Chase's "Your harness, your memory" argument that an open contract at the knowledge layer — exactly what Archeia provides — is what lets operators avoid yielding memory ownership to closed harnesses.

---

## 5. What Archeia does that no other system does (honestly)

Rather than claim to solve memory, Archeia should claim what it actually does uniquely well. Four things:

### 5.1 The knowledge layer is shared between humans and agents

Every other memory system we've surveyed (Letta, Zep, Supermemory, Mem0, MemGPT, OpenClaw) treats the human as a user who triggers agent work. Archeia treats the human as a co-editor who works on the same artifacts agents work on, in their normal editor, with git providing the coordination guarantees. This is Truth #2 in PRINCIPLES.md and no other system in the space has made it central. If your collaboration model is "operator orchestrates agents and occasionally intervenes," Archeia's shared-canvas approach is the only option. If your model is "agents run autonomously and the human gets summaries," any of the competing memory systems is fine.

### 5.2 Ownership-plus-delegation as the concurrency model

Every other coordination approach for multi-agent systems uses some combination of locks, CRDTs, consensus protocols, or merge algorithms. Archeia's ownership-per-domain plus subagent delegation means conflicts literally cannot happen at the file-write level because there's always exactly one writer holding the pen. This is Truth #4 and it is the cheapest coordination primitive that works at scale. Recent Stanford work (Single-Agent vs Multi-Agent, arXiv:2604.02460, 2026) and MIT work (Reliability Limits, arXiv:2603.26993, 2026) both argue — from different angles — that centralized decision-making with delegation beats distributed coordination under fixed compute budgets. Archeia operationalizes this insight at the artifact level.

### 5.3 Canonical cognitive-architecture mapping

Archeia's three lifecycle shapes (living, accumulating, transient) map 1:1 onto Tulving's memory taxonomy (semantic, episodic, prospective+operational) with CoALA's (Sumers et al., arXiv:2309.02427, 2023) bridge from cognitive science to LLM agents. No other in-repo knowledge system makes this mapping explicit. Archeia is the first system to apply CoALA's cognitive-architecture framework to *persistent project knowledge* rather than *in-context memory*, and the mapping is non-trivial — it gives the three shapes 50 years of empirical grounding rather than being arbitrary categories.

### 5.4 The kernel / distribution split

Every other agent-memory system is a single opinionated bundle. Archeia separates the kernel (universal substrate) from distributions (opinionated extensions for specific audiences). This is borrowed from the Linux kernel / distributions pattern and applied to agent-knowledge standards. Archeia Solo is one distribution; Archeia Research, Archeia Studio, Archeia Enterprise can all exist on the same kernel with different domains, different retention windows, different ethos. No other system in the space has named this split explicitly.

---

## 6. Where future work is needed

Documenting the gaps so they don't become hidden assumptions:

### 6.1 Staleness enforcement for living documents and accumulating records

Currently the `last_verified` frontmatter field is *advisory*. Nothing reads it, nothing flags stale content, nothing re-triggers consolidation. A planned `archeia:verify-stale` skill would close this gap by walking durable artifacts, comparing `last_verified` against distribution-defined thresholds, and producing a stale-knowledge report. Target: kernel version 0.3.

### 6.2 Cross-artifact graph traversal

The frontmatter fields `supersedes:`, `source_draft:`, `implements:`, `related_to:`, and similar constitute a lightweight graph over `.archeia/` artifacts. Archeia does not currently walk this graph. A planned `archeia:graph` skill would support queries like "show me all decisions that mention feature X" or "what's the chain from this task back to the originating vision." Target: kernel version 0.3 or 0.4.

### 6.3 Bi-temporal upgrade for accumulating records

The minimal bi-temporal support (`last_verified`) is a proxy. A full upgrade would add `valid_from:` and `valid_until:` fields to accumulating records, letting distributions track not just "when we recorded this" but "when this was known to be in force." Zep/Graphiti already does this at the memory-engine layer; Archeia could adopt the pattern. Target: kernel version 0.3 or 0.4, coordinated with distribution updates.

### 6.4 Proactive injection for peripheral knowledge

This is the hard one. The honest current answer is "open research problem, Archeia defers to future work and to dynamic-memory engines layered above." A distribution could experiment with periodic background re-indexing (similar to OpenClaw's MEMORY.md injection pattern) or with semantic triggers (similar to Saguaro's per-turn review agent). Neither is production-ready yet. Target: probably kernel version 1.0+ or later, once the field has settled on a pattern.

### 6.5 Formal integration with dynamic memory systems

A Phase-D goal: specify how a Letta, Zep, Supermemory, or Mem0 backend plugs into the harness layer while a distribution persists durable outputs to an Archeia tree. The two layers are complementary — Archeia owns persistence and structure, the dynamic memory engine owns context management and validity tracking. A formal interop spec would let users combine them without writing glue code.

---

## 7. What this means for adopters

If you are evaluating Archeia for a project, read this document before deciding.

**Archeia is the right choice if**:
- You want project knowledge that is human-editable and agent-parseable in the same files
- You want the shared canvas for human-agent collaboration on the same artifacts
- You want the structural substrate and coordination rules that prevent multi-agent collisions
- You're OK with path-based retrieval as your primary knowledge-access pattern
- You can live with basic temporal hygiene (retention windows, advisory staleness flags) instead of full validity tracking
- You're building on the harness layer yourself and will handle context management there

**Archeia is the wrong choice if**:
- You need full bi-temporal validity tracking with automatic staleness detection
- You need graph traversal over a large knowledge base with complex relationships
- You need proactive memory injection for peripheral, loosely-structured knowledge
- You need a complete drop-in memory solution that handles retrieval, learning, forgetting, and long-range reasoning all at once

For the second list, consider Zep/Graphiti or Letta for dynamic memory at the harness layer. They are stronger on those competencies, and their architecture is compatible with running an Archeia tree underneath for durable project knowledge. The two layers compose rather than compete.

---

## 8. Credit where it's due

This document exists because four essays from April 2026 made it impossible to ignore the gaps:

- **Sarah Wooders**, "Why memory isn't a plugin (it's the harness)" ([X thread, April 4, 2026](https://x.com/sarahwooders/status/2040121230473457921)). CTO of Letta (formerly MemGPT). Provided the verified framing that grounds Archeia's harness-boundary spec in KERNEL.md §9. Exact verified quote: *"Asking to plug memory into an agent harness is like asking to plug driving into a car. Managing context, and therefore memory, is a core capability and responsibility of the agent harness."*

- **Garry Tan**, "Thin Harness, Fat Skills" ([X, April 10, 2026](https://x.com/garrytan/status/2042925773300908103)). Identified the harness as a first-class layer, introduced the latent-vs-deterministic distinction (now Truth #7 in Archeia's principles), and clarified skills as parameterized method calls. His reference implementations are [gstack](https://github.com/garrytan/gstack) (23 Claude Code skills as a virtual engineering organization) and [gbrain](https://github.com/garrytan/gbrain) (personal knowledge management with a Postgres+pgvector retrieval layer underneath the markdown source-of-truth — see §4 for why this data point matters).

- **Harrison Chase**, "Your harness, your memory" ([LangChain Blog, April 11, 2026](https://blog.langchain.com/your-harness-your-memory/)). CEO of LangChain. Argued that agent harnesses and agent memory are inseparable, that closed harnesses create memory lock-in, and that open harnesses — open contracts at the knowledge layer — are the necessary response. Archeia's open-standard framing at the knowledge layer aligns directly with this argument.

- **Michael Chomsky**, analysis essay ([X, April 11, 2026](https://x.com/michael_chomsky/status/2043369126631207096)). Forced the honest audit by running Garry Tan's and Harrison Chase's positions against each other and against the gbrain evidence. Introduced the four-memory-competencies framework (sourcing it from MemoryAgentBench) as the canonical audit for any memory system. His summary — *"nobody has memory right"* — is the most credible framing in the current debate and Archeia matches it here.

- **The MemoryAgentBench team** (Hu, Wang & McAuley, arXiv:2507.05257, 2025). Providing the four canonical memory competencies against which any memory claim should be audited. This document uses their framework directly.

- **Theodore Sumers and the CoALA team** (arXiv:2309.02427, 2023). Establishing the bridge from Tulving's memory taxonomy to LLM agents. Archeia extends this bridge to the persistent-knowledge layer.

The honest position is: Archeia is a structural contribution to agentic development that makes other memory solutions tractable. It is not a full memory solution and it does not pretend to be. The field is pre-paradigmatic, the problems are genuinely hard, and credibility comes from saying so.

---

## 9. References

Cited directly in this document:

### Primary-source essays (April 2026)
- Chase, H. (2026). Your harness, your memory. *LangChain Blog*, April 11, 2026. https://blog.langchain.com/your-harness-your-memory/
- Chomsky, M. (2026). [Analysis of Garry Tan and Harrison Chase on harness + memory]. X post, April 11, 2026. https://x.com/michael_chomsky/status/2043369126631207096
- Tan, G. (2026). Thin Harness, Fat Skills. X post, April 10, 2026. https://x.com/garrytan/status/2042925773300908103
- Tan, G. (2026). gbrain (personal knowledge management with Postgres+pgvector retrieval). https://github.com/garrytan/gbrain
- Tan, G. (2026). gstack (Claude Code skills as a virtual engineering organization). https://github.com/garrytan/gstack
- Wooders, S. (2026). Why memory isn't a plugin (it's the harness). X thread, April 4, 2026. https://x.com/sarahwooders/status/2040121230473457921

### Academic research
- Cao, W., et al. (2026). Coding Agents are Effective Long-Context Processors. arXiv:2603.20432.
- Hu, Y., Wang, Y. & McAuley, J. (2025). Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions (MemoryAgentBench). arXiv:2507.05257.
- Packer, C., Fang, S., Patil, S. G., Wooders, S., Lin, K. & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as Operating Systems. arXiv:2310.08560.
- Rasmussen, P., et al. (2025). Zep: A Temporal Knowledge Graph Architecture for Agent Memory. arXiv:2501.13956.
- Snodgrass, R. T. & Ahn, I. (1986). Temporal Databases. *IEEE Computer* 19(9):35–42.
- Sumers, T., Yao, S., Narasimhan, K. & Griffiths, T. L. (2023). Cognitive Architectures for Language Agents (CoALA). arXiv:2309.02427.
- Tulving, E. (1972). Episodic and Semantic Memory. In E. Tulving & W. Donaldson (eds.), *Organization of Memory*, pp. 381–403. Academic Press.
- Single-Agent LLMs vs. Multi-Agent Systems (2026). arXiv:2604.02460.
- Reliability Limits of LLM-Based Multi-Agent Planning (2026). arXiv:2603.26993.
- A-MemGuard (2025). arXiv:2510.02373.

Full citation details for all Archeia-referenced work are in [`../standard/ONTOLOGY.md`](../standard/ONTOLOGY.md) §14.
