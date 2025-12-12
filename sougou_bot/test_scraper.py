#!/usr/bin/env python3
"""Test module to fetch telegramsearchengine HTML and compare parsing results.

Usage:
    python test_scraper.py [query]

This script will:
- Build the search URL for `telegramsearchengine.com` using the provided query
- Fetch the static HTML via urllib (no JS rendering)
- Print HTTP info, snippet of HTML, counts of likely result markers
- Run BeautifulSoup selectors used in the scraper and list found anchors
- If `search_telegram` from `scraper.py` is importable, call it and print the parsed results
"""

import sys
import urllib.parse
import urllib.request
import ssl
from bs4 import BeautifulSoup

DEFAULT_QUERY = "六合彩"


def build_url(query, page=1):
    base = "https://telegramsearchengine.com/"
    params = {
        "q": query,
        "gsc.tab": "0",
        "gsc.q": query,
        "gsc.page": str(page - 1),
    }
    return base + "?" + urllib.parse.urlencode(params)


def fetch_static_html(url, timeout=15):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    req = urllib.request.Request(url, headers=headers)
    # allow insecure ssl if needed
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            status = resp.getcode()
            content = resp.read()
            return status, content
    except Exception as e:
        return None, f"ERROR: {e}".encode("utf-8")


def analyze_html(content):
    text = content.decode("utf-8", errors="replace")
    print("\n--- HTML Snippet (first 3000 chars) ---\n")
    print(text[:3000])
    print("\n--- End Snippet ---\n")

    # quick checks
    n_gs_title = text.count('gs-title')
    n_gsc_q = text.count('gsc.q')
    n_t_me = text.count('t.me/')
    print(f"Occurrences: gs-title={n_gs_title}, gsc.q={n_gsc_q}, t.me/={n_t_me}")

    soup = BeautifulSoup(text, "html.parser")
    # selector used in scraper: div.gs-title a
    anchors = soup.select("div.gs-title a")
    print(f"BeautifulSoup found {len(anchors)} anchors using selector 'div.gs-title a'.")
    for i, a in enumerate(anchors[:10], 1):
        href = a.get("href")
        title = a.get_text(strip=True)
        print(f" {i}. title={repr(title)[:80]} href={href}")

    # also try to find any <a class="gs-title"> directly
    anchors2 = soup.select("a.gs-title")
    print(f"Found {len(anchors2)} anchors using selector 'a.gs-title'.")
    for i, a in enumerate(anchors2[:10], 1):
        print(f" a.gs-title {i}: text={repr(a.get_text(strip=True))[:80]} href={a.get('href')}")


def try_call_scraper(query):
    try:
        from scraper import search_telegram
    except Exception as e:
        print(f"Cannot import search_telegram from scraper.py: {e}")
        return

    print("\nCalling existing scraper.search_telegram (this may use Selenium and take a few seconds)...\n")
    try:
        results = search_telegram(query)
        print(f"scraper.search_telegram returned {len(results)} results")
        for i, r in enumerate(results[:10], 1):
            print(f" {i}. {r.get('title')} -> {r.get('link')}")
    except Exception as e:
        print(f"scraper.search_telegram raised an exception: {e}")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY
    print(f"Query: {query}")
    url = build_url(query)
    print(f"URL: {url}\n")

    status, content = fetch_static_html(url)
    if status is None:
        print(content.decode('utf-8', errors='replace'))
        print("\n继续：将尝试调用 Selenium 路径的 `scraper.search_telegram()` 来获取渲染后数据。")
    else:
        print(f"HTTP status: {status}; bytes: {len(content)}")
        analyze_html(content)

    # 调用现有的 scraper.search_telegram（Selenium 渲染）以比较结果
    try_call_scraper(query)
