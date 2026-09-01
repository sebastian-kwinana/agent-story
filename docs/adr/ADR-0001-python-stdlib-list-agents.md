# ADR-0001: Implement `list-agents` in Python Standard Library, Not Node.js

| Field | Value |
|---|---|
| **ADR Number** | 0001 |
| **Title** | Implement `list-agents` in Python Standard Library, Not Node.js |
| **Status** | Accepted |
| **Date** | 2026-09-01 |
| **Deciders** | Agent Story contributors |
| **Supersedes** | — |
| **Superseded by** | — |
| **Related** | `list_agents.py`, `CONTRIBUTING.md §6`, Issue #2 (Software Architecture for future-proof UI modalities) |

---

## 1. Context and Problem Statement

The `agent-story` project requires a POSIX CLI tool — colloquially `ls-agents` / `list-agents` —
that can discover all installed AI agent harnesses on a developer's machine and report their
installation status and recent session history in a standardised, machine-readable form.

At the time of this decision, the rest of `agent-story` is implemented in Node.js (the
`claude-story` daemon). The question was therefore: **should `list-agents` also be written in
Node.js, or in a different language/runtime?**

The tool's job is specifically to inspect and report on *other software*, including software that
is itself implemented in Node.js (Claude Code, Pi Agent) or that bundles its own Node.js/Bun
runtime. This creates a class of failure modes that must be reasoned about before choosing the
implementation language.

---

## 2. Decision

**`list-agents` is implemented as a single-file Python script using the Python standard library
only (`pathlib`, `sqlite3`, `json`, `shutil`, `argparse`, `dataclasses`, `abc`, `datetime`).**

No third-party pip packages are required to run the tool. The only external dependency is
`coverage`, and only during CI test execution — not at runtime.

---

## 3. Categorised and Enumerated Reasoning

### Category A — Runtime Independence from the Subject Under Inspection

**A1. Circular dependency risk.**
Several target harnesses (Claude Code, Pi Agent, Prime Agent) are themselves Node.js
applications. A Node.js–implemented `list-agents` would depend on the same runtime it is
attempting to diagnose. If a harness ships a broken or incompatible Node.js version, or if
`nvm`/`fnm` selects the wrong version for the shell context, the *diagnostic tool* itself may
fail for the same reason as the *subject being diagnosed* — producing a diagnostic dead-end with
no clear signal.

**A2. Bun compatibility fragmentation.**
An increasing number of Node.js–based agent harnesses ship with or recommend Bun as an
alternative JavaScript runtime. Bun is not binary-compatible with Node.js native addons and
resolves modules differently. A Node.js `list-agents` that is run under Bun (or vice versa) may
silently misbehave or crash, precisely when the developer is trying to understand why their
harness environment is broken.

**A3. Version matrix explosion.**
Node.js harnesses may pin incompatible `engines` ranges. Running `list-agents` in the same Node.js
process space as a harness would require version negotiation that is impossible to guarantee
without a version manager — adding another layer of potential failure to the diagnostic tool.

**A4. Self-contained runtime availability.**
Python ≥ 3.10 ships as the system Python on every current Ubuntu LTS release (22.04+), macOS
(via Xcode CLTs), and is available on Windows. It requires no `nvm`, `n`, `fnm`, `volta`, or
`bun` installation. A developer whose Node.js environment is completely broken can still invoke
`python3 list_agents.py` from a bare shell.

---

### Category B — Separation of Concerns (Instrumentation vs Subject)

**B1. Observer-effect minimisation.**
In systems monitoring and observability engineering, the instrumentation layer should perturb the
subject system as little as possible. Running a Node.js diagnostic tool loads the Node.js event
loop, may trigger `.nvmrc` / `.node-version` lookups, and activates package resolution machinery
— all of which interact with the very environment being inspected. Python's interpreter starts,
reads the filesystem, and exits without touching any Node.js infrastructure.

