# AGENTS.md

This file governs AI work inside a copied audio RSS channel based on this template.

## Scope

- Applies to the channel folder that was copied from `templates/audio-rss-channel/`.
- Read the repo root `AGENTS.md` first, then follow these channel-specific rules.

## Intended Use

- This template is for podcast-like or audio-first RSS channels.
- Every published item should have a real media file under `audio/`.
- Use `MP3` or `AAC` for the first version unless explicitly asked otherwise.

## Before Publishing

Replace all placeholders:
- `{{CHANNEL_SLUG}}`
- `{{CHANNEL_TITLE}}`
- `{{CHANNEL_DESCRIPTION}}`
- `{{PUB_DATE_RFC822}}`
- `{{EPISODE_FILE}}`
- `{{EPISODE_TITLE}}`
- `{{EPISODE_SUMMARY}}`
- `{{EPISODE_DURATION}}`
- `{{EPISODE_LENGTH_BYTES}}`
- `{{EPISODE_DATE_LABEL}}`

## Required File Set

- `index.html`
- `feed.xml`
- `channel.json`
- `update.py`
- `cover.jpg`
- `audio/<episode-file>.mp3` or `audio/<episode-file>.m4a`

## Update Workflow

When adding a new episode:
1. Prefer running `python update.py --title ... --summary ... --media-file-src ...`.
2. Add the media file under `audio/` if you are not using the wrapper.
3. Measure the real file size in bytes.
4. Add a new item to `feed.xml`.
5. Add the new episode block to `index.html`.
6. Keep the newest episode first.
7. Verify `enclosure` `url`, `length`, `type`, and `itunes:duration`.

## Apple Podcasts Notes

- Keep `xmlns:itunes` in `feed.xml`.
- Keep `itunes:image`, `itunes:author`, `itunes:summary`, `itunes:explicit`, and `itunes:category`.
- Use `cover.jpg` or `cover.png`, not `SVG`, for the published feed artwork.
- Episode artwork is optional; Apple can use the show cover when episode-specific art is absent.
- If artwork does not refresh in Apple Podcasts, publish the image under a new filename and update the channel-level image reference.
- Do not create a second Apple-only feed by default.
- If Apple Podcasts still behaves inconsistently after the main `feed.xml`, cover URL, and media URL are all confirmed public and healthy, you may add an `apple-feed.xml` fallback that mirrors the same metadata and items with a different self URL.
- If you add `apple-feed.xml`, verify both feeds stay synchronized on every future episode update.

## Validation

- `xmllint --noout feed.xml`
- Check `index.html`
- Check the media URL under `audio/`
- Check `feed.xml` `enclosure` metadata against the real file
