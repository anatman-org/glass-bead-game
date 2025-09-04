#!/usr/bin/env python

import sys
from pathlib import Path
from io import BytesIO, SEEK_SET, SEEK_END
from urllib.parse import urlencode
from json import loads, dumps
from mimetypes import guess_extension

import requests
from splitstream import splitfile

ITER_SIZE = 65536
BASEDIR = Path("qq")


class ResponseStream(object):
    def __init__(self, request_iterator):
        self._bytes = BytesIO()
        self._iterator = request_iterator

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position = self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self):
        return self._bytes.tell()

    def read(self, size=None):
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        self._bytes.seek(left_off_at)
        return self._bytes.read(size)

    def seek(self, position, whence=SEEK_SET):
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)


def main(*_):
    queryargs = "*"

    if len(sys.argv) > 1:
        queryargs = " ".join(sys.argv[1:])

    headers = {"Accept": "application/json", "Accept-Encoding": "gzip, deflate"}
    with requests.get(
        "https://prajna.io", {"qq": queryargs}, stream=True, headers=headers
    ) as r:
        for data in [
            loads(j)
            for j in splitfile(ResponseStream(r.iter_content(ITER_SIZE)), format="json")
        ]:
            _id = data["ID"]

            _path = BASEDIR / Path(_id[:2] + "/" + _id[2:4] + "/" + _id)

            _path.parent.mkdir(parents=True, exist_ok=True)

            print(f"{_path}.json")

            with open(f"{_path}.json", "w") as fjson:
                fjson.write(dumps(data, indent=4))

            if data.get("Body", "").startswith("bin:"):
                ext = guess_extension(data.get("Format", "application/bin")) or ".bin"
                print(f"{_path}{ext}")
                with requests.get(f"https://prajna.io/{_id}/-", stream=True) as b:
                    with open(f"{_path}{ext}", "wb") as fd:
                        for chunk in b.iter_content(chunk_size=ITER_SIZE):
                            fd.write(chunk)


if __name__ == "__main__":
    main()
