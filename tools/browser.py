"""
Browser tools — Chrome DevTools Protocol (CDP).
Chrome must be running: google-chrome --remote-debugging-port=9222 ...
See runtime.chrome_cmd in Agentdistro config.

TODO (community): implement each stub using websocket CDP calls.
Recommended lib: pychrome, or raw websockets to ws://localhost:9222
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def browser_navigate(url: str) -> str:
        """Navigate the browser to a URL. Returns page title after load."""
        raise NotImplementedError

    @mcp.tool()
    async def browser_click(selector: str) -> str:
        """Click a DOM element by CSS selector. Returns element outerHTML."""
        raise NotImplementedError

    @mcp.tool()
    async def browser_type(selector: str, text: str) -> str:
        """Type text into a DOM input element. Uses CDP Input.dispatchKeyEvent."""
        raise NotImplementedError

    @mcp.tool()
    async def browser_screenshot() -> str:
        """Capture a screenshot of the current browser tab. Returns base64 PNG."""
        raise NotImplementedError

    @mcp.tool()
    async def browser_eval(js: str) -> str:
        """Execute JavaScript in the current page context. Returns JSON result."""
        raise NotImplementedError

    @mcp.tool()
    async def browser_get_text(selector: str = "body") -> str:
        """Extract visible text from a DOM element (default: full page body)."""
        raise NotImplementedError

    @mcp.tool()
    async def browser_upload_file(selector: str, file_path: str) -> str:
        """Set a file input element to file_path. Uses DOM.setFileInputFiles."""
        raise NotImplementedError

    @mcp.tool()
    async def browser_new_tab(url: str = "about:blank") -> str:
        """Open a new browser tab. Returns new tab's targetId."""
        raise NotImplementedError

    @mcp.tool()
    async def browser_close_tab(target_id: str) -> str:
        """Close a browser tab by targetId."""
        raise NotImplementedError
