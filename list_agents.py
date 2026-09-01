#!/usr/bin/env python3
"""
list-agents: A modality-resilient POSIX CLI to inspect local AI agent harnesses.

Architectural patterns applied:
  - Hexagonal Architecture (Ports and Adapters): core domain is isolated from
    filesystem, database, and format specifics via typed port interfaces.
  - Strategy / Plugin Pattern: each harness implementation is a self-contained
    discovery strategy registered at runtime.
  - Presentation Fission: output is rendered through interchangeable presenter
    adapters (plain POSIX text, NDJSON stream) without coupling to domain logic.

Usage:
  python list_agents.py [--format text|json] [--harness <id>] [--verbose]
  python list_agents.py --list-harnesses
"""

from __future__ import annotations

import abc
import argparse
import dataclasses
import datetime
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Generator, List, Optional


# =====================================================================
# 1. DOMAIN CORE — Entities & Invariant Definitions
#    These are pure value objects with no I/O dependencies.
# =====================================================================


@dataclasses.dataclass(frozen=True)
class SessionRecord:
    """A single conversation or working session discovered for a harness."""

    session_id: str
    project_path: Optional[str]
    last_active: datetime.datetime
    preview: str

    def as_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "project_path": self.project_path,
            "last_active": self.last_active.isoformat(),
            "preview": self.preview,
        }


@dataclasses.dataclass(frozen=True)
class AgentMetadata:
    """Canonical, modality-neutral representation of an installed AI agent harness."""

    harness_name: str
    harness_id: str
    binary_path: Optional[str]
    is_installed: bool
    config_location: Optional[str]
    capabilities: List[str]
    recent_sessions: List[SessionRecord]

    def as_dict(self) -> dict:
        return {
            "harness_name": self.harness_name,
            "harness_id": self.harness_id,
            "binary_path": self.binary_path,
            "is_installed": self.is_installed,
            "config_location": self.config_location,
            "capabilities": list(self.capabilities),
            "recent_sessions": [s.as_dict() for s in self.recent_sessions],
        }


# =====================================================================
# 2. INBOUND PORT — HarnessDiscoveryStrategy (Sensor Interface)
#    Defines the contract each vendor adapter must satisfy.
# =====================================================================


class HarnessDiscoveryStrategy(abc.ABC):
    """Port interface for resolving vendor-specific harness state from the environment."""

    @property
    @abc.abstractmethod
    def harness_id(self) -> str:
        """Stable, machine-readable identifier (e.g. 'claude-code')."""

    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        """Human-readable harness name."""

    @abc.abstractmethod
    def discover(self) -> Optional[AgentMetadata]:
        """
        Inspect disk/databases and construct a canonical AgentMetadata entity.

        Returns None when the harness is definitively not present on this machine.
        """


# =====================================================================
# 3. HARNESS ADAPTERS — Strategies for Varied Storage Formats
#    Each adapter knows one harness's filesystem/DB layout.
# =====================================================================


def _recent_mtime_sessions(
    glob_path: Path,
    pattern: str,
    *,
    harness_name: str,
    preview_fn=None,
    project_fn=None,
    limit: int = 3,
) -> List[SessionRecord]:
    """Shared helper: glob files, sort by mtime desc, build SessionRecords."""
    sessions: List[SessionRecord] = []
    try:
        files = sorted(glob_path.glob(pattern), key=lambda f: f.stat().st_mtime, reverse=True)
        for f in files[:limit]:
            mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime, tz=datetime.timezone.utc)
            preview = preview_fn(f) if preview_fn else f"{harness_name} session"
            project = project_fn(f) if project_fn else None
            sessions.append(
                SessionRecord(
                    session_id=f.stem,
                    project_path=project,
                    last_active=mtime,
                    preview=preview,
                )
            )
    except Exception:  # noqa: BLE001 — silently degrade on permission errors etc.
        pass
    return sessions


