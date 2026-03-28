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
- `apple-feed.xml`
- `channel.json`
- `update.py`
- `cover.jpg` or a rotated filename such as `cover-20260327.jpg`
- `episodes/*.html`
- `audio/*.mp3`

## Episode Update Workflow

When adding a new episode:
1. Prefer running `python update.py --title ... --summary ... --media-file-src ...`.
2. Add the media file under `audio/` using a stable ASCII filename such as `episode-002-topic-name.mp3` if you are not using the wrapper.
3. Measure the real file size in bytes and duration with `ffprobe`.
4. Create a standalone episode page under `episodes/`.
5. Add a new `<item>` at the top of `feed.xml`.
6. Mirror the same channel metadata and item list into `apple-feed.xml`; only the `atom:link rel="self"` URL should differ.
7. Point each item `link` and `guid` to the episode page, and point `enclosure` to the real MP3 URL.
8. Keep all older `<item>` entries below the newest one in reverse chronological order; do not reorder older entries arbitrarily.
9. Update `index.html` so the newest episode appears first.
10. If there is already more than one episode, keep the older episode list below the newest one in reverse chronological order.
11. If the channel list changed, update the repo root `index.html` and `feeds/index.html` manually.

When deleting an episode:
1. Prefer running `python update.py --delete-slug <episode-page-slug>`.
2. Delete by the episode page slug such as `episode-002-token-economy-self-drive`, not by the display title.
3. Confirm the matching `episodes/<slug>.html` page is removed.
4. Confirm the matching `audio/*.mp3` file is removed.
5. Confirm the item disappears from both `feed.xml` and `apple-feed.xml`.
6. Confirm `index.html` has been rebuilt with the remaining episodes still in reverse chronological order.

## Apple Podcasts Notes

- Keep `xmlns:itunes` in `feed.xml`.
- Keep `itunes:image`, `itunes:author`, `itunes:summary`, `itunes:explicit`, and `itunes:category`.
- Keep cover art as square `JPG` or `PNG`; `3000x3000` is preferred.
- Prefer `MP3` or `AAC` for published audio.
- Do not replace published media or artwork URLs casually once clients may have cached them.
- If artwork needs to refresh in Apple Podcasts, publish it under a new filename such as `cover-20260327.jpg` and update `feed.xml` plus `index.html`; do not rely on overwriting the old file in place.
- Episode artwork is optional; Apple can use the channel cover when item-level artwork is absent.
- `apple-feed.xml` exists specifically to give Apple Podcasts a stable fallback URL if `feed.xml` is stuck behind client-side or platform-side cache.
- If `apple-feed.xml` is updated or newly added, wait until its public GitHub Pages URL actually returns `200` before testing follow flow in Apple Podcasts.

## Content Rules

- Keep the channel intro broad; do not rewrite `doublea` into a fixed vertical unless the user explicitly changes positioning.
- Each episode should have its own detail page under `episodes/`.
- Episode pages should include title, date, summary, audio player, and structured show notes when available.
- Do not let all episode links point back to the channel home page.
- Keep filenames URL-safe and stable; avoid Chinese filenames inside the published channel folder.

## Validation

- `xmllint --noout feed.xml`
- `xmllint --noout apple-feed.xml`
- `python update.py --delete-slug <episode-page-slug> --dry-run` when rehearsing a deletion
- Check the episode page URL
- Check the media URL under `audio/`
- Check `feed.xml` `enclosure` metadata against the real file
- Check the public `apple-feed.xml` URL when this channel is being tested in Apple Podcasts
