# AGENTS.md

This file governs AI work inside `feeds/doublea/`.

## Scope

- Read the repo root `AGENTS.md` first.
- Then follow these `doublea`-specific rules for channel updates.

## Channel Identity

- Channel title stays `doublea`.
- Channel slug stays `doublea`.
- This is an audio-first RSS channel intended to work well with Apple Podcasts.
- The channel is intentionally broad-topic. Recent things watched, read, noticed, or worth talking about can all become episodes.
- Published URLs under `feeds/doublea/` should remain stable after release.

## Required File Set

- `index.html`
- `feed.xml`
- `cover.jpg` or a rotated filename such as `cover-20260327.jpg`
- `episodes/*.html`
- `audio/*.mp3`

## Episode Update Workflow

When adding a new episode:
1. Add the media file under `audio/` using a stable ASCII filename such as `episode-002-topic-name.mp3`.
2. Measure the real file size in bytes and duration with `ffprobe`.
3. Create a standalone episode page under `episodes/`.
4. Add a new `<item>` at the top of `feed.xml`.
5. Point the item `link` and `guid` to the episode page, and point `enclosure` to the real MP3 URL.
6. Keep all older `<item>` entries below it in reverse chronological order; do not reorder older entries arbitrarily.
7. Update `index.html` so the newest episode appears first.
8. If there is already more than one episode, keep the older episode list below the newest one in reverse chronological order.
9. If the channel list changed, update the repo root `index.html` and `feeds/index.html` manually.

## Apple Podcasts Notes

- Keep `xmlns:itunes` in `feed.xml`.
- Keep `itunes:image`, `itunes:author`, `itunes:summary`, `itunes:explicit`, and `itunes:category`.
- Keep cover art as square `JPG` or `PNG`; `3000x3000` is preferred.
- Prefer `MP3` or `AAC` for published audio.
- Do not replace published media or artwork URLs casually once clients may have cached them.
- If artwork needs to refresh in Apple Podcasts, publish it under a new filename such as `cover-20260327.jpg` and update `feed.xml` plus `index.html`; do not rely on overwriting the old file in place.

## Content Rules

- Keep the channel intro broad; do not rewrite `doublea` into a fixed vertical unless the user explicitly changes positioning.
- Each episode should have its own detail page under `episodes/`.
- Episode pages should include title, date, summary, audio player, and structured show notes when available.
- Do not let all episode links point back to the channel home page.
- Keep filenames URL-safe and stable; avoid Chinese filenames inside the published channel folder.

## Validation

- `xmllint --noout feed.xml`
- Check the episode page URL
- Check the media URL under `audio/`
- Check `feed.xml` `enclosure` metadata against the real file
