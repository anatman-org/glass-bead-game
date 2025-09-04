import webview

from y.web import app
from y.log import LOG


def main(*args):
    webview.create_window(
        " ".join(args),
        app,
        frameless=True,
        transparent=True,
        width=1920,
        height=1080,
        x=0,
        y=0,
    )

    # window = webview.create_window(
    #    "", url="play.html", js_api=play_api, fullscreen=True, frameless=True
    # )

    debug = False
    if "debug" in argv:
        debug = True

    webview.start(debug=debug, http_port=9876)


if __name__ == "__main__":
    from logging import DEBUG
    from sys import argv

    if "debug" in argv:
        LOG.setLevel(DEBUG)

    main(*argv[0:])
