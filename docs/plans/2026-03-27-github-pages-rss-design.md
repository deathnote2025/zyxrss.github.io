# GitHub Pages RSS Site Design

## Context

This repository is a GitHub Pages static site published from the `main` branch.
The current public site URL is:

- `https://deathnote2025.github.io/zyxrss.github.io/`

The next step is to host manually maintained RSS files in a stable folder structure,
including both normal RSS feeds and podcast-style RSS feeds with audio files.

## Goals

- Serve RSS XML files directly from GitHub Pages.
- Keep one folder per channel.
- Keep one `feed.xml` per channel.
- Support both normal RSS and audio RSS with the same directory conventions.
- Provide a simple human-facing index page at the site root.
- Provide a simple human-facing page for each channel.
- Keep URLs stable for long-term subscription use.

## Non-Goals

- No feed generation pipeline yet.
- No automatic index generation yet.
- No CMS or admin backend.
- No shared media pool across channels.

## Recommended Structure

```text
/
  index.html
  feeds/
    channel-slug/
      index.html
      feed.xml
      cover.jpg
      audio/
        episode-001.mp3
```

## URL Rules

- Site home: `/`
- Channel page: `/feeds/channel-slug/`
- Feed URL: `/feeds/channel-slug/feed.xml`
- Audio file URL: `/feeds/channel-slug/audio/file-name.mp3`

## Naming Rules

- Channel folders use lowercase English slugs.
- Use `-` between words, for example `ai-weekly`.
- Do not use Chinese characters, spaces, or unstable timestamp-based folder names in URLs.
- Each channel keeps exactly one primary feed file named `feed.xml`.
- Audio files should use stable and readable names.

## Content Model

### Root `index.html`

Purpose:
- Acts as the human-facing home page.
- Lists all available channels manually.
- Links to each channel page and optionally each RSS URL.

### Channel `index.html`

Purpose:
- Acts as the human-facing channel landing page.
- Displays channel title, summary, cover image, and RSS subscription link.
- For audio channels, displays a lightweight player and links to recent audio files.

Recommended sections:
- Channel title
- Short description
- Cover image
- RSS link
- Recent content list
- Recent audio list and player when applicable
- Resource links

### `feed.xml`

Purpose:
- Machine-facing subscription entry.
- Used by RSS readers and podcast clients.
- Should not be treated as the main human-facing page.

### `audio/`

Purpose:
- Stores only audio files for the current channel.
- Keeps each channel self-contained.

## Manual Maintenance Workflow

### Add a new channel

1. Create `feeds/channel-slug/`
2. Add `feed.xml`
3. Add `cover.jpg` if needed
4. Add `audio/` if the feed includes audio
5. Add channel `index.html`
6. Update root `index.html` with a new channel link
7. Commit and push
8. Verify public URLs after Pages deploys

### Update an existing channel

1. Update `feed.xml`
2. Add or replace related assets inside the same channel folder
3. If needed, update channel `index.html`
4. Commit and push
5. Verify public URLs

## Why This Structure

- Stable URLs reduce subscription breakage.
- One channel per folder keeps maintenance simple.
- Audio and XML staying together makes troubleshooting easier.
- Human pages and machine feed endpoints remain clearly separated.
- The site can later evolve to generated indexes without breaking published feed URLs.

## Open Implementation Direction

The first implementation step should be:

1. Create the `feeds/` directory structure
2. Add one sample channel
3. Update the root home page to link to that sample channel

