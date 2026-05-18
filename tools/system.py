"""
System tools — shell commands, file I/O, process management.

TODO (community): implement via subprocess / pathlib.
Security note: run_command should sandbox or allowlist commands in production.
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def system_run(command: str, timeout: int = 30) -> str:
        """Run a shell command. Returns stdout + stderr.
        Warning: no sandboxing in v0.1 — restrict access in production."""
        raise NotImplementedError

    @mcp.tool()
    async def system_read_file(path: str) -> str:
        """Read a file and return its contents as text."""
        raise NotImplementedError

    @mcp.tool()
    async def system_write_file(path: str, content: str) -> str:
        """Write text content to a file. Creates parent dirs if needed."""
        raise NotImplementedError

    @mcp.tool()
    async def system_list_dir(path: str) -> str:
        """List directory contents. Returns JSON array of {name, type, size}."""
        raise NotImplementedError

    @mcp.tool()
    async def system_launch_app(app: str, args: list[str] | None = None) -> str:
        """Launch a desktop application by name (e.g. 'google-chrome', 'dolphin').
        Uses subprocess.Popen, non-blocking."""
        raise NotImplementedError

    @mcp.tool()
    async def system_kill_process(name: str) -> str:
        """Kill all processes matching name. Uses pkill."""
        raise NotImplementedError
