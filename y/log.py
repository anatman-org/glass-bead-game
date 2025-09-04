"""
---
title: log
---

    good hackers
    keep logs

sometimes the only way to fix an error
is to catch one in the act and study it

  and try to replay it slowly in Your head
  step by step

that means keeping a log of things You think
might be helpful when analyzing problems in the future

but the smart hackers
log not just failures but also successes

because sometimes the only way
You can find the solution to a problem

is to see the Way things were without it again
"""

import logging
import warnings
import sys
from os import environ

# logging.captureWarnings(True)
# warnings.filterwarnings("ignore", category=DeprecationWarning)
# warnings.filterwarnings("ignore")


def _init_logger():

    # Create a logger named 'y'
    logger = logging.getLogger("y")

    # Set the threshold logging level of the logger to INFO
    logger.setLevel(logging.INFO)

    if environ.get("DEBUG", False):
        logger.setLevel(logging.DEBUG)

    # Create a stream-based handler that writes the log entries
    # into the standard output stream
    handler = logging.StreamHandler(sys.stdout)

    # Create a formatter for the logs
    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s:%(module)s:%(message)s",
        datefmt="%Y%m%d-%H%M%S%z",
    )

    # Set the created formatter as the formatter of the handler
    handler.setFormatter(formatter)

    # Add the created handler to this logger
    logger.addHandler(handler)


_init_logger()
LOG = logging.getLogger("y")
