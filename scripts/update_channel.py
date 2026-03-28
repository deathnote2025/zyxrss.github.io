#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path
from typing import Optional

ATOM_NS = "http://www.w3.org/2005/Atom"
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"

ET.register_namespace("atom", ATOM_NS)
ET.register_namespace("itunes", ITUNES_NS)
ET.register_namespace("content", CONTENT_NS)


@dataclass
class ChannelConfig:
    channel_type: str
    slug: str
    channel_title: str
    channel_description: str
    base_url: str
    feed_path: str
    apple_feed_path: Optional[str]
    cover_image: str
    language: str
    entry_prefix: str
    author: Optional[str] = None
    category: Optional[str] = None
    explicit: bool = False

    @property
    def channel_url(self) -> str:
        return f"{self.base_url}/feeds/{self.slug}/"

    def public_url(self, relative_path: str) -> str:
        return f"{self.channel_url}{relative_path}".replace("//", "/").replace("https:/", "https://")


@dataclass
class Entry:
    title: str
    page_rel_path: str
    page_url: str
    guid: str
    pub_date_rfc822: str
    date_label: str
    summary_text: str
    description_html: str
    body_html: str
    entry_number: Optional[int] = None
    duration: Optional[str] = None
    media_rel_path: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    media_length: Optional[int] = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update an existing text or audio RSS channel.")
    parser.add_argument("--channel-dir", required=True, help="Absolute or relative path to the channel folder")
    parser.add_argument("--title", required=True, help="Post or episode title")
    parser.add_argument("--summary", required=True, help="Short summary used in feed and channel index")
    parser.add_argument("--content", help="Long-form body content for the detail page")
    parser.add_argument("--content-file", help="Read long-form body content from a text file")
    parser.add_argument("--entry-slug", help="Optional ASCII slug suffix for the new item")
    parser.add_argument("--pub-date-rfc822", help="Optional RFC 2822 publication date")
    parser.add_argument("--date-label", help="Optional human-readable date label")
    parser.add_argument("--media-file-src", help="Audio file source path for audio channels")
    parser.add_argument("--dry-run", action="store_true", help="Parse and print planned outputs without writing files")
    return parser.parse_args()


