"""Pages added on 08/10/2026: Mechanics & combos (how the systems combine) and Towns & radio (the 5 towns, the guidebook
radio). Called by build.py (B = the build module: layout, write, card...). Texts: content/pages.py."""
import os

import build2
import wiki_data as W

E = __import__('html').escape
T = build2.T
icon = build2.icon


def _icons(ids, size=36):
    return '<span style="display:inline-flex;gap:6px;align-items:center">%s</span>' % ''.join(icon('', i, size=size) for i in ids)


def _combo(name, ids, text, note, color):
    tip = '<div class="tip" style="margin-top:10px"><b>CAREFUL</b>%s</div>' % E(note) if note else ''
    paras = ''.join('<p>%s</p>' % E(x) for x in text.split('\n'))
    return ('<div class="box" style="border-left:3px solid %s"><h3>%s<span>%s</span></h3>%s%s</div>'
            % (color, _icons(ids), E(name), paras, tip))


def mechanics_page(B):
    secs = []
    toc = ''.join('<a class="chip" href="#%s" style="color:%s;border-color:%s">%s</a>' % (a, c, c, E(t)) for a, t, c, _i, _x in T.MECHANICS)
    for anchor, title, color, intro, combos in T.MECHANICS:
        inner = ''.join(_combo(n, ids, x, note, color) for n, ids, x, note in combos)
        if anchor == 'lures':
            rows = ''.join('<div class="item">%s<b style="min-width:0;flex:1">%s</b><span>%s &middot; %s</span></div>' % (
                icon('', i), E(n), E(far), E(long)) for i, n, far, long in T.LURES)
            inner = ('<div class="box"><h3>Every lure</h3><p>How far the zombies hear it, and for how long.</p>%s</div>' % rows
                     + ''.join(_combo(n, ids, x, note, color) for n, ids, x, note in T.LURE_COMBOS)
                     + '<div class="tip" style="margin-top:14px"><b>GOOD TO KNOW</b>%s</div>' % E(T.LURES_NOTE))
        elif anchor == 'traps':
            cards = []
            for i, n, x in T.TRAPS:
                pic = 'img/world/%s.png' % i if os.path.exists(os.path.join(B.OUT, 'img', 'world', i + '.png')) else None
                top = ('<div class="pic"><img src="%s" alt="" loading="lazy"></div>' % pic if pic else
                       '<div class="pic" style="height:72px;align-items:center">%s</div>' % icon('', i, size=56))
                cards.append('<div class="card" style="cursor:default">%s<h3>%s</h3><p>%s</p></div>' % (top, E(n), E(x)))
            inner = '<div class="cards">%s</div>' % ''.join(cards)
        elif anchor == 'tricks':
            inner = '<div class="box">%s</div>' % ''.join(
                '<div class="item" style="align-items:flex-start">%s<div><b>%s</b><p style="margin:2px 0 0">%s</p></div></div>' % (
                    icon('', i), E(n), E(x)) for i, n, x in T.TRICKS)
        secs.append('<div class="sec" id="%s"><h2 style="color:%s">%s</h2><p style="color:var(--soft)">%s</p>%s</div>' % (
            anchor, color, E(title), E(intro), inner))
        if anchor == 'frost':
            secs.append('<div class="sec" id="weapons"><h2 style="color:var(--purple)">Weapon combos</h2><div class="box">'
                        '<p>Seven weapon and mod pairs unlock a special power: the Electric Guitar with the Electric mod shocks '
                        'with every power chord, the Frying Pan with the Fire mod burns on every hit, the Combat Umbrella with '
                        'the Electric mod calls lightning in a thunderstorm...</p><p><a href="mods.html">See the 7 signature '
                        'combos on the Fabricator page &rarr;</a></p></div></div>')
    main = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px">%s</div>%s' % (toc, ''.join(secs))
    build2.page(B, 'mechanics.html', 'Mechanics & combos', 'mechanics', [], E(T.MECHANICS_INTRO), main)


