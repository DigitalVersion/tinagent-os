#!/usr/bin/env python3
# /// script
# dependencies = ["mcp[cli]", "fastmcp"]
# ///
"""
Tin OS MCP Server — entry point.

Exposes a Kubuntu desktop machine as an MCP endpoint for AI agents.
Transport: SSE (HTTP) so multiple remote agents can connect.

Usage:
    uv run mcp_server.py                  # default port 8765
    uv run mcp_server.py --port 9000
"""

import argparse
from mcp.server.fastmcp import FastMCP

from tools.browser import register as register_browser
from tools.input import register as register_input
from tools.screen import register as register_screen
from tools.system import register as register_system
from tools.audio import register as register_audio
from resources.browser import register as register_browser_resources
from resources.screen import register as register_screen_resources
from resources.system import register as register_system_resources
from prompts.tasks import register as register_prompts

mcp = FastMCP("tinagent-os")

# Register all tools, resources, prompts
register_browser(mcp)
register_input(mcp)
register_screen(mcp)
register_system(mcp)
register_audio(mcp)
register_browser_resources(mcp)
register_screen_resources(mcp)
register_system_resources(mcp)
register_prompts(mcp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    mcp.run(transport="sse", host=args.host, port=args.port)
