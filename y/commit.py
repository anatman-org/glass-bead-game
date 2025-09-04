from datetime import datetime
import subprocess
from ._chinese import ChineseHouse


def check_modified():
    proc = subprocess.Popen(["git", "status"], stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if not line:
            return False

        if (
            line.startswith(b"\tmodified:   ")
            or line.startswith(b"\tdeleted:")
            or line.startswith(b"\trenamed:")
            or line.startswith(b"\tnew file:")
        ):
            return True

    return False


def main(*args):
    house = ChineseHouse(ChineseHouse.play())
    composition = house.composition

    if not check_modified():
        return True

    house = ChineseHouse(ChineseHouse.play())
    composition = house.composition

    with open("play.log", "a") as play_log:
        # stamp = f"{composition} {datetime.now():%Y%m%d.%H%M%S}"
        stamp = f"{composition}"
        print(stamp)
        play_log.write(stamp + "\n")

    subprocess.run(("git", "commit", "-a", "-q", "-m", composition))

    return False


if __name__ == "__main__":
    from sys import argv

    exit(main(argv[1:]))
