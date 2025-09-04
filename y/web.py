from time import sleep
from pathlib import Path
from sys import argv
from random import choice as random_choice
from mimetypes import guess_type as guess_mime_type

from flask import Flask, redirect, request, send_file, current_app, abort

app = Flask(__name__, static_url_path="", static_folder="../w", template_folder="../t")

from y.log import LOG


@app.route("/")
def index():
    return redirect("/index.html")


@app.route("/<path:path>.m3u@<pos>")
def get_video(path, pos="*"):

    m3u = Path(current_app.static_folder) / (path + ".m3u")
    if not m3u.is_file():
        LOG.error(f"No file {m3u}")
        abort(404)

    url_list = [u.strip() for u in m3u.open("r").readlines()]

    try:
        pos = int(pos) % len(url_list)
        new_url = url_list[pos]

    except ZeroDivisionError:
        new_url = url_list[0]

    # new_url = random_choice(url_list)

    LOG.debug(f"redirect @{pos} to {new_url} ")

    return redirect(new_url)


@app.route("/<path:path>@<int(signed=True):num>")
def get_template_img(path, num=0):

    file_list = ()

    base = Path(current_app.static_folder) / path
    if base.is_dir():
        file_list = sorted(list([f for f in base.iterdir() if not f.is_dir()]))
    else:
        file_list = sorted(
            list((Path(current_app.static_folder)).glob(f"{path}*")),
        )

    if len(file_list) == 0:
        LOG.error(f"No files for glob {path}*")
        abort(404)

    try:
        n = int(num) % len(file_list)
    except ZeroDivisionError:
        n = 0

    file_name = file_list[n]
    mime_type = guess_mime_type(file_name)[0]
    LOG.debug(f"@{n} = {file_name} [{mime_type}]")
    try:

        return send_file(
            file_list[n],
            mimetype=mime_type,
        )
    except FileNotFoundError:
        return "", 404


@app.route("/snap")
def get_snap():
    import y.snap

    args = [f"{k}@{request.args.get(k, 0).split('?')[0]}" for k in request.args]

    args += [__name__, *argv[1:]]

    try:
        app_desc = str(app).split("'")[1]
    except IndexError:
        app_desc = str(app)

    snap_result = y.snap.main("-c", "table", app_desc, *args)
    app.logger.warning(f"snap {app_desc} {args=}")
    return "", 204


if __name__ == "__main__":
    from logging import DEBUG

    if "debug" in argv:
        LOG.setLevel(DEBUG)

    app.run(host="0.0.0.0", port=9876)
