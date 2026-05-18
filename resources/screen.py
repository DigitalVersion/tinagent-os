"""
Screen resources — live desktop state readable by agents.
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.resource("screen://current")
    async def current_screen() -> str:
        """Current screenshot of the desktop as base64 PNG."""
        raise NotImplementedError

    @mcp.resource("screen://accessibility")
    async def accessibility_tree() -> str:
        """Current AT-SPI accessibility tree as JSON. Prefer over screenshot."""
        raise NotImplementedError

    @mcp.resource("screen://active-window")
    async def active_window() -> str:
        """Title and geometry of the currently focused window."""
        raise NotImplementedError
