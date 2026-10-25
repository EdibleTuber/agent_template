"""{{AGENT_CLASS}} — minimal Agent subclass.

Extension points:
    name (ClassVar)                — short slug, e.g. "{{AGENT_NAME}}"
    env_prefix (ClassVar)          — env-var prefix, derived from name if None
    tools (ClassVar list[type])    — Tool subclasses to register
    commands (ClassVar list[type]) — Command subclasses to register
    disabled_builtins              — names from BUILTIN_TOOLS / BUILTIN_COMMANDS to skip
    setup() override               — construct domain-specific resources
    system_prompt(ctx) override    — build the per-turn system prompt
    handle_command(msg, ctx)       — dispatch slash-commands (wired below)
    handle_chat(msg, ctx)          — per-turn chat loop (wired below)
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from agent_core.agent import Agent, HandlerContext
from agent_core.inference import StreamEnd
from agent_core.protocol.messages import ResponseMessage, StreamChunkMessage

from {{agent_pkg}}.commands.hello import Hello


class {{AGENT_CLASS}}(Agent):
    name = "{{AGENT_NAME}}"
    env_prefix = "{{AGENT_PREFIX}}_"

    tools = []          # add Tool subclasses here
    commands = [Hello]  # framework builtins serve /help, /clear, etc.

    def setup(self) -> None:
        """Construct domain-specific resources here. Framework managers
        (profile, wisdom, channels, inference, retrieval, websearch,
        allowlist, approval_registry, learning, fetcher, config) are
        already populated on self at this point."""
        pass

    def system_prompt(self, ctx: HandlerContext) -> str:
        from pathlib import Path
        # Read the base prompt from prompts/system.md.
        prompt_path = Path(__file__).parent / "prompts" / "system.md"
        base = prompt_path.read_text() if prompt_path.exists() else "You are {{AGENT_CLASS}}."
        pb = self.prompt_builder
        return "\n\n".join(filter(None, [
            base,
            pb.render_profile(),
            pb.render_wisdom(),
            pb.render_scratchpad(ctx.channel_id),
            pb.render_commands_catalog(),
        ]))

    async def handle_command(self, msg, ctx: HandlerContext) -> AsyncIterator:
        """Dispatch a slash-command through the CommandRegistry the framework
        built from self.commands + BUILTIN_COMMANDS. This is what makes
        /help, /clear, and your own commands actually run."""
        async for out in self.command_registry.dispatch(msg.name, msg.args, ctx):
            yield out

    async def handle_chat(self, msg, ctx: HandlerContext) -> AsyncIterator:
        """Minimal text-only chat loop: stream a single model completion.

        Records the turn in the conversation, streams tokens to the client,
        and returns the full text. This intentionally does NOT run a
        tool-calling loop — if the model asks for tools, that is surfaced
        rather than executed. To add tools, register Tool subclasses on
        `tools` and extend the `list[ToolCall]` branch below to dispatch them
        through `self.tool_executor` and feed results back into the model.
        """
        conv = ctx.conversation
        conv.add_user(msg.text)

        mode = self.decide_mode(conv)
        reasoning = mode if mode in ("on", "off") else None

        parts: list[str] = []
        async for item in self.inference.stream(
            conv.get_messages_for_api(self.system_prompt(ctx)),
            reasoning=reasoning,
            max_tokens=self.config.max_response_tokens,
        ):
            if isinstance(item, str):
                parts.append(item)
                yield StreamChunkMessage(token=item)
            elif isinstance(item, StreamEnd):
                self.record_usage(ctx.channel_id, item.usage)
            elif isinstance(item, list):
                # list[ToolCall]: the model asked to call tools. This minimal
                # agent is text-only, so surface the request instead of
                # silently returning nothing.
                names = ", ".join(tc.name for tc in item)
                note = f"[model requested tools ({names}); this minimal agent is text-only]"
                parts.append(note)
                yield StreamChunkMessage(token=note)

        text = "".join(parts)
        conv.add_assistant(text)
        yield ResponseMessage(text=text)
