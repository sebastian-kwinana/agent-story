# Solutions Negation Engineering (SNEng) Specification

*Version: v1.0.0 (SemVer) · 2026-Q4 (CalVer)*
*Created: 2026-04-17_1431_AWST (+8)*
*Last Updated: 2026-04-17_1431_AWST (+8)*
*Status: Active — Governing all AIESAP PDE work on Agent Story*

---

## 1. Definition

**Solutions Negation Engineering** (`SNEng`) is a systematic discipline that defines, for every
agent, workstream, and work product, the *negative space*: what must NOT be built, what must NOT
be assumed, what is NOT known, and what CANNOT be known — before any positive-scope work begins.

SNEng is not pessimism. It is the engineering equivalent of a sculptor defining the marble that
must be removed before the form can emerge. In agentic AI systems, where autonomous agents can
compound errors at machine speed, the negative boundary is more important than the positive
capability list.

### 1.1 Etymology

| Component | Meaning |
|---|---|
| **Solutions** | The positive-space work products agents produce |
| **Negation** | The deliberate, structured identification of what lies *outside* valid solution space |
| **Engineering** | Rigorous, repeatable, testable — not ad hoc exclusion lists |

### 1.2 Core Axiom

> *An agent that does not know what it does not know is more dangerous than an agent that
> cannot act at all.*

This axiom derives from Gödel's incompleteness theorems (a sufficiently complex system cannot
fully describe itself from within) and is operationalised through the MVAP D9 Observer dimension.

---

## 2. The Four Pillars of SNEng

SNEng structures negation across four orthogonal pillars. Every AIESAP PDE must address all
four before commencing positive-scope work.

### Pillar 1: Anti-Pattern Registry (APR) — *What must NOT be built*

Explicit catalogue of known anti-patterns, premature optimisations, scope-creep vectors, and
architectural dead ends that the agent must actively refuse to pursue.

**Constraint ID prefix**: `SNEG-{AGENT}-APR-`

**Examples**:
- SREDA must NOT recommend Kubernetes orchestration for a local-first desktop daemon
- TQAVF must NOT achieve coverage targets by testing implementation details
- CICDP must NOT configure npm publishing before the package identity mismatch is resolved

### Pillar 2: Epistemic Boundary Declaration (EBD) — *What is NOT known*

Explicit declaration of knowledge gaps, data absences, and uncertainties that constrain the
agent's recommendations. This is the formalisation of intellectual humility.

**Constraint ID prefix**: `SNEG-{AGENT}-EBD-`

**The Three Epistemic Categories**:

| Category | Symbol | Meaning | Agent Action |
|---|---|---|---|
| Known Unknowns | `KU` | "I know that I don't know X" | Declare and escalate |
| Unknown Unknowns | `UU` | "I don't know what I don't know" | Design for discovery |
| Unknowable | `UK` | "X cannot be determined from available data" | Accept and bound |

**Examples**:
- DSTMG `KU`: Does not know conversation volume/cardinality in real user environments
- PRMGR `UU`: Cannot predict community adoption patterns (no user data exists)
- SECHR `UK`: Cannot determine original author's intent for current codebase state

### Pillar 3: Scope Negation Boundary (SNB) — *What the agent WILL NOT do*

Deliberate, affirmative refusal to work on specific tasks that are either out of scope, out of
sequence, or would create harmful coupling. Distinct from "constraints" (things the agent MUST
NOT do) — scope negation is about *choosing* not to act, even when capable.

**Constraint ID prefix**: `SNEG-{AGENT}-SNB-`

**Examples**:
- PRMGR WILL NOT define a Definition-of-Done until Phase 1 audit PDEs have reported
- OSINF WILL NOT design for scale before reliability is established
- TQAVF WILL NOT write tests for aspirational features not yet implemented

### Pillar 4: Learning Loop Integration (LLI) — *How negation feeds forward*

Integration of Eric Schmidt's Learning Loops framework: every piece of negation knowledge
(anti-patterns discovered, unknowns surfaced, scope refused) becomes a signal that feeds
forward into subsequent agents' context, creating an accelerating knowledge compound.

**Constraint ID prefix**: `SNEG-{AGENT}-LLI-`

