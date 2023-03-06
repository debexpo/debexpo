#!/bin/bash
#
#   update-translations.sh - fetch translations from weblate and integrate them
#   into debexpo repository
#
#   This file is part of debexpo
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2023 Baptiste Beauplat <lyknode@debian.org>
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

set -e

export LC_ALL=C.UTF-8
root_dir="$(dirname "$(readlink -f "$0")")/.."
remote_url="https://hosted.weblate.org/git/debexpo/debexpo/"
remote_name="weblate"
update_branch="translation/update"
next_branch="translation/next"
main_branch="live"
work_dir="$(mktemp -d --suffix="-debexpo-weblate-update")"
stat_dir="${work_dir}/stats"
update_dir="${work_dir}/update"
contrib_dir="${work_dir}/contributors"
next_todo="${work_dir}/next"
contributors_file="${root_dir}/AUTHORS"

check_requirements() {
    if ! command -v git > /dev/null; then
        fatal "git: command not found"
    fi

    if ! command -v msgcat > /dev/null; then
        fatal "msgcat: command not found (package: gettext)"
    fi
}

fatal() {
    echo "fatal: ${@}" 1>&2
    exit 1
}

abort_on_unclean_repo() {
    echo "Check repository status"

    if [[ "$(git status --porcelain | wc -l)" != "0" ]]; then
        fatal "Repository is not clean, aborting"
    fi
}

add_weblate_remote() {
    if git remote show | grep -q "${remote_name}"; then
        return
    fi

    git remote add "${remote_name}" "${remote_url}"
}

fetch_weblate() {
    echo "Fetch weblate updates"

    git branch -D "${update_branch}" "${next_branch}" > /dev/null || true
    git fetch "${remote_name}" "${main_branch}:${update_branch}" \
        "${main_branch}:${next_branch}" > /dev/null 2>&1
}

read_translation_stats() {
    messages_total=0
    messages_translated=""

    while read -r -d ' ' stat; do
        [[ "${stat}" =~ ^[0-9]+$ ]] || continue
        [[ -z "${messages_translated}" ]] && messages_translated="${stat}"
        messages_total="$((messages_total + stat))"
    done

    translated="$((messages_translated * 100 / messages_total))"
}

select_translations() {
    echo "Select translated languages"

    translations=()
    mkdir -p "${stat_dir}"
    (cd "${root_dir}" && git archive "${update_branch}") | \
        tar -x -C "${stat_dir}"
    readarray -t po_files < <(find "${stat_dir}/debexpo/" -name '*.po')

    while read -r language; do
        readarray -t current_po < <(printf '%s\n' "${po_files[@]}" |
                                    grep -F "/${language}/LC_MESSAGES/")
        read_translation_stats < <(msgcat --use-first "${current_po[@]}" |
                                   msgfmt --statistics - 2>&1)
        [[ "${translated}" -ge "95" ]] && translations+=("${language}") || true
    done < <(printf '%s\n' "${po_files[@]}" | rev | cut -d / -f 3 | rev |
             sort -u)
}

assert_valid_commit() {
    # Drop non-languages files commit
    if grep -q -v LC_MESSAGES/django.po < \
            <(git diff-tree --no-commit-id --name-only -r "${rev}"); then
        fatal "commit ${rev} contains non-languages files"
    fi

    # Drop multi-language commit
    if [[ "$(echo "${language}" | wc -l)" != "1" ]]; then
        fatal "commit ${rev} contains multiple languages"
    fi
}

filter_excluded_language_commit() {
    # Drop non selected languages
    if ! grep -q -e "^${language}\$" < \
            <(printf '%s\n' "${translations[@]}"); then
        return 0
    fi

    return 1
}

squash_commit_if_possible() {
    # Check language creation and squash
    if [[ "${subj}" =~ ^Added ]]; then
        return 0
    fi

    # Check email and squash
    if [[ "${email}" = "${prev_email}" || \
          "${prev_email}" = "noreply@weblate.org" ]]; then
        return 0
    fi

    return 1
}

build_rebase_todo() {
    # Todo for update branch
    echo "${outcome} ${rev}" >> "${update_dir}/${language}"

    # Todo for next branch
    if [[ "${outcome}" = "drop" ]]; then
        echo "pick ${rev}" >> "${next_todo}"
    else
        echo "drop ${rev}" >> "${next_todo}"
    fi
}

set_contributor_stats() {
    contrib_hash="$(echo "${email}" | sha1sum | cut -d ' ' -f 1)"
    contrib_language="${contrib_dir}/${contrib_hash}/languages"
    contrib_year="${contrib_dir}/${contrib_hash}/years"

    if [[ "${email}" = "noreply@weblate.org" ]]; then
        return
    fi

    if [[ ! -d "${contrib_dir}/${contrib_hash}" ]]; then
        mkdir -p "${contrib_dir}/${contrib_hash}"
        echo "${name} <${email}>" > "${contrib_dir}/${contrib_hash}/name"
        touch "${contrib_language}"
        touch "${contrib_year}"
    fi

    if [[ -n "${language}" ]]; then
        if ! grep -q -e "^${language}\$" "${contrib_language}"; then
            echo "${language}" >> "${contrib_language}"
        fi
    fi

    if [[ -n "${year}" ]]; then
        if ! grep -q -e "^${year}\$" "${contrib_year}"; then
            echo "${year}" >> "${contrib_year}"
        fi
    fi
}

