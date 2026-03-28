# Scripts

## `init_channel.sh`

Use this script to create a new channel from the built-in templates instead of assembling folders by hand.

### Create a new text channel

```bash
scripts/init_channel.sh \
  --type text \
  --slug ai-weekly \
  --title "AI Weekly" \
  --description "Weekly AI notes and summaries." \
  --post-slug issue-001 \
  --post-title "Issue 001: Launch" \
  --post-summary "First issue summary."
```

### Create a new audio channel

```bash
scripts/init_channel.sh \
  --type audio \
  --slug history-audio \
  --title "History Audio" \
  --description "Short history audio episodes." \
  --media-file-src /absolute/path/to/episode-001.mp3 \
  --episode-title "Episode 001: Arrival" \
  --episode-summary "First episode summary." \
  --episode-duration 03:21
```

### What the script does

- Copies the correct template from `templates/`
- Replaces placeholder tokens
- For text channels:
  - renames the placeholder first article page
- For audio channels:
  - optionally copies a real media file into `audio/`
  - infers the filename and byte length when `--media-file-src` is provided
  - currently expects `mp3` media for initialization

### What the script does not do

- It does not update the repo root `index.html`
- It does not update `feeds/index.html`
- It does not commit or push
- It does not generate a new custom cover image

After running the script, follow the repo root `AGENTS.md` and the channel-local `AGENTS.md`.

## `update_channel.py`

Use this shared Python engine to update an existing channel after the folder has already been created.

### Pattern

- Shared engine: `scripts/update_channel.py`
- Per-channel rules: `feeds/<channel-slug>/channel.json`
- Per-channel thin wrapper: `feeds/<channel-slug>/update.py`

In normal use, prefer running the channel-local wrapper.

### Update an audio channel

```bash
python feeds/doublea/update.py \
  --title "Episode title" \
  --summary "Short feed summary." \
  --content-file /absolute/path/to/show-notes.txt \
  --media-file-src /absolute/path/to/audio.mp3
```

Useful optional flags:
- `--entry-slug readable-ascii-suffix`
- `--pub-date-rfc822 "Sat, 28 Mar 2026 09:05:09 +0800"`
- `--date-label 2026-03-28`

### Update a text channel

```bash
python feeds/sample-podcast-text/update.py \
  --title "Issue title" \
  --summary "Short feed summary." \
  --content-file /absolute/path/to/post-body.txt
```

### Delete an existing item

Use the detail-page slug, not the human title.

```bash
python feeds/doublea/update.py \
  --delete-slug episode-002-token-economy-self-drive
```

```bash
python feeds/sample-podcast-text/update.py \
  --delete-slug issue-003
```

Useful optional flag:
- `--dry-run`

### What the update engine does

- Reads the channel-local `channel.json`
- Creates the next post or episode detail page
- Deletes an existing post or episode when `--delete-slug` is used
- Updates `feed.xml`
- Updates `apple-feed.xml` when the channel uses one
- Rebuilds the channel `index.html`
- Copies media files and infers byte size and duration for audio channels

When deleting an item, the engine removes:
- the matching RSS item
- the matching detail page
- the matching media file for audio channels
- the matching item in `apple-feed.xml` when that channel uses one

### What the update engine does not do

- It does not update the repo root `index.html`
- It does not update `feeds/index.html`
- It does not commit or push
- It does not rotate cover filenames automatically
