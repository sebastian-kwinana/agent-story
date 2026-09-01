# Test Strategy Analysis: Agent Harness Fixture Snapshots vs Live-Install CI

*Document type: Engineering Analysis*  
*Created: 2026-09-01*  
*Status: Accepted — recommendation adopted*  
*Author: GitHub Copilot Cloud Agent*  
*Relates to: `list_agents.py`, Issue #2, ADR-0001*

---

## 1. Problem Statement

The current test suite for `list_agents.py` uses **filesystem-isolated unit tests**: temporary
directories constructed at test time to simulate the on-disk layout of each harness
(`~/.claude/`, `~/.dsh/`, `~/.pi/`, `~/.prime/`). This provides 87% branch coverage of the
adapter, domain, and presenter layers.

Two more sophisticated testing strategies have been proposed for future work:

**Strategy A — Live Install CI Matrix:**
Idempotently install real harness software (at pinned versions) on ephemeral Ubuntu runners and
run `list_agents.py` against the actual installed state.

**Strategy B — Snapshot Fixtures:**
Capture the complete on-disk state of a harness in known, named configurations (e.g. "Claude
Code: freshly installed, zero conversations"; "Claude Code: one conversation, no sub-agents";
"Claude Code: multiple conversations with dynamic worker fleets") and commit these as versioned
test fixtures.

This document analyses both strategies, identifies their trade-offs, and delivers a prioritised
recommendation.

---

## 2. Current Test Tier (Baseline)

| Property | Current state |
|---|---|
| Approach | Filesystem-isolated unit tests with `tempfile.TemporaryDirectory` |
| Coverage | 87% branch coverage of `list_agents.py` |
| Harness coupling | Zero — no real harness software required |
| CI runtime | < 5 seconds |
| Failure modes covered | Absent harness, present but empty, SQLite schema, corrupt files, broken adapters |
| Failure modes NOT covered | Real harness data format drift, undocumented config changes, multi-harness coexistence |

The current tier is sufficient for **Stage 2 "Make it Work"** and the transition into **Stage 3
"Make it Good"**. It proves the adapter contracts and domain logic are correct against the
*modelled* filesystem layout of each harness.

---

## 3. Strategy A — Live Install CI Matrix

### 3.1 Description

Add one or more CI jobs per harness that:

1. Install the harness at a pinned version (`npm install -g claude@<version>`, etc.)
2. Optionally run a harness-specific setup script to generate known session state
3. Execute `python3 list_agents.py` and assert on the output

### 3.2 Advantages

| # | Advantage |
|---|---|
| A1 | **Format fidelity** — discovers real config/session file format changes that fixture snapshots miss until manually refreshed |
| A2 | **Regression detection** — catches breaking changes when a harness releases a new version that moves config files or changes the schema |
| A3 | **Installation verification** — validates that `list_agents.py` correctly resolves the harness binary path, not just a synthetic path |
| A4 | **CI version matrix** — can test multiple harness versions in parallel, providing a compatibility matrix |

### 3.3 Disadvantages

| # | Disadvantage |
|---|---|
| D1 | **Harness install flakiness** — npm global installs, auth flows, and binary relocation steps are notoriously fragile in CI. A harness that requires interactive authentication (e.g. `claude` login) cannot be automated without storing credentials as secrets |
| D2 | **Network dependency** — live installs depend on npm/PyPI/GitHub availability. Network partitions cause false CI failures unrelated to code changes |
| D3 | **Version pinning toil** — each new harness version requires a PR to update the pinned version in CI. Without this, the CI job silently tests an outdated version |
| D4 | **Slow CI** — installing Node.js packages globally takes 30–120 seconds per harness. A matrix of four harnesses × three versions = 12 jobs × ~60 s each = 12 minutes of CI wall time |
| D5 | **State generation complexity** — generating realistic session state (conversations, sub-agents, dynamic worker fleets) requires either running the LLM (costly, requires API keys) or scripting synthetic state files that approximate real harness output |
| D6 | **Secret management** — API keys for Claude, DeepSeek, etc. would need to be stored as repository secrets, expanding the credential surface |

### 3.4 Assessment

Live-install CI is the **correct long-term strategy** for integration/compatibility testing, but it
is **follow-up work** rather than current-scope for the following reasons:

- The current scope of `list_agents.py` is *discovery and listing*, not *session content parsing*.
  The adapter's correctness does not require a real LLM conversation to have occurred.
- The most valuable live-install test (format drift detection) is only triggered when a harness
  changes its on-disk format — a relatively infrequent event that can be detected by a separate
  monitoring job (e.g. a weekly scheduled workflow that runs against the latest harness version
  and fails loudly if output changes).
