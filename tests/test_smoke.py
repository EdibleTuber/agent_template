"""Smoke test: confirm the agent class can be imported and instantiated."""


def test_agent_class_importable():
    from {{agent_pkg}}.agent import {{AGENT_CLASS}}
    assert {{AGENT_CLASS}}.name == "{{AGENT_NAME}}"


def test_agent_can_be_instantiated():
    from {{agent_pkg}}.agent import {{AGENT_CLASS}}
    agent = {{AGENT_CLASS}}()
    assert agent.name == "{{AGENT_NAME}}"


def test_hello_command_registered():
    from {{agent_pkg}}.agent import {{AGENT_CLASS}}
    from {{agent_pkg}}.commands.hello import Hello
    assert Hello in {{AGENT_CLASS}}.commands


def test_cli_client_wired():
    # The CLI client imports and exposes a main() plus a Renderer with the
    # splash/format_message surface agent_core.adapters.cli.run_repl expects.
    from {{agent_pkg}} import cli
    assert callable(cli.main)
    renderer = cli.Renderer()
    assert isinstance(renderer.splash(), str)
    assert renderer.format_message(object()) is None
