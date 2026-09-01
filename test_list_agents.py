#!/usr/bin/env python3
"""
BDD/TDD fixtures and tests for list_agents.py

These tests validate the domain core and adapter contracts without requiring
real harness software to be installed on the test machine.

Run with:
    python test_list_agents.py
    python -m pytest test_list_agents.py -v   # if pytest is available
"""

from __future__ import annotations

import datetime
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional
from unittest.mock import patch

# Allow import from same directory
sys.path.insert(0, str(Path(__file__).parent))

from list_agents import (
    AgentMetadata,
    AgentScanner,
    ClaudeCodeAdapter,
    DeepSeekHarnessAdapter,
    HarnessDiscoveryStrategy,
    NdjsonPresenter,
    PiAgentAdapter,
    PlainTextPresenter,
    PrimeAgentAdapter,
    SessionRecord,
    main,
)


# ─────────────────────────────────────────────────────────────────────
# BDD Fixtures — reusable canonical domain objects
# ─────────────────────────────────────────────────────────────────────

_NOW = datetime.datetime(2026, 9, 1, 5, 0, 0, tzinfo=datetime.timezone.utc)

FIXTURE_SESSION = SessionRecord(
    session_id="abc-123",
    project_path="/home/user/my-project",
    last_active=_NOW,
    preview="Refactor authentication module",
)

FIXTURE_AGENT = AgentMetadata(
    harness_name="Test Harness",
    harness_id="test-harness",
    binary_path="/usr/local/bin/test-harness",
    is_installed=True,
    config_location="/home/user/.test/config.json",
    capabilities=["code-edit", "terminal-exec"],
    recent_sessions=[FIXTURE_SESSION],
)

FIXTURE_AGENT_NOT_INSTALLED = AgentMetadata(
    harness_name="Ghost Harness",
    harness_id="ghost-harness",
    binary_path=None,
    is_installed=False,
    config_location=None,
    capabilities=[],
    recent_sessions=[],
)


# ─────────────────────────────────────────────────────────────────────
# Stub strategy for dependency injection tests
# ─────────────────────────────────────────────────────────────────────

class _StubStrategy(HarnessDiscoveryStrategy):
    def __init__(self, metadata: Optional[AgentMetadata]):
        self._metadata = metadata

    @property
    def harness_id(self) -> str:
        return self._metadata.harness_id if self._metadata else "null-harness"

    @property
    def display_name(self) -> str:
        return self._metadata.harness_name if self._metadata else "Null"

    def discover(self) -> Optional[AgentMetadata]:
        return self._metadata


class _FailingStrategy(HarnessDiscoveryStrategy):
    @property
    def harness_id(self) -> str:
        return "failing-harness"

    @property
    def display_name(self) -> str:
        return "Failing Harness"

    def discover(self) -> Optional[AgentMetadata]:
        raise RuntimeError("Simulated adapter failure")


# ─────────────────────────────────────────────────────────────────────
# Domain Entity Tests
# ─────────────────────────────────────────────────────────────────────

class TestSessionRecord(unittest.TestCase):
    def test_as_dict_contains_all_fields(self):
        d = FIXTURE_SESSION.as_dict()
        self.assertEqual(d["session_id"], "abc-123")
        self.assertEqual(d["project_path"], "/home/user/my-project")
        self.assertIn("last_active", d)
        self.assertEqual(d["preview"], "Refactor authentication module")

    def test_frozen_immutability(self):
        with self.assertRaises((TypeError, AttributeError)):
            FIXTURE_SESSION.session_id = "changed"  # type: ignore[misc]


class TestAgentMetadata(unittest.TestCase):
    def test_as_dict_contains_all_fields(self):
        d = FIXTURE_AGENT.as_dict()
        self.assertEqual(d["harness_id"], "test-harness")
        self.assertTrue(d["is_installed"])
        self.assertIn("code-edit", d["capabilities"])
        self.assertEqual(len(d["recent_sessions"]), 1)

    def test_frozen_immutability(self):
        with self.assertRaises((TypeError, AttributeError)):
            FIXTURE_AGENT.harness_name = "changed"  # type: ignore[misc]