- The authentication and credential management burden is disproportionate to the value at the
  current maturity stage ("Make it Good").

**Recommended maturity gate for adoption: "Make it Great" (Stage 4)**

---

## 4. Strategy B — Snapshot Fixtures

### 4.1 Description

Capture the complete on-disk state of a harness in a known, named configuration and store it as
a versioned fixture tree in the repository. The test harness restores the fixture into a temporary
directory and runs the adapter against it.

**Named fixture states proposed:**

| Harness | State name | Description |
|---|---|---|
| Claude Code | `cc-fresh` | `~/.claude/` created, `config.json` present, no sessions |
| Claude Code | `cc-one-session` | One session file, no sub-agents |
| Claude Code | `cc-one-session-subagent` | One session, one sub-agent entry in session metadata |
| Claude Code | `cc-multi-dynamic-workers` | Multiple sessions, `dynamicWorkers` array in session JSON |
| DeepSeek Harness | `dsh-fresh` | `~/.dsh/harness.sqlite` with schema only, no rows |
| DeepSeek Harness | `dsh-sessions` | SQLite DB with three session rows |
| Pi Agent | `pi-history` | Three JSONL history files |
| Prime Agent | `prime-yaml-workspaces` | Two YAML workspace files with `description:` fields |

### 4.2 Advantages

| # | Advantage |
|---|---|
| B1 | **Zero network dependency** — fixtures are files in the repository; CI runs offline |
| B2 | **Deterministic** — the same fixture always produces the same adapter output, making assertions exact |
| B3 | **Fast** — loading a fixture tree is sub-millisecond; no install step required |
| B4 | **Named states as specification** — the fixture names are a living specification of which harness states the tool is expected to handle |
| B5 | **No secrets required** — fixture files contain synthetic (or sanitised) session data |
| B6 | **Documents real data formats** — committed fixture files serve as canonical examples of what each harness's on-disk format looks like, invaluable for new contributors writing adapters |

### 4.3 Disadvantages

| # | Disadvantage |
|---|---|
| E1 | **Manual refresh required** — when a harness changes its format, fixtures silently test the *old* format until manually updated |
| E2 | **Synthetic state only** — fixtures cannot represent all real-world edge cases; they are only as good as the engineer who crafted them |
| E3 | **Binary/database fixtures** — SQLite fixture files are binary blobs; diffs in pull requests are unreadable without tooling |
| E4 | **Storage growth** — as the number of harnesses and named states grows, fixture files add to repository size |
| E5 | **Fixture drift risk** — if the fixture authoring process is not documented, contributors may produce fixtures that do not accurately represent real harness output |

### 4.4 Mitigations for disadvantages

| Disadvantage | Mitigation |
|---|---|
| E1 (format drift) | Pair with a weekly scheduled CI job that generates a fresh fixture from the latest harness version and diffs it against the committed fixture (alert-on-change pattern) |
| E3 (SQLite binary diffs) | Store SQLite fixtures as SQL text dumps (`sqlite3 harness.sqlite .dump > harness.sql`) committed as text; the test loader runs `.read harness.sql` to reconstruct the DB |
| E4 (storage growth) | Scope fixtures to the minimum fields needed by each adapter; strip session content to one-line previews |
| E5 (drift risk) | Document the fixture authoring process in `CONTRIBUTING.md`; add a CI check that validates fixture files parse without error |

### 4.5 Assessment

Snapshot fixtures are **in-scope current work** because:

- They can be implemented without any harness software installed in CI.
- They make the *existing* adapter contracts more precise: the current unit tests construct
  synthetic paths; fixtures commit the *actual* file formats as living documentation.
- They directly support the long-term meta-harness extractor vision: a corpus of named fixture
  states is the prerequisite for building and testing session content parsers, narrative
  extractors, and `SKILLS.md` generators.
- The implementation follows the same `tempfile.TemporaryDirectory` pattern already in use —
  only the *source* of the directory tree changes (copied from `tests/fixtures/` rather than
  constructed inline).

**Recommended maturity gate for adoption: "Make it Good" (Stage 3) — next sprint**

---

## 5. Recommended Test Tier Architecture