**B2. Dependency non-overlap.**
Using Python for the diagnostic layer guarantees that its dependencies (zero, at runtime) cannot
conflict with any harness's `node_modules` tree. Adding a new harness adapter requires writing
one Python class; it cannot introduce `npm` dependency conflicts into any target harness.

**B3. Scripting-layer hygiene.**
The Unix philosophy of using different-language scripts at the automation/scripting layer to
instrument and automate a system (e.g., shell scripts instrumenting C programs, Python scripting
Java JVM analysis tools) is a well-established practice precisely to avoid the above conflicts.
`list-agents` is the scripting/automation/instrumentation layer; the harnesses are the subjects.

---

### Category C — Minimal Dependency Surface (Supply-Chain Security)

**C1. Zero runtime dependencies.**
Every third-party package is a potential vector for a software supply-chain attack (typosquatting,
dependency confusion, compromised publisher accounts). A tool with zero runtime dependencies has
the smallest possible attack surface. The stdlib modules used (`pathlib`, `sqlite3`, `json`, etc.)
are part of CPython itself and receive security patches alongside the Python interpreter.

**C2. Hash-pinned test-only dependency.**
The one external package used — `coverage` — is used only during CI test execution, hash-pinned
via `requirements-ci.txt` (`--require-hashes`), and never present in the production runtime path.
This satisfies the same supply-chain security posture that the CI pipeline enforces for GitHub
Actions (SHA-pinned action refs) and Node.js (`npm ci` checksum verification).

**C3. Reproducible installation.**
`python3 list_agents.py` requires no installation step. The tool can be copied to any machine with
Python ≥ 3.10 and run immediately, making it suitable for automated provisioning scripts,
container entrypoints, and emergency triage workflows without a package registry or internet
connection.

---

### Category D — Hexagonal Architecture Fit

**D1. Port-based extensibility without runtime coupling.**
The Hexagonal Architecture adopted for `list-agents` (Ports and Adapters, Strategy Pattern) is
language-agnostic. Implementing it in Python means that future harness adapters — including
harnesses implemented in Rust, Go, or native binaries — can be added as Python classes without
any concern about language runtime conflicts.

**D2. Fission presenter independence.**
The output presenter adapters (plain POSIX text, NDJSON) write to `stdout` using Python's
`print()`. The downstream consumer — whether a shell alias, a terminal, `jq`, a log aggregator,
or a future GUI — is entirely decoupled from the tool's implementation language.

---

### Category E — Shell Integration and OS-Level Aliasing

**E1. Shell alias / function simplicity.**
The tool is designed to be wrapped in a per-shell alias or function (`ls-agents`, `list-agents`).
A Python script invoked via `python3 list_agents.py` can be aliased cleanly in Bash, Zsh, Fish,
and POSIX `sh` without any `node`, `npx`, `bun`, or `deno` prefix — and without a shebang that
depends on a version-manager-managed `node` path.

```bash
# ~/.bashrc / ~/.zshrc
alias ls-agents='python3 /path/to/list_agents.py'

# Or as a shell function with passthrough arguments:
ls-agents() { python3 /path/to/list_agents.py "$@"; }
```

**E2. POSIX single-purpose tool contract.**
The Unix philosophy — "do one thing well, read from stdin/write to stdout, compose with pipes" —
is more naturally expressed through a Python script than through a Node.js CLI that requires an
event loop, a package directory, and potentially a transpilation step. Python's synchronous,
top-to-bottom execution model matches the mental model of a `ls`-style POSIX tool.

---

### Category F — Future-Proofing and Extensibility

**F1. Independence from the ecosystem being catalogued.**
As the number and diversity of agent harnesses grows — and as harnesses increasingly ship with
their own bundled runtimes (e.g., Electron, Bun, Deno, embedded V8) — the only way to maintain
a reliable catalogue tool is to ensure it runs on a completely orthogonal runtime stack. Python's
presence as a system language on virtually every POSIX-compliant OS makes it the natural choice.

