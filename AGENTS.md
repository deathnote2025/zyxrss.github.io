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

- Prefer using `scripts/init_channel.sh` to initialize new channels from templates.
- If a channel already has `update.py`, prefer using that wrapper instead of calling the shared engine by hand.
- For a new text channel, copy `templates/text-rss-channel/` into `feeds/<channel-slug>/`.
- For a new audio channel, copy `templates/audio-rss-channel/` into `feeds/<channel-slug>/`.
- After copying, replace every placeholder token before publishing.

## SOP: Create A New Text RSS Channel

1. Pick a stable slug like `ai-weekly`.
2. Prefer running:
   `scripts/init_channel.sh --type text --slug <channel-slug> --title "<Channel Title>" ...`
3. If the script is not used, copy `templates/text-rss-channel/` to `feeds/<channel-slug>/`.
4. Replace placeholder tokens in:
   - `index.html`
   - `feed.xml`
   - `posts/replace-with-first-article.html`
   - channel-level `AGENTS.md` if needed
5. Rename `posts/replace-with-first-article.html` to the first real post filename.
6. Ensure the channel `feed.xml` item `link` and `guid` both point to that real post page.
7. Generate or replace `cover.jpg` if the placeholder artwork should not be used.
8. Add the channel entry to the repo root `index.html`.
9. Add the channel entry to `feeds/index.html`.
10. Run validation commands.
11. Commit and push.

## SOP: Update An Existing Text RSS Channel

1. Read the channel-local `AGENTS.md`.
2. Prefer running `python update.py --title ... --summary ...`.
3. Create a new page under `posts/` if you are not using the wrapper.
4. Add a new item to `feed.xml` at the top.
5. Add the matching post summary block to `index.html` at the top.
6. Keep `link` and `guid` pointed at the real post page.
7. Re-run validation commands.
8. Commit and push.

## SOP: Delete An Existing Text RSS Item

1. Read the channel-local `AGENTS.md`.
2. Prefer running `python update.py --delete-slug <post-slug>`.
3. Delete by the detail-page slug such as `issue-003`, not by the display title.
4. Confirm the matching `posts/<post-slug>.html` file is removed.
5. Confirm the matching item is removed from `feed.xml`.
6. Confirm `index.html` has been rebuilt without the deleted item.
7. Re-run validation commands.
8. Commit and push.

## SOP: Create A New Audio RSS Channel

1. Pick a stable slug like `history-audio`.
2. Prefer running:
   `scripts/init_channel.sh --type audio --slug <channel-slug> --title "<Channel Title>" ...`
3. If the script is not used, copy `templates/audio-rss-channel/` to `feeds/<channel-slug>/`.
4. Replace placeholder tokens in:
   - `index.html`
   - `feed.xml`
   - channel-level `AGENTS.md` if needed
5. Add the first audio file under `audio/`.
6. Replace `{{EPISODE_FILE}}` with the real filename.
7. Measure the real media byte size and set `{{EPISODE_LENGTH_BYTES}}`.
8. Set `itunes:duration` to the real runtime.
9. Generate or replace `cover.jpg` if the placeholder artwork should not be used.
10. Add the channel entry to the repo root `index.html`.
11. Add the channel entry to `feeds/index.html`.
12. Run validation commands.
13. Commit and push.

## SOP: Update An Existing Audio RSS Channel

1. Read the channel-local `AGENTS.md`.
2. Prefer running `python update.py --title ... --summary ... --media-file-src ...`.
3. Add the new media file under `audio/` if you are not using the wrapper.
4. Measure its real byte size.
5. Add a new item to `feed.xml` at the top.
6. Add the matching episode block to `index.html` at the top.
7. Keep `enclosure` `url`, `length`, `type`, and `itunes:duration` aligned with the real file and artwork choice.
8. Re-run validation commands.
9. Commit and push.

## SOP: Delete An Existing Audio RSS Episode

1. Read the channel-local `AGENTS.md`.
2. Prefer running `python update.py --delete-slug <episode-slug>`.
3. Delete by the episode page slug such as `episode-002-topic-name`, not by the display title.
4. Confirm the matching `episodes/<episode-slug>.html` file is removed.
5. Confirm the matching `audio/<episode-file>.mp3` or `.m4a` file is removed.
6. Confirm the matching item is removed from `feed.xml`.
7. Confirm `apple-feed.xml` is also updated when that channel uses one.
8. Confirm `index.html` has been rebuilt without the deleted episode.
9. Re-run validation commands.
10. Commit and push.

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

1. Prefer running `feeds/<channel-slug>/update.py` when the channel has already adopted the script-managed pattern.
2. Add a new article page under `posts/`.
3. Add a new item to `feed.xml`.
4. Add the new item to the channel `index.html`.
5. Keep item links and `guid` values pointed at the real article page, not the channel home page.
6. Keep items in reverse chronological order.
7. If a published item needs to be removed, prefer `python feeds/<channel-slug>/update.py --delete-slug <post-slug>` over hand-editing multiple files.

## Required Updates For Existing Audio Channels

1. Prefer running `feeds/<channel-slug>/update.py` when the channel has already adopted the script-managed pattern.
2. Add the media file under `audio/`.
3. Add a new item to `feed.xml`.
4. Add the new episode entry to the channel `index.html`.
5. Keep `enclosure` `url`, `length`, `type`, and `itunes:duration` in sync with the real media file and artwork choice.
6. Prefer `MP3` or `AAC` for podcast media.
7. If a published episode needs to be removed, prefer `python feeds/<channel-slug>/update.py --delete-slug <episode-slug>` over manually editing feed, page, and media files separately.

## Apple Podcasts Constraints

- Use `cover.jpg` or `cover.png`, not `SVG`, for the podcast artwork used by the feed.
- Artwork should be square and ideally between `1400x1400` and `3000x3000`.
- Audio podcast feeds should include `xmlns:itunes`.
- Audio podcast feeds should include `itunes:image`, `itunes:author`, `itunes:summary`, `itunes:explicit`, and `itunes:category`.
- Episode artwork is optional. If you do not provide episode-specific art, Apple can display the show cover artwork instead.
- If artwork changes are not reflected by Apple clients, consider using a new filename.
- If you explicitly add episode-specific artwork later, test the Apple follow flow again before treating it as a default pattern.
- If an Apple follow or refresh issue persists even though the current feed, audio URL, and artwork URL are all publicly returning `200`, prefer adding a second Apple-specific feed URL such as `apple-feed.xml` instead of repeatedly mutating the original `feed.xml`.
- If a channel adopts a second Apple-specific feed, keep its channel metadata and item list synchronized with `feed.xml`; only the self-referencing feed URL should differ.
- After pushing a new alternate feed file to GitHub Pages, wait until the new public URL returns `200` before testing it in Apple Podcasts.

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
  - `xmllint --noout feeds/<channel-slug>/apple-feed.xml` when the channel keeps a separate Apple-specific feed
  - `curl -I http://127.0.0.1:<port>/feeds/<channel-slug>/`
  - `curl -I http://127.0.0.1:<port>/feeds/<channel-slug>/audio/<episode-file>`

## Do Not

- Do not point every text RSS item back to the channel home page.
- Do not leave placeholder URLs in a published channel.
- Do not keep obsolete media or artwork files once the channel has fully moved to new assets.
- Do not mix audio files from different channels in one shared folder.