```
Tier 1 (current, always-on)
  └─ Filesystem-isolated unit tests
     - tempfile-constructed directories
     - covers adapter contracts, domain logic, presenter output
     - 87% branch coverage gate
     - CI runtime: < 5 s

Tier 2 (next sprint — "Make it Good")
  └─ Snapshot fixture integration tests
     - named fixture trees in tests/fixtures/<harness>/<state>/
     - SQL text dumps for SQLite databases
     - adapter run against restored fixture → assert canonical output
     - CI runtime: < 10 s

Tier 3 (Stage 4 — "Make it Great")
  └─ Live-install compatibility matrix
     - scheduled weekly workflow (not on every PR)
     - pinned harness versions, no secrets
     - assert output shape only (not exact content)
     - alert-on-format-drift

Tier 4 (Stage 5 — "Make it Count")
  └─ Real conversation state integration tests
     - sandboxed harness instances with real LLM API calls
     - secrets managed via GitHub Actions OIDC + vault
     - named states: fresh / one-session / sub-agents / dynamic-workers
     - full session content parsing verification
```

---

## 6. Implementation Plan for Tier 2 (Snapshot Fixtures)

### 6.1 Directory structure

```
tests/
└── fixtures/
    ├── README.md                          # Fixture authoring guide
    ├── claude-code/
    │   ├── fresh/                         # ~/.claude/ with config only
    │   │   └── .claude/config.json
    │   ├── one-session/                   # One session JSON
    │   │   └── .claude/sessions/sess-001.json
    │   └── one-session-subagent/          # Session with sub-agent metadata
    │       └── .claude/sessions/sess-002.json
    ├── deepseek-harness/
    │   ├── fresh/
    │   │   └── .dsh/harness.sql           # SQL text dump of empty schema
    │   └── sessions/
    │       └── .dsh/harness.sql           # SQL dump with 3 session rows
    ├── pi-agent/
    │   ├── fresh/
    │   │   └── .pi/settings.json
    │   └── with-history/
    │       ├── .pi/settings.json
    │       └── .pi/history/sess-a.jsonl
    └── prime-agent/
        ├── fresh/
        │   └── .prime/manifest.json
        └── yaml-workspaces/
            ├── .prime/manifest.json
            └── .prime/workspaces/alpha.yaml
```

### 6.2 Test loader pattern

```python
def load_fixture(harness: str, state: str) -> Path:
    """
    Copy a named fixture tree into a temporary directory and return the
    temporary home path. The caller is responsible for cleanup via
    tempfile.TemporaryDirectory context management.
    """
    fixtures_root = Path(__file__).parent / "tests" / "fixtures"
    fixture_src = fixtures_root / harness / state
    tmp = tempfile.mkdtemp()
    shutil.copytree(fixture_src, tmp, dirs_exist_ok=True)
    # Reconstruct any SQLite databases from SQL text dumps
    for sql_file in Path(tmp).rglob("*.sql"):
        db_path = sql_file.with_suffix(".sqlite")
        with sqlite3.connect(db_path) as conn:
            conn.executescript(sql_file.read_text())
        sql_file.unlink()
    return Path(tmp)
```

### 6.3 Acceptance criteria for Tier 2

- [ ] Fixture trees committed for all four harnesses × at least two states each
- [ ] SQL text dumps replace SQLite binary blobs in version control
- [ ] `test_list_agents.py` extended with one fixture-backed test class per harness
- [ ] `tests/fixtures/README.md` documents the fixture authoring process
- [ ] CI runtime remains under 30 seconds total (Tier 1 + Tier 2)
- [ ] Coverage gate remains ≥ 80%

---

## 7. Connection to the Meta-Harness Extractor Vision

The named fixture states proposed in §4.1 are not arbitrary. They map directly to the future
capability requirements of the meta-harness extractor:

| Fixture state | Future capability it enables testing for |
|---|---|
| `cc-fresh` | Zero-state bootstrapping; handles newly installed harness gracefully |
| `cc-one-session` | Basic session extraction and narrative generation |
| `cc-one-session-subagent` | Sub-agent relationship modelling in story graph |
| `cc-multi-dynamic-workers` | Fleet/swarm session topology; `SKILLS.md` pattern extraction |

Investing in Tier 2 fixtures now creates the **test oracle infrastructure** that the story
extraction, metadata enrichment, and skills analysis features will depend on as the project
evolves from "list what's installed" to "extract and analyse what happened".

---

## 8. Summary Recommendation

| Strategy | Scope | Stage gate |
|---|---|---|
| Snapshot fixtures (Tier 2) | **In scope — next sprint** | Stage 3 "Make it Good" |
| Live-install CI matrix (Tier 3) | **Follow-up work** | Stage 4 "Make it Great" |
| Real LLM integration tests (Tier 4) | **Follow-up work** | Stage 5 "Make it Count" |

The fixture-snapshot approach should be adopted immediately because it raises test fidelity,
documents real harness data formats, enables the meta-harness extractor vision, and introduces
zero new CI complexity or credential management burden.
