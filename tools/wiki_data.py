"""Everything the wiki shows, read from the add-on (never written): the guidebook data, the BP (entities, loot tables,
TypeScript sources) and the RP (client entities, animations, lang). Hand-written texts live in zombie_wiki/content/."""
import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.dirname(HERE)
ADDON = os.path.dirname(WIKI)
GEN = os.path.join(ADDON, 'zombie_tools', 'zombie_models_generator')
RP = os.path.join(ADDON, 'zombie_RP')
BP = os.path.join(ADDON, 'zombie_BP')
SRC = os.path.join(BP, 'src')
sys.path.insert(0, GEN)

import guidebook_data as D          # noqa: E402  (the guidebook content: names, texts, tips, threat...)
import make_guidebook as M          # noqa: E402  (BP helpers: speed words, prices, loot items)

NS = 'olivares_zombie:'


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CONTENT_BOSSES = load_module(os.path.join(WIKI, 'content', 'bosses.py'), 'wiki_content_bosses').BOSSES


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def jload(path):
    return json.loads(read(path).lstrip('﻿'))


# ------------------------------------------------------------------------------------------------ names (lang)
def lang():
    out = {}
    for line in read(os.path.join(RP, 'texts', 'en_US.lang')).splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            out[k.strip()] = v.split('#')[0].strip()
    return out


LANG = lang()
ITEM_IDS = dict(re.findall(r'(\w+): "([^"]+)"', read(os.path.join(SRC, 'items', 'ItemIds.ts'))))


def item_name(item_id):
    if item_id.startswith('minecraft:'):
        return item_id.split(':')[1].replace('_', ' ').title()
    for prefix in ('item.', 'tile.'):
        if prefix + item_id + '.name' in LANG:
            return LANG[prefix + item_id + '.name']
    return item_id.split(':')[1].replace('_', ' ').title()


def entity_name(entity_id):
    return LANG.get('entity.%s.name' % entity_id, entity_id.split(':')[1].replace('_', ' ').title())


# ------------------------------------------------------------------------------------------------ RP
def client_entity(path):
    return jload(path)['minecraft:client_entity']['description']


def client_entities():
    out = {}
    for f in glob.glob(os.path.join(RP, 'entity', '*', '*.entity.json')):
        d = client_entity(f)
        out[d['identifier']] = dict(file=f, desc=d, folder=os.path.basename(os.path.dirname(f)))
    return out


CLIENT = client_entities()


def geometries():
    out = {}
    for f in glob.glob(os.path.join(RP, 'models', 'entity', '**', '*.geo.json'), recursive=True):
        try:
            for g in jload(f)['minecraft:geometry']:
                out[g['description']['identifier']] = g
        except (ValueError, KeyError):
            pass
    return out


def animations():
    out = {}
    for f in glob.glob(os.path.join(RP, 'animations', '**', '*.json'), recursive=True):
        try:
            for k, v in jload(f).get('animations', {}).items():
                out[k] = v
        except ValueError:
            pass
    return out


# ------------------------------------------------------------------------------------------------ BP
def bp_entity(zid):
    return jload(os.path.join(BP, 'entities', 'zombies', zid + '.json'))['minecraft:entity']


def loot_table(path):
    """[(item id, chance per kill 0..1, (min, max))] of a BP loot table (each pool rolled once)"""
    out = []
    try:
        data = jload(os.path.join(BP, path))
    except (OSError, ValueError):
        return out
    for pool in data.get('pools', []):
        rolls = pool.get('rolls', 1)
        rolls = rolls.get('max', 1) if isinstance(rolls, dict) else rolls
        total = sum(e.get('weight', 1) for e in pool.get('entries', []))
        for e in pool.get('entries', []):
            if e.get('type') != 'item':
                continue
            count = (1, 1)
            for fn in e.get('functions', []):
                if fn.get('function') == 'set_count':
                    c = fn['count']
                    count = (c, c) if isinstance(c, (int, float)) else (c.get('min', 1), c.get('max', 1))
            chance = min(1.0, rolls * e.get('weight', 1) / total)
            out.append((e['name'], chance, count))
    return out


def ts_files():
    return {f: read(f) for f in glob.glob(os.path.join(SRC, '**', '*.ts'), recursive=True)}


TS = ts_files()
LOOT_TS = read(os.path.join(SRC, 'items', 'Loot.ts'))


def zombie_extra_drops():
    """zombie id -> [(item id or 'armor:<set>', chance)] from Loot.ZOMBIE_ARMOR / ZOMBIE_PARTS"""
    out = {}
    for m in re.finditer(r'"olivares_zombie:(zombie_\w+)": \[ArmorSet\.(\w+), ([\d.]+)\]', LOOT_TS):
        out.setdefault(m.group(1), []).append(('armor:' + m.group(2).lower(), float(m.group(3))))
    for m in re.finditer(r'"olivares_zombie:(zombie_\w+)": \[ItemIds\.(\w+), ([\d.]+)\]', LOOT_TS):
        out.setdefault(m.group(1), []).append((ITEM_IDS.get(m.group(2), m.group(2)), float(m.group(3))))
    return out


