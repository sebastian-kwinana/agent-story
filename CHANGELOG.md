# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Maintainer note:** Update the `[Unreleased]` section with every pull request.
> When a release is cut, rename `[Unreleased]` to `[x.y.z] — YYYY-MM-DD` and
> add a new empty `[Unreleased]` block at the top.

---

## [Unreleased]

### Added

- `list_agents.py` — POSIX CLI tool implementing Hexagonal Architecture (Ports and
  Adapters) to discover installed AI agent harnesses (Claude Code, Pi Agent,
  DeepSeek Harness, Prime Agent) and render results as plain text or NDJSON.
- `test_list_agents.py` — BDD/TDD test suite (40 tests, 87 % branch coverage)
  covering domain entities, the `AgentScanner` aggregator, all four harness
  adapters (filesystem-isolated), both presenter strategies, the CLI entry point,
  and adversarial / SNEng scenarios.
- `.github/workflows/ci.yml` — GitHub Actions CI pipeline:
  - Python matrix (3.10, 3.12): tests + branch coverage gate (≥ 80 %)
  - Node.js matrix (18, 20, 22): `npm ci` integrity check + smoke test
  - SHA-pinned action refs and `permissions: contents: read` for supply-chain hardening
- `requirements-ci.txt` — hash-verified (`--require-hashes`) `coverage 7.6.12`
  covering all platform wheels (Linux x86-64/ARM, macOS, Windows).
- `CONTRIBUTING.md` — onboarding guide covering architecture, testing, commit
  conventions, PR checklist, security policy, and the project maturity ladder.
- `CHANGELOG.md` — this file; Keep-a-Changelog format.

### Changed

- `.gitignore` — expanded from 3 lines to idiomatic coverage for Python
  (`__pycache__/`, `*.pyc`, `.coverage`, `.venv/`), Node.js, OS artefacts,
  editors, logs, and secrets (`.env`, `*.pem`, `*.key`).
- `README.md` — restructured to document both `claude-story` and `list-agents`,
  added a testing section and link to `CONTRIBUTING.md`.

### Fixed

- Removed the accidentally committed binary `__pycache__/list_agents.cpython-312.pyc`
  from the git index (`git rm --cached`). The `.gitignore` now prevents recurrence.

---

## [1.0.1] — prior release

### Changed

- Minor npm publish fixes (see original `package.json` version history).

## [1.0.0] — initial release

### Added

- `claude-story` Node.js daemon: automatic conversation history manager for
  Claude Code, saving all conversations to `.claude-story/` directories as
  SQLite databases and markdown exports.
- `bin/claude-story.js` CLI with `start`, `stop`, `status`, and `help` commands.
- `lib/daemon.js`, `lib/database.js`, `lib/watcher.js` daemon internals.

---

[Unreleased]: https://github.com/sebastian-kwinana/agent-story/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/sebastian-kwinana/agent-story/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/sebastian-kwinana/agent-story/releases/tag/v1.0.0
