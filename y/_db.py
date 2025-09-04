from pathlib import Path
from os import environ
from sqlite3 import connect as sqlite_connect, OperationalError
from sqlite3.__main__ import main

from dotenv import load_dotenv

load_dotenv()
UUID_DIR_BASE = Path(environ.get("UU_BASE", Path.cwd() / "uu")).resolve()

_DB_PATH = f"{UUID_DIR_BASE}/index.sqlite"
DB = sqlite_connect(_DB_PATH)

try:
    DB.execute(
        "CREATE TABLE files ( dt TEXT, host TEXT, hash TEXT, uu TEXT, mime TEXT, path TEXT )"
    )
except OperationalError:  # table exists
    pass

try:
    DB.execute("CREATE TABLE tags ( uu TEXT, tag TEXT )")
except OperationalError:  # table exists
    pass

if __name__ == "__main__":
    from sys import argv

    main([_DB_PATH, *argv[1:]])
