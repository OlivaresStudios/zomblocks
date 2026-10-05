"""Builds the Zombie Extraction wiki into zombie_wiki/public/ (static pages: open public/index.html, no server needed).

    python tools/build.py              # everything (renders take about a minute)
    python tools/build.py --fast       # pages only, keeps the renders already made

Data: tools/wiki_data.py (read from the add-on), texts: content/*.py, look: web/css, behaviour: web/js.
"""
import datetime
import html
import json
import os
import shutil
import sys

import wiki_assets as A
import wiki_data as W

OUT = os.path.join(W.WIKI, 'public')
WEB = os.path.join(W.WIKI, 'web')
E = html.escape

THREAT_WORDS = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Very high', 5: 'Deadly'}

# sidebar: (group, [(slug, title, icon, count)]); a slug without a built page is shown as "soon"
SECTIONS = [
    ('Start here', [('index', 'Home', 'img/items/guidebook.png', None), ('guides/first-night', 'Your first night', 'img/items/canned_beans.png', None)]),
    ('Threats', [('zombies/index', 'Zombies', 'img/eggs/zombie_mime.png', 60), ('bosses/index', 'Bosses', 'img/eggs/zombie_conductor.png', 8),
                 ('infection', 'Infection', 'img/items/medicine.png', None)]),
    ('Gear', [('weapons/index', 'Weapons', 'img/items/baseball_bat.png', 43), ('mods', 'Weapon mods & Fabricator', 'img/items/electric_cable.png', None),
              ('armor/index', 'Armor sets', 'img/items/biker_chest.png', 12), ('food', 'Food & medical', 'img/items/first_aid_kit.png', None),
              ('gear', 'Survival gear', 'img/items/flashlight.png', None)]),
    ('People', [('traders', 'Traders', 'img/items/scrap.png', 8), ('allies', 'Allies', 'img/items/whistle.png', None)]),
    ('World', [('buggy', 'Rusty Buggy', 'img/items/rusty_buggy.png', None), ('world', 'Loot & world', 'img/eggs/toolbox.png', None),
               ('furniture', 'Furniture', 'img/eggs/armchair.png', 17), ('achievements', 'Achievements', 'img/items/lucky_coin.png', 23)]),
]
# what the coming sections will hold (shown on their "coming soon" page)
PLANNED = {
    'guides/first-night': ['The Zombie Guidebook you get at your first join', 'Your first weapon and where to find scrap',
                           'How not to get bitten, and what to do if you are'],
    'infection': ['The 4 stages and how fast it grows', 'What each cure really does (bandage, medicine, first aid kit, pickles)',
                  'The screens of the infection monitor', 'Armor that protects you from bites'],
    'weapons/index': ['Every melee, ranged, OP weapon, gadget and spray', 'Damage, durability or tank, special effect',
                      'Where to find each one: trader and price, loot, boss drops', 'Which weapon mods fit'],
    'mods': ['The 5 mods, their parts and where to find them', 'The 7 signature combos', 'Reinforced weapons and the costs'],
    'armor/index': ['The 12 armor sets and every piece', 'Protection, durability and the full set bonus', 'Where to find them'],
    'food': ['Every food and what it does', 'Bandage, medicine and first aid kit'],
    'gear': ['Flashlight, binoculars, walkie-talkie, decoys, motion sensor, gas column...'],
    'traders': ['The 8 kinds of trader and what each one sells', 'How stock is rolled (common, rare, OP)', 'Every price, and the barter'],
    'allies': ['Hiring an ally, its menu and its bag', 'Healing, reviving (45 s when downed), dismissing', 'The whistle compass'],
    'buggy': ['Fuel and driving', 'The 16 modules and 17 paints', 'The holographic garage and the wrench'],
    'world': ['Containers you can search and their loot', 'Supply drops', 'Special blocks: electric fence, barbed wire, glue, sprinkler, manhole',
              'Toxic clouds, noise and the Blind'],
    'furniture': ['The 17 pieces of furniture', 'Carrying, breaking and what they drop'],
    'achievements': ['The 23 achievements and how to get each one'],
}
BUILT = {slug for _g, items in SECTIONS for slug, *_rest in items}           # every section is built now

# animation buttons of the boss pages (key -> label) when the attack list order does not match the animations
BOSS_ANIM_LABELS = {'zombie_mega_mascot': {'attack1': 'Belly bump', 'attack2': 'Bounce', 'attack3': 'Deflate', 'attack4': 'Call the team'}}


def url(slug):
    return slug + '.html'


def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


def skulls(n):
    return '<span class="skulls">' + ''.join('<i class="on"></i>' if i < n else '<i></i>' for i in range(5)) + '</span>'


def zimg(z, k=0):
    return 'img/z/%s_%d.png' % (z['id'], k)


def zurl(z):
    return ('bosses/' if z['kind'] == 'boss' else 'zombies/') + z['id'] + '.html'


