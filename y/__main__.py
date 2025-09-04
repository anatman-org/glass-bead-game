#!/usr/bin/env python
# LOOM-PREFS:
#  edit_mode: full_file
#  typing: strict
#  cli_style: [-i/--input, -o/--output, -F/--format, -v/--verbose, --test]
#  tests: doctest + prefs-lint + version-check
#  env: CMD_QUEUE
#  docstring: full + changelog
#  main_callable: true

"""my – Smart launcher with *alias* expansion & optional shell aliases
=============================================================================
This launcher supports the following:
- Command aliases defined in a YAML config (via MY_CONFIG env)
- Shell-command execution with '!' prefix
- Module execution via y.<tool> or y.<tool>.__main__
- Interpolation of $1, $2..., $VAR, and built-ins like %(cwd)s
- Entry into REPL if no args provided

TODO:
- Add REPL support using prompt_toolkit or readline
- Add tracing/debug verbosity
- Prefer main() in modules before run_module fallback
- List available tools/aliases/shells
"""

import argparse
import importlib
import logging
import os
import pkgutil
import runpy
import shlex
import shutil
import subprocess
import sys
import warnings
from datetime import date
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List

import yaml
from . import load_config

# CLI argument parsing
parser = argparse.ArgumentParser(
    description="✨ Smart launcher for y-tools and shell aliases",
    epilog="Use -v/-vv/-vvv for verbosity. Aliases come from $MY_CONFIG.",
)
parser.add_argument("tool", nargs="?", help="Tool, alias, or builtin (e.g. list-tools)")
parser.add_argument(
    "args", nargs=argparse.REMAINDER, help="Arguments to pass to the tool"
)
parser.add_argument(
    "-v",
    dest="verbosity",
    action="count",
    default=0,
    help="Increase verbosity (-v, -vv, -vvv)",
)
args_ns = parser.parse_args()

# Setup logging
LOG_LEVEL = logging.WARNING - 10 * min(args_ns.verbosity, 2)
logging.basicConfig(level=LOG_LEVEL, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("y")

# Always fail on uncaught exceptions
sys.excepthook = lambda typ, val, tb: (_ for _ in ()).throw(val)

# Built-in variables
_BUILTINS = {"date": date.today().isoformat(), "cwd": os.getcwd()}

BUILTINS: Dict[str, Callable[[], None]] = {}


def _load_aliases() -> Dict[str, str]:
    cfg = os.getenv("MY_CONFIG")
    if not cfg:
        logger.info("MY_CONFIG not set; no aliases loaded.")
        return {}
    path = Path(cfg).expanduser()
    if not path.exists():
        logger.warning(f"Alias config file not found: {path}")
        return {}
    try:
        data = yaml.safe_load(path.read_text()) or {}
        logger.debug(f"Loaded aliases from {path}")
    except Exception as e:
        logger.error(f"Error loading aliases: {e}")
        return {}
    return data.get("my_aliases", {})


def _interpolate(tokens: List[str], user_args: List[str]) -> List[str]:
    env = os.environ.copy()
    out: List[str] = []
    for tok in tokens:
        if tok.startswith("$") and tok[1:].isdigit():
            idx = int(tok[1:]) - 1
            if 0 <= idx < len(user_args):
                out.append(user_args[idx])
            continue
        if tok.startswith("${") and tok.endswith("}"):
            out.append(env.get(tok[2:-1], ""))
            continue
        if tok.startswith("$") and tok[1:].isidentifier():
            out.append(env.get(tok[1:], ""))
            continue
        if "%(" in tok:
            tok = tok % _BUILTINS
        out.append(tok)
    logger.debug(f"Interpolated tokens: {out}")
    return out


def _is_shell_alias(text: str) -> bool:
    return text.lstrip().startswith("!")


def _import_tool_module(name: str) -> ModuleType | None:
    base = "y"
    for mod in (f"{base}.{name}", f"{base}.{name}.__main__"):
        try:
            return importlib.import_module(mod)
        except ModuleNotFoundError:
            continue
    return None


def _run_tool_module(mod: ModuleType, args: List[str]) -> None:
    if hasattr(mod, "main") and callable(mod.main):
        logger.info(f"Invoking {mod.__name__}.main()")
        mod.main(*args)
    else:
        logger.info(f"Falling back to run_module: {mod.__name__}")
        sys.argv = [sys.argv[0], *args]
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"'.*' found in sys.modules after import of package 'y",
                category=RuntimeWarning,
            )
            runpy.run_module(mod.__name__, run_name="__main__")


def _builtin_list_tools() -> None:
    from importlib.util import find_spec

    try:
        import y

        for _, modname, ispkg in pkgutil.iter_modules(y.__path__):
            label = "package" if ispkg else "module"
            print(f"{modname:<20} {'python':<12} {label:<40}")
    except Exception as e:
        logger.warning(f"Error listing y tools: {e}")
    for cmd in ("bash", "zsh", "fish", "sh", "zsh"):
        if shutil.which(cmd):
            print(f"{cmd:<20} {'shell':<12} system")
    for name in _load_aliases():
        print(f"{name:<20} {'alias':<12} alias")
    for builtin in BUILTINS:
        print(f"{builtin:<20} {'builtin':<12} builtin")
    print()


# Register built-in commands
BUILTINS["list-tools"] = _builtin_list_tools


def _start_repl() -> None:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter

    aliases = _load_aliases()
    words = list(BUILTINS.keys()) + list(aliases.keys())

    try:
        import y

        words += [name for _, name, _ in pkgutil.iter_modules(y.__path__)]
    except Exception:
        pass

    session = PromptSession("y> ")
    completer = WordCompleter(words, ignore_case=True)

    while True:
        try:
            line = session.prompt(completer=completer)
            args = shlex.split(line)
            if not args:
                continue
            sys.argv = [sys.argv[0], *args]
            main()
        except (EOFError, KeyboardInterrupt):
            print("Goodbye.")
            break


def main() -> None:

    try:
        if not args_ns.tool:
            logger.info("Entering REPL mode")
            _start_repl()
            sys.exit(0)

        first = args_ns.tool
        rest = args_ns.args

        if first in BUILTINS:
            BUILTINS[first]()
            sys.exit(0)

        aliases = _load_aliases()

        if first in aliases:
            raw_alias = aliases[first]
            shell_mode = _is_shell_alias(raw_alias)
            if shell_mode:
                raw_alias = raw_alias.lstrip()[1:]
            alias_tokens = shlex.split(raw_alias)
            expanded = _interpolate(alias_tokens, rest)
            if expanded and expanded[0] in aliases:
                sys.stderr.write(f"[alias] Recursive alias detected: {first}\n")
                sys.exit(1)
            if shell_mode:
                cmd = " ".join([*expanded, *rest])
                logger.info(f"Executing shell alias: {cmd}")
                subprocess.run(
                    cmd, shell=True, env=os.environ.copy(), executable="/bin/bash"
                )
                return
            args = [*expanded, *rest]
            first, *rest = args

        mod = _import_tool_module(first)
        if mod:
            _run_tool_module(mod, rest)
            return

        if shutil.which(first):
            logger.info(f"Running shell command: {first} {' '.join(rest)}")
            subprocess.run([first, *rest], check=False, env=os.environ.copy())
        else:
            sys.stderr.write(f"Unknown tool or alias: {first}\n")
            sys.exit(1)

    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    main()
