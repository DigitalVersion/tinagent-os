"""
Input tools — ydotool (Wayland) + wl-clipboard.

IMPORTANT runtime notes (from TinAgentOS config):
  type_text  → wl-copy 'text' && ydotool key ctrl+v   (NOT ydotool type)
  file upload → DOM.setFileInputFiles via CDP          (NOT click upload button)

Requires: ydotoold running, YDOTOOL_SOCKET=/run/ydotoold.socket

TODO (community): implement each stub via subprocess calls to ydotool/wl-copy.
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def input_type_text(text: str) -> str:
        """Type text at current cursor position.
        Uses wl-copy + ydotool ctrl+v (safe for unicode/Vietnamese)."""
        raise NotImplementedError

    @mcp.tool()
    async def input_key_press(keys: str) -> str:
        """Press a key or key combo. E.g. 'ctrl+c', 'Return', 'alt+F4'.
        Uses ydotool key."""
        raise NotImplementedError

    @mcp.tool()
    async def input_mouse_click(x: int, y: int, button: str = "left") -> str:
        """Click mouse at screen coordinates (x, y).
        button: 'left' | 'right' | 'middle'"""
        raise NotImplementedError

    @mcp.tool()
    async def input_mouse_move(x: int, y: int) -> str:
        """Move mouse cursor to screen coordinates (x, y)."""
        raise NotImplementedError

    @mcp.tool()
    async def input_scroll(x: int, y: int, direction: str = "down", clicks: int = 3) -> str:
        """Scroll at coordinates. direction: 'up' | 'down' | 'left' | 'right'."""
        raise NotImplementedError

    @mcp.tool()
    async def clipboard_get() -> str:
        """Read current clipboard content via wl-paste."""
        raise NotImplementedError

    @mcp.tool()
    async def clipboard_set(text: str) -> str:
        """Write text to clipboard via wl-copy."""
        raise NotImplementedError
