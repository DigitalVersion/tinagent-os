"""
Audio tools — PipeWire virtual speaker/mic.

Tin OS ships with a virtual audio loopback (virtual-speaker → virtual-mic).
Useful for TTS output or recording agent-generated audio.

TODO (community): implement via paplay / pw-play / aplay.
"""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def audio_play(file_path: str) -> str:
        """Play an audio file through the virtual speaker.
        Supports WAV, MP3, OGG. Uses paplay or pw-play."""
        raise NotImplementedError

    @mcp.tool()
    async def audio_record(duration_sec: int, output_path: str) -> str:
        """Record audio from the virtual mic for duration_sec seconds.
        Useful for capturing TTS or system audio. Uses pw-record."""
        raise NotImplementedError

    @mcp.tool()
    async def audio_tts(text: str, output_path: str | None = None) -> str:
        """Convert text to speech and play it (or save to file).
        TODO: choose TTS engine — espeak, piper, or external API."""
        raise NotImplementedError
