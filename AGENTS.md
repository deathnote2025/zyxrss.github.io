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

## SOP: Create A New Text RSS Channel

1. Pick a stable slug like `ai-weekly`.
2. Copy `templates/text-rss-channel/` to `feeds/<channel-slug>/`.
3. Replace placeholder tokens in:
   - `index.html`
   - `feed.xml`
   - `posts/replace-with-first-article.html`
   - channel-level `AGENTS.md` if needed
4. Rename `posts/replace-with-first-article.html` to the first real post filename.
5. Ensure the channel `feed.xml` item `link` and `guid` both point to that real post page.
6. Generate or replace `cover.jpg` if the placeholder artwork should not be used.
7. Add the channel entry to the repo root `index.html`.
8. Add the channel entry to `feeds/index.html`.
9. Run validation commands.
10. Commit and push.

## SOP: Update An Existing Text RSS Channel

1. Read the channel-local `AGENTS.md`.
2. Create a new page under `posts/`.
3. Add a new item to `feed.xml` at the top.
4. Add the matching post summary block to `index.html` at the top.
5. Keep `link` and `guid` pointed at the real post page.
6. Re-run validation commands.
7. Commit and push.

## SOP: Create A New Audio RSS Channel

1. Pick a stable slug like `history-audio`.
2. Copy `templates/audio-rss-channel/` to `feeds/<channel-slug>/`.
3. Replace placeholder tokens in:
   - `index.html`
   - `feed.xml`
   - channel-level `AGENTS.md` if needed
4. Add the first audio file under `audio/`.
5. Replace `{{EPISODE_FILE}}` with the real filename.
6. Measure the real media byte size and set `{{EPISODE_LENGTH_BYTES}}`.
7. Set `itunes:duration` to the real runtime.
8. Generate or replace `cover.jpg` if the placeholder artwork should not be used.
9. Add the channel entry to the repo root `index.html`.
10. Add the channel entry to `feeds/index.html`.
11. Run validation commands.
12. Commit and push.

## SOP: Update An Existing Audio RSS Channel

1. Read the channel-local `AGENTS.md`.
2. Add the new media file under `audio/`.
3. Measure its real byte size.
4. Add a new item to `feed.xml` at the top.
5. Add the matching episode block to `index.html` at the top.
6. Keep `enclosure` `url`, `length`, `type`, and `itunes:duration` aligned with the real file.
7. Re-run validation commands.
8. Commit and push.

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

## Quick Validation Examples

- Text channel:
  - `xmllint --noout feeds/<channel-slug>/feed.xml`
  - `curl -I http://127.0.0.1:<port>/feeds/<channel-slug>/`
  - `curl -I http://127.0.0.1:<port>/feeds/<channel-slug>/posts/<post-file>.html`
- Audio channel:
  - `xmllint --noout feeds/<channel-slug>/feed.xml`
  - `curl -I http://127.0.0.1:<port>/feeds/<channel-slug>/`
  - `curl -I http://127.0.0.1:<port>/feeds/<channel-slug>/audio/<episode-file>`

## Do Not

- Do not point every text RSS item back to the channel home page.
- Do not leave placeholder URLs in a published channel.
- Do not keep obsolete media or artwork files once the channel has fully moved to new assets.
- Do not mix audio files from different channels in one shared folder.