def boss_loot():
    """boss id -> {'jackpot': [...], 'bonus': [...]} with dict(item, armor, min, max, modded)"""
    block = LOOT_TS[LOOT_TS.index('static readonly BOSSES'):LOOT_TS.index('/** Zombies carrying the parts')]
    out = {}
    for m in re.finditer(r'"olivares_zombie:(zombie_\w+)": \{\s*jackpot: \[(.*?)\],\s*bonus: \[(.*?)\],\s*\}', block, re.S):
        def prizes(text):
            res = []
            for p in re.finditer(r'\{([^{}]*)\}', text):
                body = p.group(1)
                item = re.search(r'item: ItemIds\.(\w+)', body)
                armor = re.search(r'armor: ArmorSet\.(\w+)', body)
                mn = re.search(r'min: (\d+)', body)
                mx = re.search(r'max: (\d+)', body)
                res.append(dict(item=ITEM_IDS.get(item.group(1)) if item else None, armor=armor.group(1).lower() if armor else None,
                                min=int(mn.group(1)) if mn else 1, max=int(mx.group(1)) if mx else 1, modded='modded: true' in body))
            return res
        out[m.group(1)] = dict(jackpot=prizes(m.group(2)), bonus=prizes(m.group(3)))
    return out


def boss_teams():
    src = read(os.path.join(SRC, 'zombies', 'BossTeams.ts'))
    out = {}
    for m in re.finditer(r'"olivares_zombie:(zombie_\w+)": \[([^\]]*)\]', src):
        out[m.group(1)] = re.findall(r'olivares_zombie:(zombie_\w+)', m.group(2))
    return out


def braced(text, start):
    """the text of the {...} or (...) block opening at text[start]"""
    pairs = {'{': '}', '(': ')', '[': ']'}
    opener = text[start]
    closer = pairs[opener]
    depth = 0
    for i in range(start, len(text)):
        if text[i] == opener:
            depth += 1
        elif text[i] == closer:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return text[start:]


def zombie_classes():
    """typeId -> dict(bite, attacks=[dict(min, max, ranged, damage=[...])]) parsed from src/zombies/types/*.ts"""
    raw = {}
    for f, src in TS.items():
        if os.sep + 'types' + os.sep not in f:
            continue
        for m in re.finditer(r'export class (\w+) extends (\w+)', src):
            body = braced(src, src.index('{', m.end()))
            tid = re.search(r'typeId = "olivares_zombie:(\w+)"', body)
            bite = re.search(r'biteChance = ([\d.]+)', body)
            attacks = []
            for a in re.finditer(r'new ZombieAttack\(', body):
                block = braced(body, a.end() - 1)
                mn = re.search(r'minRange: ([\d.]+)', block)
                mx = re.search(r'maxRange: ([\d.]+)', block)
                attacks.append(dict(min=float(mn.group(1)) if mn else 0.0, max=float(mx.group(1)) if mx else None,
                                    ranged=bool(mn) or 'requiresSight: true' in block,
                                    damage=[int(float(d)) for d in re.findall(r'damage: ([\d.]+)', block)]))
            raw[m.group(1)] = dict(parent=m.group(2), tid=tid.group(1) if tid else None,
                                   bite=float(bite.group(1)) if bite else None, attacks=attacks)
    out = {}
    for name, c in raw.items():
        if not c['tid']:
            continue
        bite, attacks, p = c['bite'], c['attacks'], c['parent']
        while (bite is None or not attacks) and p in raw:            # inherited from the parent zombie class
            bite = raw[p]['bite'] if bite is None else bite
            attacks = attacks or raw[p]['attacks']
            p = raw[p]['parent']
        out[c['tid']] = dict(bite=0.1 if bite is None else bite, attacks=attacks)
    return out


# ------------------------------------------------------------------------------------------------ zombies
def zombies():
    """every zombie and boss, in guidebook order, with everything the pages need"""
    classes = zombie_classes()
    teams = boss_teams()
    team_of = {m: b for b, members in teams.items() for m in members}
    extra = zombie_extra_drops()
    loot = boss_loot()
    out = []
    for kind, entries in (('zombie', D.ZOMBIES), ('boss', D.BOSSES)):
        for z in entries:
            zid = z['id']
            e = bp_entity(zid)
            comps = e['components']
            ce = CLIENT[NS + zid]['desc']
            skins = [ce['textures'][k] for k in sorted(ce['textures']) if k.startswith('skin')] or [list(ce['textures'].values())[0]]
            table = comps.get('minecraft:loot', {}).get('table')
            cls = classes.get(zid, dict(bite=0.1, attacks=[]))
            out.append(dict(
                id=zid, kind=kind, name=z['name'], threat=z['threat'], damage=z['damage'], special=z['special'],
                text=z['text'], tip=z['tip'], tip_title=z.get('tip_title', 'Survival tip'), extra=D.SUMMONS.get(zid, ''),
                health=int(comps.get('minecraft:health', {}).get('value', 20)),
                speed=M.speed_word(M.bp_movement(e)),
                height=comps.get('minecraft:collision_box', {}).get('height'),
                scale=comps.get('minecraft:scale', {}).get('value', 1),
                skins=skins, geometry=ce['geometry']['default'],
                anims={k: v for k, v in ce.get('animations', {}).items() if v.startswith('animation.')},
                bite=cls['bite'], attacks=cls['attacks'],
                drops=[] if kind == 'boss' else loot_table(table) if table else [],
                extra_drops=extra.get(zid, []),
                boss=team_of.get(zid), team=teams.get(zid, []),
                loot=loot.get(zid), content=CONTENT_BOSSES.get(zid),
            ))
    return out


def counts():
    zs = [z for z in D.ZOMBIES]
    variants = 0
    for z in zs:
        ce = CLIENT[NS + z['id']]['desc']
        variants += len([k for k in ce['textures'] if k.startswith('skin')]) or 1
    return dict(zombies=len(zs), variants=variants, bosses=len(D.BOSSES), weapons=len(D.WEAPONS),
                armor=len(getattr(D, 'ARMOR', [])), survival=len(D.SURVIVAL))


def armor_sets():
    return re.findall(r'^\s+(\w+) = "(\w+)",', read(os.path.join(SRC, 'items', 'ArmorSets.ts')), re.M)