# ------------------------------------------------------------------------------------------------ layout
def layout(rel, title, body, active, scripts=''):
    depth = rel.count('/')
    root = '../' * depth
    side = []
    for group, items in SECTIONS:
        side.append('<h6>%s</h6>' % E(group))
        for slug, name, icon, count in items:
            n = '<span class="n">%d</span>' % count if count else ''
            img = '<img src="%s%s" alt="">' % (root, icon)
            if slug in BUILT:
                on = ' class="on"' if slug == active else ''
                side.append('<a%s href="%s%s">%s%s%s</a>' % (on, root, url(slug), img, E(name), n))
            else:
                on = ' class="on"' if slug == active else ''
                side.append('<a%s href="%s%s" style="color:var(--dim)">%s%s<span class="n" style="font-size:9px;letter-spacing:.12em">SOON</span></a>' % (on, root, url(slug), img, E(name)))
    return '''<!doctype html>
<html lang="en" data-root="%(root)s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s - Zombie Extraction Wiki</title>
<link rel="icon" href="%(root)simg/eggs/zombie_mime.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="%(root)scss/wiki.css"></head><body>
<header class="top"><button class="menu-btn" id="menu">Menu</button><a class="logo" href="%(root)sindex.html"><span class="biohaz"></span><span class="full">ZOMBIE EXTRACTION</span><small>WIKI</small></a>
<div class="search"><input id="q" type="search" placeholder="Search zombies, bosses, weapons..." autocomplete="off"><kbd>/</kbd><div class="results" id="results"></div></div>
<nav class="topnav"><a href="%(root)sindex.html"%(home_on)s>Wiki</a><a href="%(root)szombies/index.html">Zombies</a><a href="%(root)sbosses/index.html">Bosses</a></nav></header>
<div class="wrap"><nav class="side">%(side)s</nav><main class="main">%(body)s
<footer><span>Zombie Extraction Wiki &middot; every number comes from the add-on itself</span><span>Updated %(date)s</span><span>PEGI 10</span></footer></main></div>
<script src="%(root)sjs/search-index.js"></script><script src="%(root)sjs/wiki.js"></script>%(scripts)s
</body></html>
''' % dict(root=root, title=E(title), side=''.join(side), body=body, date=datetime.date.today().strftime('%d %b %Y'),
           home_on=' class="on"' if active == 'index' else '', scripts=scripts)


# ------------------------------------------------------------------------------------------------ pieces
def card(href, img, title, sub, count=None, soon=False, attrs=''):
    c = '<span class="count">%s</span>' % count if count else ''
    return '<a class="card%s" href="%s"%s>%s<div class="pic"><img src="%s" alt="" loading="lazy"></div><h3>%s</h3><p>%s</p></a>' % (
        ' soon' if soon else '', href, attrs, c, img, E(title), sub)


def item_row(root, item_id, label, right):
    if item_id.startswith('minecraft:'):                                  # vanilla item: no icon of ours
        return '<div class="item"><span style="width:32px;flex:none"></span>%s<span>%s</span></div>' % (E(label), E(right))
    icon = item_id.split(':')[-1]
    return '<div class="item"><img src="%simg/items/%s.png" alt="" onerror="this.style.visibility=\'hidden\'">%s<span>%s</span></div>' % (root, icon, E(label), E(right))


def anim_buttons(z):
    labels = dict(BOSS_ANIM_LABELS.get(z['id'], {}))
    content = z['content']
    order = sorted(z['anims'], key=lambda k: (0 if k == 'walk' else 1 if k.startswith('idle') else 2 if k.startswith('attack') else 3, k))
    out = []
    for i, key in enumerate(order):
        if key in labels:
            label = labels[key]
        elif key == 'walk':
            label = 'Walk'
        elif key.startswith('attack') and key[6:].isdigit():
            n = int(key[6:])
            label = content['attacks'][n - 1][0] if content and n <= len(content['attacks']) and key not in labels else 'Attack %d' % n
        elif key.startswith('death'):
            label = 'Death'
        else:
            label = key.replace('_', ' ').capitalize()
        out.append('<button data-anim="%s"%s>%s</button>' % (key, ' class="on"' if i == 0 else '', E(label)))
    return ''.join(out), (order[0] if order else '')


def infobox(z, root, rows):
    buttons, _first = anim_buttons(z)
    boss = z['kind'] == 'boss'
    return '''<aside class="info"><div class="viewer%s" id="viewer"><span class="badge">3D</span><span class="hint">drag to turn &middot; scroll to zoom</span>
<div class="still"><img src="%s%s" alt="%s"></div></div><div class="rows">%s</div></aside>''' % (
        ' boss' if boss else '', root, zimg(z), E(z['name']), ''.join('<div><span>%s</span><b>%s</b></div>' % r for r in rows))


def infection_text(z):
    return 'never infects' if not z['bite'] else '%d%% per hit' % round(z['bite'] * 100)


def viewer_scripts(root, z):
    return ('<script src="%svendor/three.js"></script><script src="%smodels/%s.js"></script><script src="%sjs/viewer.js"></script>'
            '<script>WikiViewer.mount(%s, {cycle: true});</script>' % (root, root, z['id'], root, json.dumps(z['id'])))


# ------------------------------------------------------------------------------------------------ zombie pages
def attack_rows(z):
    rows = []
    melee = [a for a in z['attacks'] if not a['ranged']]
    ranged = [a for a in z['attacks'] if a['ranged']]
    for i, a in enumerate(melee):
        reach = 'Reaches you up to %s blocks away.' % fmt(a['max']) if a['max'] else 'Close range.'
        rows.append(('Close attack' + (' %d' % (i + 1) if len(melee) > 1 else ''), reach, '%s dmg' % '+'.join(map(str, a['damage'])) if a['damage'] else 'special'))
    for i, a in enumerate(ranged):
        span = 'From %s to %s blocks away, when it can see you.' % (fmt(a['min']), fmt(a['max'])) if a['max'] else 'From a distance.'
        rows.append(('Ranged attack' + (' %d' % (i + 1) if len(ranged) > 1 else ''), span, '%s dmg' % '+'.join(map(str, a['damage'])) if a['damage'] else 'special'))
    return rows


def fmt(v):
    return ('%g' % v) if v is not None else '?'


def tags_of(z):
    t = []
    if any(a['ranged'] for a in z['attacks']):
        t.append('ranged')
    if z['bite']:
        t.append('infects')
    if z['boss']:
        t.append('team')
    return t


