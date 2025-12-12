#!/usr/bin/env python3
"""Quick test of scraper.search_telegram directly."""

from scraper import search_telegram

query = '六合彩'
print(f'Calling search_telegram("{query}")...')
try:
    results = search_telegram(query)
    print(f'\nGot {len(results)} results:\n')
    for i, r in enumerate(results, 1):
        print(f'{i:2d}. {r["title"][:60]:60s} | {r["link"][:80]}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
