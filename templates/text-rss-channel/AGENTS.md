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
- `cover.jpg`
- `posts/<post-slug>.html`

## Update Workflow

When adding a new post:
1. Create a new article page under `posts/`.
2. Add a new item to `feed.xml`.
3. Add a new entry card or summary block to `index.html`.
4. Keep the newest item first in both `feed.xml` and `index.html`.
5. Keep `link` and `guid` pointed at the real post page URL.

## Validation

- `xmllint --noout feed.xml`
- Check `index.html`
- Check each new `posts/*.html`
- Check `feed.xml` item links
