import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "update_channel.py"


class UpdateChannelDeleteTests(unittest.TestCase):
    def run_script(self, *args, cwd=None):
        return subprocess.run(
            ["python3", str(SCRIPT), *args],
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
        )

    def copy_channel(self, relative_path: str) -> Path:
        tmpdir = Path(tempfile.mkdtemp(prefix="rss-channel-test-"))
        self.addCleanup(lambda: shutil.rmtree(tmpdir, ignore_errors=True))
        target = tmpdir / Path(relative_path).name
        shutil.copytree(REPO_ROOT / relative_path, target)
        return target

    def test_delete_text_entry_removes_feed_item_and_post_file(self):
        channel_dir = self.copy_channel("feeds/sample-podcast-text")

        result = self.run_script(
            "--channel-dir",
            str(channel_dir),
            "--delete-slug",
            "issue-003",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertFalse((channel_dir / "posts" / "issue-003.html").exists())

        feed_text = (channel_dir / "feed.xml").read_text(encoding="utf-8")
        index_text = (channel_dir / "index.html").read_text(encoding="utf-8")

        self.assertNotIn("Issue 003: Stable URLs Matter", feed_text)
        self.assertNotIn("./posts/issue-003.html", index_text)

    def test_delete_audio_entry_removes_feed_items_detail_page_and_media(self):
        channel_dir = self.copy_channel("feeds/doublea")

        result = self.run_script(
            "--channel-dir",
            str(channel_dir),
            "--delete-slug",
            "episode-002-token-economy-self-drive",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertFalse((channel_dir / "episodes" / "episode-002-token-economy-self-drive.html").exists())
        self.assertFalse((channel_dir / "audio" / "episode-002-token-economy-self-drive.mp3").exists())

        feed_text = (channel_dir / "feed.xml").read_text(encoding="utf-8")
        apple_feed_text = (channel_dir / "apple-feed.xml").read_text(encoding="utf-8")
        index_text = (channel_dir / "index.html").read_text(encoding="utf-8")

        self.assertNotIn("用代币制激发自驱力", feed_text)
        self.assertNotIn("用代币制激发自驱力", apple_feed_text)
        self.assertNotIn("./episodes/episode-002-token-economy-self-drive.html", index_text)
        self.assertIn("设计有效的奖励：从斯金纳到自律", index_text)


if __name__ == "__main__":
    unittest.main()
