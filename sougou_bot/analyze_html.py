from bs4 import BeautifulSoup

html = open('rendered.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')

# Find all t.me links
links = [a for a in soup.find_all('a') if 't.me' in a.get('href', '')]
print(f'Found {len(links)} t.me links\n')

for i, l in enumerate(links[:25], 1):
    text = l.get_text(strip=True)
    href = l.get('href', '')
    print(f'{i:2d}. {text[:70]:70s} | {href[:80]}')

# Analyze parent structure of first link
if links:
    first = links[0]
    print(f'\n--- Parent structure of first link ---')
    print(f'Tag: {first.name}')
    parent = first.parent
    for i in range(5):
        if parent:
            print(f'Parent {i}: {parent.name} {parent.get("class", [])} id={parent.get("id", "")}')
            parent = parent.parent
