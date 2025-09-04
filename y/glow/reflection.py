import asyncio
import sys
from typing import Optional, TextIO

from .mirror import MirrorGlow


class ReflectionGlow(MirrorGlow):
    """
    🪞🗣️ ReflectionGlow: a Mirror that speaks back

    Inherits MirrorGlow, adds the ability to write reflections to a given file or stdout.
    Each command read produces a poetic or symbolic utterance.
    """

    def __init__(
        self,
        outlet,
        base_duration: float,
        source: Optional[TextIO] = None,
        sink: Optional[TextIO] = None,
    ):
        super().__init__(outlet, base_duration, source)
        self.sink = sink or sys.stdout

    @classmethod
    async def create(cls, outlet_spec, base_duration: float, *unknown):
        outlet = await cls.parse_outlet_spec(outlet_spec)

        # Parse optional file output
        path = None
        if "--file_out" in unknown:
            idx = unknown.index("--file_out")
            try:
                path = unknown[idx + 1]
            except IndexError:
                print("⚠️ '--file_out' specified without filename")

        sink = open(path, "a") if path else None
        return cls(outlet, base_duration, sink=sink)

    async def glow(self) -> None:
        print("🪞🗣️ ReflectionGlow listening and responding")
        base = self.base
        loop = asyncio.get_event_loop()

        responses = {
            "reflect": "I remember the shape of your silence.",
            "reverse": "You are what you reflect, not what you intend.",
            "asymmetry": "Even your flaws have geometry.",
            "rest": "In stillness, we return to pattern.",
        }

        while True:
            line = await loop.run_in_executor(None, self.source.readline)
            if not line:
                await self.sleep(base * 2.0)
                continue

            cmd = line.strip().lower()
            await super().glow()  # still run the visual effect

            phrase = responses.get(cmd, f"Unknown impulse: {cmd}")
            print(f"✍️  Reflecting: {phrase}", file=self.sink)
            self.sink.flush()
