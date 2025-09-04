#! python3

"""
a package for managing the loop
"""

from sys import stdin, stdout, stderr, argv
from time import sleep as sleep
from datetime import datetime, UTC
from subprocess import Popen, PIPE

from astral import LocationInfo
from astral.sun import sun as Sun

from .log import LOG
from .config import get_config

LOCATION = LocationInfo(
    "the Shed", "Glass", datetime.now(UTC).astimezone().tzinfo, 44.1326202, -122.9194164
)


def daylight():
    LOG.debug("DAYLUIGHT!")


def main(*args, input_stream=stdin):

    loop = get_config().get("loop")

    while loop_sleep := int(loop.get("sleep")):

        if loop.get("day-only"):
            now = datetime.now().astimezone()
            sun = Sun(LOCATION.observer, now)

            dawn = sun["dawn"]
            dusk = sun["dusk"]

            if not (dawn < now < dusk):
                LOG.debug(f"{now} is not day")
                LOG.debug(f"sleep {loop_sleep}")
                sleep(loop_sleep)
                loop = get_config().get("loop")
                continue
            else:
                LOG.debug(f"{now} is > {dawn} and < {dusk}")

        for cmd in loop.get("cmds").splitlines():

            LOG.debug(f"> {cmd}")
            with Popen(
                f"{cmd}",
                shell=True,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                close_fds=True,
            ) as p:
                for line in p.stdout.readlines():
                    LOG.debug(f"  :{line.decode('utf-8').rstrip()}")

        LOG.debug(f"sleep {loop_sleep}")
        sleep(loop_sleep)
        loop = get_config().get("loop")


if __name__ == "__main__":
    main(*argv[1:])
