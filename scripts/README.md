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