class ClaudeCodeAdapter(HarnessDiscoveryStrategy):
    """
    Adapter for Anthropic Claude Code.

    Inspects ~/.claude/ for config.json, sessions/*.json and legacy JSONL
    conversation files under ~/.claude/projects/.
    """

    @property
    def harness_id(self) -> str:
        return "claude-code"

    @property
    def display_name(self) -> str:
        return "Claude Code"

    def discover(self) -> Optional[AgentMetadata]:
        home = Path.home()
        claude_dir = home / ".claude"
        config_file = claude_dir / "config.json"
        binary = shutil.which("claude") or str(home / ".local" / "bin" / "claude")
        binary_exists = shutil.which("claude") is not None or (home / ".local" / "bin" / "claude").exists()

        is_installed = claude_dir.exists() or binary_exists
        if not is_installed:
            return None

        # --- session discovery: prefer sessions/*.json, fall back to projects/*.jsonl ---
        sessions: List[SessionRecord] = []
        sessions_dir = claude_dir / "sessions"
        if sessions_dir.is_dir():
            def _preview(f: Path) -> str:
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    return data.get("summary") or data.get("title") or "Conversation active"
                except Exception:
                    return "Conversation active"

            def _project(f: Path) -> Optional[str]:
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    return data.get("cwd")
                except Exception:
                    return None

            sessions = _recent_mtime_sessions(
                sessions_dir, "*.json",
                harness_name=self.display_name,
                preview_fn=_preview,
                project_fn=_project,
            )

        if not sessions:
            # Legacy: ~/.claude/projects/<hash>/*.jsonl
            projects_dir = claude_dir / "projects"
            if projects_dir.is_dir():
                sessions = _recent_mtime_sessions(
                    projects_dir, "**/*.jsonl",
                    harness_name=self.display_name,
                )

        return AgentMetadata(
            harness_name=self.display_name,
            harness_id=self.harness_id,
            binary_path=binary if binary_exists else None,
            is_installed=is_installed,
            config_location=str(config_file) if config_file.exists() else None,
            capabilities=["code-edit", "terminal-exec", "mcp-client", "agentic-loop"],
            recent_sessions=sessions,
        )


class PiAgentAdapter(HarnessDiscoveryStrategy):
    """
    Adapter for Pi Agent (open-source, minimal agentic loop).

    Inspects ~/.pi/ for settings.json/models.json and history/*.jsonl.
    """

    @property
    def harness_id(self) -> str:
        return "pi-agent"

    @property
    def display_name(self) -> str:
        return "Pi Agent"

    def discover(self) -> Optional[AgentMetadata]:
        pi_dir = Path.home() / ".pi"
        if not pi_dir.exists():
            return None

        settings_file = pi_dir / "settings.json"
        models_file = pi_dir / "agent" / "models.json"
        config_loc = (
            str(settings_file) if settings_file.exists()
            else str(models_file) if models_file.exists()
            else str(pi_dir)
        )

        sessions = _recent_mtime_sessions(
            pi_dir / "history", "*.jsonl",
            harness_name=self.display_name,
        )

        return AgentMetadata(
            harness_name=self.display_name,
            harness_id=self.harness_id,
            binary_path=shutil.which("pi"),
            is_installed=True,
            config_location=config_loc,
            capabilities=["swappable-models", "npm-extensions", "minimal-loop"],
            recent_sessions=sessions,
        )


