# Contributing to Agent Story

Thank you for taking the time to contribute. This document is the single source of truth for the development workflow — it is written for both **new contributors** (interns / juniors) and **senior engineers** looking to understand the project's conventions and maturity level.

---

## Table of Contents

1. [Project overview](#1-project-overview)
2. [Repository layout](#2-repository-layout)
3. [Development environment setup](#3-development-environment-setup)
4. [Running the tests](#4-running-the-tests)
5. [Code style and linting](#5-code-style-and-linting)
6. [Architecture decisions](#6-architecture-decisions)
7. [Branching and commit conventions](#7-branching-and-commit-conventions)
8. [Pull request checklist](#8-pull-request-checklist)
9. [Security policy](#9-security-policy)
10. [Maturity ladder and roadmap](#10-maturity-ladder-and-roadmap)

---

## 1. Project overview

Agent Story is a toolkit for the AI agent developer ecosystem:

| Component | Language | Entry point |
|---|---|---|
| `claude-story` daemon | Node.js ≥ 16 | `bin/claude-story.js` |
| `list-agents` CLI | Python ≥ 3.10 | `list_agents.py` |

`list-agents` applies **Hexagonal Architecture** (Ports and Adapters) so that new AI harnesses can be supported by writing a single adapter class, leaving the domain core untouched.

---

## 2. Repository layout

```
agent-story/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── bin/
│   └── claude-story.js         # Node.js CLI entry point
├── docs/
│   ├── adr/                    # Architecture Decision Records
│   │   └── ADR-0001-*.md       # Python stdlib choice for list-agents
│   ├── analysis/               # Engineering analysis documents
│   └── ...                     # Other specs and snapshots
├── lib/                        # Node.js daemon modules
├── schemas/                    # XML schemas (mvap)
├── list_agents.py              # Python CLI — Hexagonal Architecture
├── test_list_agents.py         # Python BDD/TDD test suite
├── requirements-ci.txt         # Hash-pinned Python CI dependencies
├── pyproject.toml              # PEP 517/518 Python packaging metadata
├── package.json                # Node.js package manifest
├── CHANGELOG.md                # Version history (Keep-a-Changelog format)
├── CONTRIBUTING.md             # This file
└── README.md                   # Project overview and quick start
```

---

## 3. Development environment setup

### Python component

```bash
# Python 3.10 or later required; no virtualenv needed for stdlib-only work
python --version

# Install CI dependencies (hash-verified — see Security section)
pip install --require-hashes -r requirements-ci.txt

# Verify list-agents works
python list_agents.py --list-harnesses
```

### Node.js component

```bash
# Node.js 16+ required
node --version

# Install dependencies (package-lock.json checksums verified by npm ci)
npm ci

# Smoke test
npm test
```

---

## 4. Running the tests

### Python

```bash
# Run all tests
python test_list_agents.py

# Run with branch coverage (CI uses this)
python -m coverage run --branch --source=list_agents test_list_agents.py
python -m coverage report --fail-under=80

# Run a single test class
python -m unittest test_list_agents.TestAgentScanner -v
```

The coverage gate is **80% branch coverage**. Pull requests that reduce coverage below this threshold will be blocked by CI.

### Node.js

```bash
npm test
```

This runs `claude-story status`, which exercises daemon detection and Claude Code discovery.

---

## 5. Code style and linting

### Python

The project does not yet enforce a linter in CI (tracked as a "Make it Good" backlog item — see §10). Until a linter is configured, follow these conventions manually:

- **PEP 8** line length ≤ 100 characters
- **PEP 257** docstrings on all public classes and functions
- **Type annotations** on all function signatures (PEP 484)
- `dataclasses.dataclass(frozen=True)` for all domain value objects
- Never import third-party packages in `list_agents.py` — stdlib only

To run an ad-hoc style check before opening a PR:

```bash
pip install ruff
ruff check list_agents.py test_list_agents.py
```

### Node.js

Follow the existing code style in `lib/` and `bin/`. No linter is enforced at this time.

---

## 6. Architecture decisions

### Architecture Decision Records (ADRs)

Significant architectural decisions are recorded in `docs/adr/` using a lightweight ADR format.
Each ADR is numbered sequentially and answers: context, decision, categorised reasoning,
consequences, and alternatives considered.

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](docs/adr/ADR-0001-python-stdlib-list-agents.md) | Implement `list-agents` in Python Standard Library, Not Node.js | Accepted |

When making a significant architectural decision, create a new ADR file before (or alongside) the
implementation PR.

### `list_agents.py` — Hexagonal Architecture

The module is divided into six layers (numbered in the source file):

| Layer | Responsibility |
|---|---|
| **1 — Domain Core** | `SessionRecord`, `AgentMetadata` — pure immutable value objects, no I/O |
| **2 — Inbound Port** | `HarnessDiscoveryStrategy` ABC — contract every adapter must satisfy |
| **3 — Adapters** | `ClaudeCodeAdapter`, `PiAgentAdapter`, `DeepSeekHarnessAdapter`, `PrimeAgentAdapter` |
| **4 — Aggregator** | `AgentScanner` — orchestrates strategies, never touches I/O directly |
| **5 — Presenter Port** | `PresenterStrategy` ABC — output channel contract |
| **6 — Wiring** | `main()` — the only place that knows about concrete implementations |

**Adding a new harness adapter:**

1. Create a class inheriting `HarnessDiscoveryStrategy` in `list_agents.py`.
2. Implement `harness_id`, `display_name`, and `discover()`.
3. Append an instance to `_DEFAULT_STRATEGIES`.
4. Write at least three tests (not-installed, installed-no-sessions, installed-with-sessions).

The domain core in layers 1–4 must **never** depend on a UI or output format. Presenters in layer 5 must **never** depend on domain internals beyond calling `as_dict()`.

### CI supply-chain hardening

- All GitHub Actions are pinned to full commit SHAs, not mutable tags.
- `npm ci` verifies `package-lock.json` checksums.
- `pip install --require-hashes` verifies every Python wheel SHA-256 digest.
- The workflow uses `permissions: contents: read` (least privilege).

---

## 7. Branching and commit conventions

### Branch naming

```
<type>/<short-description>
```

Examples: `feature/prime-agent-adapter`, `fix/pyc-gitignore`, `docs/contributing`

### Commit messages

Follow the **Conventional Commits** format:

```
<type>(<scope>): <short imperative description>

[optional body — explain why, not what]
[optional footer — breaking changes, closes #issue]
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `ci`, `chore`

Examples:
```
feat(list-agents): add Ollama harness adapter
fix(ci): pin actions/setup-python to SHA ref
docs: add CONTRIBUTING.md
test(list-agents): cover PrimeAgent YAML workspace path
```

---

## 8. Pull request checklist

Before requesting review, verify all of the following:

- [ ] `python test_list_agents.py` passes with **zero failures**
- [ ] `python -m coverage report --fail-under=80` passes
- [ ] `npm ci && npm test` passes
- [ ] No `.pyc`, `__pycache__/`, `.env`, or secret files are staged (`git status`)
- [ ] New adapter classes have at least three unit tests
- [ ] Public classes and functions have docstrings
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] PR description references the relevant issue number

---

## 9. Security policy

- **Never commit secrets.** If you accidentally commit a key, rotate it immediately and open an issue.
- **Do not add third-party Python dependencies** to `list_agents.py` without a security review and hash-pinning entry in `requirements-ci.txt`.
- **Do not add npm packages** without running `npm audit` and pinning the version in `package-lock.json`.
- Discovered vulnerabilities: please report privately via the repository's GitHub Security Advisory tab rather than opening a public issue.

---

## 10. Maturity ladder and roadmap

This project self-assesses at **Stage 2 — "Make it Work"**, transitioning toward Stage 3.

| Stage | Description | Status |
|---|---|---|
| ✅ Make it Bootstrap | Repo, tooling, initial scaffold | Complete |
| ✅ Make it Work | Core logic runs, CI passes, tests exist | Complete |
| 🔄 Make it Good | Linting enforced in CI, type-checker, `pyproject.toml`, full README | In progress |
| ⬜ Make it Great | Packaging, versioning, changelog automation, integration tests | Backlog |
| ⬜ Make it Count | Observability, performance profiling, security audit | Backlog |
| ⬜ Make it Ship | Release automation, signed artefacts, PyPI/npm publish | Backlog |

### Known "Make it Good" backlog items

- [ ] Add `ruff` (or `flake8`) lint step to `ci.yml`
- [ ] Add `mypy --strict` type-check step to `ci.yml`
- [ ] Add `pyproject.toml` with PEP 517 metadata
- [ ] Enforce `CHANGELOG.md` update in PR template
- [ ] Add a PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
