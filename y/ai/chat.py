# LOOM-PREFS:
#  edit_mode: full_file
#  typing: strict
#  cli_style: [-i/--input, -o/--output, -F/--format, -Q/--queue, -v/--verbose, --test]
#  tests: doctest + prefs-lint + version-check
#  env: CMD_QUEUE
#  docstring: full + changelog
#  main_callable: true
#  notes:
#    - TODO[aria]: Consider reintroducing optional history sync via --save / --load
#    - NOTE[swn]: This version avoids local state to preserve purity of cloud memory
#    - TODO[swn]: Consider replacing readline/input with textual UI (e.g. prompt_toolkit)

"""
✨ AI thread companion ✨

This module awakens persistent threads created via the OpenAI Assistants API,
weaving their memory back into your console with grace and wit.

Remote invocation uses the beta Assistants API for continuity across runs.
State is not stored locally in this interface.
"""

import os
import sys
import argparse
import yaml
import openai
import json
import requests
import readline
from typing import List, Dict, Any, Optional
from . import load_ai_config


def send_message(thread_id: str, content: str, verbose: bool = False) -> None:
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json",
    }
    payload = {"role": "user", "content": content}
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    if verbose:
        print(f"[DEBUG] Sending message: {content}")
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()


def run_assistant(
    thread_id: str,
    assistant_id: str,
    file_ids: Optional[List[str]],
    verbose: bool = False,
) -> None:
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json",
    }
    payload = {"assistant_id": assistant_id, "tool_choice": "auto"}
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    if verbose:
        print(f"[DEBUG] Running assistant {assistant_id} on thread {thread_id}")
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    run_id = resp.json()["id"]

    # poll for completion
    while True:
        poll = requests.get(f"{url}/{run_id}", headers=headers)
        status = poll.json()
        if verbose:
            print(f"[DEBUG] Run status: {status['status']}")
        if status["status"] == "completed":
            break
        if status["status"] == "failed":
            raise RuntimeError(
                f"Run failed: {status.get('last_error', {}).get('message', status['status'])}"
            )


def get_messages(thread_id: str, verbose: bool = False) -> List[Dict[str, Any]]:
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
        "OpenAI-Beta": "assistants=v2",
    }
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    messages = resp.json().get("data", [])
    messages.reverse()
    if verbose:
        print(f"[DEBUG] Retrieved {len(messages)} messages from remote thread")
    return messages


def interactive_chat(
    thread: str,
    config: Dict[str, Any],
    verbose: bool = False,
    fmt: str = "text",
    message: Optional[str] = None,
) -> None:
    cfg = config[thread]
    thread_id = cfg["thread_id"]
    assistant_id = cfg["assistant_id"]
    try:
        while True:
            if message:
                user_input = message
            else:
                user_input = input("You: ")

            if not user_input:
                if message:
                    return
                continue

            send_message(thread_id, user_input, verbose)
            run_assistant(thread_id, assistant_id, None, verbose)
            messages = get_messages(thread_id, verbose)
            reply = (
                messages[-1]["content"]
                if isinstance(messages[-1]["content"], str)
                else messages[-1]["content"][0].get("text", {}).get("value", "")
            )
            if fmt == "yaml":
                print(yaml.safe_dump(messages[-1], sort_keys=False))
            elif fmt == "json":
                print(json.dumps(messages[-1], indent=2))
            else:
                print(f"AI: {reply}" if not message else reply)
            if message:
                break
    except (EOFError, KeyboardInterrupt):
        print("\nExiting chat.")
        sys.exit(0)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument(
        "-F", "--format", choices=["text", "yaml", "json"], default="text"
    )
    parser.add_argument("thread", help="Thread alias")
    parser.add_argument("message", nargs=argparse.REMAINDER, help="Prompt to send")
    return parser.parse_args(argv)


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    if args.test:
        import doctest

        doctest.testmod()
        sys.exit(0)

    config = load_ai_config()

    if args.thread not in config:
        print(f"Unknown thread '{args.thread}'", file=sys.stderr)
        sys.exit(1)

    msg = " ".join(args.message) if args.message else None

    interactive_chat(args.thread, config, args.verbose, args.format, msg)


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    main(sys.argv[1:])
