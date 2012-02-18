#!/bin/bash
#
#   mass-reimporter.sh - Reimport all the packages from a pool into debexpo
#
#   This file is part of debexpo - http://debexpo.workaround.org
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

# Debexpo importer scripts with arguments. Should end in -c
IMPORTER="$(dirname "$0")/debexpo_importer.py --skip-email --skip-gpg-check -i development.ini -c"

# The directory where files are supposed to be uploaded
UPLOAD_DIR=$(dirname "$0")/../../tmp/

# Forge a changes file for $1 in directory $2. We copy all the
# (supposedly) needed files in $2 before forging the changes file.
forge_changes () {
    dsc_file="$1"
    temp_dir="$2"
    dsc_dir=$(dirname "$dsc_file")
    dsc_root=$(basename "$dsc_file" .dsc)
    cur_dir=$(pwd)

    find $dsc_dir -maxdepth 1 -type f | while read file; do
        cp $file $temp_dir
    done

    dpkg-source -x $dsc_file $temp_dir/extracted

    cd $temp_dir/extracted
    fakeroot dh_gencontrol
    mv debian/files debian/files.tmp
    cat debian/files.tmp | while read deb section priority; do
        deb_noarch="${deb%_*.deb}"
        shopt -s nullglob
        files=(../${deb_noarch}*.deb)
        if [ "${#files[@]}" -eq 0 ]; then
            file=$deb
        else
            file=$(basename "${files[0]}")
        fi
        echo "$file $section $priority" >> debian/files
    done
    if ! dpkg-genchanges > "../${dsc_root}_forged.changes"; then
        echo "!!! dpkg-genchanges for ${dsc_root} failed, a .deb is surely missing. Trying to fake a source-only upload"
        dpkg-genchanges -S > "../${dsc_root}_forged.changes"
    fi
    cd $cur_dir
}

# Copy the files associated to the $1 changes file into $2. Ugly hack:
# use dput in dry-run mode to get which files would be uploaded...
copy_changes () {
    changes_file="$1"
    destdir="$2"

    dput -u -s "${changes_file}" | awk '/Uploading/{print $4}' | while read f; do
        cp "$f" "$destdir"
    done
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
    forge_and_upload "$dsc" "${UPLOAD_DIR}"
    $IMPORTER "${dsc_root}_forged.changes" >/dev/null 2>/dev/null
done