def zombie_page(z, by_id, all_zombies):
    rel = zurl(z)
    root = '../'
    boss = by_id.get(z['boss']) if z['boss'] else None
    chips = ['<span class="chip %s">%s THREAT</span>' % ('red' if z['threat'] >= 4 else 'yellow' if z['threat'] >= 2 else 'green', THREAT_WORDS[z['threat']].upper())]
    chips.append('<span class="chip red">CAN INFECT</span>' if z['bite'] else '<span class="chip green">NEVER INFECTS</span>')
    if boss:
        chips.append('<a class="chip boss" href="%s%s">TEAM OF %s</a>' % (root, zurl(boss), E(boss['name'].upper())))
    lead = E(z['text']) + (' <span style="color:var(--muted)">%s</span>' % E(z['extra']) if z['extra'] else '')
    attacks = ''.join('<div class="attack"><b>%s</b><p>%s</p><span class="dmg">%s</span></div>' % (E(n), E(d), E(v)) for n, d, v in attack_rows(z))
    abilities = '<p><b style="color:var(--text)">Special:</b> %s. <b style="color:var(--text)">Damage:</b> %s.</p>%s' % (E(z['special']), E(z['damage']), attacks)
    variants = ''.join('<figure data-skin="%d"%s><img src="%s%s" alt="" loading="lazy"><figcaption>Variant %d</figcaption></figure>' % (
        k, ' class="on"' if k == 0 else '', root, zimg(z, k), k + 1) for k in range(len(z['skins'])))
    drops = ''.join(item_row(root, i, W.item_name(i), '%d%% &middot; x%s' % (round(c * 100), n[0] if n[0] == n[1] else '%d-%d' % n)) for i, c, n in z['drops'])
    for i, c in z['extra_drops']:
        if i.startswith('armor:'):
            drops += item_row(root, i[6:] + '_chest', '%s armor piece' % i[6:].title(), '%d%%' % round(c * 100))
        else:
            drops += item_row(root, i, W.item_name(i), '%d%%' % round(c * 100))
    drops = drops.replace('&amp;middot;', '&middot;')
    same = [o for o in all_zombies if o['kind'] == 'zombie' and o['threat'] == z['threat'] and o['id'] != z['id']][:6]
    see = ''.join('<a href="%s%s"><img src="%s%s" alt="" loading="lazy"><b>%s</b></a>' % (root, zurl(o), root, zimg(o), E(o['name'])) for o in same)
    team = ''
    if boss:
        team = '<div class="box"><h3>Boss team</h3><p>%s calls it into its fights.</p><div class="mini"><a href="%s%s"><img src="%s%s" alt=""><b>%s</b></a></div></div>' % (
            E(boss['name']), root, zurl(boss), root, zimg(boss), E(boss['name']))
    rows = [('Threat', skulls(z['threat'])), ('Health', '%d &#10084;' % z['health']), ('Speed', E(z['speed'])), ('Damage', E(z['damage'])),
            ('Infection', infection_text(z)), ('Height', '%g blocks' % round((z['height'] or 1.9) * z['scale'], 1)), ('Variants', str(len(z['skins'])))]
    body = '''<div class="crumbs"><a href="../index.html">Wiki</a> / <a href="index.html">Zombies</a> / <b>%(name)s</b></div>
<div class="entry"><div><div class="title"><h1>%(name)s</h1></div><div class="title" style="margin-top:8px">%(chips)s</div>
<p class="lead">%(lead)s</p>
<div class="box"><h3>Abilities</h3>%(abilities)s</div>
<div class="tip"><b>%(tip_title)s</b>%(tip)s</div>
<div class="box"><h3>Variants</h3><p>Each one you meet wears one of these %(nvar)d outfits. Click one to see it in 3D.</p><div class="variants">%(variants)s</div></div>
%(drops)s%(team)s
<div class="box"><h3>Same threat level</h3><div class="mini">%(see)s</div></div>
</div>%(info)s</div>''' % dict(name=E(z['name']), chips=''.join(chips), lead=lead, abilities=abilities, tip_title=E(z['tip_title'].upper()), tip=E(z['tip']),
                               variants=variants, nvar=len(z['skins']), drops='<div class="box"><h3>Drops</h3>%s</div>' % drops if drops else '', team=team, see=see,
                               info=infobox(z, root, rows))
    write(rel, layout(rel, z['name'], body, 'zombies/index', viewer_scripts(root, z)))


def zombie_list(zs):
    rel = 'zombies/index.html'
    cards = []
    for z in [z for z in zs if z['kind'] == 'zombie']:
        sub = '%s<span>%d &#10084;</span>' % (skulls(z['threat']), z['health'])
        cards.append('<a class="card" href="%s" data-name="%s" data-threat="%d" data-health="%d" data-tags="%s"><div class="pic"><img src="../%s" alt="" loading="lazy"></div><h3>%s</h3><div class="meta">%s</div></a>' % (
            z['id'] + '.html', E(z['name']), z['threat'], z['health'], ' '.join(tags_of(z)), zimg(z), E(z['name']), sub))
    body = '''<div class="crumbs"><a href="../index.html">Wiki</a> / <b>Zombies</b></div>
<div class="pagehead"><div><h1>Zombies</h1><p>%d kinds of infected, each in 3 variants. Threat goes from 1 (a nuisance) to 5 (run). Bosses have <a href="../bosses/index.html">their own page</a>.</p></div></div>
<div class="filters"><input id="ftext" type="search" placeholder="Filter by name..."><span class="lbl">Threat</span>%s<span class="lbl">Show</span>
<button data-tag-btn="ranged">Ranged</button><button data-tag-btn="infects">Can infect</button><button data-tag-btn="team">Boss team</button>
<span class="lbl">Sort</span><select id="fsort"><option value="threat">Threat</option><option value="health">Health</option><option value="name">Name</option></select>
<span style="color:var(--muted);font-size:12px"><b id="fcount" style="color:var(--text)"></b> shown</span></div>
<div class="cards" data-filter-grid>%s</div><p class="empty" id="fempty" style="display:none">No zombie matches these filters.</p>''' % (
        len(cards), ''.join('<button data-threat-btn="%d">%d</button>' % (i, i) for i in range(1, 6)), ''.join(cards))
    write(rel, layout(rel, 'Zombies', body, 'zombies/index'))