def die(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_channel_config(channel_dir: Path) -> ChannelConfig:
    config_path = channel_dir / "channel.json"
    if not config_path.is_file():
        die(f"Missing channel config: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    required = [
        "type",
        "slug",
        "channel_title",
        "channel_description",
        "base_url",
        "feed_path",
        "cover_image",
        "language",
        "entry_prefix",
    ]
    missing = [key for key in required if not data.get(key)]
    if missing:
        die(f"channel.json is missing required keys: {', '.join(missing)}")

    return ChannelConfig(
        channel_type=data["type"],
        slug=data["slug"],
        channel_title=data["channel_title"],
        channel_description=data["channel_description"],
        base_url=data["base_url"].rstrip("/"),
        feed_path=data["feed_path"],
        apple_feed_path=data.get("apple_feed_path") or None,
        cover_image=data["cover_image"],
        language=data["language"],
        entry_prefix=data["entry_prefix"],
        author=data.get("author"),
        category=data.get("category"),
        explicit=bool(data.get("explicit", False)),
    )


def now_rfc822() -> str:
    return format_datetime(datetime.now().astimezone())


def label_from_rfc822(value: str) -> str:
    return parsedate_to_datetime(value).astimezone().strftime("%Y-%m-%d")


def sanitize_slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def strip_tags(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"</p>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"</li>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{2,}", "\n", value)
    return value.strip()


def extract_first_paragraph(value: str) -> str:
    match = re.search(r"<p>(.*?)</p>", value, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return strip_tags(match.group(1))
    return strip_tags(value)


def extract_list_items(value: str) -> list[str]:
    items: list[str] = []
    for raw in re.findall(r"<li>(.*?)</li>", value, flags=re.IGNORECASE | re.DOTALL):
        cleaned = strip_tags(raw)
        if cleaned:
            items.append(cleaned)
    return items


def read_detail_content(args: argparse.Namespace) -> str:
    if args.content_file:
        content_path = Path(args.content_file)
        if not content_path.is_file():
            die(f"Content file not found: {content_path}")
        return content_path.read_text(encoding="utf-8").strip()
    if args.content:
        return args.content.strip()
    return args.summary.strip()


def content_to_html(raw_text: str) -> str:
    blocks = re.split(r"\n\s*\n", raw_text.strip())
    rendered: list[str] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if all(re.match(r"^[-*]\s+", line) for line in lines):
            cleaned_items = [html.escape(re.sub(r"^[-*]\s+", "", line)) for line in lines]
            items = "".join(f"<li>{item}</li>" for item in cleaned_items)
            rendered.append(f"<ul>\n{items}\n</ul>")
            continue
        if all(re.match(r"^\d+[.)]\s+", line) for line in lines):
            cleaned_items = [html.escape(re.sub(r"^\d+[.)]\s+", "", line)) for line in lines]
            items = "".join(f"<li>{item}</li>" for item in cleaned_items)
            rendered.append(f"<ol>\n{items}\n</ol>")
            continue
        paragraph = " ".join(lines)
        rendered.append(f"<p>{html.escape(paragraph)}</p>")
    return "\n".join(rendered)


def build_feed_description(summary: str) -> str:
    return summary.strip()


def infer_media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    mapping = {
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".aac": "audio/aac",
    }
    if suffix not in mapping:
        die(f"Unsupported media type: {path.suffix}")
    return mapping[suffix]


def ffprobe_duration(path: Path) -> str:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    seconds = float(result.stdout.strip())
    minutes = int(seconds // 60)
    remainder = int(round(seconds - minutes * 60))
    if remainder == 60:
        minutes += 1
        remainder = 0
    return f"{minutes:02d}:{remainder:02d}"


def parse_existing_entries(feed_path: Path, config: ChannelConfig) -> list[Entry]:
    if not feed_path.is_file():
        return []

    tree = ET.parse(feed_path)
    channel = tree.getroot().find("channel")
    if channel is None:
        die(f"Invalid RSS feed: {feed_path}")

    entries: list[Entry] = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link).strip()
        pub_date = (item.findtext("pubDate") or now_rfc822()).strip()
        description_html = (item.findtext("description") or "").strip()
        page_rel_path = relative_channel_path(config, link)
        media_rel_path = None
        media_url = None
        media_type = None
        media_length = None
        duration = None
        entry_number = None

        enclosure = item.find("enclosure")
        if enclosure is not None:
            media_url = (enclosure.attrib.get("url") or "").strip()
            media_rel_path = relative_channel_path(config, media_url)
            media_type = enclosure.attrib.get("type")
            if enclosure.attrib.get("length"):
                media_length = int(enclosure.attrib["length"])

        if config.channel_type == "audio":
            duration = item.findtext(f"{{{ITUNES_NS}}}duration")
            raw_number = item.findtext(f"{{{ITUNES_NS}}}episode")
            if raw_number and raw_number.isdigit():
                entry_number = int(raw_number)

        entries.append(
            Entry(
                title=title,
                page_rel_path=page_rel_path,
                page_url=link,
                guid=guid,
                pub_date_rfc822=pub_date,
                date_label=label_from_rfc822(pub_date),
                summary_text=extract_first_paragraph(description_html),
                description_html=extract_first_paragraph(description_html),
                body_html="",
                entry_number=entry_number,
                duration=duration,
                media_rel_path=media_rel_path,
                media_url=media_url,
                media_type=media_type,
                media_length=media_length,
            )
        )

    return entries


def relative_channel_path(config: ChannelConfig, public_url: str) -> str:
    prefix = config.channel_url
    if public_url.startswith(prefix):
        return public_url[len(prefix):]
    return public_url


def next_entry_number(entries: list[Entry], config: ChannelConfig) -> int:
    numbers = [entry.entry_number for entry in entries if entry.entry_number is not None]
    if numbers:
        return max(numbers) + 1
    return len(entries) + 1


def build_entry_slug(args: argparse.Namespace, config: ChannelConfig, entry_number: int, media_source: Optional[Path]) -> str:
    if args.entry_slug:
        suffix = sanitize_slug(args.entry_slug)
    else:
        suffix = ""
        if media_source is not None:
            suffix = sanitize_slug(media_source.stem)
        if not suffix:
            suffix = sanitize_slug(args.title)
    suffix = re.sub(rf"^{re.escape(config.entry_prefix)}-\d+-?", "", suffix)
    prefix = f"{config.entry_prefix}-{entry_number:03d}"
    return f"{prefix}-{suffix}" if suffix else prefix


def create_new_entry(args: argparse.Namespace, channel_dir: Path, config: ChannelConfig, existing_entries: list[Entry]) -> Entry:
    pub_date = args.pub_date_rfc822 or now_rfc822()
    date_label = args.date_label or label_from_rfc822(pub_date)
    content_text = read_detail_content(args)
    body_html = content_to_html(content_text)
    description_html = build_feed_description(args.summary)

    if config.channel_type == "audio":
        if not args.media_file_src:
            die("--media-file-src is required for audio channels")
        media_source = Path(args.media_file_src)
        if not media_source.is_file():
            die(f"Audio source not found: {media_source}")
        entry_number = next_entry_number(existing_entries, config)
        entry_slug = build_entry_slug(args, config, entry_number, media_source)
        media_type = infer_media_type(media_source)
        media_rel_path = f"audio/{entry_slug}{media_source.suffix.lower()}"
        media_target = channel_dir / media_rel_path
        page_rel_path = f"episodes/{entry_slug}.html"
        page_url = config.public_url(page_rel_path)
        if not args.dry_run:
            shutil.copy2(media_source, media_target)
        media_length = media_target.stat().st_size if media_target.exists() else media_source.stat().st_size
        duration = ffprobe_duration(media_target if media_target.exists() else media_source)
        return Entry(
            title=args.title.strip(),
            page_rel_path=page_rel_path,
            page_url=page_url,
            guid=page_url,
            pub_date_rfc822=pub_date,
            date_label=date_label,
            summary_text=args.summary.strip(),
            description_html=description_html,
            body_html=body_html,
            entry_number=entry_number,
            duration=duration,
            media_rel_path=media_rel_path,
            media_url=config.public_url(media_rel_path),
            media_type=media_type,
            media_length=media_length,
        )

    entry_number = next_entry_number(existing_entries, config)
    entry_slug = build_entry_slug(args, config, entry_number, None)
    page_rel_path = f"posts/{entry_slug}.html"
    page_url = config.public_url(page_rel_path)
    return Entry(
        title=args.title.strip(),
        page_rel_path=page_rel_path,
        page_url=page_url,
        guid=page_url,
        pub_date_rfc822=pub_date,
        date_label=date_label,
        summary_text=args.summary.strip(),
        description_html=html.escape(args.summary.strip()),
        body_html=body_html,
    )


def write_feed_file(feed_path: Path, config: ChannelConfig, entries: list[Entry], self_rel_path: str, include_content_ns: bool) -> None:
    root = ET.Element("rss", {"version": "2.0"})

    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = config.channel_title
    ET.SubElement(channel, "link").text = config.channel_url
    ET.SubElement(channel, "description").text = config.channel_description
    if config.channel_type == "audio":
        ET.SubElement(channel, f"{{{ITUNES_NS}}}author").text = config.author or config.channel_title
        ET.SubElement(channel, f"{{{ITUNES_NS}}}type").text = "episodic"
        ET.SubElement(channel, f"{{{ITUNES_NS}}}summary").text = config.channel_description
        ET.SubElement(channel, f"{{{ITUNES_NS}}}explicit").text = "true" if config.explicit else "false"
        ET.SubElement(channel, f"{{{ITUNES_NS}}}category", {"text": config.category or "Technology"})
    ET.SubElement(channel, "language").text = config.language
    ET.SubElement(channel, "lastBuildDate").text = entries[0].pub_date_rfc822 if entries else now_rfc822()
    ET.SubElement(
        channel,
        f"{{{ATOM_NS}}}link",
        {
            "href": config.public_url(self_rel_path),
            "rel": "self",
            "type": "application/rss+xml",
        },
    )

    ET.SubElement(channel, f"{{{ITUNES_NS}}}image", {"href": config.public_url(config.cover_image)}) if config.channel_type == "audio" else None
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = config.public_url(config.cover_image)
    ET.SubElement(image, "title").text = config.channel_title
    ET.SubElement(image, "link").text = config.channel_url

    for entry in entries:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = entry.title
        ET.SubElement(item, "link").text = entry.page_url
        ET.SubElement(item, "guid").text = entry.guid
        ET.SubElement(item, "pubDate").text = entry.pub_date_rfc822
        ET.SubElement(item, "description").text = entry.description_html
        if config.channel_type == "audio":
            if entry.duration:
                ET.SubElement(item, f"{{{ITUNES_NS}}}duration").text = entry.duration
            if entry.entry_number is not None:
                ET.SubElement(item, f"{{{ITUNES_NS}}}episode").text = str(entry.entry_number)
            ET.SubElement(item, f"{{{ITUNES_NS}}}episodeType").text = "full"
            ET.SubElement(item, f"{{{ITUNES_NS}}}explicit").text = "true" if config.explicit else "false"
            ET.SubElement(
                item,
                "enclosure",
                {
                    "url": entry.media_url or "",
                    "length": str(entry.media_length or 0),
                    "type": entry.media_type or "audio/mpeg",
                },
            )

    ET.indent(root, space="  ")
    tree = ET.ElementTree(root)
    tree.write(feed_path, encoding="utf-8", xml_declaration=True)


def render_audio_index(config: ChannelConfig, entries: list[Entry]) -> str:
    latest = entries[0] if entries else None
    older = entries[1:] if len(entries) > 1 else []
    highlight_source = latest.body_html if latest and latest.body_html else (latest.description_html if latest else "")
    highlights = extract_list_items(highlight_source)[:4] if latest else []
    older_html = ""
    if older:
        cards = []
        for entry in older:
            cards.append(
                f"""      <article class="episode">
        <h3><a href="./{html.escape(entry.page_rel_path)}">{html.escape(entry.title)}</a></h3>
        <p>{html.escape(entry.summary_text)}</p>
        <audio controls preload="none">
          <source src="./{html.escape(entry.media_rel_path or '')}" type="{html.escape(entry.media_type or 'audio/mpeg')}">
        </audio>
        <p><a href="./{html.escape(entry.page_rel_path)}">查看往期详情</a></p>
      </article>"""
            )
        older_html = f"""
    <section class="section">
      <h2>Earlier Episodes</h2>
{os.linesep.join(cards)}
    </section>"""

    highlight_html = ""
    if highlights:
        items = "\n".join(f"        <li>{html.escape(item)}</li>" for item in highlights)
        highlight_html = f"""
    <section class="section">
      <h2>Episode Highlights</h2>
      <ul class="resource-list">
{items}
      </ul>
    </section>"""

    latest_html = ""
    resources = ""
    if latest:
        latest_html = f"""
    <section class="section">
      <h2>Latest Episode</h2>
      <article class="episode">
        <h3><a href="./{html.escape(latest.page_rel_path)}">{html.escape(latest.title)}</a></h3>
        <p>{html.escape(latest.summary_text)}</p>
        <audio controls preload="none">
          <source src="./{html.escape(latest.media_rel_path or '')}" type="{html.escape(latest.media_type or 'audio/mpeg')}">
        </audio>
        <p><a href="./{html.escape(latest.page_rel_path)}">查看本期完整提要</a></p>
      </article>
    </section>"""
        resources = f"""
        <li><a href="./{html.escape(latest.page_rel_path)}">Latest episode detail page</a></li>
        <li><a href="./{html.escape(latest.media_rel_path or '')}">Latest audio file</a></li>"""

    apple_link = (
        f'\n          <a class="button" href="./{html.escape(config.apple_feed_path)}">Apple Podcasts RSS</a>\n'
        if config.apple_feed_path
        else '\n          <a class="button" href="./feed.xml">订阅 RSS</a>\n'
    )
    standard_link = (
        f'          <a class="button alt" href="./{html.escape(config.feed_path)}">标准 RSS</a>\n'
        if config.apple_feed_path
        else ""
    )
    open_latest = ""
    if latest:
        open_latest = (
            f'          <a class="button alt" href="./{html.escape(latest.page_rel_path)}">打开本期详情</a>\n'
            f'          <a class="button alt" href="./{html.escape(latest.media_rel_path or "")}">打开音频文件</a>\n'
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(config.channel_title)}</title>
  <style>
    :root {{
      --bg: #f9f3eb;
      --card: rgba(255, 255, 255, 0.9);
      --line: rgba(31, 41, 55, 0.12);
      --text: #172030;
      --muted: #596577;
      --accent: #b45309;
      --accent-dark: #8a3900;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      padding: 26px 16px 40px;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(180, 83, 9, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(2, 132, 199, 0.14), transparent 26%),
        linear-gradient(180deg, #fdf9f4 0%, #f0e5d7 100%);
      font-family: "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    }}

    main {{
      width: min(960px, 100%);
      margin: 0 auto;
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--card);
      box-shadow: 0 24px 80px rgba(31, 41, 55, 0.12);
    }}

    .hero {{
      display: grid;
      grid-template-columns: 180px 1fr;
      gap: 22px;
      align-items: center;
    }}

    .cover {{
      width: 100%;
      aspect-ratio: 1 / 1;
      border-radius: 22px;
      overflow: hidden;
      border: 1px solid var(--line);
      background: rgba(255, 250, 244, 0.8);
    }}

    .cover img {{
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2.1rem, 5vw, 3.6rem);
      line-height: 0.98;
    }}

    p {{
      margin: 14px 0 0;
      color: var(--muted);
      line-height: 1.75;
    }}

    .links,
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 18px;
    }}

    .button,
    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      text-decoration: none;
    }}

    .button {{
      padding: 12px 16px;
      background: var(--accent);
      color: #fff8f1;
      font-weight: 700;
    }}

    .button.alt {{
      background: rgba(255, 255, 255, 0.75);
      color: var(--text);
      border: 1px solid var(--line);
    }}

    .pill {{
      padding: 10px 14px;
      border: 1px solid var(--line);
      color: var(--accent-dark);
      background: rgba(255, 248, 240, 0.9);
      font-size: 0.94rem;
      font-weight: 700;
    }}

    .section {{
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid var(--line);
    }}

    .section h2 {{
      margin: 0;
      font-size: 1.2rem;
    }}

    .episode {{
      margin-top: 16px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background: rgba(255, 251, 246, 0.88);
    }}

    .episode h3 {{
      margin: 0;
      font-size: 1.06rem;
    }}

    .episode p {{
      margin-top: 10px;
    }}

    audio {{
      width: 100%;
      margin-top: 14px;
    }}

    .resource-list {{
      margin: 14px 0 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.8;
    }}

    a {{ color: inherit; }}

    @media (max-width: 720px) {{
      .hero {{ grid-template-columns: 1fr; }}
      .cover {{ max-width: 220px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="cover">
        <img src="./{html.escape(config.cover_image)}" alt="{html.escape(config.channel_title)} cover">
      </div>
      <div>
        <h1>{html.escape(config.channel_title)}</h1>
        <p>{html.escape(config.channel_description)}</p>
        <div class="links">
{apple_link}{standard_link}{open_latest}          <a class="button alt" href="../">返回频道索引</a>
        </div>
        <div class="meta">
          <span class="pill">Slug: {html.escape(config.slug)}</span>
          <span class="pill">Audio RSS</span>
          <span class="pill">Script-managed</span>
        </div>
      </div>
    </section>{latest_html}{highlight_html}{older_html}

    <section class="section">
      <h2>Resources</h2>
      <ul class="resource-list">
        {f'<li><a href="./{html.escape(config.apple_feed_path)}">Apple Podcasts RSS</a></li>' if config.apple_feed_path else ''}
        <li><a href="./{html.escape(config.feed_path)}">RSS feed.xml</a></li>
        <li><a href="./{html.escape(config.cover_image)}">Cover image</a></li>{resources}
      </ul>
    </section>
  </main>
</body>
</html>
"""


def render_text_index(config: ChannelConfig, entries: list[Entry]) -> str:
    cards = []
    for entry in entries:
        cards.append(
            f"""      <article class="entry">
        <h3><a href="./{html.escape(entry.page_rel_path)}">{html.escape(entry.title)}</a></h3>
        <div class="date">{html.escape(entry.date_label)}</div>
        <p>{html.escape(entry.summary_text)}</p>
        <p><a href="./{html.escape(entry.page_rel_path)}">打开原文</a></p>
      </article>"""
        )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(config.channel_title)}</title>
  <style>
    :root {{
      --bg: #f7f0e8;
      --card: rgba(255, 255, 255, 0.9);
      --line: rgba(31, 41, 55, 0.12);
      --text: #172030;
      --muted: #5d6878;
      --accent: #9f3e16;
      --accent-soft: #fff6ef;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      padding: 28px 16px 42px;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(159, 62, 22, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(3, 105, 161, 0.12), transparent 26%),
        linear-gradient(180deg, #fcf8f3 0%, #efe4d7 100%);
      font-family: "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    }}

    main {{
      width: min(980px, 100%);
      margin: 0 auto;
      padding: 30px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--card);
      box-shadow: 0 24px 78px rgba(31, 41, 55, 0.12);
    }}

    .hero {{
      display: grid;
      grid-template-columns: 180px 1fr;
      gap: 22px;
      align-items: center;
    }}

    .cover {{
      width: 100%;
      aspect-ratio: 1 / 1;
      border-radius: 22px;
      overflow: hidden;
      border: 1px solid var(--line);
      background: var(--accent-soft);
    }}

    .cover img {{
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2.1rem, 5vw, 3.6rem);
      line-height: 0.98;
    }}

    p {{
      margin: 14px 0 0;
      color: var(--muted);
      line-height: 1.8;
    }}

    .links,
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 18px;
    }}

    .button,
    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      text-decoration: none;
    }}

    .button {{
      padding: 12px 16px;
      background: var(--accent);
      color: #fff8f2;
      font-weight: 700;
    }}

    .button.alt {{
      background: rgba(255, 255, 255, 0.75);
      color: var(--text);
      border: 1px solid var(--line);
    }}

    .pill {{
      padding: 10px 14px;
      border: 1px solid var(--line);
      background: rgba(255, 247, 240, 0.92);
      color: var(--accent);
      font-size: 0.94rem;
      font-weight: 700;
    }}

    .section {{
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid var(--line);
    }}

    .section h2 {{
      margin: 0;
      font-size: 1.2rem;
    }}

    .entry {{
      margin-top: 16px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background: rgba(255, 250, 244, 0.88);
    }}

    .entry h3 {{
      margin: 0;
      font-size: 1.05rem;
    }}

    .entry .date {{
      margin-top: 8px;
      color: var(--accent);
      font-size: 0.92rem;
      font-weight: 700;
    }}

    .entry p {{
      margin-top: 12px;
    }}

    .resource-list {{
      margin: 14px 0 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.8;
    }}

    a {{ color: inherit; }}

    @media (max-width: 720px) {{
      .hero {{ grid-template-columns: 1fr; }}
      .cover {{ max-width: 220px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="cover">
        <img src="./{html.escape(config.cover_image)}" alt="{html.escape(config.channel_title)} cover">
      </div>
      <div>
        <h1>{html.escape(config.channel_title)}</h1>
        <p>{html.escape(config.channel_description)}</p>
        <div class="links">
          <a class="button" href="./{html.escape(config.feed_path)}">订阅 RSS</a>
          <a class="button alt" href="../">返回频道索引</a>
        </div>
        <div class="meta">
          <span class="pill">Slug: {html.escape(config.slug)}</span>
          <span class="pill">Text-only RSS</span>
          <span class="pill">Script-managed</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Recent Posts</h2>
{os.linesep.join(cards)}
    </section>

    <section class="section">
      <h2>Resources</h2>
      <ul class="resource-list">
        <li><a href="./{html.escape(config.feed_path)}">RSS feed.xml</a></li>
        <li><a href="./{html.escape(config.cover_image)}">Cover image</a></li>
      </ul>
    </section>
  </main>
</body>
</html>
"""


def render_audio_detail(config: ChannelConfig, entry: Entry) -> str:
    content_html = entry.body_html or f"<p>{html.escape(entry.summary_text)}</p>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(entry.title)} | {html.escape(config.channel_title)}</title>
  <style>
    :root {{
      --bg: #f9f2e8;
      --card: rgba(255, 255, 255, 0.9);
      --line: rgba(31, 41, 55, 0.12);
      --text: #172030;
      --muted: #5c6777;
      --accent: #b45309;
      --accent-dark: #8a3900;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      padding: 28px 16px 44px;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(180, 83, 9, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(2, 132, 199, 0.12), transparent 24%),
        linear-gradient(180deg, #fcf8f3 0%, #efe4d6 100%);
      font-family: "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    }}

    main {{
      width: min(920px, 100%);
      margin: 0 auto;
      padding: 30px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--card);
      box-shadow: 0 24px 80px rgba(31, 41, 55, 0.12);
    }}

    .eyebrow {{
      margin: 0 0 12px;
      color: var(--accent);
      font-size: 0.82rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2rem, 5vw, 3.4rem);
      line-height: 1.05;
    }}

    p,
    li {{
      color: var(--muted);
      line-height: 1.8;
    }}

    .meta,
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 18px;
    }}

    .pill,
    .button {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      text-decoration: none;
    }}

    .pill {{
      padding: 10px 14px;
      border: 1px solid var(--line);
      background: rgba(255, 249, 242, 0.92);
      color: var(--accent-dark);
      font-weight: 700;
    }}

    .button {{
      padding: 12px 16px;
      background: var(--accent);
      color: #fff8f1;
      font-weight: 700;
    }}

    .button.alt {{
      background: rgba(255, 255, 255, 0.76);
      color: var(--text);
      border: 1px solid var(--line);
    }}

    .section {{
      margin-top: 26px;
      padding-top: 24px;
      border-top: 1px solid var(--line);
    }}

    .section h2 {{
      margin: 0;
      font-size: 1.18rem;
    }}

    audio {{
      width: 100%;
      margin-top: 16px;
    }}

    ul,
    ol {{
      margin: 14px 0 0;
      padding-left: 22px;
    }}

    blockquote {{
      margin: 16px 0 0;
      padding: 16px 18px;
      border-left: 4px solid var(--accent);
      border-radius: 0 18px 18px 0;
      background: rgba(255, 248, 240, 0.92);
      color: var(--text);
    }}

    a {{ color: inherit; }}
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">{html.escape(config.channel_title)} Episode {entry.entry_number or ''}</p>
    <h1>{html.escape(entry.title)}</h1>
    <p>{html.escape(entry.summary_text)}</p>

    <div class="meta">
      <span class="pill">发布日期：{html.escape(entry.date_label)}</span>
      <span class="pill">时长：{html.escape(entry.duration or '--:--')}</span>
      <span class="pill">频道：{html.escape(config.channel_title)}</span>
    </div>

    <div class="actions">
      <a class="button" href="../{html.escape(entry.media_rel_path or '')}">播放 MP3</a>
      <a class="button alt" href="../{html.escape(config.apple_feed_path or config.feed_path)}">打开 RSS</a>
      <a class="button alt" href="../">返回频道页</a>
    </div>

    <section class="section">
      <h2>本期音频</h2>
      <audio controls preload="none">
        <source src="../{html.escape(entry.media_rel_path or '')}" type="{html.escape(entry.media_type or 'audio/mpeg')}">
      </audio>
    </section>

    <section class="section">
      <h2>本期内容</h2>
      {content_html}
    </section>
  </main>
</body>
</html>
"""


def render_text_detail(config: ChannelConfig, entry: Entry) -> str:
    content_html = entry.body_html or f"<p>{html.escape(entry.summary_text)}</p>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(entry.title)} | {html.escape(config.channel_title)}</title>
  <style>
    :root {{
      --bg: #f8f1e7;
      --card: rgba(255, 255, 255, 0.92);
      --line: rgba(31, 41, 55, 0.12);
      --text: #172030;
      --muted: #5d6878;
      --accent: #9f3e16;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      padding: 28px 16px 40px;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(159, 62, 22, 0.16), transparent 28%),
        linear-gradient(180deg, #fcf8f3 0%, #efe4d7 100%);
      font-family: "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    }}

    main {{
      width: min(820px, 100%);
      margin: 0 auto;
      padding: 32px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--card);
      box-shadow: 0 24px 78px rgba(31, 41, 55, 0.12);
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2rem, 5vw, 3.4rem);
      line-height: 1.02;
    }}

    .meta {{
      margin-top: 12px;
      color: var(--accent);
      font-weight: 700;
    }}

    p,
    li {{
      margin: 16px 0 0;
      color: var(--muted);
      line-height: 1.9;
      font-size: 1.04rem;
    }}

    ul,
    ol {{
      padding-left: 24px;
    }}

    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 24px;
    }}

    .actions a {{
      display: inline-flex;
      padding: 12px 16px;
      border-radius: 999px;
      text-decoration: none;
      background: rgba(255, 255, 255, 0.8);
      border: 1px solid var(--line);
      color: var(--text);
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{html.escape(entry.title)}</h1>
    <div class="meta">{html.escape(entry.date_label)} · {html.escape(config.channel_title)}</div>
    {content_html}
    <div class="actions">
      <a href="../">返回频道首页</a>
      <a href="../{html.escape(config.feed_path)}">打开 RSS</a>
    </div>
  </main>
</body>
</html>
"""


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    channel_dir = Path(args.channel_dir).resolve()
    if not channel_dir.is_dir():
        die(f"Channel directory not found: {channel_dir}")

    config = load_channel_config(channel_dir)
    main_feed_path = channel_dir / config.feed_path
    existing_entries = parse_existing_entries(main_feed_path, config)
    new_entry = create_new_entry(args, channel_dir, config, existing_entries)
    all_entries = [new_entry] + existing_entries

    if args.dry_run:
        print(json.dumps({
            "channel": config.slug,
            "type": config.channel_type,
            "new_page": new_entry.page_rel_path,
            "new_media": new_entry.media_rel_path,
            "entry_number": new_entry.entry_number,
            "feed_count_after": len(all_entries),
        }, ensure_ascii=False, indent=2))
        return

    if config.channel_type == "audio":
        write_text(channel_dir / new_entry.page_rel_path, render_audio_detail(config, new_entry))
        write_text(channel_dir / "index.html", render_audio_index(config, all_entries))
        write_feed_file(main_feed_path, config, all_entries, config.feed_path, include_content_ns=False)
        if config.apple_feed_path:
            write_feed_file(channel_dir / config.apple_feed_path, config, all_entries, config.apple_feed_path, include_content_ns=True)
    else:
        write_text(channel_dir / new_entry.page_rel_path, render_text_detail(config, new_entry))
        write_text(channel_dir / "index.html", render_text_index(config, all_entries))
        write_feed_file(main_feed_path, config, all_entries, config.feed_path, include_content_ns=False)

    print(f"Updated channel: {config.slug}")
    print(f"New detail page: {new_entry.page_rel_path}")
    if new_entry.media_rel_path:
        print(f"New media file: {new_entry.media_rel_path}")
    print(f"Feed updated: {config.feed_path}")
    if config.apple_feed_path:
        print(f"Apple feed updated: {config.apple_feed_path}")


if __name__ == "__main__":
    main()
