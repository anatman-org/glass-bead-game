#!/bin/sh

UUDIR=uu

lookup() {

  cat lookup.tsv | while read KV; do
    _base=$( echo ${KV} | cut -f 1 -d, )
    _regx=$( echo ${KV} | cut -f 2 -d, )
    echo "$@" | grep "${_regx}" >/dev/null && echo ${_base} && return
  done

} 

while read LINE; do

  _full=$( echo "${LINE}" | grep 'Not Found' | sed -e 's@\[\(.*\)\] Not Found: .*@\1@' )
  if [ -z "${_full}" ]; then
      continue
  fi

  _dir1=$( echo $_full | cut -c -2 )
  _dir2=$( echo $_full | cut -c 3-4 )
  _rest=$( echo $_full | cut -c 5- )

  _orig="${_dir1}/${_dir2}/${_rest}"
  _lfsp="/work/git/lfs/${_orig}"

  _extn=$( file -b --extension "${_lfsp}" | cut -f1 -d/ | sed -e 's/jpeg/jpg/' )
  if [ "${_extn}" == "???" ]; then
    _full_ext=$( file -b "${_lfsp}" )
    _extn=$(lookup "${_full_ext}")
  fi

  if [ -z "${_extn}" ]; then
    _extn="bin"
  fi

  echo -n "Adding ${_lfsp} "
  _hid=$( sha256sum "${_lfsp}" | cut -f 1 -d ' ')
  _uid=$( uuidgen -x -n @oid --sha1 -N ${_hid} )
  _ud1=$( echo ${_uid} | cut -c1-2 )
  _ud2=$( echo ${_uid} | cut -c3-4 )

  _dest=${UUDIR}/${_ud1}/${_ud2}/${_uid}.${_extn}
  mkdir -p ${UUDIR}/${_ud1}/${_ud2}

  echo "${_dest}"
  cp "${_lfsp}" ${_dest}

done