# ------------------------------------------------------------------------------------------------ boss pages
def boss_page(z, by_id):
    rel = zurl(z)
    root = '../'
    c = z['content']
    attacks = ''.join('<div class="attack"><b>%s</b><p>%s</p><span class="dmg%s">%s</span></div>' % (E(n), E(d), '' if 'dmg' in v else ' info', E(v)) for n, d, v in c['attacks'])
    phases = ''.join('<div class="phase"><b>%s</b><p>%s</p></div>' % (E(t), E(x)) for t, x in c.get('phases', []))
    team = ''.join('<a href="%s%s"><img src="%s%s" alt="" loading="lazy"><b>%s</b></a>' % (root, zurl(by_id[m]), root, zimg(by_id[m]), E(by_id[m]['name'])) for m in z['team'] if m in by_id)

    def prize(p):
        if p['armor']:
            return item_row(root, p['armor'] + '_chest', '%s armor piece' % p['armor'].title(), 'random piece')
        n = 'x%d' % p['min'] if p['min'] == p['max'] else 'x%d-%d' % (p['min'], p['max'])
        return item_row(root, p['item'], W.item_name(p['item']) + (' (with a mod)' if p['modded'] else ''), n)
    loot = z['loot'] or dict(jackpot=[], bonus=[])
    chips = '<span class="chip boss">BOSS</span>' + ('<span class="chip red">CAN INFECT</span>' if z['bite'] else '<span class="chip green">NEVER INFECTS</span>')
    rows = [('Threat', skulls(5)), ('Health', '%d &#10084;' % z['health']), ('Speed', E(z['speed'])), ('Damage', E(z['damage'])),
            ('Infection', infection_text(z)), ('Height', '%g blocks' % round((z['height'] or 1.9) * z['scale'], 1)), ('Team', '%d zombies' % len(z['team']))]
    body = '''<div class="crumbs"><a href="../index.html">Wiki</a> / <a href="index.html">Bosses</a> / <b>%(name)s</b></div>
<div class="entry"><div><div class="title"><h1>%(name)s</h1>%(chips)s</div>
<p class="lead">%(lead)s</p>
<div class="box"><h3>Boss bar</h3><p>Shown over its head during the fight, in its own theme.</p><div class="bossbar"><img class="pix" src="../img/bossbars/%(id)s.png" alt=""></div></div>
<div class="box"><h3>Attacks</h3>%(attacks)s</div>
%(phases)s
<div class="box"><h3>Armor</h3><p>%(takes)s</p></div>
<div class="box"><h3>Team</h3><p>The zombies it calls into the fight, 2 at a time.</p><div class="mini">%(team)s</div></div>
<div class="box"><h3>Loot</h3><p>Every player who hurt it gets their own loot in their inventory: 20 to 30 scrap, 1 jackpot and 2 different bonus items. 25%% chance that a weapon comes upgraded (a random mod, or Reinforced III).</p>
<div class="loot"><div class="lootcol"><h4>Jackpot (1 of)</h4>%(jackpot)s</div><div class="lootcol"><h4>Bonus (2 of)</h4>%(bonus)s</div></div></div>
<div class="tip"><b>HOW TO BEAT IT</b><ul>%(strategy)s</ul></div>
</div>%(info)s</div>''' % dict(name=E(z['name']), id=z['id'], chips=chips, lead=E(c['lead']), attacks=attacks,
                               phases='<div class="box"><h3>Phases</h3>%s</div>' % phases if phases else '', takes=E(c['takes']), team=team,
                               jackpot=''.join(prize(p) for p in loot['jackpot']), bonus=''.join(prize(p) for p in loot['bonus']),
                               strategy=''.join('<li>%s</li>' % E(s) for s in c['strategy']), info=infobox(z, root, rows))
    write(rel, layout(rel, z['name'], body, 'bosses/index', viewer_scripts(root, z)))


def boss_list(bosses):
    rel = 'bosses/index.html'
    cards = ''.join(card(b['id'] + '.html', '../' + zimg(b), b['name'], '%d &#10084; &middot; team of %d' % (b['health'], len(b['team']))) for b in bosses)
    body = '''<div class="crumbs"><a href="../index.html">Wiki</a> / <b>Bosses</b></div>
<div class="pagehead"><div><h1>Bosses</h1><p>8 giants, each with its own attacks, its own team of zombies, its own boss bar and its own loot. Every player who hurts a boss gets a share of it.</p></div></div>
<div class="cards">%s</div>''' % cards
    write(rel, layout(rel, 'Bosses', body, 'bosses/index'))


# ------------------------------------------------------------------------------------------------ where to find (any item)
RARITY_CHIP = {'Common': 'green', 'Rare': 'yellow', 'OP': 'red'}
KIND_TEXT = {'Melee': 'Melee weapon', 'Ranged': 'Ranged weapon', 'Spray': 'Spray weapon (tank)', 'Thrown': 'Thrown weapon',
             'Gadget': 'Gadget', 'Shield': 'Shield'}


def pct(p):
    return ('%.1f%%' % (p * 100)) if p < 0.0995 else '%d%%' % round(p * 100)


