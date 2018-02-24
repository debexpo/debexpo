#!/bin/bash
#
#   mass-reimporter.sh - Reimport all the packages from a pool into debexpo
#
#   This file is part of debexpo - https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2012 Nicolas Dandrimont <nicolas.dandrimont@crans.org>
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

set -e
#set -x
shopt -s nullglob

# Debexpo importer scripts with arguments. Should end in -c
IMPORTER="$(dirname "$0")/debexpo_importer.py --skip-email --skip-gpg-check -i /var/www/debexpo/live.ini -c"

# The directory where files are supposed to be uploaded
UPLOAD_DIR=/var/cache/debexpo/incoming

# Forge a changes file for $1 in directory $2. We copy all the
# (supposedly) needed files in $2 before forging the changes file.
forge_changes () {
    dsc_file="$1"
    temp_dir="$2"
    dsc_dir=$(dirname "$dsc_file")
    dsc_root=$(basename "$dsc_file" .dsc)
    cur_dir=$(pwd)

    version=${dsc_root##*_}

    # copy the .dsc and related files
    dcmd cp $dsc_file $temp_dir || return 1

    cd $dsc_dir

    files=(*_${version}_*.deb)

    # copy the other interesting files (.debs)
    for file in "${files[@]}"; do
        cp $file $temp_dir
    done

    dpkg-source -x $dsc_file $temp_dir/extracted >/dev/null

    cd $temp_dir/extracted

    if [ "${#files[@]}" -ne "0" ]; then
        : > debian/files
        for file in "${files[@]}"; do
            section=$(dpkg-deb -f "../$file" Section)
            priority=$(dpkg-deb -f "../$file" Priority)
            echo "$file $section $priority" >> debian/files
        done
        dpkg-genchanges -sa > "../${dsc_root}_forged.changes" 2>/dev/null
    else
        dpkg-genchanges -S -sa > "../${dsc_root}_forged.changes" 2>/dev/null
    fi

    cd $cur_dir

    echo "Generated ${dsc_root}_forged.changes"
}

# Copy the files associated to the $1 changes file into $2. Ugly hack:
# use dput in dry-run mode to get which files would be uploaded...
copy_changes () {
    changes_file="$1"
    destdir="$2"

    dcmd cp "${changes_file}" -v "$destdir"
}

# Forge a changes file for $1 and upload it into $2.
forge_and_upload () {
    dsc_file="$1"
    upload_dir="$2"

    temp_dir=$(mktemp -d /tmp/reimportXXXXXXX)

    forge_changes "${dsc_file}" "${temp_dir}"

    dsc_root=$(basename "$dsc_file" .dsc)
    changes_file="${temp_dir}/${dsc_root}_forged.changes"

    copy_changes "${changes_file}" "${upload_dir}"

    rm -r "${temp_dir}"
}


if [ -z "$1" ]; then
    echo "$0 [debian archive pool]"
    echo
    echo "Reimport the whole debian archive pool into debexpo"
    echo "You should empty the package-related databases first"
    exit 127
fi

find "$1" -name '*.dsc' | while read dsc; do
    dsc_root=$(basename "$dsc" .dsc)
    if forge_and_upload "$dsc" "${UPLOAD_DIR}" ; then
       $IMPORTER "${dsc_root}_forged.changes" || continue
    else
        echo "Skip incomplete package $1"
    fi
done
