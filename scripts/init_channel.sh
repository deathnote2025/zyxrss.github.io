#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_BASE_URL="https://deathnote2025.github.io/zyxrss.github.io"

usage() {
  cat <<'EOF'
Usage:
  scripts/init_channel.sh --type text --slug <slug> --title <title> [options]
  scripts/init_channel.sh --type audio --slug <slug> --title <title> [options]

Common options:
  --type <text|audio>           Channel type
  --slug <slug>                 Published channel slug
  --title <title>               Channel title
  --description <text>          Channel description
  --output-root <dir>           Channel root dir (default: <repo>/feeds)
  --base-url <url>              Base site url (default: https://deathnote2025.github.io/zyxrss.github.io)
  --pub-date-rfc822 <date>      Feed pubDate / lastBuildDate
  --help                        Show this help

Text-only options:
  --post-slug <slug>            First post slug (default: first-post)
  --post-title <title>          First post title (default: First Post)
  --post-summary <text>         First post summary
  --post-date-label <date>      Human-readable date label (default: today)

Audio options:
  --episode-file <name>         Episode media filename (default: episode-001.mp3)
  --episode-title <title>       First episode title (default: Episode 001)
  --episode-summary <text>      First episode summary
  --episode-duration <time>     Episode duration like 03:21 (default: 00:01)
  --episode-length-bytes <n>    Media file size in bytes (default: 0)
  --media-file-src <path>       Copy a real media file into audio/ and infer filename/byte length

Examples:
  scripts/init_channel.sh \
    --type text \
    --slug ai-weekly \
    --title "AI Weekly" \
    --description "Weekly AI notes and summaries." \
    --post-slug issue-001 \
    --post-title "Issue 001: Launch"

  scripts/init_channel.sh \
    --type audio \
    --slug history-audio \
    --title "History Audio" \
    --description "Short history audio episodes." \
    --media-file-src /path/to/episode-001.mp3 \
    --episode-title "Episode 001: Arrival" \
    --episode-duration 03:21
EOF
}

die() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

replace_in_file() {
  local placeholder="$1"
  local replacement="$2"
  local file="$3"
  LC_ALL=C LANG=C PERL_BADLANG=0 PLACEHOLDER="$placeholder" REPLACEMENT="$replacement" perl -0pi -e 's/\Q$ENV{PLACEHOLDER}\E/$ENV{REPLACEMENT}/g' "$file"
}

replace_all_in_dir() {
  local dir="$1"
  local placeholder="$2"
  local replacement="$3"
  while IFS= read -r file; do
    replace_in_file "$placeholder" "$replacement" "$file"
  done < <(find "$dir" -type f \( -name '*.md' -o -name '*.html' -o -name '*.xml' \) | sort)
}

current_rfc822() {
  LC_ALL=C date "+%a, %d %b %Y %H:%M:%S %z"
}

current_label_date() {
  date "+%Y-%m-%d"
}

channel_type=""
slug=""
title=""
description=""
output_root="${REPO_ROOT}/feeds"
base_url="${DEFAULT_BASE_URL}"
pub_date_rfc822="$(current_rfc822)"

post_slug="first-post"
post_title="First Post"
post_summary="Replace this summary with the first real text item."
post_date_label="$(current_label_date)"

episode_file="episode-001.mp3"
episode_title="Episode 001"
episode_summary="Replace this summary with the first real episode."
episode_duration="00:01"
episode_length_bytes="0"
media_file_src=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type) channel_type="${2:-}"; shift 2 ;;
    --slug) slug="${2:-}"; shift 2 ;;
    --title) title="${2:-}"; shift 2 ;;
    --description) description="${2:-}"; shift 2 ;;
    --output-root) output_root="${2:-}"; shift 2 ;;
    --base-url) base_url="${2:-}"; shift 2 ;;
    --pub-date-rfc822) pub_date_rfc822="${2:-}"; shift 2 ;;
    --post-slug) post_slug="${2:-}"; shift 2 ;;
    --post-title) post_title="${2:-}"; shift 2 ;;
    --post-summary) post_summary="${2:-}"; shift 2 ;;
    --post-date-label) post_date_label="${2:-}"; shift 2 ;;
    --episode-file) episode_file="${2:-}"; shift 2 ;;
    --episode-title) episode_title="${2:-}"; shift 2 ;;
    --episode-summary) episode_summary="${2:-}"; shift 2 ;;
    --episode-duration) episode_duration="${2:-}"; shift 2 ;;
    --episode-length-bytes) episode_length_bytes="${2:-}"; shift 2 ;;
    --media-file-src) media_file_src="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown argument: $1" ;;
  esac