def find_box(find, by_id, root):
    """the 'Where to find it' block of an item page"""
    parts = []
    if find['traders']:
        rows = []
        for t in find['traders']:
            price = ' + '.join('%d %s' % (n, W.item_name(i)) for i, n in t['barter']) if t['barter'] else '%d scrap' % t['price']
            amount = ' (x%d)' % t['amount'] if t['amount'] > 1 else ''
            rows.append('<div class="item"><img src="%simg/items/scrap.png" alt="">%s%s <span style="margin-left:6px;color:var(--muted)">%s &middot; %s</span><span>in stock %d%% of the time</span></div>' % (
                root, E(price), amount, E(', '.join(t['who'])), E(t['category_name']), t['stock']))
        parts.append('<h4 class="findh">Traders</h4>' + ''.join(rows))
    if find['bosses']:
        rows = ''.join('<a href="%s%s"><img src="%s%s" alt="" loading="lazy"><b>%s</b><span style="display:block;color:var(--muted);font-size:11px">%s</span></a>' % (
            root, zurl(by_id[b]), root, zimg(by_id[b]), E(by_id[b]['name']), 'jackpot' if k == 'jackpot' else 'bonus item') for b, k in find['bosses'])
        parts.append('<h4 class="findh">Boss loot</h4><div class="mini">%s</div>' % rows)
    if find['loot']:
        rows = ''.join('<div class="item"><span style="margin:0;color:var(--soft)">%s</span><span>%s</span></div>' % (E(label), pct(p)) for label, p in sorted(find['loot'], key=lambda x: -x[1]))
        parts.append('<h4 class="findh">Containers and finds <small>(chance each time)</small></h4>' + rows)
    if find['zombies']:
        rows = ''.join('<a href="%s%s"><img src="%s%s" alt="" loading="lazy"><b>%s</b><span style="display:block;color:var(--muted);font-size:11px">%s</span></a>' % (
            root, zurl(by_id[z]), root, zimg(by_id[z]), E(by_id[z]['name']), pct(c)) for z, c in find['zombies'] if z in by_id)
        parts.append('<h4 class="findh">Dropped by</h4><div class="mini">%s</div>' % rows)
    if find['craft']:
        parts.append('<h4 class="findh">Craft it</h4><p>Crafting table: %s.</p>' % ', '.join('%d %s' % (n, E(W.item_name(i))) for i, n in find['craft']))
    return '<div class="box"><h3>Where to find it</h3>%s</div>' % ''.join(parts) if parts else ''


# ------------------------------------------------------------------------------------------------ weapons
def wurl(w):
    return 'weapons/%s.html' % w['id']


def weapon_page(w, ws, by_id, mods):
    rel = wurl(w)
    root = '../'
    chips = '<span class="chip grey">%s</span><span class="chip %s">%s</span>' % (E(KIND_TEXT.get(w['kind'], w['kind']).upper()), RARITY_CHIP[w['rarity']], w['rarity'].upper())
    if w['moddable']:
        chips += '<a class="chip boss" href="../mods.html">ACCEPTS MODS</a>'
    modbox = ''
    buttons = ''
    if w['moddable']:
        sig = {s['mod']: s['text'] for s in w['signatures']}
        cards = []
        for m in mods['mods']:
            extra = '<p style="color:var(--yellow);margin:4px 0 0">Signature combo: %s</p>' % E(sig[m['id']]) if m['id'] in sig else ''
            cards.append('<div class="item" style="align-items:flex-start"><img src="%simg/items/%s.png" alt=""><div><b>%s mod</b><p style="margin:2px 0 0">%s</p>%s</div><span>%s + %d scrap</span></div>' % (
                root, m['part'].split(':')[1], E(m['name']), E(m['effect']), extra, E(m['part_name']), m['scrap']))
        modbox = '<div class="box"><h3>Weapon mods</h3><p>The <a href="../mods.html">Fabricator</a> can put one of these on it. Try them on the 3D model.</p>%s</div>' % ''.join(cards)
        buttons = '<button data-mod="" class="on">No mod</button>' + ''.join('<button data-mod="%s">%s</button>' % (m['letter'], E(m['name'])) for m in mods['mods'])
    if w['id'] == 'shuriken':
        sm = mods['shuriken']
        chips += '<a class="chip boss" href="../mods.html">ACCEPTS MODS</a>'
        cards = ''.join('<div class="item" style="align-items:flex-start"><img src="%simg/items/%s.png" alt=""><div><b>%s Shuriken</b><p style="margin:2px 0 0">%s</p></div><span>%s + %d scrap</span></div>' % (
            root, m['part'].split(':')[1], E(m['name']), E(m['effect']), E(m['part_name']), sm['scrap']) for m in sm['mods'])
        modbox = '<div class="box"><h3>Shuriken mods</h3><p>Right click the <a href="../mods.html">Fabricator</a> with shurikens in hand: the mod goes on up to %d shurikens of the stack and works on every hit. The model does not change; the name and the description do, and a shuriken you pick up again keeps its mod.</p>%s</div>' % (sm['batch'], cards)
    same = [o for o in ws if o['kind'] == w['kind'] and o['id'] != w['id']][:8]
    see = ''.join('<a href="%s%s"><img src="%simg/w/%s.png" alt="" loading="lazy"><b>%s</b></a>' % (root, wurl(o), root, o['id'], E(o['name'])) for o in same)
    rows = [('Type', E(w['kind'])), ('Damage', E(w['damage'])), ('Uses', E(w['uses'])), ('Special', E(w['special'])), ('Rarity', w['rarity'])]
    if w['find']['traders']:
        t = min(w['find']['traders'], key=lambda x: x['price'] or 999)
        rows.append(('Price', '%d scrap' % t['price'] if t['price'] else 'barter'))
    info = '''<aside class="info"><div class="viewer" id="viewer"><span class="badge">3D</span><span class="hint">drag to turn &middot; scroll to zoom</span>
<div class="still"><img src="../img/w/%s.png" alt=""></div></div>%s<div class="rows">%s</div></aside>''' % (
        w['id'], '<div class="anims">%s</div>' % buttons if buttons else '', ''.join('<div><span>%s</span><b>%s</b></div>' % r for r in rows))
    body = '''<div class="crumbs"><a href="../index.html">Wiki</a> / <a href="index.html">Weapons</a> / <b>%(name)s</b></div>
<div class="entry"><div><div class="title"><h1>%(name)s</h1></div><div class="title" style="margin-top:8px">%(chips)s</div>
<p class="lead">%(text)s</p>
<div class="tip"><b>%(tip_title)s</b>%(tip)s</div>
%(find)s%(modbox)s
<div class="box"><h3>Other %(kind)s weapons</h3><div class="mini">%(see)s</div></div>
</div>%(info)s</div>''' % dict(name=E(w['name']), chips=chips, text=E(w['text']), tip_title=E(w['tip_title'].upper()), tip=E(w['tip']),
                               find=find_box(w['find'], by_id, root), modbox=modbox, kind=E(w['kind'].lower()), see=see, info=info)
    scripts = ('<script src="../vendor/three.js"></script><script src="../models/w_%s.js"></script><script src="../js/viewer.js"></script>'
               '<script>WikiViewer.mount(%s);</script>' % (w['id'], json.dumps('w_' + w['id'])))
    write(rel, layout(rel, w['name'], body, 'weapons/index', scripts))


