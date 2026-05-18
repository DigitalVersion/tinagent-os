"""
Browser resources — live browser state readable by agents.
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.resource("browser://tabs")
    async def browser_tabs() -> str:
        """List of open browser tabs as JSON: [{id, url, title, active}]."""
        raise NotImplementedError

    @mcp.resource("browser://current-url")
    async def current_url() -> str:
        """URL of the currently active browser tab."""
        raise NotImplementedError

    @mcp.resource("browser://page-source")
    async def page_source() -> str:
        """HTML source of the current page."""
        raise NotImplementedError