**The SNEng Learning Loop**:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │  Agent    │───▶│  Work    │───▶│ Negation │     │
│   │  Activates│    │  Product │    │ Artefact │     │
│   └──────────┘    └──────────┘    └────┬─────┘     │
│                                        │            │
│                                        ▼            │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │  Improved│◀───│  Updated │◀───│ Feed into│     │
│   │  Persona │    │  Handoff │    │ Next Agent│     │
│   └──────────┘    └──────────┘    └──────────┘     │
│                                                     │
│   Speed of this loop = competitive moat             │
│   (Eric Schmidt / Moonshots Podcast principle)      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 3. SNEng × Eric Schmidt's Learning Loops

### 3.1 Theoretical Alignment

Eric Schmidt's framework posits that in the AI era, the speed of the learning loop is the only
defensible moat. Sebastian Malcolm's insight extends this: the *granularity* of the loop
matters — micro-scale feedback within and between agents compounds faster than macro-scale
project retrospectives.

SNEng operationalises this for agentic AI systems:

| Schmidt Principle | SNEng Operationalisation |
|---|---|
| "Capture fresh data" | Each agent's negation artefacts (APR, EBD, SNB) ARE fresh data |
| "Feed it back into the model" | Negation artefacts update MVAP lineage (D7) and next agent's handoff context |
| "Deploy improved version" | Updated MVAP = improved agent persona = faster next iteration |
| "Fastest learner wins" | Agents that surface unknowns fastest create the tightest feedback loops |

### 3.2 Professional Assessment of Applicability

**Agreement** — Schmidt's Learning Loops are directly and powerfully applicable to this project:

1. **Agent Story IS a learning loop system**. The daemon captures conversation data → processes
   it → stores structured output → enables search/retrieval. The product itself is a learning
   loop for human-AI interaction history.

2. **The AIESAP PDE system IS a learning loop**. Phase 1 agents audit → findings feed Phase 2
   agents → Phase 3 agents synthesise. Each phase learns from the previous. SNEng ensures
   negative findings (what's broken, what's unknown) are captured with equal fidelity to
   positive findings.

3. **The compound effect is real**. An agent that discovers an anti-pattern (e.g., SREDA finds
   `fs.watch()` is unreliable on NFS) and feeds that into TQAVF's context means TQAVF
   immediately writes tests for that edge case — rather than discovering it independently
   three iterations later.

**Pushback** — Two areas where uncritical application would harm this project:

1. **"Context velocity" must be bounded by coherence**. Schmidt optimises for speed of data
   flowing back into model weights. For agentic AI agents operating on a codebase, unbounded
   context velocity creates *context pollution* — agents drowning in findings from other agents,
   losing focus on their own domain. SNEng's Scope Negation Boundary (Pillar 3) is the
   necessary counterweight: agents must refuse context that is out of their scope, even if
   it's "fresh data."

2. **"Recursive self-improvement" requires guardrails**. Schmidt's vision of AI systems capable
   of self-improvement is aspirational but, applied naively to code-modifying agents, creates
   a risk of *coherence drift* — agents modifying their own constraints to remove inconvenient
   boundaries. The MVAP D9 Observer dimension exists precisely to detect this drift. An agent's
   SNEng constraints must be externally auditable, not self-modifiable.

### 3.3 The Micro Learning Loop — Sebastian Malcolm's Extension

The distinction between Schmidt's macro "learning loop" and Malcolm's "micro learning loop"
is valuable and should be formalised:

| Scale | Loop | Cycle Time | Example in Agent Story |
|---|---|---|---|
| **Macro** | Project-level | Days–Weeks | Full PDE audit cycle → updated roadmap |
| **Meso** | Phase-level | Hours–Days | Phase 1 findings → Phase 2 context injection |
| **Micro** | Agent-level | Minutes–Hours | Single agent discovering an unknown → declaring it in EBD → feeding it into handoff |

SNEng operates primarily at the **micro** and **meso** scales, which is where compound
advantage accrues fastest.

---

## 4. SNEng Constraint Taxonomy

All SNEng constraints in MVAP XML files follow this naming convention:

```
SNEG-{AGENT_ACRONYM}-{PILLAR}-{SEQUENCE}
```