def _town_pictures(B, fast):
    d = os.path.join(B.OUT, 'img', 'towns')
    os.makedirs(d, exist_ok=True)
    for t in W.D.TOWNS:
        key = t['pic'].split('/')[-1]
        path = os.path.join(d, key + '.png')
        if fast and os.path.exists(path):
            continue
        W.M.picture(t['pic'], (420, 300)).save(path)


def _signal(bars, text):
    g = '|' * bars
    return ('<div style="font:600 15px ui-monospace,Consolas,monospace;background:#050807;border:1px solid var(--line);'
            'border-radius:8px;padding:8px 12px;margin:6px 0;color:#9aa5a0"><span style="color:#55605a">[</span><span style="color:var(--green)">%s</span>'
            '<span style="color:#2f3833">%s</span><span style="color:#55605a">]</span> %s</div>' % (g, '|' * (4 - bars), E(text)))


def towns_page(B, fast=False):
    _town_pictures(B, fast)
    radio = ('<div class="box" style="display:grid;grid-template-columns:120px 1fr;gap:18px;align-items:center">'
             '<div style="text-align:center"><img class="pix" src="img/items/guidebook.png" alt="" style="width:96px;height:96px;'
             'image-rendering:pixelated"></div><div><h3 style="margin:0 0 6px">The action bar, as you walk</h3>%s%s%s%s</div></div>') % (
        _signal(1, 'Weak signal 1450m'), _signal(2, 'Ashford 820m'), _signal(4, 'Pinecrest 180m'), _signal(1, 'Weak signal'))
    towns = []
    for t in W.D.TOWNS:
        key = t['pic'].split('/')[-1]
        towns.append('<div class="card" style="cursor:default" id="%s"><div class="pic" style="height:200px"><img src="img/towns/%s.png" alt="" loading="lazy"></div>'
                     '<h3>%s</h3><p style="color:var(--yellow);font-size:12px;margin:0 0 6px">%s %s</p><p>%s</p>'
                     '<img src="img/monitor/town_%s.png" alt="TOWN DISCOVERED: %s" loading="lazy" style="width:100%%;margin-top:10px;image-rendering:pixelated;border-radius:6px"></div>' % (
                         key, key, E(t['name']), E(t['line'][0]), E(t['line'][1]), E(T.TOWN_TEXTS.get(key, t['text'])), key, E(t['name'])))
    main = '''<div class="sec"><h2>The guidebook radio</h2>%s%s</div>
<div class="sec"><h2>The 5 towns</h2><p style="color:var(--soft)">Each town only appears in the biomes that suit it. Below each one: the screen your monitor shows when you discover it.</p><div class="cards">%s</div></div>
<div class="sec"><h2>Life in town</h2>%s</div>''' % (
        radio, build2.steps(T.RADIO_HOW, 'var(--yellow)'), ''.join(towns), build2.steps(T.TOWN_FACTS, 'var(--green)'))
    build2.page(B, 'towns.html', 'Towns & radio', 'towns', [], E(T.TOWNS_INTRO), main)


def search_entries():
    out = [dict(title='Mechanics & combos', url='mechanics.html', kind='section', icon='img/items/gas_column.png',
                keys='combo trick explosion water electricity frost lure trap')]
    for anchor, title, _c, _i, combos in T.MECHANICS:
        for name, ids, text, _n in combos:
            out.append(dict(title=name, url='mechanics.html#%s' % anchor, kind='combo', icon='img/items/%s.png' % ids[0], keys=title + ' ' + text[:80]))
    for name, ids, text, _n in T.LURE_COMBOS:
        out.append(dict(title=name, url='mechanics.html#lures', kind='combo', icon='img/items/%s.png' % ids[0], keys='lure ' + text[:80]))
    for t in W.D.TOWNS:
        key = t['pic'].split('/')[-1]
        out.append(dict(title=t['name'], url='towns.html#%s' % key, kind='town', icon='img/items/guidebook.png',
                        keys='town radio ' + t['line'][1]))
    out.append(dict(title='Guidebook radio', url='towns.html', kind='section', icon='img/items/guidebook.png',
                    keys='radio compass signal weak signal town discovered'))
    return out