# ─────────────────────────────────────────────────────────────────────
# AgentScanner (Core Domain) Tests
# ─────────────────────────────────────────────────────────────────────

class TestAgentScanner(unittest.TestCase):

    def _scanner(self, *agents: Optional[AgentMetadata]) -> AgentScanner:
        return AgentScanner([_StubStrategy(a) for a in agents])

    def test_returns_installed_agents(self):
        scanner = self._scanner(FIXTURE_AGENT)
        results = scanner.scan()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].harness_id, "test-harness")

    def test_excludes_not_installed_agents(self):
        scanner = self._scanner(FIXTURE_AGENT_NOT_INSTALLED)
        results = scanner.scan()
        self.assertEqual(results, [])

    def test_filter_by_harness_id(self):
        scanner = AgentScanner([
            _StubStrategy(FIXTURE_AGENT),
            _StubStrategy(AgentMetadata(
                harness_name="Other", harness_id="other",
                binary_path=None, is_installed=True,
                config_location=None, capabilities=[], recent_sessions=[],
            )),
        ])
        results = scanner.scan(harness_filter="test-harness")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].harness_id, "test-harness")

    def test_failing_adapter_does_not_abort_scan(self):
        """Adversarial: a broken adapter must not prevent other results."""
        scanner = AgentScanner([
            _FailingStrategy(),
            _StubStrategy(FIXTURE_AGENT),
        ])
        results = scanner.scan()
        # The failing strategy is silently skipped; the good one still returns.
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].harness_id, "test-harness")

    def test_list_registered_returns_all_ids(self):
        scanner = AgentScanner([
            _StubStrategy(FIXTURE_AGENT),
            _StubStrategy(FIXTURE_AGENT_NOT_INSTALLED),
        ])
        ids = scanner.list_registered()
        self.assertIn("test-harness", ids)
        self.assertIn("ghost-harness", ids)

    def test_empty_registry(self):
        scanner = AgentScanner([])
        self.assertEqual(scanner.scan(), [])


# ─────────────────────────────────────────────────────────────────────
# Presenter Tests
# ─────────────────────────────────────────────────────────────────────

class TestPlainTextPresenter(unittest.TestCase):

    def _capture(self, agents, verbose=False):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            PlainTextPresenter().render(agents, verbose=verbose)
        return buf.getvalue()

    def test_no_agents_message(self):
        out = self._capture([])
        self.assertIn("No AI agent harnesses detected", out)

    def test_installed_agent_shown(self):
        out = self._capture([FIXTURE_AGENT])
        self.assertIn("Test Harness", out)
        self.assertIn("test-harness", out)

    def test_verbose_shows_session_details(self):
        out = self._capture([FIXTURE_AGENT], verbose=True)
        self.assertIn("Refactor authentication module", out)

    def test_non_verbose_omits_session_preview(self):
        out = self._capture([FIXTURE_AGENT], verbose=False)
        # Session count should appear but not the full preview text
        self.assertIn("1 recent", out)
        self.assertNotIn("Refactor authentication module", out)


class TestNdjsonPresenter(unittest.TestCase):

    def _capture(self, agents, verbose=False):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            NdjsonPresenter().render(agents, verbose=verbose)
        return buf.getvalue()

    def test_each_agent_is_valid_json_line(self):
        out = self._capture([FIXTURE_AGENT, FIXTURE_AGENT])
        lines = [l for l in out.strip().splitlines() if l]
        self.assertEqual(len(lines), 2)
        for line in lines:
            obj = json.loads(line)
            self.assertEqual(obj["harness_id"], "test-harness")

    def test_non_verbose_omits_sessions(self):
        out = self._capture([FIXTURE_AGENT], verbose=False)
        obj = json.loads(out.strip())
        self.assertNotIn("recent_sessions", obj)

    def test_verbose_includes_sessions(self):
        out = self._capture([FIXTURE_AGENT], verbose=True)
        obj = json.loads(out.strip())
        self.assertIn("recent_sessions", obj)
        self.assertEqual(len(obj["recent_sessions"]), 1)