parse_one_commit() {
    year="$(git log --format=%as -n 1 "${rev}" | cut -d '-' -f 1)"
    email="$(git log --format=%ae -n 1 "${rev}")"
    name="$(git log --format=%an -n 1 "${rev}")"
    language="$(git diff-tree --no-commit-id --name-only -r "${rev}" |
                rev | cut -d / -f 3 | rev | sort -u)"
    outcome="pick"

    assert_valid_commit
    filter_excluded_language_commit && outcome="drop" || true

    if [[ -n "${prev[${language}]}" ]]; then
        subj="$(git log --format=%s -n 1 "${rev}")"
        prev_subj="$(git log --format=%s -n 1 "${prev[${language}]}")"
        prev_email="$(git log --format=%ae -n 1 "${prev[${language}]}")"

        if [[ "${subj}" = "${prev_subj}" || \
              "${prev_email}" = "noreply@weblate.org" ]]; then
            squash_commit_if_possible && outcome="fixup" || true
        fi
    fi

    build_rebase_todo

    if [[ "${outcome}" != "drop" ]]; then
        prev[${language}]="${rev}"
        set_contributor_stats
    fi
}

rebase_branches() {
    echo "Rebase ${update_branch} on ${main_branch}"

    GIT_SEQUENCE_EDITOR="cat ${update_dir}/* >" git rebase -i \
        "${main_branch}" "${update_branch}" > /dev/null 2>&1

    update_contributors

    echo "Rebase ${next_branch} on ${update_branch}"

    GIT_SEQUENCE_EDITOR="cat ${next_todo} >" git rebase -i \
        "${update_branch}" "${next_branch}" > /dev/null 2>&1

    echo "Switch to ${update_branch} branch"

    git checkout "${update_branch}"
}

parse_commits() {
    echo "Build rebase todo"

    declare -A prev

    mkdir -p "${update_dir}"

    while read -r rev; do
        parse_one_commit
    done < <(git rev-list "${main_branch}..${update_branch}" | tac)
}

commit_new_contributors_file() {
    git add "${contributors_file}"
    git commit -m "Update AUTHORS file with translators" > /dev/null
}

hash_one_contributor() {
    name="$(echo "${line}" | cut -d ' ' -f 4- | cut -d '<' -f 1 | head -c -2)"
    email="$(echo "${line}" | cut -d '<' -f 2 | cut -d '>' -f 1)"
    years=($(echo "${line}" | cut -d ' ' -f 3 | tr '-' ' '))
    languages=($(echo "${line}" | cut -d '>' -f 2 | tr -d '(),'))
    year=""

    for language in "${languages[@]}"; do
        set_contributor_stats
    done

    language=""
    for year in "${years[@]}"; do
        set_contributor_stats
    done
}

hash_existing_contributors() {
    csplit "--prefix=${contributors_file}." "${contributors_file}" \
        '/^Translators$/1' > /dev/null

    while read -r line; do
        hash_one_contributor
    done < <(tail -n +3 "${contributors_file}.01")

    rm -f "${contributors_file}.01"
}

reset_contributors_file() {
    mv -f "${contributors_file}.00" "${contributors_file}"

    echo -e "-----------\n" >> "${contributors_file}"
}

get_contrib_years() {
    if [[ "$(wc -l "${contrib_hash}/years" | cut -d ' ' -f 1)" = "1" ]]; then
        cat "${contrib_hash}/years"
    else
        year_start="$(sort -n "${contrib_hash}/years" | head -1)"
        year_end="$(sort -n "${contrib_hash}/years" | tail -1)"

        echo "${year_start}-${year_end}"
    fi
}

get_contrib_languages() {
    first="1"

    while read -r language; do
        if [[ "${first}" = 0 ]]; then
            echo -n ", "
        else
            first="0"
        fi

        echo -n "${language}"
    done < <(sort "${contrib_hash}/languages")
}

add_contributor_to_file() {
    header="Copyright ©"
    name="$(cat "${contrib_hash}/name")"
    years="$(get_contrib_years)"
    languages="$(get_contrib_languages)"

    echo "${header} ${years} ${name} (${languages})"
}

update_contributors() {
    echo "Update AUTHORS file"

    hash_existing_contributors
    reset_contributors_file

    while read -r contrib_hash; do
        add_contributor_to_file
    done < <(find "${contrib_dir}" -mindepth 1 -maxdepth 1 -type d) \
        | sort -f -k 4 >> "${contributors_file}"

    commit_new_contributors_file
}

cleanup() {
    if [[ -d "${work_dir}" ]]; then
        rm -rf "${work_dir}"
    fi
}

trap cleanup EXIT
check_requirements
abort_on_unclean_repo
add_weblate_remote
fetch_weblate
select_translations
parse_commits
rebase_branches
