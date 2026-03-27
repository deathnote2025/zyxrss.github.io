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
- `cover.jpg`
- `audio/<episode-file>.mp3` or `audio/<episode-file>.m4a`

## Update Workflow

When adding a new episode:
1. Add the media file under `audio/`.
2. Measure the real file size in bytes.
3. Add a new item to `feed.xml`.
4. Add the new episode block to `index.html`.
5. Keep the newest episode first.
6. Add item-level `itunes:image`; if there is no episode-specific image yet, use the same URL as the channel cover.
7. Verify `enclosure` `url`, `length`, `type`, `itunes:duration`, and `itunes:image`.

## Apple Podcasts Notes

- Keep `xmlns:itunes` in `feed.xml`.
- Keep `itunes:image`, `itunes:author`, `itunes:summary`, `itunes:explicit`, and `itunes:category`.
- Keep item-level `itunes:image` on each episode; if there is no separate episode artwork, default it to the channel cover URL.
- Use `cover.jpg` or `cover.png`, not `SVG`, for the published feed artwork.
- If artwork does not refresh in Apple Podcasts, publish the image under a new filename and update both channel-level and item-level image references.

## Validation

- `xmllint --noout feed.xml`
- Check `index.html`
- Check the media URL under `audio/`
- Check `feed.xml` `enclosure` metadata against the real file