done

[[ -n "$channel_type" ]] || die "--type is required"
[[ -n "$slug" ]] || die "--slug is required"
[[ -n "$title" ]] || die "--title is required"
[[ "$channel_type" == "text" || "$channel_type" == "audio" ]] || die "--type must be text or audio"
[[ "$slug" =~ ^[a-z0-9-]+$ ]] || die "--slug must use lowercase English letters, digits, and hyphen only"

if [[ -z "$description" ]]; then
  if [[ "$channel_type" == "text" ]]; then
    description="${title} text RSS channel."
  else
    description="${title} audio RSS channel."
  fi
fi

template_dir="${REPO_ROOT}/templates/${channel_type}-rss-channel"
[[ -d "$template_dir" ]] || die "Template not found: $template_dir"

target_dir="${output_root}/${slug}"
[[ ! -e "$target_dir" ]] || die "Target already exists: $target_dir"

mkdir -p "$output_root"
cp -R "$template_dir" "$target_dir"

if [[ "$channel_type" == "text" ]]; then
  mv "${target_dir}/posts/replace-with-first-article.html" "${target_dir}/posts/${post_slug}.html"
else
  if [[ -n "$media_file_src" ]]; then
    [[ -f "$media_file_src" ]] || die "Media source not found: $media_file_src"
    episode_file="$(basename "$media_file_src")"
    cp "$media_file_src" "${target_dir}/audio/${episode_file}"
    episode_length_bytes="$(wc -c < "${target_dir}/audio/${episode_file}" | tr -d ' ')"
  fi

  [[ "$episode_file" == *.mp3 ]] || die "The current init script supports mp3 media initialization only"
fi

replace_all_in_dir "$target_dir" "{{CHANNEL_SLUG}}" "$slug"
replace_all_in_dir "$target_dir" "{{CHANNEL_TITLE}}" "$title"
replace_all_in_dir "$target_dir" "{{CHANNEL_DESCRIPTION}}" "$description"
replace_all_in_dir "$target_dir" "{{PUB_DATE_RFC822}}" "$pub_date_rfc822"

if [[ "$channel_type" == "text" ]]; then
  replace_all_in_dir "$target_dir" "{{POST_SLUG}}" "$post_slug"
  replace_all_in_dir "$target_dir" "{{POST_TITLE}}" "$post_title"
  replace_all_in_dir "$target_dir" "{{POST_SUMMARY}}" "$post_summary"
  replace_all_in_dir "$target_dir" "{{POST_DATE_LABEL}}" "$post_date_label"
else
  replace_all_in_dir "$target_dir" "{{EPISODE_FILE}}" "$episode_file"
  replace_all_in_dir "$target_dir" "{{EPISODE_TITLE}}" "$episode_title"
  replace_all_in_dir "$target_dir" "{{EPISODE_SUMMARY}}" "$episode_summary"
  replace_all_in_dir "$target_dir" "{{EPISODE_DURATION}}" "$episode_duration"
  replace_all_in_dir "$target_dir" "{{EPISODE_LENGTH_BYTES}}" "$episode_length_bytes"
  replace_all_in_dir "$target_dir" "{{EPISODE_DATE_LABEL}}" "$(current_label_date)"
fi

replace_all_in_dir "$target_dir" "${DEFAULT_BASE_URL}" "$base_url"

printf 'Initialized %s channel at %s\n' "$channel_type" "$target_dir"
printf 'Next steps:\n'
printf '1. Review %s\n' "${target_dir}/AGENTS.md"
printf '2. Update root index.html and feeds/index.html entries\n'
printf '3. Run xmllint --noout %s/feed.xml\n' "$target_dir"