class DeepSeekHarnessAdapter(HarnessDiscoveryStrategy):
    """
    Adapter for DeepSeek Harness (dsh).

    Reads ~/.dsh/harness.sqlite for session metadata when available,
    with graceful fallback to filesystem JSONL logs.
    """

    @property
    def harness_id(self) -> str:
        return "deepseek-harness"

    @property
    def display_name(self) -> str:
        return "DeepSeek Harness"

    def discover(self) -> Optional[AgentMetadata]:
        dsh_dir = Path.home() / ".dsh"
        if not dsh_dir.exists():
            return None

        db_path = dsh_dir / "harness.sqlite"
        sessions: List[SessionRecord] = []

        if db_path.exists():
            try:
                with sqlite3.connect(db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    cur.execute(
                        """
                        SELECT id, workspace_path, updated_at, latest_prompt
                        FROM sessions
                        ORDER BY updated_at DESC
                        LIMIT 3
                        """
                    )
                    for row in cur.fetchall():
                        ts = row["updated_at"]
                        # Support both Unix-ms integers and ISO strings
                        if isinstance(ts, (int, float)):
                            dt = datetime.datetime.fromtimestamp(ts / 1000.0, tz=datetime.timezone.utc)
                        else:
                            dt = datetime.datetime.fromisoformat(str(ts))
                        sessions.append(
                            SessionRecord(
                                session_id=str(row["id"]),
                                project_path=row["workspace_path"],
                                last_active=dt,
                                preview=(row["latest_prompt"] or "")[:120] or "DSH session",
                            )
                        )
            except (sqlite3.Error, KeyError):
                pass

        if not sessions:
            # Fallback: JSONL logs
            sessions = _recent_mtime_sessions(
                dsh_dir / "logs", "*.jsonl",
                harness_name=self.display_name,
            )

        plugins_file = dsh_dir / "plugins.yaml"
        config_loc = str(plugins_file) if plugins_file.exists() else str(dsh_dir)

        return AgentMetadata(
            harness_name=self.display_name,
            harness_id=self.harness_id,
            binary_path=shutil.which("dsh"),
            is_installed=True,
            config_location=config_loc,
            capabilities=["runtime-plugin-reload", "sqlite-state", "cordis-di"],
            recent_sessions=sessions,
        )


class PrimeAgentAdapter(HarnessDiscoveryStrategy):
    """
    Adapter for Prime Agent — a dynamic harness capable of rewriting its own
    capabilities at runtime.

    Inspects ~/.prime/ for manifest.json and workspace YAML definitions.
    """

    @property
    def harness_id(self) -> str:
        return "prime-agent"

    @property
    def display_name(self) -> str:
        return "Prime Agent"

    def discover(self) -> Optional[AgentMetadata]:
        prime_dir = Path.home() / ".prime"
        if not prime_dir.exists():
            return None

        manifest = prime_dir / "manifest.json"
        workspaces_dir = prime_dir / "workspaces"

        sessions: List[SessionRecord] = []
        if workspaces_dir.is_dir():
            def _preview(f: Path) -> str:
                try:
                    import importlib.util
                    # Lightweight YAML scalar reader (no PyYAML required)
                    for line in f.read_text(encoding="utf-8").splitlines():
                        if line.strip().startswith("description:"):
                            return line.split(":", 1)[1].strip()
                except Exception:
                    pass
                return "Prime workspace"

            sessions = _recent_mtime_sessions(
                workspaces_dir, "*.yaml",
                harness_name=self.display_name,
                preview_fn=_preview,
            )
            if not sessions:
                sessions = _recent_mtime_sessions(
                    workspaces_dir, "*.json",
                    harness_name=self.display_name,
                )

        caps = ["self-modifying-capabilities", "dynamic-plugin-graph", "workspace-isolation"]
        try:
            if manifest.exists():
                data = json.loads(manifest.read_text(encoding="utf-8"))
                caps = data.get("capabilities", caps)
        except Exception:
            pass

        return AgentMetadata(
            harness_name=self.display_name,
            harness_id=self.harness_id,
            binary_path=shutil.which("prime"),
            is_installed=True,
            config_location=str(manifest) if manifest.exists() else str(prime_dir),
            capabilities=caps,
            recent_sessions=sessions,
        )


# =====================================================================
# 4. CORE AGGREGATOR DOMAIN — AgentScanner
#    Orchestrates discovery strategies; has zero knowledge of I/O.
# =====================================================================


class AgentScanner:
    """
    Core domain service.  Receives a registry of HarnessDiscoveryStrategy
    instances and aggregates their results into a canonical list.
    """

    def __init__(self, strategies: List[HarnessDiscoveryStrategy]) -> None:
        self._strategies = strategies

    def scan(self, *, harness_filter: Optional[str] = None) -> List[AgentMetadata]:
        """
        Run all registered discovery strategies and return installed harnesses.

        Args:
            harness_filter: If provided, only run the strategy whose harness_id
                            matches this value (case-insensitive).

        Returns:
            Ordered list of AgentMetadata for detected (is_installed=True) harnesses.
        """
        results: List[AgentMetadata] = []
        for strategy in self._strategies:
            if harness_filter and strategy.harness_id.lower() != harness_filter.lower():
                continue
            try:
                metadata = strategy.discover()
            except Exception as exc:  # noqa: BLE001
                # Degrade gracefully; a broken adapter must not abort the scan.
                metadata = None
                _warn(f"[{strategy.harness_id}] discovery failed: {exc}")
            if metadata is not None and metadata.is_installed:
                results.append(metadata)
        return results

    def list_registered(self) -> List[str]:
        return [s.harness_id for s in self._strategies]


# =====================================================================
# 5. OUTBOUND PRESENTER PORTS — Fission Output Adapters
#    Each presenter renders domain records into a target modality.
# =====================================================================


class PresenterStrategy(abc.ABC):
    """Output port interface — decouples domain results from presentation media."""

    @abc.abstractmethod
    def render(self, agents: List[AgentMetadata], *, verbose: bool = False) -> None:
        """Write the canonical results to the appropriate output channel."""


class PlainTextPresenter(PresenterStrategy):
    """POSIX-idiomatic human-readable text output for terminals."""

    _TICK = "✅"
    _CROSS = "❌"

    def render(self, agents: List[AgentMetadata], *, verbose: bool = False) -> None:
        if not agents:
            print("No AI agent harnesses detected on this machine.")
            return

        print(f"{'─' * 52}")
        print(f"  AI Agent Harnesses Detected: {len(agents)}")
        print(f"{'─' * 52}")

        for ag in agents:
            status = self._TICK if ag.is_installed else self._CROSS
            print(f"\n{status}  {ag.harness_name}  [{ag.harness_id}]")
            if ag.binary_path:
                print(f"     Binary  : {ag.binary_path}")
            if ag.config_location:
                print(f"     Config  : {ag.config_location}")
            if ag.capabilities:
                print(f"     Caps    : {', '.join(ag.capabilities)}")

            if ag.recent_sessions:
                print(f"     Sessions: {len(ag.recent_sessions)} recent")
                if verbose:
                    for s in ag.recent_sessions:
                        ts = s.last_active.strftime("%Y-%m-%d %H:%M UTC")
                        proj = f"  ({s.project_path})" if s.project_path else ""
                        print(f"       • [{ts}]{proj}  {s.preview[:80]}")
            else:
                print("     Sessions: none found")

        print(f"\n{'─' * 52}")


class NdjsonPresenter(PresenterStrategy):
    """
    Newline-delimited JSON (NDJSON) stream — machine-readable output
    compatible with jq, log aggregators, and downstream pipelines.
    """

    def render(self, agents: List[AgentMetadata], *, verbose: bool = False) -> None:
        for ag in agents:
            d = ag.as_dict()
            if not verbose:
                d.pop("recent_sessions", None)
            print(json.dumps(d, default=str))


# =====================================================================
# 6. DEPENDENCY WIRING — Registry & Entry Point
#    Composes strategies and presenters; this is the only place that
#    knows about concrete implementations.
# =====================================================================

_DEFAULT_STRATEGIES: List[HarnessDiscoveryStrategy] = [
    ClaudeCodeAdapter(),
    PiAgentAdapter(),
    DeepSeekHarnessAdapter(),
    PrimeAgentAdapter(),
]

_PRESENTERS = {
    "text": PlainTextPresenter(),
    "json": NdjsonPresenter(),
}


def _warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="list-agents",
        description=(
            "POSIX CLI tool to list installed AI agent harnesses and their recent sessions.\n"
            "Implements Hexagonal Architecture with Strategy adapters per harness."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--format",
        choices=list(_PRESENTERS.keys()),
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--harness",
        metavar="ID",
        default=None,
        help="Only scan a specific harness by its ID (e.g. claude-code)",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Include recent session details in output",
    )
    p.add_argument(
        "--list-harnesses",
        action="store_true",
        help="Print registered harness IDs and exit",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    scanner = AgentScanner(_DEFAULT_STRATEGIES)

    if args.list_harnesses:
        for hid in scanner.list_registered():
            print(hid)
        return 0

    agents = scanner.scan(harness_filter=args.harness)
    presenter = _PRESENTERS[args.format]
    presenter.render(agents, verbose=args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
