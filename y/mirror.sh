#!/bin/sh

#  --no-parent \

wget \
  -e robots=off \
  --user-agent "Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-GB; rv:1.9.0.1) Gecko/2008070206 Firefox/3.0.1" \
  --random-wait \
  --wait 3 \
  --mirror \
  --convert-links \
  --adjust-extension \
  --page-requisites \
  --restrict-file-names=nocontrol \
  --content-disposition \
  --directory-prefix=mirror \
  $@