**F2. Meta-harness extractor evolution path.**
The long-term vision for `agent-story` is a modular meta-harness extractor: a tool that can
extract conversations, metadata, and git history from any agent harness and transform them into
narratives, task analyses, and `SKILLS.md` artefacts. As this vision is realised, the Python
component will act as the cross-runtime orchestration layer, calling into harness-specific
tools (which may be Node.js, Rust, or Go CLIs) via subprocess — without being subject to their
runtime constraints.

**F3. Resilience to Node.js ecosystem disruptions.**
The Node.js ecosystem has historically experienced breaking changes (CommonJS → ESM, V8 update
incompatibilities, native addon ABI breaks). A Python-based diagnostic tool is completely immune
to these disruptions and can continue to function during periods when the Node.js ecosystem on a
target machine is in a degraded or transitional state.

---

## 4. Consequences

### Positive

- Zero coupling between the diagnostic tool and the environments it diagnoses.
- No npm package management required; the tool is a single file.
- Supply-chain attack surface is minimal (stdlib only at runtime).
- Adapter additions are simple Python classes; no build step required.
- The tool works even when all Node.js harnesses on the machine are broken.
- Shell aliasing is clean and portable across POSIX shells.

### Negative / Trade-offs

- Developers who primarily work in Node.js must read and maintain Python code for the `list-agents` component.
- The project now spans two language runtimes, which marginally increases contributor onboarding surface.
- No shared code reuse between `claude-story` (Node.js) and `list-agents` (Python); any domain types must be independently maintained.

### Mitigations

- The Python component is confined to a single file (`list_agents.py`) with a single test file (`test_list_agents.py`), minimising the learning surface.
- The architecture is documented inline (numbered layers in the source) and in `CONTRIBUTING.md §6`, so the design intent is clear to Node.js–primary contributors.
- As the meta-harness extractor vision matures, the interprocess boundary between Python orchestration and Node.js harness-specific components will be formalised via subprocess/IPC patterns, making the two-language model a feature rather than a liability.

---

## 5. Alternatives Considered

### 5.1 Node.js (Rejected)

As detailed in Category A–C above: circular runtime dependency risk, Bun fragmentation, and
version matrix explosion make Node.js a poor choice for a tool whose primary job is to diagnose
Node.js agent harnesses.

### 5.2 Shell Script (Bash/POSIX sh) (Rejected)

A shell script could implement basic directory and file detection. However:
- SQLite querying (`DeepSeekHarnessAdapter`) requires either an external `sqlite3` binary (not
  always present) or complex `awk`/`sed` parsing of binary data.
- JSON parsing without `jq` (not always installed) is fragile.
- Unit testing shell scripts (mocking filesystem, asserting output) is significantly harder than
  Python's `unittest`/`tempfile` approach.
- The Hexagonal Architecture with typed ports cannot be expressed cleanly in POSIX shell.

### 5.3 Go (single binary) (Deferred)

A compiled Go binary would solve the runtime-independence problem elegantly and produce a single
distributable binary with no interpreter dependency. This is a strong candidate for the "Make it
Ship" stage when `list-agents` reaches v1.0.0 and requires cross-platform binary distribution.
Deferred because:
- Adding a Go toolchain to the CI matrix at the current "Make it Good" stage adds build
  complexity disproportionate to the current scope.
- The Python implementation can be rewritten in Go incrementally, preserving the same
  port/adapter design (the Hexagonal Architecture is language-agnostic).

### 5.4 Rust (single binary) (Deferred — same rationale as Go)

---

## 6. References

- [The Art of Unix Programming — Eric S. Raymond, Chapter 1: Philosophy](http://www.catb.org/esr/writings/taoup/html/ch01s06.html)
- [Hexagonal Architecture — Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [SLSA Supply Chain Levels for Software Artefacts](https://slsa.dev/)
- [pip `--require-hashes` documentation](https://pip.pypa.io/en/stable/topics/secure-installs/)
- `CONTRIBUTING.md §6` — Architecture decisions (this repository)
- Issue #2 — Software Architecture for future-proof UI modalities (this repository)