def num(s):
    import re
    m = re.match(r'\s*(\d+)', s or '')
    return int(m.group(1)) if m else 0


def weapon_list(ws):
    rel = 'weapons/index.html'
    order = ['Melee', 'Ranged', 'Spray', 'Thrown', 'Gadget', 'Shield']
    cards = []
    for w in ws:
        tags = [w['kind'].lower(), w['rarity'].lower()] + (['mods'] if w['moddable'] else [])
        cards.append('<a class="card" href="%s.html" data-name="%s" data-threat="0" data-damage="%d" data-rarity="%d" data-tags="%s"><div class="pic"><img src="../img/w/%s.png" alt="" loading="lazy"></div><h3>%s</h3><div class="meta"><span>%s &middot; %s</span><span class="chip %s" style="font-size:9px;padding:1px 6px">%s</span></div></a>' % (
            w['id'], E(w['name']), num(w['damage']), {'Common': 1, 'Rare': 2, 'OP': 3}[w['rarity']], ' '.join(tags), w['id'], E(w['name']), E(w['kind']),
            E(w['damage'] + (' dmg' if w['damage'].isdigit() else '')), RARITY_CHIP[w['rarity']], w['rarity'].upper()))
    kinds = ''.join('<button data-tag-btn="%s">%s</button>' % (k.lower(), k) for k in order if any(w['kind'] == k for w in ws))
    body = '''<div class="crumbs"><a href="../index.html">Wiki</a> / <b>Weapons</b></div>
<div class="pagehead"><div><h1>Weapons</h1><p>%d weapons, from the baseball bat to the Vortex Launcher. Every page tells you where to find it: which trader sells it and how often, which containers hide it, which boss drops it.</p></div></div>
<div class="filters"><input id="ftext" type="search" placeholder="Filter by name...">%s<button data-tag-btn="op">OP</button><button data-tag-btn="mods">Accepts mods</button>
<span class="lbl">Sort</span><select id="fsort"><option value="rarity">Rarity</option><option value="damage">Damage</option><option value="name">Name</option></select>
<span style="color:var(--muted);font-size:12px"><b id="fcount" style="color:var(--text)"></b> shown</span></div>
<div class="cards" data-filter-grid>%s</div><p class="empty" id="fempty" style="display:none">No weapon matches these filters.</p>''' % (len(ws), kinds, ''.join(cards))
    write(rel, layout(rel, 'Weapons', body, 'weapons/index'))


def extra_sentences(note, effect):
    """the guidebook sentences that add something to the effect (not 'From ...', not the same numbers again)"""
    import re
    digits = set(re.findall(r'\d+', effect))
    for sentence in [x.strip() for x in note.split('.') if x.strip()]:
        if sentence.startswith('From ') or set(re.findall(r'\d+', sentence)) <= digits:
            continue
        yield sentence + '.'


def build_rows():
    """the build cards of the Fabricator (make_fabricator.BLOCK_RECIPES)"""
    import make_fabricator as MF
    rows = []
    for key, name, count, effect, parts in MF.BLOCK_RECIPES:
        cost = ' + '.join('%d %s' % (n, W.item_name('olivares_zombie:' + it)) for it, n in parts)
        rows.append('<div class="item"><img class="pix" src="img/items/%s.png" alt="" style="width:28px;height:28px"><b>%s x%d</b><span style="margin-left:12px;color:var(--soft)">%s</span><span>%s</span></div>' % (
            key, E(name), count, E(effect), E(cost)))
    return ''.join(rows)


