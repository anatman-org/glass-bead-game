# LOOM-PREFS:
#  edit_mode: full_file
#  typing: strict
#  cli_style: [-i/--input, -o/--output, -F/--format, -Q/--queue, -v/--verbose, -t/--thread, --all, --since]
#  tests: doctest + prefs-lint + version-check
#  env: MY_CONFIG, QDIR
#  docstring: full
#  main_callable: true
#  notes:
#    - TODO[Lilt]: implement upload
#    - TODO[Lilt]: implement download with filename formatter in `-o/--output` or default to original filename in $QDIR
#    - TODO[Lilt]: Catch pagination limits and explicitly walk through messages.list() using cursors.
#    - TODO[Lilt]: Wrap all thread fetches in backoff+retry wrappers with jitter.
#    - TODO[Lilt]: Create a thread health-check mode to preflight size, last activity, rate limit headers, etc.
#    - TODO[Aria]: reconcile webui and cli tool file_ids

import os
import sys
import argparse
import json
import yaml
from datetime import datetime, timezone
from typing import Optional, Union
from openai import OpenAI
from y.ai import load_ai_config
from fnmatch import fnmatch

client = OpenAI()


def iso8601(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def export_thread(
    thread_id: str, outdir: str, name: Optional[str] = None, fmt: str = "yaml"
):
    """Fetch messages from a thread and write to $QDIR/{name}.{ext}, including metadata."""
    thread = client.beta.threads.retrieve(thread_id=thread_id)
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    fname = name or thread_id
    path = os.path.join(outdir, f"{fname}.{fmt}")

    export = {
        "thread_id": thread.id,
        "created_at": iso8601(thread.created_at),
        "metadata": thread.metadata,
        "messages": [],
    }

    for m in reversed(messages.data):
        file_ids = getattr(m, "file_ids", None)
        export["messages"].append(
            {
                "id": m.id,
                "created_at": iso8601(m.created_at),
                "role": m.role,
                "content": m.content[0].text.value.strip(),
                "file_ids": file_ids,
            }
        )

    with open(path, "w") as f:
        if fmt == "json":
            json.dump(export, f, indent=2)
        elif fmt == "txt":
            for msg in export["messages"]:
                f.write(
                    f"[{msg['role'].upper()} @ {msg['created_at']}]:\n{msg['content']}\n\n"
                )
        else:
            yaml.dump(export, f, sort_keys=False)


def resolve_thread_id(name_or_id: str, config: dict) -> Optional[str]:
    if name_or_id.startswith("thread_"):
        return name_or_id
    entry = config.get(name_or_id)
    if isinstance(entry, dict):
        return entry.get("thread_id")
    return None


def action_export(args, config):
    outdir = os.getenv("QDIR") or "."
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    thread_args = args.thread or []
    if args.all:
        thread_args.extend(
            k for k, v in config.items() if isinstance(v, dict) and "thread_id" in v
        )

    if not thread_args:
        raise ValueError("Must provide at least one thread name/ID")

    if args.since:
        try:
            since_time = datetime.fromisoformat(args.since).timestamp()
        except ValueError:
            if os.path.exists(args.since):
                since_time = os.path.getmtime(args.since)
            else:
                raise ValueError(
                    "--since must be a date (YYYY-MM-DD) or valid file path"
                )
    else:
        since_time = 0

    for name in thread_args:
        tid = resolve_thread_id(name, config)
        if not tid:
            raise ValueError(f"Could not resolve thread: {name}")
        thread = client.beta.threads.retrieve(thread_id=tid)
        if thread.created_at < since_time:
            if args.verbose:
                print(f"[DEBUG] Skipping {tid} (created before --since)")
            continue
        base = args.output or name or tid
        if args.verbose:
            print(f"[DEBUG] Exporting {tid} to {outdir} as {base}.{args.format}")
        export_thread(tid, outdir, name=base, fmt=args.format)
        print(f"Exported thread: {name} -> {tid}")


def action_list(args, config):
    threads = []
    for name, entry in config.items():
        if not isinstance(entry, dict):
            continue
        tid = entry.get("thread_id")
        if not tid:
            continue
        if args.filter and not any(
            fnmatch(name, pat) or fnmatch(tid, pat) for pat in args.filter
        ):
            continue
        thread = client.beta.threads.retrieve(thread_id=tid)
        threads.append(
            {
                "name": name,
                "thread_id": thread.id,
                "created_at": iso8601(thread.created_at),
                "metadata": thread.metadata,
            }
        )

    if args.format == "json":
        print(json.dumps(threads, indent=2))
    elif args.format == "yaml":
        print(yaml.dump(threads, sort_keys=False))
    else:
        for t in threads:
            print(f"{t['name']:<16} {t['thread_id']:<36} {t['created_at']}")


def action_list_files(args):
    file_ids = args.file_ids
    if not file_ids:
        files = client.files.list().data
    else:
        files = [client.files.retrieve(file_id=fid) for fid in file_ids]

    if args.format == "json":
        print(json.dumps([f.__dict__ for f in files], indent=2))
    elif args.format == "yaml":
        print(yaml.dump([f.__dict__ for f in files], sort_keys=False))
    else:
        for f in files:
            print(f"{f.id:<28} {f.created_at:<12} {f.filename}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)

    export_parser = subparsers.add_parser("export", help="Export thread(s)")
    export_parser.add_argument("thread", nargs="*", help="Thread name or ID")
    export_parser.add_argument(
        "--all", action="store_true", help="Export all threads in config"
    )
    export_parser.add_argument(
        "--since", help="Date string or file path to filter newer threads"
    )
    export_parser.add_argument(
        "-F", "--format", choices=["yaml", "json", "txt"], default="yaml"
    )
    export_parser.add_argument(
        "-o", "--output", help="Output base name (without extension)"
    )
    export_parser.add_argument("-v", "--verbose", action="store_true")

    list_parser = subparsers.add_parser("list-threads", help="List known threads")
    list_parser.add_argument(
        "filter", nargs="*", help="Optional glob filters (alias or ID)"
    )
    list_parser.add_argument(
        "-F", "--format", choices=["text", "yaml", "json"], default="text"
    )

    file_parser = subparsers.add_parser("list-files", help="List uploaded files")
    file_parser.add_argument(
        "file_ids", nargs="*", help="File ID(s) to show, or empty for all"
    )
    file_parser.add_argument(
        "-F", "--format", choices=["text", "yaml", "json"], default="text"
    )

    args = parser.parse_args(argv)
    config = load_ai_config()

    if args.action == "export":
        action_export(args, config)
    elif args.action == "list-threads":
        action_list(args, config)
    elif args.action == "list-files":
        action_list_files(args)


if __name__ == "__main__":
    main(sys.argv[1:])
