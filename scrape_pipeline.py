import datetime
import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import requests


def url_to_slug(url: str) -> str:
    slug = re.sub(r"^https?://", "", url)
    slug = re.sub(r"[/.]", "_", slug)
    return slug.strip("_")


if __name__ == '__main__':
    load_dotenv()

    api_key = os.getenv("FIRECRAWL_API_KEY")

    api_url = "https://api.firecrawl.dev/v2/search"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "query": "Chipotle investor relations press releases",
        "limit": 5,
        "scrapeOptions": {"formats": ["markdown"]}
    }

    response = requests.post(api_url, headers=headers, json=payload)

    data = response.json()
    results = data["data"]["web"]

    today = datetime.date.today().isoformat()
    out_dir = Path("knowledge/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Firecrawl returned {len(results)} results")

    for r in results:
        slug = url_to_slug(r["url"])
        filename = f"{today}_{slug}.md"
        filepath = out_dir / filename

        if not r.get("markdown"):
            print(f"  [no content] {filename}")
            continue

        if filepath.exists():
            print(f"  [skipped] {filename}")
            continue

        content = (
            f"---\n"
            f"title: {r['title']}\n"
            f"url: {r['url']}\n"
            f"scraped_at: {today}\n"
            f"---\n\n"
            f"{r['markdown']}"
        )
        filepath.write_text(content, encoding="utf-8")
        print(f"  [saved] {filename}")