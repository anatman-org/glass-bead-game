import asyncio
from asyncio.exceptions import CancelledError
import argparse
from typing import Type

from . import GlowBase, discover_glow_classes

from dotenv import load_dotenv
import os

load_dotenv("env")
DEFAULT_LAMP = os.getenv("GLOW_LAMP", "192.168.0.1")

glow_classes = discover_glow_classes()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lilt's Glow Rhythm", allow_abbrev=False
    )
    parser.add_argument(
        "--mode",
        choices=list(glow_classes.keys()),
        default="totient",
        help="Select rhythm mode",
    )
    parser.add_argument(
        "--duration", type=float, default=1.0, help="Base duration in seconds"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=DEFAULT_LAMP,
        help="Target device, optionally with outlet index as 'host:idx'",
    )
    args, unknown = parser.parse_known_args()

    # Pass along extra args to subclass create() if supported
    glow_class = glow_classes[args.mode]

    # Instantiate glow
    glow_instance = await glow_class.create(args.device, args.duration, *unknown)

    try:
        if hasattr(glow_class, "create"):
            glow_instance = await glow_class.create(
                args.device, args.duration, *unknown
            )
        else:
            glow_instance = glow_class(args.device, args.duration)

        await glow_instance.glow()

    except (KeyboardInterrupt, CancelledError):
        await glow_instance.outlet.turn_off()


if __name__ == "__main__":
    asyncio.run(main())
