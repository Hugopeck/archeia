# Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?

**Source:** [arxiv.org/html/2602.11988v1](https://arxiv.org/html/2602.11988v1)
**Authors:** Thibaud Gloaguen, Niels Mündler, Mark Müller, Veselin Raychev, Martin Vechev
**Venue:** ICML 2026
**ArXiv ID:** 2602.11988v1
**License:** CC BY 4.0

---

## Abstract

This research investigates whether context files like AGENTS.md actually improve
coding agent performance, despite industry-wide recommendations to include them.
The authors evaluated agents using SWE-bench Lite tasks and a novel benchmark
called AGENTbench containing 138 instances from 12 repositories with
developer-written context files.

The findings were counterintuitive: "LLM-generated context files tend to
_reduce_ task success rates compared to providing no repository context, while
also _increasing inference cost_ by over 20%." Developer-provided files showed
modest improvements but similar cost increases. Agents using context files
engaged in broader exploration and testing but did not achieve better outcomes.

---

## 1 Introduction

### Background on Context Files

Context files represent an emerging best practice in AI-assisted software
development. Industry leaders have widely promoted this approach, with over
60,000 public repositories containing such files. Despite this adoption, "the
impact of context files on the coding agent's ability to solve complex software
engineering tasks has not been rigorously studied."

The authors identified two key research gaps:
1. Context files weren't available for prior benchmark instances
2. Popular repositories used in benchmarks aren't representative of most
   codebases

### This Work: Benchmarking Context Files' Impact

The research addresses these gaps by:
- Creating AGENTbench: a new benchmark of 138 instances from 12 niche
  repositories containing developer-written context files
- Evaluating multiple coding agents across different LLMs
- Testing three settings: no context files, LLM-generated files, and
  developer-provided files
- Analyzing agent behavior through trace analysis

### Key Contributions

1. **AGENTbench** — A curated benchmark specifically designed to evaluate context
   files' impact using real-world issues and developer-committed context files

2. **Extensive evaluation** showing that LLM-generated context files decrease
   agent performance while developer-written files provide only marginal
   improvements

3. **Detailed behavioral analysis** revealing that context files encourage more
   exploration and testing without improving task resolution

---

## 2 Background and Related Work

### Coding Agents

Coding agents are LLM-based systems that autonomously resolve software
engineering tasks using specialized tools for file operations, code execution,
and web searches. Their success on benchmarks like SWE-bench has driven rapid
adoption by major companies and model providers.

### Context Files

As agents were adopted more broadly, practitioners began creating context files
to help agents navigate unfamiliar codebases. These files typically contain
repository overviews, tooling information, style guides, and patterns. Major
providers including Anthropic, OpenAI, and others now recommend this practice.

### Prior Evaluation Work

Previous research collected and categorized context file content but focused on
descriptive metrics rather than effectiveness. Individual developers reported
anecdotal improvements, but "we are the first to investigate the impact of
actively used context files on agent behavior and performance at scale."

### Repository-Level Evaluation

Following SWE-bench's introduction, evaluating agents on real-world repository
tasks became standard practice. Research has expanded to feature addition, test
generation, and security. This work extends that tradition by examining context
files' role in task resolution.

---

## 3 AGENTbench

### 3.1 Notation and Definitions

- **Repository (R)**: A codebase that can have patches applied
- **Test suite (T)**: Collection of tests executed on a repository
- **Issue (I)**: A task for the coding agent
- **Instance**: A tuple (I, R, T, X*) where X* is the golden patch
- **Success rate**: Percentage of predicted patches where all tests pass

### 3.2 Generation of AGENTbench Instances

#### Repository Selection

The authors needed repositories with:
- Developer-written context files (AGENTS.md, CLAUDE.md, etc.)
- Python as primary language
- Functional test suites
- At least 400 pull requests

#### Pull Request Filtering

From 5,694 PRs across candidate repositories, instances were filtered to
include:
- PRs referencing issues
- PRs modifying Python files
- Changes introducing deterministic, testable behavior
- Valid execution environments (87% passed validation)

Unlike SWE-bench Lite, the authors didn't require PRs to contain unit tests,
accommodating niche repositories with less formal practices.

#### Task Description Generation

Many small repositories have imprecise issue descriptions. An LLM agent produced
standardized task descriptions with six sections: description, reproduction
steps, expected behavior, observed behavior, specification, and additional
information. Manual review of 10% confirmed no solution leakage.

#### Unit Test Generation

Since most PRs lacked modifiable unit tests, an LLM generated tests from:
- Standardized task descriptions
- Original code changes
- Base repository state
- Existing test patterns

Tests were validated to fail on base state and pass on patched code, achieving
75% average coverage of modified code.

#### Overview of AGENTbench

The final benchmark comprises:
- **138 instances** from **12 repositories**
- Average **415.3 words** in PR bodies
- Codebases ranging from **151 to 26,602 files**
- Context files averaging **641 words** across **9.7 sections**

---

## 4 Experimental Evaluation

### 4.1 Experimental Setup

#### Coding Agents Tested

Four agent-model combinations:
- Claude Code with Sonnet-4.5
- Codex with GPT-5.2 and GPT-5.1 mini
- Qwen Code with Qwen3-30b-coder

#### Datasets

- **SWE-bench Lite**: 300 tasks from 11 popular Python repositories without
  context files
- **AGENTbench**: 138 tasks from 12 niche repositories with developer-provided
  context files

#### Three Evaluation Settings

1. **None**: No context files
2. **LLM**: Agent-generated context files using recommended procedures
3. **Human**: Developer-provided context files (AGENTbench only)

#### Metrics

Primary: success rate (percentage of instances with passing tests)
Secondary: number of steps to completion and total inference cost

### 4.2 Main Results

#### LLM-Generated Context Files Show Negative Effects

Across eight settings, LLM-generated context files:
- Reduced average resolution rates by 0.5% on SWE-bench Lite
- Reduced average resolution rates by 2% on AGENTbench
- Increased steps by 2.45 and 3.92 on average respectively
- Increased costs by 20% and 23%

#### Developer-Provided Context Files Show Marginal Gains

Human-written context files:
- Outperform LLM-generated versions across all agents
- Improve performance compared to no context (except Claude Code)
- Still increase average steps by 3.34 and costs by up to 19%

#### Context Files Don't Provide Effective Overviews

Measuring steps before agents accessed files modified in original patches:

"Both on SWE-bench Lite and AGENTbench the presence of context files does not
meaningfully reduce this metric." Context files weren't helping agents locate
relevant code faster.

Most generated context files (95-99% depending on model) included codebase
overviews, yet this didn't improve code discovery efficiency.

#### Context Files Are Redundant With Existing Documentation

When documentation files (.md, examples, docs/) were removed, "LLM-generated
context files not only consistently improve performance by 2.7% on average, but
also outperform developer-written documentation."

This suggests generated files redundantly duplicate existing documentation in
well-documented repositories, explaining why they help in poorly-documented
projects.

### 4.3 Trace Analysis

#### Increased Testing and Exploration

Context files significantly increased:
- Test execution frequency
- Repository navigation (grep, file reading/writing)
- Repository-specific tooling usage
- Overall exploration behaviors

#### Instructions Are Followed

Agents respected context file instructions:
- Tools mentioned in context files were used 1.6x more frequently
- Repository-specific tools: 2.5x more when mentioned

This contradicted any hypothesis that poor results stemmed from non-compliance.

#### Following Context Files Requires More Thinking

Context files increased reasoning tokens by:
- 22% for GPT-5.2 on SWE-bench Lite
- 14% for GPT-5.1 mini on SWE-bench Lite
- 14% and 10% on AGENTbench respectively

Context files actually made tasks cognitively harder for agents.

### 4.4 Ablations

#### Stronger Models Don't Generate Better Context Files

Using GPT-5.2 to generate context files for all agents:
- Improved performance 2% on SWE-bench Lite
- Degraded performance 3% on AGENTbench

"Stronger models do not necessarily generate superior context files."

#### No Consistent Prompt Differences

Testing different generation prompts showed:
- No consistent winner across agents and datasets
- Some agents performed better with non-matching prompts
- Sensitivity to prompt choice was generally small

---

## 5 Limitations and Future Work

### Niche Programming Languages

The evaluation focused on Python, a well-represented language in training data.
"Future work may investigate the effect of context files on more niche
programming languages and toolchains that are less represented in the training
data."

### Context Files Beyond Task Resolution

This work evaluated task resolution only. Future research could explore impacts
on code efficiency, security, and other quality metrics.

### Improving Context File Generation

The disparity between human and LLM-generated context files suggests
opportunities for better automatic generation approaches. Techniques in planning
and continuous learning from prior tasks could be applicable.

---

## 6 Conclusion

This comprehensive evaluation of context files across multiple agents reveals a
significant gap between industry recommendations and empirical outcomes. While
developer-written context files provide marginal improvements, LLM-generated
alternatives actually reduce performance while increasing costs substantially.

The research suggests that "context files have only marginal effect on agent
behavior, and are likely only desirable when manually written." Future
development should focus on generating minimal, task-relevant guidance rather
than comprehensive repository documentation.

---

## Relevance to Archeia Evals

This paper is directly relevant to the Archeia evaluation framework. Key
parallels and contrasts:

| Dimension | This paper | Archeia Phase 4 |
|-----------|-----------|-----------------|
| **Conditions** | None / LLM-generated / Human-written | l0 (baseline) / l1 (root + archeia) / l2 (full bundle) |
| **Task types** | Bug-fix PRs (SWE-bench style) | Ask, plan, implement (3 difficulty levels) |
| **Models** | Sonnet 4.5, GPT-5.2, Qwen3 | Haiku |
| **Repos** | 12 niche Python repos | 5 multi-language repos (11k-450k LOC) |
| **Key finding** | LLM docs hurt, human docs marginal | l1 saves tokens, l2 helps simple tasks |

**Shared findings:**
- LLM-generated docs increase token/cost overhead (paper: +20-23%, Archeia l2: variable)
- No statistically significant overall score improvement from docs
- Context files change agent behavior (more exploration) without reliably improving outcomes

**Where Archeia differs:**
- Archeia tests ask/plan tasks where docs show clearer benefit (+2-4%)
- Archeia's l1 condition (root docs only) shows consistent token savings (-14.6% on medium/large repos), suggesting lighter-touch documentation is more effective
- The paper's "redundancy with existing docs" finding aligns with Archeia's observation that arq (well-documented, small) regresses with more docs

**Implications for Archeia:**
- Supports shipping l1 (minimal architecture docs) over l2 (full bundle)
- Suggests focusing on repos with poor existing documentation
- Validates the need to test with stronger models (paper used Sonnet 4.5; Archeia used Haiku)
