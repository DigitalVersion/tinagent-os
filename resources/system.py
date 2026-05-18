"""
System resources — machine state readable by agents.
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.resource("system://status")
    async def system_status() -> str:
        """Machine health: CPU, RAM, disk, uptime as JSON."""
        raise NotImplementedError

    @mcp.resource("system://processes")
    async def running_processes() -> str:
        """Top 20 running processes by CPU as JSON."""
        raise NotImplementedError

    @mcp.resource("system://clipboard")
    async def clipboard_content() -> str:
        """Current clipboard content via wl-paste."""
        raise NotImplementedError

    @mcp.resource("system://env")
    async def environment() -> str:
        """Relevant environment variables (DISPLAY, WAYLAND_DISPLAY, HOME, etc.)."""
        raise NotImplementedError