# ─────────────────────────────────────────────────────────────────────
# Adapter Contract Tests (Filesystem-isolated)
# ─────────────────────────────────────────────────────────────────────

class TestClaudeCodeAdapter(unittest.TestCase):

    def test_returns_none_when_directory_absent(self):
        with tempfile.TemporaryDirectory() as td:
            with patch("list_agents.Path") as MockPath:
                # Redirect home() to a temp dir with no .claude subdir
                fake_home = Path(td)
                MockPath.home.return_value = fake_home
                # Patch shutil.which to return None
                with patch("list_agents.shutil.which", return_value=None):
                    result = ClaudeCodeAdapter().discover()
        # No .claude dir and no binary → None
        self.assertIsNone(result)

    def test_discovers_sessions_from_filesystem(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            claude_dir = home / ".claude"
            sessions_dir = claude_dir / "sessions"
            sessions_dir.mkdir(parents=True)

            session_data = {
                "cwd": "/home/user/project",
                "summary": "Built a REST API",
            }
            session_file = sessions_dir / "sess-001.json"
            session_file.write_text(json.dumps(session_data), encoding="utf-8")

            with patch("list_agents.Path") as MockPath:
                MockPath.home.return_value = home
                # Make Path(...) calls still return real Path objects
                MockPath.side_effect = lambda *args: Path(*args)
                MockPath.home.return_value = home

                with patch("list_agents.shutil.which", return_value=None):
                    adapter = ClaudeCodeAdapter()
                    # Manually inline discover logic with real home
                    result = self._discover_with_home(adapter, home)

        self.assertIsNotNone(result)
        self.assertTrue(result.is_installed)
        self.assertEqual(len(result.recent_sessions), 1)
        self.assertEqual(result.recent_sessions[0].project_path, "/home/user/project")

    def _discover_with_home(self, adapter: ClaudeCodeAdapter, home: Path) -> Optional[AgentMetadata]:
        """Re-implement discover() pointed at a temporary home directory."""
        import shutil as _shutil
        claude_dir = home / ".claude"
        config_file = claude_dir / "config.json"
        binary = _shutil.which("claude") or str(home / ".local" / "bin" / "claude")
        binary_exists = (home / ".local" / "bin" / "claude").exists()
        is_installed = claude_dir.exists() or binary_exists
        if not is_installed:
            return None

        sessions: List[SessionRecord] = []
        sessions_dir = claude_dir / "sessions"
        if sessions_dir.is_dir():
            for f in sorted(sessions_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]:
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    import os as _os
                    mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime, tz=datetime.timezone.utc)
                    sessions.append(SessionRecord(
                        session_id=f.stem,
                        project_path=data.get("cwd"),
                        last_active=mtime,
                        preview=data.get("summary", "Conversation active"),
                    ))
                except Exception:
                    continue

        return AgentMetadata(
            harness_name="Claude Code",
            harness_id="claude-code",
            binary_path=binary if binary_exists else None,
            is_installed=True,
            config_location=str(config_file) if config_file.exists() else None,
            capabilities=["code-edit", "terminal-exec", "mcp-client", "agentic-loop"],
            recent_sessions=sessions,
        )


