# Agent Story

> A toolkit for the Claude Code ecosystem.
>
> **claude-story** — Automatic conversation history manager (Node.js daemon).  
> **list-agents** — POSIX CLI tool to discover all installed AI agent harnesses (Python).

---

## 📦 Components

| Tool | Language | Purpose |
|---|---|---|
| `claude-story` / `cs` | Node.js | Auto-saves Claude Code conversations to markdown + SQLite |
| `list-agents` | Python 3.10+ | Lists installed AI agent harnesses and recent sessions |

---

## 🚀 Quick Start

### claude-story (Node.js)

```bash
# Install globally from npm
npm install -g claude-story

# Start monitoring (run once, runs as background daemon)
claude-story start

# Check status
claude-story status
```

### list-agents (Python)

```bash
# No installation required — stdlib only
python list_agents.py

# Machine-readable NDJSON output (pipe to jq)
python list_agents.py --format json --verbose | jq .

# Target a specific harness
python list_agents.py --harness claude-code

# List all registered harness adapters
python list_agents.py --list-harnesses
```

---

## ✨ Features

### claude-story

- **🤖 Automatic Monitoring** — Detects all Claude Code conversations without manual setup
- **📁 Project Auto-Detection** — Creates `.claude-story/` directories in each project automatically
- **💾 SQLite Database** — Stores conversation metadata with unique IDs and timestamps
- **📄 Markdown Export** — Auto-exports conversations to readable markdown files
- **🔍 Cross-Project Search** — Compatible with MCP servers for enhanced search capabilities
- **⚡ Real-time Sync** — Conversations saved as you chat with Claude
- **🙈 Git Integration** — Automatically adds `.claude-story/` to .gitignore when created

### list-agents

- **🔌 Hexagonal Architecture** — Core domain fully decoupled from filesystem/database specifics
- **🧩 Strategy / Plugin Pattern** — Each harness is an independent discovery adapter
- **📤 Fission Presenters** — Plain POSIX text or NDJSON stream output
- **🛡️ Graceful Degradation** — Broken or missing harnesses never abort the scan
- **🔒 Zero external dependencies** — Python standard library only

Supported harnesses out of the box:

| Harness | Config location | Session storage |
|---|---|---|
| Claude Code | `~/.claude/` | JSON + JSONL |
| Pi Agent | `~/.pi/` | JSONL history |
| DeepSeek Harness (dsh) | `~/.dsh/` | SQLite + JSONL |
| Prime Agent | `~/.prime/` | YAML/JSON workspaces |

---

## 🎯 How claude-story Works

Claude Story monitors `~/.claude/projects/` where Claude Code stores conversation data:

1. **Detects** the conversation in real-time
2. **Creates** a `.claude-story/` directory in your project
3. **Saves** the conversation to a SQLite database
4. **Exports** to markdown files in `history/` folder

```
your-project/
├── .claude-story/
│   ├── conversations.db     # SQLite database
│   ├── history/             # Markdown exports
│   │   ├── 2025-01-15T10-30-45Z-building-new-feature.md
│   │   └── 2025-01-15T14-22-10Z-debugging-issue.md
│   └── .what-is-this.md     # Documentation
```

---

## 🛠 Commands

### claude-story

```bash
claude-story start     # Start daemon (runs in background)
claude-story status    # Check daemon status and detected conversations
claude-story stop      # Stop daemon
claude-story help      # Show help
```

### list-agents

```bash
python list_agents.py                          # Human-readable text
python list_agents.py --format json            # NDJSON (one object per line)
python list_agents.py --format json --verbose  # Include session details
python list_agents.py --harness claude-code    # Scan only one harness
python list_agents.py --list-harnesses         # Print registered adapter IDs
```

---

## 📦 Installation

### claude-story

```bash
npm install -g claude-story
```

Requires: **Node.js >= 16.0.0**

### list-agents

No installation. Requires **Python >= 3.10** (standard library only).

```bash
python list_agents.py --help
```

---

## 🔧 Requirements

| Tool | Runtime | Min version |
|---|---|---|
| claude-story | Node.js | 16.0.0 |
| list-agents | Python | 3.10 |

Platform: **macOS / Linux** (POSIX). Windows support is not currently tested.

---

## 🧪 Development & Testing

```bash
# Python tests with coverage
pip install --require-hashes -r requirements-ci.txt
python -m coverage run --branch --source=list_agents test_list_agents.py
python -m coverage report --fail-under=80

# Node.js smoke test
npm ci
npm test
```

