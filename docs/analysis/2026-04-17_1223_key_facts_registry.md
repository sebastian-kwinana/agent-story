# Key Facts Registry: agent-story

*Created: 2026-04-17 12:23 AWST (+8)*
*Last Updated: 2026-04-17 12:23 AWST (+8)*
*Registry Type: Ternary Logic Isomorphism {TRUE, FALSE, UNCERTAIN}*

---

## Purpose

This registry records key facts about the `agent-story` project using ternary logic classification. Each fact is categorised as TRUE (confirmed), FALSE (confirmed absent/incorrect), or UNCERTAIN (requires investigation or human decision).

---

## TRUE — Confirmed Facts

| ID | Category | Fact | Evidence |
|---|---|---|---|
| KF-T-001 | Architecture | The project is a Node.js background daemon that monitors Claude Code conversations | `lib/daemon.js` — `ClaudeStoryDaemon` class |
| KF-T-002 | Architecture | The daemon uses `fs.watch()` with `{ recursive: true }` for file monitoring | `lib/daemon.js:188` |
| KF-T-003 | Architecture | Data is stored in per-project SQLite databases at `.claude-story/conversations.db` | `lib/database.js:8` |
| KF-T-004 | Architecture | Conversations are exported to Markdown files in `.claude-story/history/` | `lib/database.js:9`, `lib/database.js:184-225` |
| KF-T-005 | Dependencies | Runtime dependencies are `sqlite3` ^5.1.6 and `uuid` ^9.0.0 | `package.json:15-18` |
| KF-T-006 | Dependencies | Project uses ESM modules (`"type": "module"`) | `package.json:6` |
| KF-T-007 | Dependencies | Minimum Node.js version is 16.0.0 | `package.json:20` |
| KF-T-008 | Lifecycle | The project has zero automated tests | `package.json:12` — test script runs `status` command |
| KF-T-009 | Lifecycle | The project has zero GitHub Issues | GitHub API: `totalCount: 0` |
| KF-T-010 | Lifecycle | The project has zero GitHub Releases | GitHub API: empty releases array |
| KF-T-011 | Lifecycle | All branches (main, feature/modular-story-engine, chore/add-CLAUDE.md, copilot/*) point to the same commit SHA | `1bbfbd679e531b0d344e10e3afacd4f3b74106ad` |
| KF-T-012 | Governance | No CI/CD pipeline exists (only the dynamic Copilot agent workflow) | GitHub Actions API |
| KF-T-013 | Governance | No branch protection rules are configured | GitHub Branches API: `protected: false` for all |
| KF-T-014 | Governance | No CODEOWNERS, SECURITY.md, CONTRIBUTING.md, or CODE_OF_CONDUCT.md exist | File system scan |
| KF-T-015 | Identity | The LICENSE file is missing despite being listed in package.json `files` array | `package.json:48` references LICENSE; file absent |
| KF-T-016 | Identity | package.json repo URL points to `ryanriggin/claude-story` but actual repo is `sebastian-kwinana/agent-story` | `package.json:38-39` |
| KF-T-017 | Identity | The npm package name is `claude-story` but the GitHub repo name is `agent-story` | `package.json:2` vs GitHub |
| KF-T-018 | Architecture | The daemon keeps alive via `setInterval(() => {}, 30000)` with no health check logic | `lib/daemon.js:362` |
| KF-T-019 | Architecture | PID file is stored at `~/.claude-story-daemon.pid` | `lib/daemon.js:17` |
| KF-T-020 | Architecture | Log file is stored at `~/.claude-story-daemon.log` with no rotation | `lib/daemon.js:18` |
| KF-T-021 | Architecture | `watcher.js` and `daemon.js` contain significant code duplication | Both implement `processJsonlFile`/`processConversationFile`, `extractAssistantContent`, and file scanning |
| KF-T-022 | Data | SQLite does not enable WAL mode or foreign key enforcement | `lib/database.js` — no `PRAGMA` statements |
| KF-T-023 | Data | Database uses parameterised queries for INSERT/UPDATE (good security practice) | `lib/database.js:72,99,269` |
| KF-T-024 | Versioning | Current version is 1.0.1 which implies production-ready, but the project is pre-alpha | `package.json:3` |

## FALSE — Confirmed Negatives

| ID | Category | Fact | Evidence |
|---|---|---|---|
| KF-F-001 | Testing | The project does NOT have any test framework installed | No test runner in devDependencies |
| KF-F-002 | Testing | The project does NOT have any test files | No `test/`, `__tests__/`, or `*.test.js` files |
| KF-F-003 | CI/CD | The project does NOT have any GitHub Actions CI workflows | Only dynamic Copilot agent workflow |
| KF-F-004 | Linting | The project does NOT have ESLint, Prettier, or any linter configured | No `.eslintrc`, `.prettierrc`, or similar |
| KF-F-005 | Documentation | The project does NOT have a Wiki | GitHub API indicates no wiki |
| KF-F-006 | Documentation | The project does NOT have API documentation beyond the README | Only README.md and INSTALL.md |
| KF-F-007 | Operational | The project does NOT have a Docker configuration | No Dockerfile or docker-compose.yml |
| KF-F-008 | Operational | The project does NOT have systemd/launchd service definitions | No service configuration files |
| KF-F-009 | Operational | The project does NOT have health check endpoints or watchdog integration | No health check logic in daemon |
| KF-F-010 | Data | The project does NOT have a database schema migration framework | Schema is created inline in `createTables()` |
| KF-F-011 | MCP | The project does NOT have any MCP server integration despite README claims | README mentions MCP compatibility but no MCP code exists |
| KF-F-012 | Security | The project does NOT have a SECURITY.md or vulnerability disclosure policy | File absent |
| KF-F-013 | Platform | The project does NOT support Windows | README states "Windows support coming soon" |

## UNCERTAIN — Requires Investigation or Decision

| ID | Category | Question | Assessment | Required Action |
|---|---|---|---|---|
| KF-U-001 | Identity | Should the npm package be renamed from `claude-story` to `agent-story`? | The GitHub repo was renamed but package.json was not updated | Human decision required |
| KF-U-002 | Identity | Is the original author `ryanriggin` still involved? | Package.json references their GitHub but repo is under `sebastian-kwinana` | Human clarification required |
| KF-U-003 | Versioning | Should version be reset to 0.x.x to reflect pre-alpha status? | v1.0.1 is misleading; SemVer convention suggests 0.x.x for pre-release | Human decision required |
| KF-U-004 | Licensing | What MIT LICENSE file content should be generated? | Licence type is declared but file is missing; copyright holder uncertain | Human decision required |
| KF-U-005 | Architecture | Should `watcher.js` be removed in favour of `daemon.js`? | Significant code duplication exists; unclear if watcher.js is used elsewhere | Code analysis required |
| KF-U-006 | Platform | What is the priority for Windows support? | README promises "coming soon" but no implementation exists | Human decision required |
| KF-U-007 | Data | Should conversation data be encrypted at rest? | Currently plaintext SQLite; conversations may contain sensitive code | Security review required |
| KF-U-008 | Ecosystem | Should MCP server integration be a roadmap priority? | README advertises MCP compatibility but no implementation exists | Product decision required |
| KF-U-009 | Naming | Is the `cs` alias appropriate? (may conflict with C# compiler on some systems) | `bin` declares both `claude-story` and `cs` | Collision analysis required |
| KF-U-010 | Governance | Who has admin access to the GitHub repository? | Cannot determine from available API data | Human verification required |
| KF-U-011 | Deployment | Should the daemon be managed by process supervisors or be self-managing? | Currently self-managing with PID file; alternatives include systemd, PM2 | Architecture decision required |
| KF-U-012 | Community | Is this project intended for public open-source contribution? | MIT licence suggests yes, but no contribution infrastructure exists | Human decision required |

---

## Registry Metadata

| Attribute | Value |
|---|---|
| Total Facts | 49 |
| TRUE | 24 |
| FALSE | 13 |
| UNCERTAIN | 12 |
| Coverage | All 8 project classifiers represented |
| Next Review | Upon completion of Phase 1 AIESAP audits |