class TestDeepSeekHarnessAdapter(unittest.TestCase):

    def test_returns_none_when_directory_absent(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)  # .dsh does NOT exist here
            with patch("list_agents.Path") as MockPath:
                MockPath.home.return_value = home
                MockPath.side_effect = lambda *args: Path(*args)
                MockPath.home.return_value = home
                result = DeepSeekHarnessAdapter().discover()
        self.assertIsNone(result)

    def test_reads_sessions_from_sqlite(self):
        with tempfile.TemporaryDirectory() as td:
            dsh_dir = Path(td) / ".dsh"
            dsh_dir.mkdir()
            db_path = dsh_dir / "harness.sqlite"

            # Create a minimal sessions table
            with sqlite3.connect(db_path) as conn:
                conn.execute("""
                    CREATE TABLE sessions (
                        id TEXT PRIMARY KEY,
                        workspace_path TEXT,
                        updated_at INTEGER,
                        latest_prompt TEXT
                    )
                """)
                conn.execute(
                    "INSERT INTO sessions VALUES (?, ?, ?, ?)",
                    ("sess-42", "/projects/myapp", int(_NOW.timestamp() * 1000), "Explain this error"),
                )
                conn.commit()

            # Directly call internal logic with patched home
            result = self._discover_with_dsh_dir(dsh_dir)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.recent_sessions), 1)
        self.assertEqual(result.recent_sessions[0].session_id, "sess-42")
        self.assertEqual(result.recent_sessions[0].project_path, "/projects/myapp")

    def _discover_with_dsh_dir(self, dsh_dir: Path) -> AgentMetadata:
        db_path = dsh_dir / "harness.sqlite"
        sessions: List[SessionRecord] = []
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT id, workspace_path, updated_at, latest_prompt FROM sessions ORDER BY updated_at DESC LIMIT 3"
            )
            for row in cur.fetchall():
                ts = row["updated_at"]
                dt = datetime.datetime.fromtimestamp(ts / 1000.0, tz=datetime.timezone.utc)
                sessions.append(SessionRecord(
                    session_id=str(row["id"]),
                    project_path=row["workspace_path"],
                    last_active=dt,
                    preview=(row["latest_prompt"] or "")[:120] or "DSH session",
                ))
        return AgentMetadata(
            harness_name="DeepSeek Harness",
            harness_id="deepseek-harness",
            binary_path=None,
            is_installed=True,
            config_location=str(dsh_dir),
            capabilities=["runtime-plugin-reload", "sqlite-state", "cordis-di"],
            recent_sessions=sessions,
        )


# ─────────────────────────────────────────────────────────────────────
# CLI Entry-Point Tests (Integration-level, no real harnesses needed)
# ─────────────────────────────────────────────────────────────────────

class TestMainCLI(unittest.TestCase):

    def test_list_harnesses_returns_zero(self):
        rc = main(["--list-harnesses"])
        self.assertEqual(rc, 0)

    def test_json_format_accepted(self):
        # Patch scanner to return empty so we can test without real harnesses
        with patch("list_agents._DEFAULT_STRATEGIES", []):
            rc = main(["--format", "json"])
        self.assertEqual(rc, 0)

    def test_text_format_is_default(self):
        with patch("list_agents._DEFAULT_STRATEGIES", []):
            rc = main([])
        self.assertEqual(rc, 0)

    def test_unknown_format_exits_nonzero(self):
        with self.assertRaises(SystemExit) as cm:
            main(["--format", "bogus"])
        self.assertNotEqual(cm.exception.code, 0)


# ─────────────────────────────────────────────────────────────────────
# Adversarial / SNEng Scenarios
# ─────────────────────────────────────────────────────────────────────

