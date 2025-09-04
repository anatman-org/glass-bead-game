#!/usr/bin/env python

from datetime import datetime
from math import log as math_ln, ceil, floor
from os.path import getmtime as os_path_getmtime


from tqdm import tqdm
from cv2 import imread, VideoWriter_fourcc, VideoWriter, resize, error as cv2_error

from PIL import Image as pil_Image
from PIL.PngImagePlugin import PngInfo as pil_PngInfo
from PIL.ExifTags import TAGS as pil_ExifTAGS

from .log import LOG

VID_FILE = "out.mp4"
SIZE = (1920, 1080)
FPS = 24


def sort_files(value):
    return value.split("/")[-1]


def fixed_frame_count(ts, last):
    return 4


def proportional_frame_count(ts, last):

    delta = 1
    count = FPS

    if last:
        delta = ts - last
        try:
            count = int(delta / (60 * 24))
        except (ZeroDivisionError, ValueError):
            count = 1

    if count < 1:
        count = 1
    elif count > FPS:
        count = FPS

    return count


def log_frame_count(ts, last):

    delta = 1
    count = FPS

    if last:
        delta = ts - last
        try:
            count = int(math_ln(delta / FPS))
        except (ZeroDivisionError, ValueError):
            count = FPS

    if count < 1:
        count = 1
    elif count > FPS:
        count = FPS

    return count


def inverse_frame_count(ts, last):

    delta = 0
    count = FPS

    if last:
        delta = ts - last
        try:
            count = math_ln(FPS / delta)
        except (ZeroDivisionError, ValueError):
            count = FPS

    if count < 1:
        count = 1
    elif count > FPS:
        count = FPS

    return count


def get_timestamp(filename):

    try:
        return datetime.strptime(
            filename.split("/")[-1].split(".")[0], "%Y%m%d%H%M%S"
        ).timestamp()
    except ValueError:
        LOG.debug(f"{filename=} timestamp error")

    meta_file = pil_Image.open(filename)
    info = meta_file.info

    if "timestamp" in info:
        return datetime.strptime(info[timestamp], "%Y%m%d%H%M%S").timestamp()

    try:
        exif = {
            pil_ExifTAGS[k]: v
            for k, v in meta_file._getexif().items()
            if k in pil_ExifTAGS
        }
        for k in exif:
            if k.startswith("DateTime"):
                return datetime.strptime(exif[k], "%Y:%m:%d %H:%M:%S").timestamp()
    except AttributeError:
        LOG.debug(f"{filename=} no EXIF")

    return os_path_getmtime(filename)


_FRAME_COUNT_METHOD = inverse_frame_count


def video_from_frames(*args):

    include = []
    exclude = []

    include = [a[1:] for a in args if a[0] == "+"]
    if include:
        args = [a for a in args if a[0] != "+"]

    exclude = [a[1:] for a in args if a[0] == "-"]
    if exclude:
        args = [a for a in args if a[0] != "-"]

    files = sorted([a for a in args], key=get_timestamp)

    codec = VideoWriter_fourcc(*"mp4v")
    video = VideoWriter(VID_FILE, codec, FPS, SIZE)

    last = None
    for f in tqdm(range(len(files)), desc="making video"):

        filename = files[f]
        img = imread(files[f])

        pil = pil_Image.open(filename)

        _force_include = False
        if include:
            for i in include:
                if i in pil.text.keys():
                    LOG.info(f"{filename} include {i}")
                    _force_include = True
                    break

        _exclude = False
        if not _force_include and exclude:
            for i in exclude:
                try:
                    if i in pil.text.keys():
                        LOG.info(f"{filename} exclude {i}")
                        _exclude = True
                        continue
                except (SyntaxError, OSError):
                    break

        if _exclude:
            continue

        try:
            img = resize(img, SIZE)
        except cv2_error:
            LOG.error(f"{filename} resize failure")
            continue

        ts = get_timestamp(filename)

        # SET FRAME METHOD
        frames = int(_FRAME_COUNT_METHOD(ts, last))
        LOG.debug(f"{filename} count={frames:04}")
        for i in range(frames):
            video.write(img)

        last = ts

    video.release()


def main(*args):

    return video_from_frames(*args)


if __name__ == "__main__":
    from sys import argv

    main(*argv[1:])