CI runs automatically on every push and pull request via GitHub Actions (`.github/workflows/ci.yml`).

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full development workflow.

---

## 🆚 Claude Story vs SpecStory

| Feature | SpecStory (Cursor) | Claude Story (Claude Code) |
|---|---|---|
| Auto-detection | ✅ | ✅ |
| SQLite database | ✅ | ✅ |
| Markdown export | ✅ | ✅ |
| Project directories | `.specstory/` | `.claude-story/` |
| Setup required | None | `claude-story start` |

---

## 🔍 MCP Server Integration

Claude Story outputs standard markdown files that can be indexed by any MCP (Model Context Protocol) server for enhanced search and retrieval across projects.

---

## 🚨 Security & Privacy

- **Local only** — All data stays on your machine
- **No network requests** — Works completely offline
- **User path security** — Uses `~/` instead of hardcoded paths
- **Supply-chain hardened CI** — SHA-pinned GitHub Actions, hash-verified pip installs

---

## 📝 License

MIT © Agent Story contributors

---

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full guide.

**Short version:**
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Run the test suite before committing
4. Open a Pull Request

## 🐛 Issues

Found a bug? [Open an issue](https://github.com/sebastian-kwinana/agent-story/issues)

---

**Made with ❤️ for the AI agent developer community**

## 🚀 Quick Start

```bash
# Install globally from npm
npm install -g claude-story

# Start monitoring (run once)
claude-story start

# Check status
claude-story status
```

That's it! Claude Story will now automatically save all your Claude Code conversations to `.claude-story/` directories in each project.

## ✨ Features

- **🤖 Automatic Monitoring** - Detects all Claude Code conversations without manual setup
- **📁 Project Auto-Detection** - Creates `.claude-story/` directories in each project automatically  
- **💾 SQLite Database** - Stores conversation metadata with unique IDs and timestamps
- **📄 Markdown Export** - Auto-exports conversations to readable markdown files
- **🔍 Cross-Project Search** - Compatible with MCP servers for enhanced search capabilities
- **⚡ Real-time Sync** - Conversations saved as you chat with Claude
- **🙈 Git Integration** - Automatically adds `.claude-story/` to .gitignore when created

## 🎯 How It Works

Claude Story monitors the `~/.claude/projects/` directory where Claude Code stores conversation data. When you use Claude Code in any project, it automatically:

1. **Detects** the conversation in real-time
2. **Creates** a `.claude-story/` directory in your project
3. **Saves** the conversation to a SQLite database
4. **Exports** to markdown files in `history/` folder

## 📂 File Structure

After installation, your projects will have:

```
your-project/
├── .claude-story/
│   ├── conversations.db     # SQLite database
│   ├── history/             # Markdown exports
│   │   ├── 2025-01-15T10-30-45Z-building-new-feature.md
│   │   └── 2025-01-15T14-22-10Z-debugging-issue.md
│   └── .what-is-this.md     # Documentation
```

## 🛠 Commands

```bash
# Start monitoring (runs continuously)
claude-story start
# or
cs start

# Check detection status  
claude-story status
# or  
cs status

# Stop monitoring
claude-story stop
# or
cs stop

# Show help
claude-story help
# or
cs help
```

## 📦 Installation

Claude Story is available as an npm package:

```bash
npm install -g claude-story
```

## 🔧 Requirements

- **Node.js** >= 16.0.0
- **Claude Code** installed and used at least once
- **macOS/Linux** (Windows support coming soon)

## 🆚 Claude Story vs SpecStory

| Feature | SpecStory (Cursor) | Claude Story (Claude Code) |
|---------|-------------------|---------------------------|
| Auto-detection | ✅ | ✅ |
| SQLite database | ✅ | ✅ |
| Markdown export | ✅ | ✅ |
| Project directories | `.specstory/` | `.claude-story/` |
| Setup required | None | `claude-story start` |

## 🔍 MCP Server Integration

Claude Story outputs standard markdown files that can be indexed by any MCP (Model Context Protocol) server for enhanced search and retrieval across projects. The organized file structure makes it easy to integrate with existing workflow tools.

## 🚨 Security & Privacy

- **Local only** - All data stays on your machine
- **No network requests** - Works completely offline
- **User path security** - Uses `~/` instead of hardcoded paths
- **Excludes sensitive data** - Filters out potential secrets and credentials

## 📝 License

MIT © Claude Story Team

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Issues

Found a bug? [Report it here](https://github.com/your-username/claude-story/issues)

---

**Made with ❤️ for the Claude Code community**