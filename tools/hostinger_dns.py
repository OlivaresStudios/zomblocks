"""Points zomblocks.eu to GitHub Pages in the DNS zone at Hostinger (where the domain was bought), through the Hostinger
API. The API token is read from the HOSTINGER_API_TOKEN environment variable (hPanel > Account > API), never stored here.

    python tools/hostinger_dns.py            shows the zone and what would change (nothing is written)
    python tools/hostinger_dns.py --apply    validates the change, then writes it

The apex gets GitHub Pages' 4 IPv4 and 4 IPv6 addresses, www a CNAME to olivaresstudios.github.io; an ALIAS or CNAME
on the apex (Hostinger's parking page) is removed first. Every other record (mail, TXT...) is left as it is.
"""
import json
import os
import sys
import urllib.error
import urllib.request

DOMAIN = 'zomblocks.eu'
API = 'https://developers.hostinger.com/api/dns/v1/zones/' + DOMAIN
TTL = 3600
WANTED = [
    {'name': '@', 'type': 'A', 'ttl': TTL, 'records': [{'content': ip} for ip in (
        '185.199.108.153', '185.199.109.153', '185.199.110.153', '185.199.111.153')]},
    {'name': '@', 'type': 'AAAA', 'ttl': TTL, 'records': [{'content': ip} for ip in (
        '2606:50c0:8000::153', '2606:50c0:8001::153', '2606:50c0:8002::153', '2606:50c0:8003::153')]},
    {'name': 'www', 'type': 'CNAME', 'ttl': TTL, 'records': [{'content': 'olivaresstudios.github.io.'}]},
]


def call(method, url, body=None):
    token = os.environ.get('HOSTINGER_API_TOKEN')
    if not token:
        sys.exit('HOSTINGER_API_TOKEN is not set (hPanel > Account > API: create a token)')
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
                                          'Accept': 'application/json',
                                          'User-Agent': 'zomblocks-wiki-dns/1.0'})   # the default Python agent is refused
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode()
    except urllib.error.HTTPError as e:
        sys.exit('%s %s -> %d %s' % (method, url, e.code, e.read().decode()[:500]))
    return json.loads(text) if text.strip() else {}


def show(zone):
    for rr in sorted(zone, key=lambda r: (r['name'], r['type'])):
        print('  %-6s %-6s %s' % (rr['name'], rr['type'], ', '.join(x['content'] for x in rr.get('records', []))))


def main():
    zone = call('GET', API)
    print('zone now:')
    show(zone)
    stale = [{'name': '@', 'type': rr['type']} for rr in zone if rr['name'] == '@' and rr['type'] in ('ALIAS', 'CNAME')]
    print('to remove:', ', '.join('%(name)s %(type)s' % s for s in stale) or 'nothing')
    print('to write:')
    show(WANTED)
    if '--apply' not in sys.argv:
        print('dry run: add --apply to write it')
        return
    body = {'overwrite': True, 'zone': WANTED}
    if stale:
        call('DELETE', API, {'filters': stale})
    call('POST', API + '/validate', body)
    call('PUT', API, body)
    print('zone after:')
    show(call('GET', API))


if __name__ == '__main__':
    main()
