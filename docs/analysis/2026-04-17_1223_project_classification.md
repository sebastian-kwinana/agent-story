# Project Classification Analysis: agent-story

*Created: 2026-04-17 12:23 AWST (+8)*
*Last Updated: 2026-04-17 12:23 AWST (+8)*
*Analyst: GitHub Copilot Cloud Agent (Anthropic Claude Sonnet 4)*

## Purpose

This document classifies the `agent-story` project across 8 orthogonal classifier dimensions to inform the selection of Problem Domain Expert (PDE) AIESAPs. Each classifier identifies a facet of the project that demands specialist analysis for the project to achieve its Definition-of-Done as reliable, robust, 24×7 foundational software infrastructure.

---

## Classifier 1: Technical Domain (TD)

| Attribute | Value |
|---|---|
| **Classification** | Developer Tooling — AI Conversation Lifecycle Management |
| **Rationale** | The project is a CLI daemon (`claude-story`) that monitors, captures, persists, and exports Claude Code AI conversations. It operates in the developer-tooling ecosystem, augmenting the Claude Code IDE experience with conversation history. |
| **PDE Implication** | Requires expertise in CLI/daemon design patterns, developer experience (DX), and AI-tooling ecosystems. |

## Classifier 2: Architectural Pattern (AP)

| Attribute | Value |
|---|---|
| **Classification** | Background Daemon + File System Watcher + ETL Pipeline |
| **Rationale** | The system is a long-running Node.js daemon that uses `fs.watch()` to monitor `~/.claude/projects/` for JSONL files, transforms them into structured SQLite records, and loads/exports them as Markdown. This is a classic Extract-Transform-Load pattern wrapped in a daemon lifecycle. |
| **PDE Implication** | Requires expertise in daemon reliability, process supervision, file system event handling edge cases, and data pipeline robustness. |

## Classifier 3: Lifecycle Stage (LS)

| Attribute | Value |
|---|---|
| **Classification** | Early Prototype / Pre-Alpha (v1.0.1 label notwithstanding) |
| **Rationale** | Despite the v1.0.1 version, the project has: zero automated tests, zero CI/CD workflows, zero GitHub Issues, zero Releases, zero Wiki pages, no LICENSE file (referenced in package.json `files` but absent), a repository URL mismatch (`ryanriggin/claude-story` in package.json vs `sebastian-kwinana/agent-story` actual), and no branch protection. All branches point to the same commit SHA. |
| **PDE Implication** | Requires expertise in software maturity assessment, quality gates, and staged release engineering. |

## Classifier 4: Operational Mode (OM)

| Attribute | Value |
|---|---|
| **Classification** | Long-Running Service / 24×7 Infrastructure Daemon |
| **Rationale** | The user's stated goal is for this to "run 24×7 as foundational software infrastructure." Currently, the daemon uses a PID file for lifecycle management, `setInterval` keepalive, `SIGTERM` handling, and detached child process spawning. However, it lacks health checks, watchdog timers, crash recovery, log rotation, and systemd/launchd integration. |
| **PDE Implication** | Requires expertise in service reliability engineering, process supervision, observability, and operational runbooks. |

## Classifier 5: Data Management (DM)

| Attribute | Value |
|---|---|
| **Classification** | Local-First Embedded Database (SQLite) + File-Based Export |
| **Rationale** | Data flows: JSONL → in-memory parse → SQLite (conversations + messages tables) → Markdown export. The database is per-project (`.claude-story/conversations.db`). There is no backup strategy, no migration framework, no data integrity validation, and no WAL mode configuration for concurrent access safety. |
| **PDE Implication** | Requires expertise in embedded database management, data durability, schema migration, and backup/restore strategies. |

## Classifier 6: Integration Surface (IS)

| Attribute | Value |
|---|---|
| **Classification** | File System I/O + npm Ecosystem + MCP Protocol (Aspirational) |
| **Rationale** | Current integrations: Node.js `fs` module for file watching, `sqlite3` native addon for database, `uuid` for ID generation. The README mentions MCP server compatibility but no MCP integration exists. The npm package declares global installation via `preferGlobal: true`. |
| **PDE Implication** | Requires expertise in Node.js native addon reliability, npm package distribution, and MCP protocol design. |

## Classifier 7: Governance Maturity (GM)

| Attribute | Value |
|---|---|
| **Classification** | Ungoverned / No Quality Gates |
| **Rationale** | The project has: no test suite (`"test": "node ./bin/claude-story.js status"` is a smoke check, not a test), no linter configuration, no CI/CD pipeline (only the dynamic Copilot agent workflow), no code review process, no branch protection rules, no CODEOWNERS file, no security policy, no contribution guidelines beyond a template in the README. |
| **PDE Implication** | Requires expertise in software governance, CI/CD pipeline design, quality gate definition, and developer workflow automation. |

## Classifier 8: Ecosystem Role (ER)

| Attribute | Value |
|---|---|
| **Classification** | Foundational Developer Infrastructure / Enabling Platform |
| **Rationale** | The user explicitly states this project should become "foundational software infrastructure that will profoundly enable the sustainable success of other projects." This positions it as a platform-level dependency — other projects' workflows will depend on its reliable operation. This dramatically raises the bar for reliability, backward compatibility, and API stability. |
| **PDE Implication** | Requires expertise in platform engineering, API contract design, semantic versioning discipline, backward compatibility strategy, and ecosystem stewardship. |

---

## Classification Summary Matrix

| # | Classifier | Code | Classification | Risk Level |
|---|---|---|---|---|
| 1 | Technical Domain | TD | Developer Tooling — AI Conversation Management | Medium |
| 2 | Architectural Pattern | AP | Background Daemon + FS Watcher + ETL Pipeline | High |
| 3 | Lifecycle Stage | LS | Early Prototype / Pre-Alpha | Critical |
| 4 | Operational Mode | OM | Long-Running 24×7 Infrastructure Daemon | Critical |
| 5 | Data Management | DM | Local-First SQLite + File Export | High |
| 6 | Integration Surface | IS | File System I/O + npm + MCP (Aspirational) | Medium |
| 7 | Governance Maturity | GM | Ungoverned / No Quality Gates | Critical |
| 8 | Ecosystem Role | ER | Foundational Enabling Platform | High |

## PDE Selection Rationale

The 3 classifiers rated **Critical** (LS, OM, GM) and the 3 rated **High** (AP, DM, ER) demand specialist attention. Combined with the 2 **Medium** classifiers (TD, IS), this justifies selecting **7** Problem Domain Expert AIESAPs (an odd number) to ensure decisive majority voting on cross-cutting concerns.

See: `docs/aiesap/2026-04-17_1223_pde_selection.md` for the selected 7 AIESAPs.
