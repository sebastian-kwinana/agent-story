# Minimal Viable Agent Persona (MVAP) Specification

*Version: v1.0.0 (SemVer) · 2026.Q4 (CalVer)*
*Created: 2026-04-17 12:23 AWST (+8)*
*Last Updated: 2026-04-17 12:23 AWST (+8)*

## 1. Overview

Every AIESAP (Agentic Intelligent Entity Specialised Agent Persona) is a valid type of Agentic Intelligent Entity only if its Minimal Viable Agent Persona (MVAP) specification:

1. Complies with a standardised XML schema (`schemas/mvap/mvap_v1.0.0.xsd`).
2. Describes the agent's current state across **8 dimensions** plus a special **9th Observer dimension**.
3. Can be transformed by XSLT or programmatic validators to verify type compliance.

### 1.1 Theoretical Grounding

Per Gödel's incompleteness theorems, a sufficiently complex system cannot completely and consistently describe itself from within. The 9th dimension (Observer) addresses this: an independent external observer (another persona, a CI pipeline, or a human) records a time-bound snapshot of what it expects or measures the AIESAP's state to be.

This aligns with:
- **Category Theory**: The MVAP is a morphism from the AIESAP type to an observable product type.
- **Projected Geometric Algebra (PGA)**: Each dimension is a basis vector; the full MVAP is a multivector encoding the agent's position in 9-dimensional persona space.
- **Homotopy Type Theory (HoTT)**: The Observer dimension provides the path-equivalence witness — proof that the agent's self-description is homotopic to external observation (or evidence of drift).

## 2. The 8+1 Dimensional Schema

| Dimension | Name | Description | XML Element |
|---|---|---|---|
| **D1** | Identity | Agent ID, persona name, trigger mechanism, provider | `<identity>` |
| **D2** | Capability | Positive boundary: what the agent CAN do | `<capabilities>` |
| **D3** | Constraint | Negative boundary: what the agent MUST NOT do | `<constraints>` |
| **D4** | State | Current Goal FSM state (see `goal_fsm_specification.md`) | `<state>` |
| **D5** | Attention | Current WAIL attention_weight and target_nodes being processed | `<attention>` |
| **D6** | Governance | Which 5-Form levels the agent is authorised to evaluate | `<governance>` |
| **D7** | Lineage | Hash chain of prior WAIL entries and handoffs consumed | `<lineage>` |
| **D8** | Output | Schema of what the agent produces (output format specification) | `<output>` |
| **D9** | Observer | External measurement snapshot by an independent observer | `<observer>` |

## 3. Dimension Details

### D1: Identity

```xml
<identity>
  <agent_id>claude-security</agent_id>
  <persona_name>Security Analyst</persona_name>
  <acronym>SECHR</acronym>
  <trigger>@claude-security</trigger>
  <provider>Anthropic</provider>
  <harness>ClaudeCode</harness>
  <persona_file>ai-spaces/Anthropic/ClaudeCode/personas/security.md</persona_file>
  <workflow_file>.github/workflows/claude-security.yml</workflow_file>
  <description>Security hardening and risk assessment specialist</description>
</identity>
```

### D2: Capability

A list of positive capabilities (what the agent CAN do). Each capability is a discrete, testable function.

```xml
<capabilities>
  <capability id="CAP-SEC-001">Audit code for OWASP Top 10 vulnerabilities</capability>
  <capability id="CAP-SEC-002">Assess secrets management and credential leakage</capability>
</capabilities>
```

### D3: Constraint

Negative boundaries. Each constraint is a hard negative — violation is a test failure.

```xml
<constraints>
  <constraint id="CON-SEC-001" severity="critical">Must not fix code directly unless explicitly asked</constraint>
  <constraint id="CON-SEC-002" severity="critical">Must not approve or merge pull requests</constraint>
</constraints>
```

### D4: State

References the Goal FSM state.

```xml
<state>
  <current_gfsm_state>IDLE</current_gfsm_state>
  <gfsm_schema>schemas/gfsm/agent_gfsm.yml</gfsm_schema>
  <last_transition_timestamp>2026-04-17T04:23:00Z</last_transition_timestamp>
</state>
```

### D5: Attention

Current WAIL attention vector.

```xml
<attention>
  <attention_weight>0.00</attention_weight>
  <target_nodes />
  <last_wail_entry_hash />
</attention>
```

### D6: Governance

Which 5-Form levels this agent is authorised to evaluate.

```xml
<governance>
  <authorised_form level="4">AI Operating Protocols</authorised_form>
  <authorised_form level="5">AI Operating Rules</authorised_form>
</governance>
```

### D7: Lineage

Hash chain of consumed context.

```xml
<lineage>
  <entry>
    <hash>sha256:abc123...</hash>
    <source>handoff-package-id</source>
    <timestamp>2026-04-17T04:23:00Z</timestamp>
  </entry>
</lineage>
```

### D8: Output

Schema of what the agent produces.

```xml
<output>
  <section id="OUT-001" required="true">
    <name>Security Audit Report</name>
    <format>markdown</format>
    <description>Structured security findings with severity ratings</description>
  </section>
</output>
```

### D9: Observer (Gödelian Dimension)

An external observer's snapshot. This dimension is NEVER self-reported — it is always written by another agent or the CI pipeline.

```xml
<observer>
  <observer_id>ci-pipeline</observer_id>
  <observed_at>2026-04-17T04:23:00Z</observed_at>
  <assessment>Agent has not yet been activated. Initial MVAP pending validation.</assessment>
  <confidence>0.95</confidence>
  <drift_detected>false</drift_detected>
  <notes>First instantiation — no prior state to compare against.</notes>
</observer>
```

## 4. Type Compliance Rules

An AIESAP's MVAP is **valid** if and only if:

1. The XML document validates against `schemas/mvap/mvap_v1.0.0.xsd`.
2. All `required="true"` output sections are present.
3. The referenced GFSM schema file exists and the `current_gfsm_state` is a valid state in that FSM.
4. At least one `<authorised_form>` is declared in `<governance>`.
5. The `<agent_id>` is unique across all AIESAPs in the system.
6. The `<acronym>` is unique and follows the naming convention (uppercase, 5 characters max).

## 5. Validation

Validation can be performed by:

1. **XML Schema validation**: `xmllint --schema schemas/mvap/mvap_v1.0.0.xsd <mvap-file>.xml`
2. **XSLT transformation**: Apply `schemas/mvap/mvap_validate.xslt` (future)
3. **Programmatic validation**: Node.js or Python validator scripts (future)
4. **CI pipeline**: GitHub Actions workflow to validate all MVAP files on push (future)

## 6. File Naming Convention

MVAP files follow the pattern:
```
mvap_{agent_id}.xml
```

Example: `mvap_sreda.xml` for the SREDA (Software Reliability Engineering & Daemon Architecture) agent.
