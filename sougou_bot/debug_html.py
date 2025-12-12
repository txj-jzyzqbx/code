#!/usr/bin/env python3
"""Debug script to save and analyze Selenium-rendered HTML from telegramsearchengine."""

import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

path = ChromeDriverManager().install()
service = Service(path)
driver = webdriver.Chrome(service=service, options=options)

query = sys.argv[1] if len(sys.argv) > 1 else '六合彩'
url = f'https://telegramsearchengine.com/?q={query}&gsc.tab=0&gsc.q={query}&gsc.page=0'

print(f'[debug] Fetching {url}')
driver.set_page_load_timeout(30)
driver.get(url)
print('[debug] Page loaded')

import time
time.sleep(5)  # wait for JS rendering

html = driver.page_source
driver.quit()

print(f'[debug] HTML length: {len(html)} bytes')

# Save to file
with open('rendered.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('[debug] Saved to rendered.html')

# Analyze structure
soup = BeautifulSoup(html, 'html.parser')

# Look for any <a> tags that might be results
print('\n--- Looking for <a> tags with t.me in href ---')
t_me_links = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    if 't.me' in href:
        title = a.get_text(strip=True)
        t_me_links.append((title, href))
        print(f'  {title[:60]} -> {href}')

print(f'\nFound {len(t_me_links)} t.me links\n')

# Look for common result container patterns
print('--- Checking various CSS selectors ---')
selectors = [
    'div.gs-title a',
    'a.gs-title',
    'div.gs-webResult a',
    'div.gs-snippet a',
    'div[data-result] a',
    'div.result a',
    'a[href*="t.me"]',
    'div.gsc-result a',
    'div.gsc_table_cell a',
    'li a[href*="t.me"]',
]

for selector in selectors:
    found = soup.select(selector)
    print(f'  {selector:40s} -> {len(found)} elements')
    if found and len(found) <= 3:
        for elem in found:
            print(f'      {elem.get_text(strip=True)[:60]}')

# Print snippet of HTML around t.me
print('\n--- HTML snippet around first t.me link ---')
if t_me_links:
    idx = html.find(t_me_links[0][1])
    if idx > 0:
        snippet_start = max(0, idx - 300)
        snippet_end = min(len(html), idx + 500)
        print(html[snippet_start:snippet_end])
