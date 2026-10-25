"""CLI client for {{AGENT_CLASS}}.

Connects a terminal REPL to a running {{AGENT_NAME}} daemon over its Unix
socket. Start the daemon first (``python -m {{agent_pkg}}``), then run this in
another terminal:

    python -m {{agent_pkg}}.cli      # or the installed `{{AGENT_NAME}}-cli` script

The REPL (agent_core.adapters.cli.run_repl) is a library, not an entry point of
its own: it needs a Renderer and the daemon's socket path, both wired up here.
The socket path is derived the same way the daemon derives it, by loading the
agent's config — so the two always agree.
"""
from __future__ import annotations

import asyncio
import os

from agent_core.adapters.cli import run_repl
from agent_core.config import BaseConfig, load_config

from {{agent_pkg}}.agent import {{AGENT_CLASS}}


class Renderer:
    """Minimal Renderer: a start-up banner plus default message formatting.

    `format_message` returns None for every message, which tells run_repl to
    fall back to agent_core's default rendering for the generic message types
    (StreamChunk, Response, Error, ToolProgress, ...). Override it to render
    agent-specific message types your agent emits.
    """

    def splash(self) -> str:
        return "{{AGENT_CLASS}} — type /help for commands, Ctrl-D to exit."

    def format_message(self, msg: object) -> str | None:
        return None


def main() -> None:
    config = load_config(
        BaseConfig,
        agent_name={{AGENT_CLASS}}.name,
        env_prefix={{AGENT_CLASS}}.env_prefix,
    )
    asyncio.run(run_repl(config.socket_path, Renderer(), cwd=os.getcwd()))


if __name__ == "__main__":
    main()
