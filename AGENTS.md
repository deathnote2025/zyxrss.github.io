# AGENTS.md

This file governs AI work for the whole repository.

## Repo Purpose

- This repository hosts static RSS channels on GitHub Pages.
- Public base URL: `https://deathnote2025.github.io/zyxrss.github.io/`
- All published channels live under `feeds/<channel-slug>/`.
- One channel folder maps to one public RSS endpoint at `feeds/<channel-slug>/feed.xml`.

## First Rule

- Before editing a specific channel, read the closest `AGENTS.md` in that channel or template folder.
- Repo-level rules apply everywhere unless a deeper `AGENTS.md` narrows the scope.

## Channel Types

- Text RSS:
  - Use when each item should point to a real article page.
  - Each item must have its own HTML page under `posts/`.
- Audio RSS:
  - Use when each item includes playable media through `enclosure`.
  - Audio files belong in the channel's own `audio/` folder.

## Where To Start

- For a new text channel, copy `templates/text-rss-channel/` into `feeds/<channel-slug>/`.
- For a new audio channel, copy `templates/audio-rss-channel/` into `feeds/<channel-slug>/`.
- After copying, replace every placeholder token before publishing.

## Naming Rules

- Channel folder names must use lowercase English slugs with `-`.
- Do not rename an existing published channel slug unless explicitly requested.
- Keep the main feed filename fixed as `feed.xml`.
- Text post pages should use stable filenames under `posts/`.
- Audio files should use stable readable names such as `episode-001.mp3`.

## Required Updates For Any New Channel

1. Create or copy the channel folder under `feeds/`.
2. Replace placeholder text in `index.html`, `feed.xml`, cover assets, and channel-level `AGENTS.md` if needed.
3. Update the root [index.html](/Users/yuxiangzhang/SynologyDrive/syno_drive/python/project/crawler/rss/zyxrss.github.io/index.html) to add a new channel card or entry.
4. Update [feeds/index.html](/Users/yuxiangzhang/SynologyDrive/syno_drive/python/project/crawler/rss/zyxrss.github.io/feeds/index.html) to add the channel.
5. Verify the public-facing file set for that channel.

## Required Updates For Existing Text Channels

1. Add a new article page under `posts/`.
2. Add a new item to `feed.xml`.
3. Add the new item to the channel `index.html`.
4. Keep item links and `guid` values pointed at the real article page, not the channel home page.
5. Keep items in reverse chronological order.

## Required Updates For Existing Audio Channels

1. Add the media file under `audio/`.
2. Add a new item to `feed.xml`.
3. Add the new episode entry to the channel `index.html`.
4. Keep `enclosure` `url`, `length`, `type`, and `itunes:duration` in sync with the real media file.
5. Prefer `MP3` or `AAC` for podcast media.

## Apple Podcasts Constraints

- Use `cover.jpg` or `cover.png`, not `SVG`, for the podcast artwork used by the feed.
- Artwork should be square and ideally between `1400x1400` and `3000x3000`.
- Audio podcast feeds should include `xmlns:itunes`.
- Audio podcast feeds should include `itunes:image`, `itunes:author`, `itunes:summary`, `itunes:explicit`, and `itunes:category`.
- If artwork changes are not reflected by Apple clients, consider using a new filename.

## Verification Before Push

- Run `xmllint --noout feeds/<channel-slug>/feed.xml`.
- Serve locally with `python3 -m http.server <port>` from repo root when checking pages.
- Verify:
  - `/<channel>/`
  - `/<channel>/feed.xml`
  - any text item page URLs
  - any audio media URLs
  - cover asset URLs if the channel uses them

## Do Not

- Do not point every text RSS item back to the channel home page.
- Do not leave placeholder URLs in a published channel.
- Do not keep obsolete media or artwork files once the channel has fully moved to new assets.
- Do not mix audio files from different channels in one shared folder.
