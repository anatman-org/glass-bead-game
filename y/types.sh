#!/bin/sh

find $@ -type f | \
  awk -F. '{ print $NF }' | \
  sort | uniq -c