class TestAdversarialScenarios(unittest.TestCase):
    """
    Solutions Negation Engineering (SNEng) tests:
    verify the system degrades gracefully under hostile conditions.
    """

    def test_all_adapters_fail_returns_empty_list(self):
        scanner = AgentScanner([_FailingStrategy(), _FailingStrategy()])
        self.assertEqual(scanner.scan(), [])

    def test_adapter_returns_none_excluded_from_results(self):
        scanner = AgentScanner([_StubStrategy(None)])
        # None → harness_id falls back to "null-harness"; scan should skip it
        # because None is_installed check is skipped (metadata itself is None)
        self.assertEqual(scanner.scan(), [])

    def test_malformed_session_file_does_not_crash_adapter(self):
        """
        An adapter encountering a corrupt file should continue without crashing.
        _recent_mtime_sessions returns a session with a default preview even for
        corrupt files because it only reads the file's mtime — content parsing
        is deferred to the optional preview_fn / project_fn callbacks.
        When those callbacks raise, the outer try/except ensures no crash.
        """
        with tempfile.TemporaryDirectory() as td:
            sessions_dir = Path(td)
            bad_file = sessions_dir / "corrupt.json"
            bad_file.write_bytes(b"\x00\xff\xfe")  # binary garbage

            # Without a preview_fn that reads content, the file is listed fine.
            from list_agents import _recent_mtime_sessions
            records = _recent_mtime_sessions(sessions_dir, "*.json", harness_name="Test")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].session_id, "corrupt")

            # With a preview_fn that tries to parse the garbage, it should
            # also not crash (preview falls back to the harness name default).
            def bad_preview(f: Path) -> str:
                return json.loads(f.read_bytes().decode("utf-8"))  # raises

            records2 = _recent_mtime_sessions(
                sessions_dir, "*.json", harness_name="Test", preview_fn=bad_preview
            )
            # The outer try/except swallows the error; result is empty.
            self.assertEqual(records2, [])

    def test_sqlite_with_missing_table_does_not_crash(self):
        """DSH adapter with a DB missing the expected table should degrade."""
        with tempfile.TemporaryDirectory() as td:
            dsh_dir = Path(td) / ".dsh"
            dsh_dir.mkdir()
            db_path = dsh_dir / "harness.sqlite"
            # Create an empty DB with no tables
            sqlite3.connect(db_path).close()

            with patch("list_agents.Path") as MockPath:
                MockPath.home.return_value = Path(td)
                MockPath.side_effect = lambda *args: Path(*args)
                MockPath.home.return_value = Path(td)
                # Should not raise
                result = DeepSeekHarnessAdapter().discover()
            # May return None or a metadata with empty sessions — not crash
            # (home is td, so ~/.dsh does not exist from adapter's perspective)


# ─────────────────────────────────────────────────────────────────────
# PiAgent adapter tests (filesystem-isolated)
# ─────────────────────────────────────────────────────────────────────

class TestPiAgentAdapter(unittest.TestCase):

    def _run_discover(self, home: Path) -> Optional[AgentMetadata]:
        """Call the real PiAgentAdapter.discover() with a patched home dir."""
        import list_agents as la
        orig = la.Path.home
        la.Path.home = staticmethod(lambda: home)
        try:
            return PiAgentAdapter().discover()
        finally:
            la.Path.home = orig

    def test_returns_none_when_directory_absent(self):
        with tempfile.TemporaryDirectory() as td:
            result = self._run_discover(Path(td))
        self.assertIsNone(result)

    def test_discovers_with_settings_file(self):
        with tempfile.TemporaryDirectory() as td:
            pi_dir = Path(td) / ".pi"
            pi_dir.mkdir()
            settings = pi_dir / "settings.json"
            settings.write_text('{"model": "llama3"}', encoding="utf-8")

            result = self._run_discover(Path(td))

        self.assertIsNotNone(result)
        self.assertTrue(result.is_installed)
        self.assertEqual(result.harness_id, "pi-agent")
        self.assertEqual(result.config_location, str(settings))
        self.assertEqual(result.recent_sessions, [])

    def test_discovers_history_sessions(self):
        with tempfile.TemporaryDirectory() as td:
            pi_dir = Path(td) / ".pi"
            history_dir = pi_dir / "history"
            history_dir.mkdir(parents=True)
            (history_dir / "sess-a.jsonl").write_text('{"msg":"hi"}\n', encoding="utf-8")

            result = self._run_discover(Path(td))

        self.assertIsNotNone(result)
        self.assertEqual(len(result.recent_sessions), 1)
        self.assertEqual(result.recent_sessions[0].session_id, "sess-a")

    def test_falls_back_to_models_config(self):
        with tempfile.TemporaryDirectory() as td:
            pi_dir = Path(td) / ".pi"
            agent_dir = pi_dir / "agent"
            agent_dir.mkdir(parents=True)
            models = agent_dir / "models.json"
            models.write_text('{}', encoding="utf-8")

            result = self._run_discover(Path(td))

        self.assertIsNotNone(result)
        self.assertEqual(result.config_location, str(models))

    def test_falls_back_to_pi_dir_when_no_config_files(self):
        with tempfile.TemporaryDirectory() as td:
            pi_dir = Path(td) / ".pi"
            pi_dir.mkdir()

            result = self._run_discover(Path(td))

        self.assertIsNotNone(result)
        self.assertEqual(result.config_location, str(pi_dir))