def mods_page(ws, mods, finder, by_id):
    import importlib.util
    spec = importlib.util.spec_from_file_location('wiki_fab', os.path.join(W.WIKI, 'content', 'fabricator.py'))
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    rel = 'mods.html'
    root = ''
    wid = {w['id']: w for w in ws}
    gb = {m['name']: m for m in W.D.WEAPON_MODS}
    mod_cards = []
    for m in mods['mods']:
        f = finder.find(m['part'])
        note = ' '.join(x for x in extra_sentences(gb.get(m['name'], {}).get('text', ''), m['effect']))
        mod_cards.append('<div class="box"><h3><img class="pix" src="img/items/%s.png" alt="" style="width:28px;height:28px">%s mod</h3><p><b style="color:var(--text)">Effect:</b> %s. %s</p><p><b style="color:var(--text)">Cost:</b> 1 %s + %d scrap at the Fabricator.</p>%s</div>' % (
            m['part'].split(':')[1], E(m['name']), E(m['effect']), E(note), E(m['part_name']), m['scrap'], find_box(f, by_id, root).replace('<div class="box"><h3>Where to find it</h3>', '<div><h4 class="findh" style="margin-top:10px">Where to find the %s</h4>' % E(m['part_name']), 1)))
    weapons_grid = ''.join('<a href="%s"><img src="img/w/%s.png" alt="" loading="lazy"><b>%s</b></a>' % (wurl(wid[k]), k, E(wid[k]['name'])) for k in mods['moddable'] if k in wid)
    if 'shuriken' in wid:
        weapons_grid += '<a href="%s"><img src="img/w/shuriken.png" alt="" loading="lazy"><b>Shuriken</b><span style="display:block;color:var(--yellow);font-size:11px;padding:0 6px">%s only</span></a>' % (
            wurl(wid['shuriken']), E(', '.join(m['name'] for m in mods['shuriken']['mods'])))
    mod_by_id = {m['id']: m for m in mods['mods']}
    combos = ''.join('<a href="%s"><img src="img/w/%s_%s.png" alt="" loading="lazy" style="height:110px"><b>%s + %s</b><span style="display:block;color:var(--yellow);font-size:11px;padding:0 6px">%s</span></a>' % (
        wurl(wid[s['weapon']]), s['weapon'], mod_by_id[s['mod']]['letter'], E(wid[s['weapon']]['name']), E(mod_by_id[s['mod']]['name']), E(s['text'])) for s in mods['signatures'] if s['weapon'] in wid)
    steps = ''.join('<div class="phase" style="border-color:var(--yellow)"><b style="color:var(--yellow)">%d. %s</b><p>%s</p></div>' % (i + 1, E(t), E(x)) for i, (t, x) in enumerate(C.HOW_TO))
    levels = ''.join('<div class="item"><b style="font-family:var(--px)">Reinforced %s</b><span style="margin-left:12px;color:var(--soft)">+%d%% durability</span><span>%d duct tape + %d scrap</span></div>' % (
        'I' * (i + 1), round(mods['reinforce_bonus'] * 100 * (i + 1)), t, s) for i, (t, s) in enumerate(mods['reinforce']))
    fab = finder.find('olivares_zombie:fabricator')
    body = '''<div class="crumbs"><a href="index.html">Wiki</a> / <b>Weapon mods &amp; Fabricator</b></div>
<div class="entry"><div><div class="title"><h1>Weapon mods &amp; Fabricator</h1></div><p class="lead">%(intro)s</p>
<div class="box"><h3>How to use the Fabricator</h3>%(steps)s<h3 style="margin-top:14px">What the panel shows</h3>%(examples)s</div>
%(fab)s
<div class="sec"><h2>Signature combos</h2><p style="color:var(--soft)">These weapon + mod pairs get a bonus of their own.</p><div class="mini">%(combos)s</div></div>
<div class="sec"><h2>Weapons that accept a mod</h2><div class="mini">%(grid)s</div></div>
<div class="sec"><h2>Reinforced weapons</h2><div class="box"><p>%(reinforce)s</p>%(levels)s</div></div>
<div class="tip"><b>REPAIRS</b>%(wrench)s</div>
<div class="sec"><h2>The 5 mods</h2>%(mods)s</div>
<div class="sec"><h2>Blocks you can build</h2><p style="color:var(--soft)">Right click the workbench without a melee weapon in hand.</p><div class="box">%(blocks)s</div></div>
</div><aside class="info"><div class="viewer" id="viewer"><span class="badge">3D</span><span class="hint">drag to turn &middot; scroll to zoom</span><div class="still"><img src="img/misc/fabricator.png" alt=""></div></div>
<div class="rows"><div><span>Mods</span><b>%(nmods)d</b></div><div><span>Mod cost</span><b>1 part + 3 scrap</b></div><div><span>Combos</span><b>%(ncombos)d</b></div><div><span>Weapons</span><b>%(nweapons)d</b></div><div><span>Reinforced</span><b>3 levels</b></div></div></aside></div>''' % dict(
        intro=E(C.INTRO), steps=steps, examples=__import__('build2').holo_gallery(__import__('build2').T.FAB_EXAMPLES), fab=find_box(fab, by_id, root).replace('Where to find it', 'Getting a Fabricator'), mods=''.join(mod_cards),
        combos=combos, grid=weapons_grid, blocks=build_rows(), reinforce=E(C.REINFORCE), levels=levels, wrench=E(C.WRENCH),
        nmods=len(mods['mods']), ncombos=len(mods['signatures']), nweapons=len([k for k in mods['moddable'] if k in wid]) + ('shuriken' in wid))
    scripts = '<script src="vendor/three.js"></script><script src="models/fabricator.js"></script><script src="js/viewer.js"></script><script>WikiViewer.mount("fabricator");</script>'
    write(rel, layout(rel, 'Weapon mods & Fabricator', body, 'mods', scripts))


