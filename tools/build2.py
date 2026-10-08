"""Second half of the wiki pages: armor, food & medical, survival gear, infection, traders, allies, buggy, world,
furniture, achievements and the first night guide. Called by build.py (B = the build module: layout, write, cards...)."""
import importlib.util
import json
import os
import re

import wiki_data as W
import wiki_data2 as W2

E = __import__('html').escape


def content(name):
    spec = importlib.util.spec_from_file_location('wiki_content_' + name, os.path.join(W.WIKI, 'content', name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = content('pages')


def icon(root, item_id, cls='pix', size=32):
    if item_id.startswith('minecraft:'):                                  # vanilla item: no icon of ours
        return '<span style="display:inline-block;width:%dpx;flex:none"></span>' % size
    return '<img class="%s" src="%simg/items/%s.png" alt="" style="width:%dpx;height:%dpx" onerror="this.style.visibility=\'hidden\'">' % (
        cls, root, item_id.split(':')[-1], size, size)


def steps(rows, color='var(--yellow)', fmt=None):
    return ''.join('<div class="phase" style="border-color:%s"><b style="color:%s">%s</b><p>%s</p></div>' % (
        color, color, E(t), E(x.format(**fmt) if fmt else x)) for t, x in rows)


def holo_gallery(examples, root=''):
    return '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin-top:12px">%s</div>' % ''.join(
        '<figure style="margin:0;background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:8px"><img src="%simg/holo/%s.png" alt="" loading="lazy" style="width:100%%;image-rendering:pixelated;border-radius:6px"><figcaption style="color:var(--soft);font-size:12px;margin-top:6px">%s</figcaption></figure>' % (
            root, n, E(c)) for n, c in examples)


def find_line(B, find, root, by_id):
    """a short 'where to find it' line for list pages"""
    parts = []
    if find['traders']:
        t = min(find['traders'], key=lambda x: x['price'] or 999)
        who = ', '.join(sorted({w for x in find['traders'] for w in x['who']}))
        parts.append('<b>%s</b> %s' % (('%d scrap' % t['price']) if t['price'] else 'barter', E(who)))
    if find['bosses']:
        parts.append('boss loot: ' + ', '.join('<a href="%s%s">%s</a>' % (root, B.zurl(by_id[b]), E(by_id[b]['name'])) for b, _k in find['bosses']))
    if find['zombies']:
        parts.append('dropped by ' + ', '.join('<a href="%s%s">%s</a>' % (root, B.zurl(by_id[z]), E(by_id[z]['name'])) for z, _c in find['zombies'] if z in by_id))
    if find['loot']:
        best = sorted(find['loot'], key=lambda x: -x[1])[:2]
        parts.append(', '.join('%s %s' % (E(label.replace(' (search)', '')), B.pct(p)) for label, p in best))
    if find['craft']:
        parts.append('craft: ' + ', '.join('%d %s' % (n, E(W.item_name(i))) for i, n in find['craft']))
    return ' &middot; '.join(parts) or 'rare find'


def stat_rows(rows):
    return '<div class="rows">%s</div>' % ''.join('<div><span>%s</span><b>%s</b></div>' % r for r in rows)


def side_pic(src, rows, extra=''):
    return '<aside class="info"><div class="viewer" style="cursor:default"><div class="still" style="display:flex"><img src="%s" alt=""></div></div>%s%s</aside>' % (
        src, extra, stat_rows(rows))


def page(B, rel, title, active, crumbs, lead, main, aside='', scripts=''):
    root = '../' * rel.count('/')
    crumb = ' / '.join('<a href="%s%s">%s</a>' % (root, u, E(t)) for t, u in crumbs)
    body = '<div class="crumbs"><a href="%sindex.html">Wiki</a> / %s%s<b>%s</b></div>' % (root, crumb, ' / ' if crumb else '', E(title))
    head = '<div class="title"><h1>%s</h1></div><p class="lead">%s</p>' % (E(title), lead)
    body += ('<div class="entry"><div>%s%s</div>%s</div>' % (head, main, aside)) if aside else (head + main)
    B.write(rel, B.layout(rel, title, body, active, scripts))


# ------------------------------------------------------------------------------------------------ armor
def armor_pages(B, sets, by_id, finder):
    cats = W2.trade_categories()
    traders = W.traders()
    loot_src = W.LOOT_TS[W.LOOT_TS.index('static readonly ARMOR'):]
    crate_sets = [s.lower() for s in re.findall(r'ArmorSet\.(\w+)', loot_src[:loot_src.index(');')])]
    crate_chance = next((c for t, c in W.drop_calls(W.read(os.path.join(W.SRC, 'props', 'SupplyCrate.ts'))) if t == 'ARMOR'), 0)
    stock = W2.stock_chances()
    rare_sets = re.findall(r'"(\w+)_"', re.search(r'const RARE_SETS = \[(.*?)\]', W.read(os.path.join(W.SRC, 'npcs', 'TradeOffers.ts'))).group(1))
    root = '../'
    cards = []
    for s in sets:
        rarity = 'OP' if s['op'] else 'Rare' if s['key'] in rare_sets else 'Common'
        s['rarity'] = rarity
        cards.append('<a class="card" href="%s.html" data-name="%s" data-threat="0" data-protection="%d" data-tags="%s"><div class="pic"><img src="../img/armor/%s.png" alt="" loading="lazy"></div><h3>%s</h3><div class="meta"><span>%d pieces &middot; %d armor</span><span class="chip %s" style="font-size:9px;padding:1px 6px">%s</span></div><p style="margin-top:4px">%s</p></a>' % (
            s['key'], E(s['name']), s['protection'], rarity.lower(), s['key'], E(s['name']), len(s['pieces']), s['protection'], B.RARITY_CHIP[rarity], rarity.upper(), E(s['text'])))
        # where to find (whole set)
        parts = []
        cat = next((c for c in cats if any(o['item'] == s['pieces'][0]['item'] for o in c['offers'])), None)
        if cat:
            who = [t['name'] for t in traders if cat['id'] in t['categories']]
            parts.append('<h4 class="findh">Traders</h4><div class="item">%s<b>%s</b><span style="margin-left:8px;color:var(--muted)">%s</span><span>each piece in stock %d%% of the time</span></div>' % (
                icon(root, W.NS + 'scrap'), E(cat['name']), E(', '.join(who)), stock[rarity]))
        bosses = [b for b, loot in finder.boss.items() for p in loot['jackpot'] if p['armor'] == s['key']]
        if bosses:
            parts.append('<h4 class="findh">Boss loot</h4><div class="mini">%s</div>' % ''.join(
                '<a href="%s%s"><img src="%s%s" alt=""><b>%s</b><span style="display:block;color:var(--muted);font-size:11px">jackpot: 1 random piece</span></a>' % (
                    root, B.zurl(by_id[b]), root, B.zimg(by_id[b]), E(by_id[b]['name'])) for b in bosses))
        zs = [(z, c) for z in by_id.values() for i, c in z['extra_drops'] if i == 'armor:' + s['key']]
        if zs:
            parts.append('<h4 class="findh">Dropped by</h4><div class="mini">%s</div>' % ''.join(
                '<a href="%s%s"><img src="%s%s" alt=""><b>%s</b><span style="display:block;color:var(--muted);font-size:11px">%s, 1 random piece</span></a>' % (
                    root, B.zurl(z), root, B.zimg(z), E(z['name']), B.pct(c)) for z, c in zs))
        if s['key'] in crate_sets:
            parts.append('<h4 class="findh">Supply crates</h4><p>%s chance per crate to hold one random piece of a common set (%d sets).</p>' % (B.pct(crate_chance), len(crate_sets)))
        pieces = ''.join('<div class="item">%s<div><b>%s</b><p style="margin:0">%s slot</p></div><span>%d armor &middot; %d uses &middot; %d scrap</span></div>' % (
            icon(root, p['item']), E(p['name']), p['slot'], p['protection'], p['durability'] or 0, p['price']) for p in s['pieces'])
        others = ''.join('<a href="%s.html"><img src="../img/armor/%s.png" alt="" loading="lazy"><b>%s</b></a>' % (o['key'], o['key'], E(o['name'])) for o in sets if o['key'] != s['key'])
        main = '''<div class="title" style="margin-top:8px"><span class="chip %s">%s</span><span class="chip grey">%d PIECES</span></div>
<div class="tip"><b>FULL SET BONUS</b>%s</div>
<div class="box"><h3>Pieces</h3>%s<p style="color:var(--muted);font-size:12px">Armor points like vanilla armor (a diamond chestplate gives 8). Prices at the trader.</p></div>
<div class="box"><h3>Where to find it</h3>%s</div>
<div class="box"><h3>Other sets</h3><div class="mini">%s</div></div>''' % (B.RARITY_CHIP[rarity], rarity.upper(), len(s['pieces']), E(T.ARMOR_BONUS.get(s['key'], s['bonus'])),
                                                                         pieces, ''.join(parts) or '<p>Rare find.</p>', others)
        rows = [('Pieces', str(len(s['pieces']))), ('Armor', '%d points' % s['protection']), ('Uses', '%d per piece' % (s['pieces'][0]['durability'] or 0)),
                ('Full set price', '%d scrap' % sum(p['price'] for p in s['pieces'])), ('Rarity', rarity)]
        aside = '''<aside class="info"><div class="viewer" id="viewer"><span class="badge">3D</span><span class="hint">drag to turn &middot; scroll to zoom</span>
<div class="still"><img src="../img/armor/%s.png" alt=""></div></div><div class="anims"><button data-anim="walk" class="on">Walk</button><button data-anim="idle">Idle</button></div>%s</aside>''' % (s['key'], stat_rows(rows))
        scripts = '<script src="../vendor/three.js"></script><script src="../models/armor_%s.js"></script><script src="../js/viewer.js"></script><script>WikiViewer.mount("armor_%s");</script>' % (s['key'], s['key'])
        page(B, 'armor/%s.html' % s['key'], s['name'] + ' set', 'armor/index', [('Armor sets', 'armor/index.html')], E(s['text']), main, aside, scripts)
    main = '''<div class="filters"><input id="ftext" type="search" placeholder="Filter by name..."><button data-tag-btn="common">Common</button><button data-tag-btn="rare">Rare</button><button data-tag-btn="op">OP</button>
<span class="lbl">Sort</span><select id="fsort"><option value="protection">Armor</option><option value="name">Name</option></select><span style="color:var(--muted);font-size:12px"><b id="fcount" style="color:var(--text)"></b> shown</span></div>
<div class="cards" data-filter-grid>%s</div><p class="empty" id="fempty" style="display:none">No set matches.</p>''' % ''.join(cards)
    page(B, 'armor/index.html', 'Armor sets', 'armor/index', [], E(T.ARMOR_INTRO), main)


# ------------------------------------------------------------------------------------------------ food & medical, gear
def item_cards(B, entries, finder, by_id, root, anchor_prefix):
    out = []
    for e in entries:
        iid = W.NS + e['icon']
        f = finder.find(iid)
        if e['icon'] == 'water_flask':
            f2 = finder.find(W.NS + 'water_flask_empty')
            f = {k: (f[k] or f2[k]) for k in f}
        out.append('<div class="item" id="%s%s" style="align-items:flex-start;padding:10px 12px">%s<div style="min-width:0"><b style="font-family:var(--px);font-size:15px">%s</b> <span class="chip grey" style="font-size:10px;padding:1px 7px">%s: %s</span><p style="margin:4px 0 2px">%s</p><p style="margin:0;color:var(--muted);font-size:12px">%s</p></div></div>' % (
            anchor_prefix, e['icon'], icon(root, iid, size=40), E(e['name']), E(e['line'][0]), E(e['line'][1]), E(e['text']), find_line(B, f, root, by_id)))
    return ''.join(out)


def food_page(B, finder, by_id):
    root = ''
    medical = [s for s in W.D.SURVIVAL if s['id'] in ('bandage', 'medicine', 'first_aid_kit')]
    med = ''.join('<div class="item" id="item-%s" style="align-items:flex-start;padding:10px 12px">%s<div><b style="font-family:var(--px);font-size:15px">%s</b><p style="margin:4px 0 2px">%s</p><p style="margin:0;color:var(--muted);font-size:12px">%s</p></div></div>' % (
        s['id'], icon(root, W.NS + s['id'], size=40), E(s['name']), E(s['text']), find_line(B, finder.find(W.NS + s['id']), root, by_id)) for s in medical)
    main = '''<div class="sec"><h2>Medical</h2><div class="box">%s<p style="color:var(--muted);font-size:12px">What each one does to the infection: see <a href="infection.html">Infection</a>.</p></div></div>
<div class="sec"><h2>Food</h2><div class="box">%s</div></div>
<div class="tip"><b>CHEF SET</b>With the full <a href="armor/chef.html">Chef armor set</a>, every food also heals you.</div>''' % (med, item_cards(B, W.D.FOOD, finder, by_id, root, 'item-'))
    page(B, 'food.html', 'Food & medical', 'food', [], 'Every food does something more than filling you up: speed, warmth, strength, protection from bites... '
         'Each line tells you what it does and where to find it.', main)


def gear_page(B, finder, by_id):
    root = ''
    dep_ids = ['sound_decoy', 'portable_speaker', 'light_projector', 'fan_propeller', 'gas_column', 'oxygen_tank', 'virus_barrel', 'shopping_cart']
    deps = [s for s in W.D.SURVIVAL if s['id'] in dep_ids]
    cans = [s for s in W.D.SURVIVAL if s['id'] in ('fuel_canister', 'nitrogen_canister')]
    dep_cards = ''.join('<div class="card" id="item-%s" style="cursor:default"><div class="pic"><img src="img/world/%s.png" alt="" loading="lazy"></div><h3>%s</h3><p>%s</p><p style="margin-top:6px;color:var(--yellow);font-size:12px">%s</p><p style="margin-top:6px">%s</p></div>' % (
        s['id'], s['id'], E(s['name']), E(s['text']), E(s['tip']), find_line(B, finder.find(W.NS + s['id']), root, by_id)) for s in deps)
    can = ''.join('<div class="item" id="item-%s" style="align-items:flex-start;padding:10px 12px">%s<div><b style="font-family:var(--px);font-size:15px">%s</b><p style="margin:4px 0 2px">%s</p><p style="margin:0;color:var(--muted);font-size:12px">%s</p></div></div>' % (
        s['id'], icon(root, W.NS + s['id'], size=40), E(s['name']), E(s['text']), find_line(B, finder.find(W.NS + s['id']), root, by_id)) for s in cans)
    main = '''<div class="sec"><h2>Survival gear</h2><div class="box">%s</div></div>
<div class="sec"><h2>Deployables</h2><p style="color:var(--soft)">Place them or throw them, then let them do the work.</p><div class="cards">%s</div></div>
<div class="sec"><h2>Canisters</h2><div class="box">%s</div></div>''' % (item_cards(B, W.D.GEAR, finder, by_id, root, 'item-'), dep_cards, can)
    page(B, 'gear.html', 'Survival gear', 'gear', [], 'Tools, gadgets and devices that keep you alive: lights, radios, decoys, traps and the canisters that refill your tank weapons.', main)


# ------------------------------------------------------------------------------------------------ infection
def infection_page(B, zs, by_id):
    root = ''
    inf = W2.infection()
    stages = ''
    colors = ['var(--green)', 'var(--yellow)', 'var(--red)', 'var(--deep)']
    for i, (name, threshold) in enumerate(inf['stages']):
        stages += '<div class="item" style="align-items:center;padding:10px 12px;gap:14px"><img src="img/monitor/stage_%d.png" alt="" style="width:170px;height:auto;image-rendering:auto"><div><b style="font-family:var(--px);font-size:16px;color:%s">%s</b> <span class="chip grey" style="font-size:10px">FROM %d</span><p style="margin:4px 0 0">%s</p></div></div>' % (
            i, colors[i], E(name), threshold, E(T.INFECTION_STAGES.get(name, '')))
    cures = ''.join('<div class="item">%s<div><b>%s</b><p style="margin:0">%s</p></div></div>' % (icon(root, W.NS + k), E(n), E(t)) for k, n, t in T.INFECTION_CURES)
    other = ''.join('<div class="phase"><b>%s</b><p>%s</p></div>' % (E(t), E(x)) for t, x in T.INFECTION_OTHER)
    biters = sorted([z for z in zs if z['bite']], key=lambda z: (-z['bite'], z['name']))
    bite_rows = ''.join('<a href="%s"><img src="%s" alt="" loading="lazy"><b>%s</b><span style="display:block;color:var(--muted);font-size:11px">%d%% per hit &middot; +%d</span></a>' % (
        B.zurl(z), B.zimg(z), E(z['name']), round(z['bite'] * 100), z['severity']) for z in biters)
    import make_infection_monitor as IM
    msgs = ''.join('<figure style="margin:0;text-align:center"><img src="img/monitor/%s.png" alt="" style="width:100%%;max-width:220px"><figcaption style="color:var(--muted);font-size:12px">%s</figcaption></figure>' % (
        m[0], E(m[2].title() + ' - ' + m[3].lower())) for m in IM.MESSAGES)
    turned = ', '.join('<a href="%s">%s</a>' % (B.zurl(by_id[z]), E(by_id[z]['name'])) for z in inf['turned'] if z in by_id)
    main = '''<div class="sec"><h2>The 4 stages</h2><div class="box">%s</div><p style="color:var(--soft)">%s Die while Turning or Turned and you rise as a zombie: %s.</p></div>
<div class="sec"><h2>How to treat it</h2><div class="box">%s</div><div class="box"><h3>Also good to know</h3>%s</div></div>
<div class="sec"><h2>The monitor</h2><div class="box"><p>%s</p><div style="display:flex;gap:10px;flex-wrap:wrap;margin:10px 0"><img src="img/monitor/paused.png" alt="" style="width:220px"></div><p style="color:var(--muted);font-size:12px">After a bandage the monitor says PAUSED. After a treatment:</p><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px">%s</div></div></div>
<div class="sec"><h2>Zombies that infect</h2><p style="color:var(--soft)">Chance per hit, and how much one bite adds.</p><div class="mini">%s</div></div>''' % (
        stages, E(T.INFECTION_GROWTH), turned, cures, other, E(T.MONITOR_TEXT), msgs, bite_rows)
    page(B, 'infection.html', 'Infection', 'infection', [], E(T.INFECTION_INTRO), main)


# ------------------------------------------------------------------------------------------------ traders & allies
def traders_page(B):
    root = ''
    cats = {c['id']: c for c in W2.trade_categories()}
    types = W.traders()
    stock = W2.stock_chances()
    cards = []
    for i, t in enumerate(types):
        names = ' &middot; '.join(E(cats[c]['name']) for c in t['categories'] if c in cats)
        cards.append('<div class="card" style="cursor:default"><div class="pic"><img src="img/npc/trader_%d.png" alt="" loading="lazy"></div><h3>%s</h3><p style="color:var(--text)">%s</p><p style="margin-top:4px;font-style:italic">"%s"</p></div>' % (
            i, E(t['name']), names, E(t['greetings'][0])))
    lists = []
    for cid, c in cats.items():
        who = ', '.join(t['name'] for t in types if cid in t['categories'])
        rows = []
        for o in c['offers']:
            if o.get('ally'):
                price, link = '%d scrap' % o['price'], ' <a href="allies.html">(see Allies)</a>'
            elif o['barter']:
                price, link = ' + '.join('%d %s' % (n, E(W.item_name(i))) for i, n in o['barter']), ''
            else:
                price, link = '%d scrap' % o['price'], ''
            amount = ' x%d' % o['amount'] if o['amount'] > 1 else ''
            rows.append('<div class="item">%s<b>%s%s</b>%s<span class="chip %s" style="font-size:9px;padding:1px 6px;margin-left:8px">%s</span><span>%s</span></div>' % (
                icon(root, o['item']), E(o['label']), amount, link, B.RARITY_CHIP[o['rarity']], o['rarity'].upper(), price))
        lists.append('<div class="box" id="cat-%s"><h3>%s</h3><p style="color:var(--muted);font-size:12px;margin-top:-4px">Sold by: %s</p>%s</div>' % (cid, E(c['name']), E(who), ''.join(rows)))
    how = ''.join('<div class="phase" style="border-color:var(--yellow)"><b style="color:var(--yellow)">%s</b><p>%s</p></div>' % (E(t), E(x.format(**stock))) for t, x in T.TRADERS_HOW)
    main = '''<div class="sec"><h2>How trading works</h2><div class="box">%s</div></div>
<div class="sec"><h2>The 8 traders</h2><div class="cards">%s</div></div>
<div class="sec"><h2>Every offer</h2>%s</div>''' % (how, ''.join(cards), ''.join(lists))
    page(B, 'traders.html', 'Traders', 'traders', [], E(T.TRADERS_INTRO), main)


def allies_page(B):
    root = ''
    a = W2.allies()
    hire = next((o['price'] for c in W2.trade_categories() for o in c['offers'] if o.get('ally')), 20)
    skins = ''.join('<figure><img src="img/npc/survivor_ally_%d.png" alt="" loading="lazy"></figure>' % i for i in range(len(a['skins'])))
    fmt = dict(chance=round(a['loot_chance'] * 100), bag=a['bag'], radius=a['revive_radius'], revive=a['revive'], bleed=a['bleed_out'])
    rem = ''.join('<div class="item">%s<b>%s</b><span>+%d health%s</span></div>' % (icon(root, r['item']), E(r['label']), r['heal'],
                                                                                   ' + %g s regeneration' % r['regen'] if r['regen'] else '') for r in a['remedies'])
    total = sum(w for _t, w, _p in a['finds']) or 1
    names = {'SNACKS': 'Snacks', 'MEDICAL': 'Medical supplies', 'GADGETS': 'Gadgets', 'TIER1_WEAPONS': 'Melee weapons'}
    finds = ''.join('<div class="item"><b>%s</b><span>%d%% of the finds &middot; %d scrap to buy</span></div>' % (names.get(t, t.title()), round(100 * w / total), p) for t, w, p in a['finds'])
    main = '''<div class="sec"><h2>How allies work</h2><div class="box">%s</div></div>
<div class="sec"><h2>Healing an ally</h2><div class="box"><p>Open their menu while you carry one of these: a button heals them with it.</p>%s</div></div>
<div class="sec"><h2>What they find</h2><div class="box">%s</div></div>
<div class="sec"><h2>Their looks</h2><div class="variants" style="grid-template-columns:repeat(6,1fr)">%s</div></div>
<div class="tip"><b>ACHIEVEMENT</b>Revive a downed survivor to unlock No One Left Behind.</div>''' % (steps(T.ALLIES_HOW, fmt=fmt), rem, finds, skins)
    rows = [('Health', '%d &#10084;' % a['health']), ('Damage', str(a['damage'])), ('Bag', '%d things' % a['bag']), ('Hire', '%d scrap' % hire),
            ('Revive', '%g s sneaking' % a['revive']), ('Time to save them', '%d s' % a['bleed_out'])]
    page(B, 'allies.html', 'Allies', 'allies', [], E(T.ALLIES_INTRO), main, side_pic('img/npc/survivor_ally_0.png', rows))


# ------------------------------------------------------------------------------------------------ buggy
def buggy_page(B, finder, by_id):
    root = ''
    cat = W2.buggy_catalog()
    num = W2.buggy_numbers()
    fmt = dict(range=int(num.get('TANK_RANGE', 7500)), hull=int(num.get('MAX_HULL', 100)))
    secs = []
    for c in cat:
        if c['name'] == 'Dye':
            sw = ''.join('<figure style="margin:0;text-align:center"><img src="img/buggy/p_%s.png" alt="" loading="lazy" style="max-width:100%%"><figcaption style="font-size:12px;color:var(--muted)">%s<br>%s</figcaption></figure>' % (
                card['key'], E(card['name']), E(', '.join('%d %s' % (n, W.item_name(i)) for i, n in card['cost'])) or 'free') for card in c['cards'])
            secs.append('<div class="sec"><h2>Paint</h2><p style="color:var(--soft)">Every paint costs one vanilla dye; Bare Rust is free.</p><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px">%s</div></div>' % sw)
            continue
        cards = []
        for card in c['cards']:
            pic = '<div class="pic"><img src="img/buggy/m_%s.png" alt="" loading="lazy"></div>' % card['key'] if card['kind'] == 'module' else ''
            cost = ''.join('<span style="display:inline-flex;align-items:center;gap:4px;margin-right:8px">%s%d %s</span>' % (icon(root, i, size=20), n, E(W.item_name(i))) for i, n in card['cost']) or 'free'
            text = card['text'] or {'repair': 'Repairs the whole hull of a wrecked or damaged buggy.', 'pack': 'Packs the buggy back into its item, with its modules and paint (empty the trunk first).'}.get(card['key'], '')
            cards.append('<div class="card" style="cursor:default">%s<h3>%s</h3><p>%s</p><p style="margin-top:8px;color:var(--text);font-size:12px">%s</p></div>' % (pic, E(card['name']), E(text), cost))
        secs.append('<div class="sec"><h2>%s</h2><div class="cards">%s</div></div>' % (E(c['name']), ''.join(cards)))
    f = finder.find(W.NS + 'rusty_buggy')
    main = '''<div class="sec"><h2>Driving</h2><div class="box">%s</div></div>
<div class="sec"><h2>The garage</h2><div class="box">%s<h3 style="margin-top:14px">What the panel shows</h3>%s</div></div>%s
<div class="box"><h3>Where to find it</h3><p>%s</p></div>''' % (steps(T.BUGGY_HOW, fmt=fmt), steps(T.GARAGE_HOW, 'var(--blue)'), holo_gallery(T.GARAGE_EXAMPLES), ''.join(secs), find_line(B, f, root, by_id))
    price = min((t['price'] for t in f['traders']), default=0)
    rows = [('Seats', '2'), ('Full tank', '~%d blocks' % fmt['range']), ('Hull', str(fmt['hull'])), ('Modules', str(sum(len(c['cards']) for c in cat if c['name'] not in ('Dye', 'Service')))),
            ('Paints', str(sum(len(c['cards']) for c in cat if c['name'] == 'Dye'))), ('Price', '%d scrap' % price if price else '-')]
    page(B, 'buggy.html', 'Rusty Buggy', 'buggy', [], E(T.BUGGY_INTRO), main, side_pic('img/buggy/full.png', rows))


# ------------------------------------------------------------------------------------------------ world
TABLE_NAMES = {'SNACKS': 'Snacks', 'SCRAP': 'Scrap', 'GADGETS': 'Gadgets', 'LID': 'Trash can lid', 'TRINKETS': 'Trinkets', 'TIER1_WEAPONS': 'Melee weapon',
               'MEDICAL': 'Medical supplies', 'TOOLS': 'Tools', 'BUGGY': 'Rusty Buggy', 'ARMOR': 'Armor piece', 'PACKAGE': 'Package'}


def world_page(B):
    root = ''
    conts, tables, restock = W2.containers()
    boxes = []
    for c in conts:
        rows = []
        merged = {}
        for t, ch in c['rolls']:
            merged[t] = 1 - (1 - merged.get(t, 0)) * (1 - ch)
        for t, ch in merged.items():
            items = tables.get(t, [])
            top = ', '.join(E(W.item_name(i)) for i, _s, _a, _b in sorted(items, key=lambda x: -x[1])[:6]) if t != 'ARMOR' else 'a random piece of a common armor set'
            more = ' and %d more' % (len(items) - 6) if len(items) > 6 and t != 'ARMOR' else ''
            rows.append('<div class="item" style="align-items:flex-start"><b style="min-width:120px">%s</b><p style="margin:0">%s%s</p><span>%s</span></div>' % (
                E(TABLE_NAMES.get(t, t.title())), top, more, B.pct(ch)))
        verb = 'Smash it' if c['smash'] else 'Search it'
        boxes.append('<div class="box" id="%s"><h3><img src="img/world/%s.png" alt="" style="height:56px;width:auto">%s</h3><p>%s: each line is the chance to get something of that kind.</p>%s</div>' % (
            c['id'], c['id'], E(c['name']), verb, ''.join(rows)))
    block_cards = ''.join('<div class="card" style="cursor:default" id="%s"><div class="pic"><img src="img/world/%s.png" alt="" loading="lazy"></div><h3>%s</h3><p>%s</p><p style="margin-top:6px;color:var(--yellow);font-size:12px">%s: %s</p></div>' % (
        s['icon'], s['icon'], E(s['name']), E(T.BLOCK_TEXTS.get(s['icon'], s['text'])), E(s['line'][0]), E(s['line'][1])) for s in W.D.BLOCKS)
    hazards = ''.join('<div class="phase" style="border-color:var(--red)"><b style="color:var(--red)">%s</b><p>%s</p></div>' % (E(t), E(x)) for t, x in T.HAZARDS)
    main = '''<div class="sec"><h2>Containers</h2><p style="color:var(--soft)">%s</p>%s</div>
<div class="sec"><h2>Supply drops</h2><div class="box"><p>%s</p></div></div>
<div class="sec"><h2>Special blocks</h2><div class="cards">%s</div></div>
<div class="sec"><h2>Hazards</h2><div class="box">%s</div></div>
<div class="sec"><h2>Noise</h2><div class="box"><p>%s</p></div></div>''' % (E(T.CONTAINERS_TEXT.format(restock=restock)), ''.join(boxes), E(T.SUPPLY_DROP), block_cards, hazards, E(T.NOISE_TEXT))
    page(B, 'world.html', 'Loot & world', 'world', [], E(T.WORLD_INTRO), main)


# ------------------------------------------------------------------------------------------------ furniture
def furniture_pages(B, items):
    cards = []
    loot_names = {'SNACKS': 'snacks'}
    for f in items:
        tags = 'carry' if f['carry'] else 'heavy'
        cards.append('<a class="card" href="furniture/%s.html" data-name="%s" data-threat="0" data-hits="%d" data-tags="%s"><div class="pic"><img src="img/furniture/%s_0.png" alt="" loading="lazy"></div><h3>%s</h3><div class="meta"><span>%d hits</span><span>%s</span></div></a>' % (
            f['id'], E(f['name']), f['hits'], tags, f['id'], E(f['name']), f['hits'], 'carry it' if f['carry'] else 'too heavy'))
        rel = 'furniture/%s.html' % f['id']
        variants = ''.join('<figure data-skin="%d"%s><img src="../img/furniture/%s_%d.png" alt="" loading="lazy"><figcaption>Colour %d</figcaption></figure>' % (
            k, ' class="on"' if k == 0 else '', f['id'], k, k + 1) for k in range(len(f['skins'])))
        rows = [('Hits to break', str(f['hits'])), ('Material', f['material'].lower()), ('Carry', 'yes' if f['carry'] else 'no, too heavy'),
                ('Weight', str(f['weight'])), ('Thrown', '%d damage' % (3 + 2 * f['weight']) if f['carry'] else '-'), ('Drops', loot_names.get(f['loot'], 'nothing') if f['loot'] else 'nothing')]
        aside = '''<aside class="info"><div class="viewer" id="viewer"><span class="badge">3D</span><span class="hint">drag to turn &middot; scroll to zoom</span>
<div class="still"><img src="../img/furniture/%s_0.png" alt=""></div></div>%s</aside>''' % (f['id'], stat_rows(rows))
        lead = '%s %s' % ('Light enough to carry and throw.' if f['carry'] else 'Too heavy to carry: a solid block for your barricades.',
                          'Breaks after %d hits.' % f['hits'])
        main = '<div class="box"><h3>Colours</h3><p>It comes in %d colours. Click one to see it in 3D.</p><div class="variants" style="grid-template-columns:repeat(4,1fr)">%s</div></div>' % (len(f['skins']), variants)
        scripts = '<script src="../vendor/three.js"></script><script src="../models/f_%s.js"></script><script src="../js/viewer.js"></script><script>WikiViewer.mount("f_%s");</script>' % (f['id'], f['id'])
        page(B, rel, f['name'], 'furniture', [('Furniture', 'furniture.html')], E(lead), main, aside, scripts)
    main = '''<div class="box">%s</div>
<div class="filters"><input id="ftext" type="search" placeholder="Filter by name..."><button data-tag-btn="carry">Can carry</button><button data-tag-btn="heavy">Too heavy</button>
<span class="lbl">Sort</span><select id="fsort"><option value="hits">Hits</option><option value="name">Name</option></select><span style="color:var(--muted);font-size:12px"><b id="fcount" style="color:var(--text)"></b> shown</span></div>
<div class="cards" data-filter-grid>%s</div><p class="empty" id="fempty" style="display:none">Nothing matches.</p>''' % (steps(T.FURNITURE_HOW, 'var(--blue)'), ''.join(cards))
    page(B, 'furniture.html', 'Furniture', 'furniture', [], E(T.FURNITURE_INTRO), main)


# ------------------------------------------------------------------------------------------------ achievements, guide
def achievements_page(B):
    root = ''
    rows = ''.join('<div class="card" style="cursor:default"><div class="pic" style="height:72px;align-items:center"><img class="pix" src="img/items/%s.png" alt="" style="width:56px;height:56px;image-rendering:pixelated"></div><h3>%s</h3><p>%s</p>%s</div>' % (
        a['icon'], E(a['name']), E(a['text']), '<p style="margin-top:6px;color:var(--yellow);font-size:12px">Goal: %d</p>' % a['goal'] if a['goal'] > 1 else '') for a in W2.achievements())
    page(B, 'achievements.html', 'Achievements', 'achievements', [], E(T.ACHIEVEMENTS_INTRO), '<div class="cards">%s</div>' % rows)


def guide_page(B):
    links = {'Read the guidebook': '../towns.html', 'Grab a weapon': '../weapons/index.html', 'Search everything': '../world.html',
             'Collect scrap': '../traders.html', 'Do not get bitten': '../infection.html', 'Find a friend': '../allies.html',
             'Barricade': '../furniture.html', 'Know your enemy': '../zombies/index.html'}
    pics = {'Read the guidebook': '../img/items/guidebook.png', 'Grab a weapon': '../img/w/baseball_bat.png', 'Search everything': '../img/world/toolbox.png',
            'Collect scrap': '../img/npc/trader_0.png', 'Do not get bitten': '../img/monitor/stage_1.png', 'Find a friend': '../img/npc/survivor_ally_0.png',
            'Barricade': '../img/furniture/cupboard_0.png', 'Know your enemy': '../img/z/zombie_onehand_0.png'}
    out = []
    for i, (t, x) in enumerate(T.FIRST_NIGHT):
        more = ' <a href="%s">Read more &rarr;</a>' % links[t] if links.get(t) else ''
        out.append('<div class="box" style="display:grid;grid-template-columns:110px 1fr;gap:16px;align-items:center"><div style="text-align:center"><img src="%s" alt="" style="%s"></div><div><span class="step" style="font:700 11px Inter,sans-serif;color:var(--green);letter-spacing:.12em">STEP %d</span><h3 style="margin:4px 0">%s</h3><p>%s%s</p></div></div>' % (
            pics[t], 'width:80px;height:80px;image-rendering:pixelated' if pics[t].endswith('guidebook.png') else 'max-height:100px;max-width:110px',
            i + 1, E(t), E(x), more))
    page(B, 'guides/first-night.html', 'Your first night', 'guides/first-night', [], 'New to Zomblocks? Eight steps to survive your first night.', ''.join(out))


# ------------------------------------------------------------------------------------------------ search entries
def search_entries(sets, furniture):
    out = [dict(title=s['name'] + ' set', url='armor/%s.html' % s['key'], kind='armor', icon='img/items/%s_%s.png' % (s['key'], s['pieces'][0]['piece']),
                keys=' '.join([s['bonus']] + [p['name'] for p in s['pieces']])) for s in sets]
    out += [dict(title=f['name'], url='furniture/%s.html' % f['id'], kind='furniture', icon='img/eggs/%s.png' % f['id'], keys='furniture') for f in furniture]
    out += [dict(title=e['name'], url='food.html#item-%s' % e['icon'], kind='food', icon='img/items/%s.png' % e['icon'], keys=' '.join(e['line'])) for e in W.D.FOOD]
    out += [dict(title=s['name'], url='food.html#item-%s' % s['id'], kind='medical', icon='img/items/%s.png' % s['id'], keys='heal cure') for s in W.D.SURVIVAL if s['id'] in ('bandage', 'medicine', 'first_aid_kit')]
    out += [dict(title=e['name'], url='gear.html#item-%s' % e['icon'], kind='gear', icon='img/items/%s.png' % e['icon'], keys=' '.join(e['line'])) for e in W.D.GEAR]
    out += [dict(title=s['name'], url='gear.html#item-%s' % s['id'], kind='gear', icon='img/items/%s.png' % s['id'], keys='deployable')
            for s in W.D.SURVIVAL if s['id'] in ('sound_decoy', 'portable_speaker', 'light_projector', 'fan_propeller', 'gas_column', 'oxygen_tank', 'virus_barrel', 'shopping_cart', 'fuel_canister', 'nitrogen_canister')]
    out += [dict(title=t['name'], url='traders.html', kind='trader', icon='img/items/scrap.png', keys='trader ' + ' '.join(t['categories'])) for t in W.traders()]
    out += [dict(title=a['name'], url='achievements.html', kind='achievement', icon='img/items/%s.png' % a['icon'], keys=a['text']) for a in W2.achievements()]
    return out