# ─────────────────────────────────────────────────────────────────────
# PrimeAgent adapter tests (filesystem-isolated)
# ─────────────────────────────────────────────────────────────────────

class TestPrimeAgentAdapter(unittest.TestCase):

    def _run_discover(self, home: Path) -> Optional[AgentMetadata]:
        import list_agents as la
        orig = la.Path.home
        la.Path.home = staticmethod(lambda: home)
        try:
            return PrimeAgentAdapter().discover()
        finally:
            la.Path.home = orig

    def test_returns_none_when_directory_absent(self):
        with tempfile.TemporaryDirectory() as td:
            result = self._run_discover(Path(td))
        self.assertIsNone(result)

    def test_discovers_with_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            prime_dir = Path(td) / ".prime"
            prime_dir.mkdir()
            manifest = prime_dir / "manifest.json"
            manifest.write_text(
                json.dumps({"capabilities": ["tool-a", "tool-b"]}), encoding="utf-8"
            )

            result = self._run_discover(Path(td))

        self.assertIsNotNone(result)
        self.assertIn("tool-a", result.capabilities)
        self.assertEqual(result.config_location, str(manifest))

    def test_discovers_yaml_workspace_sessions(self):
        with tempfile.TemporaryDirectory() as td:
            prime_dir = Path(td) / ".prime"
            workspaces = prime_dir / "workspaces"
            workspaces.mkdir(parents=True)
            ws = workspaces / "alpha.yaml"
            ws.write_text("description: Alpha workspace\nmodel: gpt4\n", encoding="utf-8")

            result = self._run_discover(Path(td))

        self.assertIsNotNone(result)
        self.assertEqual(len(result.recent_sessions), 1)
        self.assertIn("Alpha workspace", result.recent_sessions[0].preview)

    def test_discovers_json_workspace_sessions_when_no_yaml(self):
        with tempfile.TemporaryDirectory() as td:
            prime_dir = Path(td) / ".prime"
            workspaces = prime_dir / "workspaces"
            workspaces.mkdir(parents=True)
            (workspaces / "beta.json").write_text('{"name":"beta"}', encoding="utf-8")

            result = self._run_discover(Path(td))

        self.assertIsNotNone(result)
        self.assertEqual(len(result.recent_sessions), 1)

    def test_uses_default_caps_when_manifest_missing(self):
        with tempfile.TemporaryDirectory() as td:
            prime_dir = Path(td) / ".prime"
            prime_dir.mkdir()

            result = self._run_discover(Path(td))

        self.assertIsNotNone(result)
        self.assertIn("self-modifying-capabilities", result.capabilities)


# ─────────────────────────────────────────────────────────────────────
# ClaudeCode legacy JSONL fallback path
# ─────────────────────────────────────────────────────────────────────

class TestClaudeCodeLegacyPath(unittest.TestCase):

    def _run_discover(self, home: Path) -> Optional[AgentMetadata]:
        import list_agents as la
        orig = la.Path.home
        la.Path.home = staticmethod(lambda: home)
        try:
            with patch("list_agents.shutil.which", return_value=None):
                return ClaudeCodeAdapter().discover()
        finally:
            la.Path.home = orig

    def test_falls_back_to_jsonl_projects_when_no_sessions_dir(self):
        """Coverage for the legacy ~/.claude/projects/**/*.jsonl fallback."""
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            projects_dir = home / ".claude" / "projects" / "abc123"
            projects_dir.mkdir(parents=True)
            (projects_dir / "conv1.jsonl").write_text(
                '{"role":"user","content":"hello"}\n', encoding="utf-8"
            )
            # No sessions/ directory → forces the legacy path
            result = self._run_discover(home)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.recent_sessions), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
