import asyncio
import importlib
import pkgutil
import inspect
import os
from typing import Type, Union

from kasa import Discover, Device
from dotenv import load_dotenv

load_dotenv("env")
DEFAULT_LAMP = os.getenv("ARIA_LAMP", "192.168.0.1")


class GlowBase:
    outlet: Device
    base: float

    @staticmethod
    async def parse_outlet_spec(outlet_spec: Union[str, Device]) -> Device:
        if isinstance(outlet_spec, Device):
            return outlet_spec

        if ":" in outlet_spec:
            hostname, index = outlet_spec.split(":", 1)
            index = int(index)
        else:
            hostname = outlet_spec
            index = 0

        async def resolve():
            dev = await Discover.discover_single(hostname)
            await dev.update()
            return dev.children[index] if dev.children else dev

        return await resolve()

    def __init__(self, outlet: Device, base_duration: float):
        self.outlet = outlet
        self.base = base_duration

    @classmethod
    async def create(
        cls, outlet_spec: Union[str, Device], base_duration: float, *_
    ) -> "GlowBase":
        outlet = await cls.parse_outlet_spec(outlet_spec)
        return cls(outlet, base_duration)

    async def sleep(self, seconds: float):
        await asyncio.sleep(seconds * self.base)

    async def glow(self) -> None:
        raise NotImplementedError("Subclasses must implement the glow method.")


def discover_glow_classes() -> dict[str, Type[GlowBase]]:

    glow_classes: dict[str, Type[GlowBase]] = {}

    for _, modname, ispkg in pkgutil.iter_modules(__path__):
        if ispkg or modname.startswith("_"):
            continue

        module = importlib.import_module(f"{__name__}.{modname}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, GlowBase) and obj is not GlowBase:
                glow_classes[modname] = obj

    return glow_classes
