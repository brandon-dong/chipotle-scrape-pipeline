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
