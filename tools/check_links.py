"""Checks the built wiki: every link (href) and image / script (src) of every page points to an existing file.
    python tools/check_links.py        (must end with "0 broken")"""
import glob
import os
import re
from urllib.parse import unquote

PUBLIC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
broken = []
pages = glob.glob(os.path.join(PUBLIC, '**', '*.html'), recursive=True)
for page in pages:
    html = open(page, encoding='utf-8').read()
    base = os.path.dirname(page)
    for attr, link in re.findall(r'(href|src)="([^"]+)"', html):
        if link.startswith(('http', 'data:', '#', 'mailto:')):
            continue
        path = unquote(link.split('#')[0].split('?')[0])
        if not path:
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, path))):
            broken.append((os.path.relpath(page, PUBLIC), attr, link))
seen = set()
for b in broken:
    if b[2] not in seen:
        print(*b)
        seen.add(b[2])
print('%d pages, %d broken (%d distinct targets)' % (len(pages), len(broken), len(seen)))
