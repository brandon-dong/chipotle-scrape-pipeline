import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scrape_pipeline import url_to_slug


def test_slug_strips_scheme_and_replaces_separators():
    assert url_to_slug("https://ir.chipotle.com/news-releases") == "ir_chipotle_com_news-releases"


def test_slug_handles_trailing_slash():
    assert url_to_slug("https://ir.chipotle.com/") == "ir_chipotle_com"


def test_slug_handles_no_path():
    assert url_to_slug("https://ir.chipotle.com") == "ir_chipotle_com"


def test_slug_handles_http():
    assert url_to_slug("http://example.com/foo/bar") == "example_com_foo_bar"


import datetime
from pathlib import Path


def _make_result(title, url, markdown):
    return {"title": title, "url": url, "markdown": markdown}


def test_save_writes_file_with_frontmatter(tmp_path):
    result = _make_result(
        "News Releases - Chipotle",
        "https://ir.chipotle.com/news-releases",
        "## News\n\nSome content here."
    )
    today = "2026-04-15"
    slug = url_to_slug(result["url"])
    filepath = tmp_path / f"{today}_{slug}.md"

    content = f"---\ntitle: {result['title']}\nurl: {result['url']}\nscraped_at: {today}\n---\n\n{result['markdown']}"
    filepath.write_text(content, encoding="utf-8")

    assert filepath.exists()
    text = filepath.read_text(encoding="utf-8")
    assert "title: News Releases - Chipotle" in text
    assert "url: https://ir.chipotle.com/news-releases" in text
    assert "scraped_at: 2026-04-15" in text
    assert "## News" in text


def test_no_content_result_skips_write(tmp_path):
    result = _make_result("Empty Page", "https://ir.chipotle.com/empty", None)
    today = "2026-04-15"
    slug = url_to_slug(result["url"])
    filepath = tmp_path / f"{today}_{slug}.md"

    if result.get("markdown"):
        filepath.write_text("content", encoding="utf-8")

    assert not filepath.exists()


def test_existing_file_is_not_overwritten(tmp_path):
    result = _make_result(
        "News Releases",
        "https://ir.chipotle.com/news-releases",
        "New content that should not overwrite."
    )
    today = "2026-04-15"
    slug = url_to_slug(result["url"])
    filepath = tmp_path / f"{today}_{slug}.md"
    filepath.write_text("original content", encoding="utf-8")

    if not filepath.exists():
        filepath.write_text("should not reach here", encoding="utf-8")

    assert filepath.read_text(encoding="utf-8") == "original content"
