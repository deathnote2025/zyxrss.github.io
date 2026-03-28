# AGENTS.md

This file governs AI work inside a copied text RSS channel based on this template.

## Scope

- Applies to the channel folder that was copied from `templates/text-rss-channel/`.
- Read the repo root `AGENTS.md` first, then follow these channel-specific rules.

## Intended Use

- This template is for text-only RSS channels.
- Each RSS item must link to a real HTML page under `posts/`.
- Do not add an `audio/` directory unless the channel is intentionally being converted into an audio feed.

## Before Publishing

Replace all placeholders:
- `{{CHANNEL_SLUG}}`
- `{{CHANNEL_TITLE}}`
- `{{CHANNEL_DESCRIPTION}}`
- `{{PUB_DATE_RFC822}}`
- `{{POST_SLUG}}`
- `{{POST_TITLE}}`
- `{{POST_SUMMARY}}`
- `{{POST_DATE_LABEL}}`

## Required File Set

- `index.html`
- `feed.xml`
- `channel.json`
- `update.py`
- `cover.jpg`
- `posts/<post-slug>.html`

## Update Workflow

When adding a new post:
1. Prefer running `python update.py --title ... --summary ...`.
2. Create a new article page under `posts/` if you are not using the wrapper.
3. Add a new item to `feed.xml`.
4. Add a new entry card or summary block to `index.html`.
5. Keep the newest item first in both `feed.xml` and `index.html`.
6. Keep `link` and `guid` pointed at the real post page URL.

When deleting a post:
1. Prefer running `python update.py --delete-slug <post-slug>`.
2. Delete by the page slug such as `issue-003`, not by the human title.
3. Confirm the matching `posts/<post-slug>.html` file disappears.
4. Confirm the item disappears from `feed.xml`.
5. Confirm `index.html` has been rebuilt without the deleted post.

## Validation

- `xmllint --noout feed.xml`
- `python update.py --delete-slug <post-slug> --dry-run` when rehearsing a deletion
- Check `index.html`
- Check each new `posts/*.html`
- Check `feed.xml` item links
