<!-- BEFORE INIT -->
# Agent Template

This repository is a starter scaffold for building agents on top of
[agent_core](https://github.com/EdibleTuber/agent_core).

**Run the init script to scaffold a real agent:**

```bash
./scripts/init-agent.sh <agent-name>
```

The agent name must be a lowercase slug (letters, digits, hyphens; must start
with a letter). Examples: `re-lab`, `coding`, `my-agent`.

The script will:
- Ask for a one-line description of your agent
- Rename the package directory and service files
- Replace all placeholders in all files
- Remove this "Before Init" section from the README
- Remove itself

After init, install, configure `.env`, and run the smoke test to confirm
everything wires up.

<!-- END BEFORE INIT -->

---

# {{AGENT_NAME}}

{{AGENT_DESCRIPTION}}

## Install

```bash
python -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
```

Requires Python 3.12+. `agent_core` is pulled from GitHub at install time.

## Configure

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
$EDITOR .env
```

Key variables:
- `{{AGENT_PREFIX}}_INFERENCE_URL` — Ollama base URL (default: `http://localhost:11434`)
- `{{AGENT_PREFIX}}_MODEL` — model name to use
- `{{AGENT_PREFIX}}_VAULT_PATH` — path to your vault directory
- `{{AGENT_PREFIX}}_COLLECTION_ID` — vector collection name for retrieval

See `.env.example` for the full list.

## Run

Start the daemon:

```bash
.venv/bin/python -m {{agent_pkg}}
```

Or use the installed script:

```bash
.venv/bin/{{AGENT_NAME}}-daemon
```

Connect the CLI client (separate terminal). It reads the same config as the
daemon to find the socket, so no arguments are needed:

```bash
.venv/bin/python -m {{agent_pkg}}.cli
```

Or use the installed script:

```bash
.venv/bin/{{AGENT_NAME}}-cli
```

The client lives in `{{agent_pkg}}/cli.py` — a thin wrapper around
`agent_core.adapters.cli.run_repl` with a minimal `Renderer`. Edit its
`Renderer.format_message` to render any agent-specific message types you add.

## Smoke Test

```bash
.venv/bin/pytest tests/ -v
```

Expected: 4 tests pass (import, instantiation, command registration, CLI client wiring).

## Discord (optional)

Discord is not wired by default. The Discord adapter is a **client** of the
daemon — a separate process (like the CLI) that connects over the daemon's
socket. `agent_core.adapters.discord_gateway` ships composition helpers, not a
bot class or a `run_daemon` gateway: you bring your own `discord.Client`
subclass. To opt in:

1. Fold the `discord` extra into the `agent_core` dependency in
   `pyproject.toml` (it's a git-URL dependency, so the extra goes on that line):

   ```toml
   "agent_core[discord] @ git+https://github.com/EdibleTuber/agent_core.git@v1.12.1",
   ```

2. Add a Discord bot module (e.g. `{{agent_pkg}}/discord_bot.py`) with a
   `discord.Client` subclass that bridges Discord to the running daemon using
   the helpers in `agent_core.adapters.discord_gateway`:
   - `UserConnectionManager` — per-user `DaemonConnection`s to the socket
   - `parse_discord_message` — split `!cmd` vs chat intents
   - `rewrite_slash_prefixes` — translate `/cmd` → `!cmd`
   - `format_tool_progress`, `split_message` — Discord formatting

3. Run the bot as its own process alongside the daemon (it connects as a
   client; it is **not** passed to `run_daemon`).

## Systemd Setup

Two service files are included in `systemd/`. Edit the `WorkingDirectory` and
`EnvironmentFile` paths to match your deployment, then:

```bash
cp systemd/{{AGENT_NAME}}-daemon.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now {{AGENT_NAME}}-daemon
```

The CLI client (`{{agent_pkg}}.cli`) is typically run interactively rather than
as a service, so no unit file is provided for it.

---

## Architecture

```
{{agent_pkg}}/
    agent.py         {{AGENT_CLASS}} — your Agent subclass; add commands + tools here
    __main__.py      python -m {{agent_pkg}} entry point (calls run_daemon)
    cli.py           terminal REPL client; python -m {{agent_pkg}}.cli
    prompts/
        system.md    system prompt — edit to define your agent's identity
    commands/
        hello.py     example Command; copy to add your own
    tools/
        __init__.py  placeholder; add Tool subclasses and register on the class
```

### Extension points

| Point | How to use |
|---|---|
| `{{AGENT_CLASS}}.commands` | Add `Command` subclasses; `/help` is automatic |
| `{{AGENT_CLASS}}.tools` | Add `Tool` subclasses; executor picks them up |
| `{{AGENT_CLASS}}.disabled_builtins` | Remove built-in commands/tools by name |
| `{{AGENT_CLASS}}.setup()` | Construct domain resources after framework managers are ready |
| `{{AGENT_CLASS}}.system_prompt(ctx)` | Build the per-turn system prompt |
| `{{AGENT_CLASS}}.handle_command(msg, ctx)` | Dispatch slash-commands (wired to the registry by default) |
| `{{AGENT_CLASS}}.handle_chat(msg, ctx)` | Per-turn chat loop (minimal text-only streaming by default; extend for tools) |
| `{{AGENT_CLASS}}.decide_mode(conversation)` | Override reasoning-mode logic |

> The scaffold ships working `handle_command` and `handle_chat`
> implementations in `agent.py`. The chat loop is text-only: it streams a
> single model completion and does **not** execute tool calls. To run tools,
> register `Tool` subclasses on `tools` and extend the `list[ToolCall]` branch
> in `handle_chat` to dispatch through `self.tool_executor`.

Full API docs: [agent_core](https://github.com/EdibleTuber/agent_core)
