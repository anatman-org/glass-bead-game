#!/bin/sh

if [ -f ./.env ]; then
  source ./.env
fi

YT_DLP_FMT="bestvideo[vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best"
YT_DLP_OUT="${QDIR}/%(webpage_url_domain)s/%(id)s=%(title)s.%(ext)s"


#  --restrict-filenames \
#  --replace-in-metadata filename '[^a-zA-Z0-9-]+' '_' \
#  --parse-metadata "%(?P<title>[a-zA-Z0-9-]+)s:%(file_name)s" \
#  --parse-metadata "%(title)+.100U"
#  --parse-metadata "${downloadTimestamp}:%(meta_download_date)s" \
#  --parse-metadata "%(like_count)s:%(meta_likes)s" \
#  --parse-metadata "%(dislike_count)s:%(meta_dislikes)s" \
#  --parse-metadata "%(view_count)s:%(meta_views)s" \
#  --parse-metadata "%(average_rating)s:%(meta_rating)s" \
#  --parse-metadata "%(release_date>%Y-%m-%d,upload_date>%Y-%m-%d)s:%(meta_publish_date)s" \

exec yt-dlp \
  --cookies-from-browser "${YT_DLP_COOKIES}" \
  --add-metadata \
  --sub-lang en \
  --write-sub \
  --write-auto-sub \
  --write-description \
  --write-thumbnail \
  --write-info-json \
  --embed-thumbnail \
  --embed-subs \
  --embed-metadata \
  --ignore-errors \
  --replace-in-metadata title '\.' '' \
  --restrict-filenames \
  --format "${YT_DLP_FMT}" \
  --output "${YT_DLP_OUT}" \
  $@
