"""
Prompt templates — reusable task blueprints for agents.
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.prompt()
    async def web_task(goal: str, url: str | None = None) -> str:
        """Guide an agent to complete a web-based task.
        Starts with navigation if url provided, then pursues goal."""
        start = f"Navigate to {url} first. Then: " if url else ""
        return (
            f"{start}Complete the following web task: {goal}\n\n"
            "Use browser_navigate, browser_click, browser_type, browser_screenshot "
            "to interact. Use browser_get_text to read page content. "
            "Take a screenshot after each major step to verify progress."
        )

    @mcp.prompt()
    async def ui_task(description: str) -> str:
        """Guide an agent to complete a desktop UI task using mouse/keyboard."""
        return (
            f"Complete the following desktop task: {description}\n\n"
            "Use screen_screenshot to see the current state. "
            "Use screen_find_element to locate UI elements. "
            "Use input_mouse_click and input_type_text to interact. "
            "Verify each step with a new screenshot before continuing."
        )

    @mcp.prompt()
    async def research_task(topic: str, output_format: str = "markdown") -> str:
        """Guide an agent to research a topic using the browser."""
        return (
            f"Research the following topic: {topic}\n\n"
            f"Output format: {output_format}\n\n"
            "Open the browser, search for relevant information, "
            "read multiple sources, and synthesize findings. "
            "Use browser_get_text to extract content without screenshots when possible."
        )

    @mcp.prompt()
    async def file_task(instruction: str, working_dir: str = "~/agent-workspace") -> str:
        """Guide an agent to complete a file system task."""
        return (
            f"Working directory: {working_dir}\n"
            f"Task: {instruction}\n\n"
            "Use system_list_dir to explore, system_read_file to read, "
            "system_write_file to write. Use system_run for complex operations."
        )