# ------------------------------------------------------------------------------------------------ home + soon pages
def home(zs, by_id, counts):
    bosses = [z for z in zs if z['kind'] == 'boss']
    hero = by_id['zombie_conductor']
    soon = lambda slug: slug not in BUILT  # noqa: E731
    browse = ''.join([
        card('zombies/index.html', zimg(by_id['zombie_mime']), 'Zombies', 'Threat, abilities, counters', counts['zombies']),
        card('bosses/index.html', zimg(by_id['zombie_slender']), 'Bosses', '3D models, teams, loot', counts['bosses']),
        card(url('weapons/index'), 'img/misc/weapons.png', 'Weapons', 'Damage, durability, where to find', counts['weapons'], soon('weapons/index')),
        card(url('armor/index'), zimg(by_id['zombie_firefighter']), 'Armor sets', 'Pieces and set bonuses', counts['armor'], soon('armor/index')),
        card(url('traders'), 'img/npc/trader.png', 'Traders', 'Stock, prices, rarity', None, soon('traders')),
        card(url('allies'), 'img/npc/ally.png', 'Allies', 'Hire, heal, revive', None, soon('allies')),
        card(url('buggy'), 'img/misc/buggy.png', 'Rusty Buggy', '16 modules, 17 paints', None, soon('buggy')),
        card(url('mods'), 'img/misc/fabricator.png', 'Fabricator', 'Mods and signature combos', None, soon('mods')),
    ])
    boss_row = ''.join('<a href="%s"><img src="%s" alt="" loading="lazy"><b>%s</b></a>' % (zurl(b), zimg(b), E(b['name'])) for b in bosses)
    body = '''<section class="hero"><div class="txt"><span class="tag">&#9763; OUTBREAK DATABASE</span>
<h1>Know what's<br><span>coming for you.</span></h1>
<p>Every zombie, boss, weapon and trick of Zombie Extraction, with the real stats taken straight from the add-on. Look up a threat before it looks you up.</p>
<div class="stats"><div class="stat"><b>%(zombies)d</b><span>zombies</span></div><div class="stat"><b>%(variants)d</b><span>variants</span></div><div class="stat"><b>%(bosses)d</b><span>bosses</span></div><div class="stat"><b>%(weapons)d</b><span>weapons</span></div><div class="stat"><b>%(armor)d</b><span>armor sets</span></div></div></div>
<div class="art"><img class="bar pix" src="img/bossbars/%(hero)s.png" alt=""><a class="who" href="%(hero_url)s"><img src="%(hero_img)s" alt="%(hero_name)s"></a></div></section>
<div class="sec"><h2>Browse the outbreak</h2><div class="cards">%(browse)s</div></div>
<div class="sec"><h2>New here? Start with these</h2><div class="guides">
<a class="guide" href="guides/first-night.html"><span class="step">STEP 1</span><b>Your first night</b><p>The guidebook, your first weapon, where to find scrap and how not to get bitten.</p></a>
<a class="guide" href="infection.html"><span class="step">STEP 2</span><b>Infection, explained</b><p>The 4 stages, what each cure really does, and how to read the monitor next to your hand.</p></a>
<a class="guide" href="traders.html"><span class="step">STEP 3</span><b>Scrap economy</b><p>What every trader sells, how their stock is rolled, and what is worth your scrap.</p></a></div></div>
<div class="sec"><h2>The 8 bosses</h2><div class="bossrow">%(boss_row)s</div></div>''' % dict(
        counts, hero=hero['id'], hero_url=zurl(hero), hero_img=zimg(hero), hero_name=E(hero['name']), browse=browse, boss_row=boss_row)
    write('index.html', layout('index.html', 'Home', body, 'index'))


def soon_pages():
    for group, items in SECTIONS:
        for slug, name, icon, _count in items:
            if slug in BUILT:
                continue
            rel = url(slug)
            root = '../' * rel.count('/')
            plan = ''.join('<li>%s</li>' % E(p) for p in PLANNED.get(slug, []))
            body = '''<div class="crumbs"><a href="%sindex.html">Wiki</a> / <b>%s</b></div><div class="soonpage"><div class="pagehead"><div><h1>%s</h1>
<p><span class="chip yellow">COMING SOON</span></p></div></div><div class="box"><h3>What this page will cover</h3><ul>%s</ul></div>
<p style="color:var(--muted)">Meanwhile, the Zombie Guidebook in game already has a page about it.</p></div>''' % (root, E(name), E(name), plan)
            write(rel, layout(rel, name, body, slug))


def search_index(zs, ws=(), extra=()):
    entries = []
    for z in zs:
        entries.append(dict(title=z['name'], url=zurl(z), kind='boss' if z['kind'] == 'boss' else 'zombie', icon='img/eggs/%s.png' % z['id'],
                            keys=' '.join([z['special'], z['damage'], z['id'].replace('_', ' ')] + tags_of(z))))
    for w in ws:
        entries.append(dict(title=w['name'], url=wurl(w), kind='weapon', icon='img/items/%s.png' % w['id'],
                            keys=' '.join([w['kind'], w['special'], w['rarity']])))
    entries += list(extra)
    for group, items in SECTIONS:
        for slug, name, icon, _c in items:
            entries.append(dict(title=name, url=url(slug), kind='section' if slug in BUILT else 'soon', icon=icon, keys=group))
    write('js/search-index.js', 'window.WIKI_INDEX = %s;\n' % json.dumps(entries, separators=(',', ':')))


def main():
    fast = '--fast' in sys.argv
    zs = W.zombies()
    by_id = {z['id']: z for z in zs}
    counts = W.counts()
    if not fast and os.path.isdir(OUT):
        shutil.rmtree(OUT, ignore_errors=True)            # a folder held by OneDrive or a browser stays: files are rewritten anyway
    os.makedirs(OUT, exist_ok=True)
    for sub in ('css', 'js'):
        shutil.copytree(os.path.join(WEB, sub), os.path.join(OUT, sub), dirs_exist_ok=True)
    A.build(OUT, zs, renders=not fast)
    finder = W.Finder(zs)
    ws = W.weapons(finder)
    mods = W.mod_catalog()
    A.build_weapons(OUT, ws, mods, renders=not fast)
    for w in ws:
        weapon_page(w, ws, by_id, mods)
    weapon_list(ws)
    mods_page(ws, mods, finder, by_id)
    import build2
    import wiki_assets2 as A2
    import wiki_data2 as W2
    me = sys.modules[__name__]
    sets = W2.armor_sets_full(finder)
    furn = W2.furniture()
    A2.build(OUT, sets, furn, W2.containers()[0], renders=not fast)
    build2.armor_pages(me, sets, by_id, finder)
    build2.food_page(me, finder, by_id)
    build2.gear_page(me, finder, by_id)
    build2.infection_page(me, zs, by_id)
    build2.traders_page(me)
    build2.allies_page(me)
    build2.buggy_page(me, finder, by_id)
    build2.world_page(me)
    build2.furniture_pages(me, furn)
    build2.achievements_page(me)
    build2.guide_page(me)
    extra = build2.search_entries(sets, furn)
    for z in zs:
        (boss_page(z, by_id) if z['kind'] == 'boss' else zombie_page(z, by_id, zs))
    zombie_list(zs)
    boss_list([z for z in zs if z['kind'] == 'boss'])
    home(zs, by_id, counts)
    soon_pages()
    search_index(zs, ws, extra)
    print('wiki -> %s (%d zombie pages, %d boss pages, %d weapon pages)' % (OUT, sum(z['kind'] == 'zombie' for z in zs), sum(z['kind'] == 'boss' for z in zs), len(ws)))


if __name__ == '__main__':
    main()