| Component | Values | Example |
|---|---|---|
| `SNEG` | Fixed prefix — identifies Solutions Negation Engineering constraints | `SNEG` |
| `{AGENT_ACRONYM}` | Agent's 5-char acronym | `SREDA`, `TQAVF`, `CICDP` |
| `{PILLAR}` | `APR` (Anti-Pattern), `EBD` (Epistemic Boundary), `SNB` (Scope Negation), `LLI` (Learning Loop) | `APR` |
| `{SEQUENCE}` | 3-digit zero-padded sequence | `001`, `002` |

**Full example**: `SNEG-SREDA-APR-001` — SREDA's first anti-pattern constraint.

**Severity mapping**:

| Severity | Meaning in SNEng Context |
|---|---|
| `critical` | Violation would cause the agent to work on fundamentally wrong things |
| `high` | Violation would waste significant effort or create harmful coupling |
| `medium` | Violation would reduce output quality or create rework |
| `low` | Violation would create minor inefficiency |

---

## 5. Project Motto Assessment

### The Proposed Motto

> *"Keep learning, stay coherent, and Be Excellent To One Another!"*

### Professional Pushback

**What works well**:
- "Keep learning" directly embodies Schmidt's Learning Loops and SNEng Pillar 4 (LLI)
- "Stay coherent" maps to the Gödelian Observer concept (D9) and drift detection
- The inclusive, collaborative tone sets the right cultural foundation for a multi-agent system

**What needs refinement**:
- The motto is three imperatives joined by "and" — rhetorically, this dilutes impact
- "Be Excellent To One Another" (Bill & Ted, 1989) is warmly humanistic but may undercut
  the professional gravitas expected of "foundational software infrastructure that will
  profoundly enable the sustainable success of other projects"
- The motto contains no negation — for a project built on SNEng, the motto should acknowledge
  the discipline of knowing what NOT to do

### Recommendation

**Use the motto for the whole Agent Story project**, not for SNEng specifically. The Bill &
Ted reference signals that this is a project with personality, and the "Be Excellent To One
Another" ethos is genuinely valuable for multi-agent collaboration culture — agents that
"compete" rather than "cooperate" produce worse outcomes.

**For SNEng specifically**, consider a complementary sub-motto that captures the negation
discipline:

> *"Know what you don't know. Refuse what you shouldn't do. Feed it forward."*

**Paired together**:
- **Agent Story**: *"Keep learning, stay coherent, and Be Excellent To One Another!"*
- **SNEng**: *"Know what you don't know. Refuse what you shouldn't do. Feed it forward."*

---

## 6. Application to AIESAP MVAP Files

Every AIESAP MVAP XML file in this project must include SNEng constraints across all four
pillars. These constraints are added to the existing `<constraints>` dimension (D3) using the
`SNEG-` prefix convention.

The minimum SNEng constraint set per agent is:

| Pillar | Minimum Count | Rationale |
|---|---|---|
| APR (Anti-Pattern) | 2 | At least 2 known things the agent must refuse to build |
| EBD (Epistemic Boundary) | 2 | At least 2 declared knowledge gaps |
| SNB (Scope Negation) | 1 | At least 1 deliberate scope refusal |
| LLI (Learning Loop) | 1 | At least 1 commitment to feed negation forward |

Additionally, each agent's `<lineage>` dimension (D7) must include a reference to this
SNEng specification as consumed context, ensuring traceability.

---

## 7. Relationship to MVAP Dimensions

| MVAP Dimension | SNEng Pillar | Relationship |
|---|---|---|
| D2 (Capabilities) | APR | Capabilities are the positive space; APR defines the negative complement |
| D3 (Constraints) | APR, EBD, SNB, LLI | SNEng constraints are encoded directly in D3 |
| D5 (Attention) | SNB | Scope negation limits where attention may be directed |
| D7 (Lineage) | LLI | Learning loop outputs are recorded as lineage entries |
| D8 (Output) | EBD | Outputs should include "Unknowns Registry" sections |
| D9 (Observer) | All | Observer validates that SNEng constraints are being honoured |

---

## 8. Governance

This specification is governed at Level 4 (AI Operating Protocols) of the 5-Form governance
framework. Changes to this specification require:

1. A pull request with rationale
2. Review by at least one human (HOTL principle)
3. Updated MVAP files for all affected agents
4. Updated handoff context packages

---

*"Know what you don't know. Refuse what you shouldn't do. Feed it forward."*
