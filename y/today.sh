#!/bin/sh

cd /work/media/Play/Today

TODAY=$( date +"%Y-%m-%d" )

find ../../Shows -name '*.info.json' -newermt ${TODAY} | \
  while read VID_INFO; do

    VID_BASE=${VID_INFO/.info.json/}

    CHANNEL=$( jq -r .channel < ${VID_INFO} | tr -d '/' )
    TITLE=$( jq -r .title < ${VID_INFO} | tr -d '/' )
    LINK="${TODAY} ${CHANNEL} - ${TITLE}.mp4"

    echo "${LINK} => ${VID_BASE}.mp4"
    ln -s "${VID_BASE}.mp4" "${LINK}"
    # rename 's/[<>:"\\|?*]/_/g' "${LINK}"

  done


