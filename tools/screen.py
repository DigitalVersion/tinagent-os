"""
Screen tools — screenshot, accessibility tree, element finder.

Priority order (from TinAgentOS config): dbus > cdp > ydotool
For screen reading, prefer accessibility tree over pixel-based OCR.

TODO (community): implement via scrot/grim (Wayland screenshot) + AT-SPI dbus.
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def screen_screenshot() -> str:
        """Capture full desktop screenshot. Returns base64 PNG.
        Uses grim (Wayland) or scrot fallback."""
        raise NotImplementedError

    @mcp.tool()
    async def screen_screenshot_region(x: int, y: int, width: int, height: int) -> str:
        """Capture a region of the screen. Returns base64 PNG."""
        raise NotImplementedError

    @mcp.tool()
    async def screen_get_accessibility_tree() -> str:
        """Return AT-SPI accessibility tree as JSON.
        Preferred over screenshot for reading UI state — less tokens, more precise.
        Uses pydbus + AT-SPI2."""
        raise NotImplementedError

    @mcp.tool()
    async def screen_find_element(label: str) -> str:
        """Find a UI element by accessible name/label. Returns element info + coordinates.
        Uses AT-SPI tree search."""
        raise NotImplementedError

    @mcp.tool()
    async def screen_get_active_window() -> str:
        """Return title and geometry of the currently focused window."""
        raise NotImplementedError
