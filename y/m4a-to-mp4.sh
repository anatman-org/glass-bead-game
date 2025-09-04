#!/bin/sh


for FILE in "$@"; do

  ffmpeg -loop 1 -i cover.jpg \
    -i "${FILE}" \
    -c:v libx264 -vf "scale=640:trunc(ow/a/2)*2" \
    -tune stillimage \
    -c:a aac -b:a 192k -pix_fmt yuv420p -shortest \
    "${FILE/mp3/mp4}"

done
