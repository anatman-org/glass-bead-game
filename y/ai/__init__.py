# LOOM-PREFS:
#  edit_mode: full_file
#  typing: strict
#  cli_style: [-i/--input, -o/--output, -F/--format, -Q/--queue, -v/--verbose, --test]
#  tests: doctest + prefs-lint + version-check
#  env: CMD_QUEUE
#  docstring: full + changelog
#  main_callable: true

import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment from .env if present
load_dotenv()


def load_ai_config() -> Dict[str, Any]:
    """
    Loads the AI assistant config from the path in $MY_CONFIG.
    Returns the 'my_ai' section.
    """
    config_path = os.getenv("MY_CONFIG")
    if not config_path:
        raise EnvironmentError("MY_CONFIG not set in environment")
    with open(config_path) as f:
        full = yaml.safe_load(f)
    return full.get("my_ai", {})
