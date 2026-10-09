"""Everything the wiki shows, read from the add-on (never written): the guidebook data, the BP (entities, loot tables,
scripts) and the RP (client entities, animations, lang). Hand-written texts live in zombie_wiki/content/.

The add-on read is the newest package of Add-on/READY TO SEND/<name>_<version>/Content (since 09/10/2026), else the
dev packs next to the wiki. Its BP has no TypeScript any more, only the bundled scripts/**/main.js: script_modules()
cuts it back into its modules ('items/Loot', 'npcs/Trader'...) and every reader below accepts both forms."""
import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.dirname(HERE)
ADDON = os.path.dirname(WIKI)


def _folder(env, *names):
    """the ZOMBIE_RP / ZOMBIE_BP / ZOMBIE_TOOLS environment variable, else the first of `names` next to the wiki"""
    if os.environ.get(env):
        return os.environ[env]
    for n in names:
        if os.path.isdir(os.path.join(ADDON, n)):
            return os.path.join(ADDON, n)
    return os.path.join(ADDON, names[0])


def _version(content):
    m = re.search(r'_(\d+(?:\.\d+)*)$', os.path.basename(os.path.dirname(content)))
    return tuple(int(x) for x in m.group(1).split('.')) if m else ()


def _package(kind):
    """Add-on/READY TO SEND/<name>_<version>/Content/<kind>/<pack> of the newest version (kind: resource_packs...)"""
    found = glob.glob(os.path.join(ADDON, 'READY TO SEND', '*', 'Content', kind, '*', 'manifest.json'))
    found.sort(key=lambda m: _version(os.path.dirname(os.path.dirname(os.path.dirname(m)))))
    return os.path.dirname(found[-1]) if found else None


# the packaged add-on (READY TO SEND), else Add-on/{zombie_RP, zombie_BP} or the clones of the repos side by side;
# ZOMBIE_RP / ZOMBIE_BP / ZOMBIE_TOOLS override both
GEN = os.path.join(_folder('ZOMBIE_TOOLS', 'zombie_tools', 'CLAUDE_TOOLS'), 'zombie_models_generator')
RP = os.environ.get('ZOMBIE_RP') or _package('resource_packs') or _folder('ZOMBIE_RP', 'zombie_RP')
BP = os.environ.get('ZOMBIE_BP') or _package('behavior_packs') or _folder('ZOMBIE_BP', 'zombie_BP')
os.environ.setdefault('ZOMBIE_RP', RP)
os.environ.setdefault('ZOMBIE_BP', BP)
SRC = os.path.join(BP, 'src')
sys.path.insert(0, GEN)

import guidebook_data as D          # noqa: E402  (the guidebook content: names, texts, tips, threat...)
import make_guidebook as M          # noqa: E402  (BP helpers: speed words, prices, loot items)

NS = 'olivares_zomblocks:'


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CONTENT_BOSSES = load_module(os.path.join(WIKI, 'content', 'bosses.py'), 'wiki_content_bosses').BOSSES


def locate(rel):
    """the RP file `rel` (e.g. models/entity/olivares/zomblocks/gas_column.geo.json) wherever it is in the category
    sub-folders of its folder (props/, projectiles/, npcs/, weapons/, gear/...)"""
    folder, name = os.path.split(os.path.join(RP, rel))
    for dirpath, dirs, files in os.walk(folder):
        dirs.sort()
        if name in files:
            return os.path.join(dirpath, name)
    return os.path.join(RP, rel)


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def jload(path):
    return json.loads(read(path).lstrip('﻿'))


# ------------------------------------------------------------------------------------------------ scripts
def _unescape(text):
    """the bundle writes \\xA7 / \\u2019 where the sources had the characters themselves"""
    return re.sub(r'\\x([0-9A-Fa-f]{2})|\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1) or m.group(2), 16)), text)


def script_modules():
    """module ('items/Loot', 'zombies/types/Clown'...) -> its source: the TypeScript of zombie_BP/src when the BP has
    it, else the modules of the bundled scripts/**/*.js, cut at the '// <path>/<module>.js' line before each one"""
    out = {}
    if os.path.isdir(SRC):
        for f in glob.glob(os.path.join(SRC, '**', '*.ts'), recursive=True):
            out[os.path.relpath(f, SRC)[:-3].replace(os.sep, '/')] = read(f)
        return out
    prefix = NS.rstrip(':').replace('_', '/') + '/'                      # olivares/zomblocks/
    for f in glob.glob(os.path.join(BP, 'scripts', '**', '*.js'), recursive=True):
        parts = re.split(r'^// (\S+)\.js\n', read(f), flags=re.M)
        for name, body in zip(parts[1::2], parts[2::2]):
            name = name.split('/scripts/')[-1]
            out[name[len(prefix):] if name.startswith(prefix) else name] = _unescape(body)
    return out


def src(module):
    """the source of one script module ('items/Loot'); '' when it does not exist"""
    return TS.get(module, '')


def number(text):
    """a number as the scripts write it: 0.105, 45_000, 45e3, 5 * 60 * 1e3"""
    text = text.replace('_', '').strip()
    if not re.fullmatch(r'[\d.eE+\-*/() ]+', text):
        raise ValueError('not a number: %r' % text)
    return float(eval(text, {'__builtins__': {}}))                   # noqa: S307 (digits and operators only)


def constant(name, module=None):
    """the value of a constant: `static readonly NAME = ...;` (TypeScript), `Class.NAME = ...;` or `var NAME = ...;`
    (bundle). Searched in `module`, else in every module. Returns the raw text after '='."""
    pat = r'(?:static readonly |\b[A-Za-z_]\w*\.|\b(?:const|var|let) )%s(?:: [^=\n]+)? = ([^;\n]+);' % name
    for text in ([src(module)] if module else TS.values()):
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()
    raise KeyError(name)


def constant_number(name, module=None):
    return number(constant(name, module))


CLASS_RE = re.compile(r'(?:var (\w+) = class(?: \w+)?|(?:export )?(?:abstract )?class (\w+)) extends (\w+) \{')


def classes(text):
    """[(class name, parent name, body)] of the classes of a module (TypeScript or bundle)"""
    out = []
    for m in CLASS_RE.finditer(text):
        out.append((m.group(1) or m.group(2), m.group(3), braced(text, m.end() - 1)))
    return out


def statement_block(text, head):
    """the [...] or {...} assigned right after `head` (a regex), e.g. 'BOSSES = ' -> the object literal"""
    m = re.search(head, text)
    if not m:
        return ''
    start = m.end()
    while text[start] not in '[{(':
        start += 1
    return braced(text, start)


# ------------------------------------------------------------------------------------------------ names (lang)
def lang():
    out = {}
    for line in read(os.path.join(RP, 'texts', 'en_US.lang')).splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            out[k.strip()] = v.split('#')[0].strip()
    return out


TS = script_modules()
LANG = lang()
ITEM_IDS = dict(re.findall(r'(\w+): "([^"]+)"', src('items/ItemIds')))


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
    for f in glob.glob(os.path.join(RP, 'entity', '**', '*.entity.json'), recursive=True):
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
    return jload(os.path.join(BP, 'entities', 'olivares', 'zomblocks', 'zombies', zid + '.json'))['minecraft:entity']


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


LOOT_TS = src('items/Loot')


def zombie_extra_drops():
    """zombie id -> [(item id or 'armor:<set>', chance)] from Loot.ZOMBIE_ARMOR / ZOMBIE_PARTS"""
    out = {}
    for m in re.finditer(r'"olivares_zomblocks:(zombie_\w+)": \[ArmorSet\.(\w+), ([\d.]+)\]', LOOT_TS):
        out.setdefault(m.group(1), []).append(('armor:' + m.group(2).lower(), float(m.group(3))))
    for m in re.finditer(r'"olivares_zomblocks:(zombie_\w+)": \[ItemIds\.(\w+), ([\d.]+)\]', LOOT_TS):
        out.setdefault(m.group(1), []).append((ITEM_IDS.get(m.group(2), m.group(2)), float(m.group(3))))
    return out


def boss_loot():
    """boss id -> {'jackpot': [...], 'bonus': [...]} with dict(item, armor, min, max, modded)"""
    block = statement_block(LOOT_TS, r'(?:static readonly |Loot\.)BOSSES(?:: [^=]+)? = ')
    out = {}
    for m in re.finditer(r'"olivares_zomblocks:(zombie_\w+)": \{\s*jackpot: \[(.*?)\],\s*bonus: \[(.*?)\],?\s*\}', block, re.S):
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
    out = {}
    for m in re.finditer(r'"olivares_zomblocks:(zombie_\w+)": \[([^\]]*)\]', src('zombies/BossTeams')):
        out[m.group(1)] = re.findall(r'olivares_zomblocks:(zombie_\w+)', m.group(2))
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


def ts_constants():
    """'Class.NAME' -> 'olivares_zomblocks:...' for the static string constants of every script (indirect type ids):
    `static readonly NAME = "..."` inside a TypeScript class, `Class.NAME = "...";` after a class of the bundle"""
    out = {}
    for text in TS.values():
        for c in re.finditer(r'export (?:abstract )?class (\w+)', text):
            body = braced(text, text.index('{', c.end()))
            for k, v in re.findall(r'static readonly (\w+) = "(olivares_zomblocks:\w+)"', body):
                out['%s.%s' % (c.group(1), k)] = v
        for cls, k, v in re.findall(r'^(\w+)\.(\w+) = "(olivares_zomblocks:\w+)";', text, re.M):
            out['%s.%s' % (cls, k)] = v
    return out


TS_CONSTANTS = ts_constants()


def class_type_id(body):
    """the zombie id a class is for: typeId = "olivares_zomblocks:x" or typeId = Some.CONSTANT"""
    m = re.search(r'typeId = "olivares_zomblocks:(\w+)"', body)
    if m:
        return m.group(1)
    m = re.search(r'typeId = _?(\w+\.\w+);', body)
    return TS_CONSTANTS.get(m.group(1), '').split(':')[-1] or None if m else None


def zombie_classes():
    """typeId -> dict(bite, attacks=[dict(min, max, ranged, damage=[...])]) parsed from the zombies/types/* modules"""
    base = src('zombies/ZombieType')                                     # the defaults every zombie starts from
    m = re.search(r'biteChance = ([\d.]+)', base)
    default_bite = float(m.group(1)) if m else 0.1
    m = re.search(r'biteSeverity = (\d+)', base)
    default_sev = int(m.group(1)) if m else 15
    raw = {}
    for f, text in TS.items():
        if not f.startswith('zombies/types/'):
            continue
        for name, parent, body in classes(text):
            tid = class_type_id(body)
            bite = re.search(r'biteChance = ([\d.]+)', body)
            sev = re.search(r'biteSeverity = (\d+)', body)
            attacks = []
            for a in re.finditer(r'new ZombieAttack\(', body):
                block = braced(body, a.end() - 1)
                mn = re.search(r'minRange: ([\d.]+)', block)
                mx = re.search(r'maxRange: ([\d.]+)', block)
                attacks.append(dict(min=float(mn.group(1)) if mn else 0.0, max=float(mx.group(1)) if mx else None,
                                    ranged=bool(mn) or 'requiresSight: true' in block,
                                    damage=[int(float(d)) for d in re.findall(r'damage: ([\d.]+)', block)]))
            raw[name] = dict(parent=parent, tid=tid, bite=float(bite.group(1)) if bite else None, attacks=attacks,
                             severity=int(sev.group(1)) if sev else None)
    out = {}
    for name, c in raw.items():
        if not c['tid']:
            continue
        bite, attacks, sev, p = c['bite'], c['attacks'], c['severity'], c['parent']
        while (bite is None or not attacks or sev is None) and p in raw:   # inherited from the parent zombie class
            bite = raw[p]['bite'] if bite is None else bite
            sev = raw[p]['severity'] if sev is None else sev
            attacks = attacks or raw[p]['attacks']
            p = raw[p]['parent']
        out[c['tid']] = dict(bite=default_bite if bite is None else bite, attacks=attacks, severity=default_sev if sev is None else sev)
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
            cls = classes.get(zid, dict(bite=0.1, attacks=[], severity=15))
            out.append(dict(
                id=zid, kind=kind, name=z['name'], threat=z['threat'], damage=z['damage'], special=z['special'],
                text=z['text'], tip=z['tip'], tip_title=z.get('tip_title', 'Survival tip'), extra=D.SUMMONS.get(zid, ''),
                health=int(comps.get('minecraft:health', {}).get('value', 20)),
                speed=M.speed_word(M.bp_movement(e)),
                height=comps.get('minecraft:collision_box', {}).get('height'),
                scale=comps.get('minecraft:scale', {}).get('value', 1),
                skins=skins, geometry=ce['geometry']['default'],
                anims={k: v for k, v in ce.get('animations', {}).items() if v.startswith('animation.')},
                bite=cls['bite'], attacks=cls['attacks'], severity=cls['severity'],
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
    """[(enum name, set key)] of ArmorSet: `  Biker = "biker",` (TypeScript) or `ArmorSet2["Biker"] = "biker";` (bundle)"""
    text = src('items/ArmorSets')
    return re.findall(r'^\s+(\w+) = "(\w+)",', text, re.M) or re.findall(r'\w+\["(\w+)"\] = "(\w+)";', text)


# ------------------------------------------------------------------------------------------------ where to find things
def loot_tables_ts():
    """Loot.ts table name -> [(item id, share 0..1, min, max)]"""
    out = {}
    for m in re.finditer(r'(?:static readonly |\bLoot\.)(\w+) = new LootTable\(', LOOT_TS):
        rows = []
        for e in re.finditer(r'\{ item: ItemIds\.(\w+), weight: (\d+)(?:, min: (\d+))?(?:, max: (\d+))? \}', braced(LOOT_TS, m.end() - 1)):
            rows.append((ITEM_IDS.get(e.group(1), e.group(1)), int(e.group(2)), int(e.group(3) or 1), int(e.group(4) or e.group(3) or 1)))
        total = sum(r[1] for r in rows) or 1
        out[m.group(1)] = [(i, w / total, mn, mx) for i, w, mn, mx in rows]
    return out


def drop_calls(text):
    """[(table, chance)] of the Loot.dropFrom(...) lines of a script. The condition `if (Utils.chance(p))` is on the
    same line (TypeScript) or on the line before (bundle); `for (let i = 0; i < n; i++)` before it drops n times."""
    out = []
    lines = text.splitlines()
    for k, line in enumerate(lines):
        if 'Loot.dropFrom(' not in line:
            continue
        before = lines[k - 1] if k else ''
        cond = re.search(r'if \(Utils\.chance\(([\d.]+)\)\)', line) or re.search(r'^\s*if \(Utils\.chance\(([\d.]+)\)\)\s*$', before)
        p = float(cond.group(1)) if cond else 1.0
        loop = re.search(r'^\s*for \(let \w+ = 0; \w+ < (\d+); \w+\+\+\)\s*$', before)
        if loop:
            out += drop_calls(line.strip()) * (int(loop.group(1)) - 1)
        tern = re.search(r'Utils\.chance\(([\d.]+)\) \? Loot\.(\w+) : Loot\.(\w+)', line)
        if tern:
            q = float(tern.group(1))
            out += [(tern.group(2), p * q), (tern.group(3), p * (1 - q))]
            continue
        t = re.search(r'Loot\.dropFrom\([^)]*?Loot\.(\w+)', line)
        if t:
            out.append((t.group(1), p))
    return out


def loot_sources():
    """[(source label, [(table, chance per search/drop)])] - every place the Loot.ts tables come out of"""
    out = []
    for m in re.finditer(r'name: "([^"]+)", loot: \[(.*?)\], sound', src('props/Searchable')):
        out.append(('%s (search)' % m.group(1), [(t, float(c)) for t, c in re.findall(r'\[Loot\.(\w+), ([\d.]+)\]', m.group(2))]))
    out.append(('Supply crate', drop_calls(src('props/SupplyCrate'))))
    distress = src('props/DistressDrop')
    if 'static open(' in distress:
        out.append(('Distress drop crate', drop_calls(distress[distress.index('static open('):])))
    for f in furniture_loot():                                        # 1-2 rolls: one sure, the second half the time
        lo, hi = f['rolls']
        out.append(('Broken %s' % f['name'].lower(), [(f['loot'], 1.0)] * lo + [(f['loot'], 0.5)] * (hi - lo)))
    out.append(("Santa Bloater's gifts", drop_calls(src('zombies/types/Bloaters'))))
    out.append(('Mailman (25% of the time)', [('PACKAGE', 0.25)]))
    out.append(('Lucky Coin bonus on your kills', [(t, c * 0.35) for t, c in drop_calls(src('items/Survival'))]))
    am = src('npcs/AllyMenu')
    finds = re.findall(r'\[Loot\.(\w+), (\d+), \d+\]', am)
    total = sum(int(w) for _, w in finds) or 1
    chance = constant_number('LOOT_CHANCE', 'npcs/AllyMenu')
    out.append(("An ally's bag (per zombie it kills)", [(t, chance * int(w) / total) for t, w in finds]))
    return out


def furniture_loot():
    """the furniture that drops a loot table when it breaks: [dict(id, name, loot, rolls=(min, max))]"""
    out = []
    for m in re.finditer(r'\{ typeId: "(\w+)", name: "([^"]+)",[^\n]*?, loot: Loot\.(\w+)(?:, lootRolls: \[(\d+), (\d+)\])? \}',
                         src('furniture/FurnitureCatalog')):
        out.append(dict(id=m.group(1), name=m.group(2), loot=m.group(3), rolls=(int(m.group(4) or 1), int(m.group(5) or 1))))
    return out


def recipes():
    """result item id -> [(ingredient id, count)]"""
    out = {}
    for f in glob.glob(os.path.join(BP, 'recipes', '**', '*.json'), recursive=True):
        d = jload(f)
        key = next(k for k in d if k.startswith('minecraft:recipe'))
        r = d[key]
        res = r['result']['item'] if isinstance(r['result'], dict) else r['result']
        ings = {}
        for i in r.get('ingredients', []):
            ings[i['item']] = ings.get(i['item'], 0) + i.get('count', 1)
        out[res] = sorted(ings.items(), key=lambda x: -x[1])
    return out


def trade_offers():
    """(item id -> [dict(category, price, amount, rarity, barter)], category id -> name)"""
    text = src('npcs/TradeOffers')
    sets = {}
    for name in ('OP_ITEMS', 'RARE_ITEMS'):
        m = re.search(SET_RE % name, text, re.S)
        sets[name] = {ITEM_IDS.get(x, x) for x in re.findall(r'ItemIds\.(\w+)', m.group(1))} if m else set()
    m = re.search(r'(?:const|var|let) OP_SETS = \[(.*?)\]', text)
    op_sets = re.findall(r'"(\w+)"', m.group(1)) if m else []
    m = re.search(r'(?:const|var|let) RARE_SETS = \[(.*?)\]', text)
    rare_sets = re.findall(r'"(\w+)"', m.group(1)) if m else []

    def rarity(item):
        name = item.split(':')[-1]
        if item in sets['OP_ITEMS'] or any(name.startswith(p) for p in op_sets):
            return 'OP'
        if item in sets['RARE_ITEMS'] or any(name.startswith(p) for p in rare_sets):
            return 'Rare'
        return 'Common'
    out, names = {}, {}
    body = text[re.search(r'(?:static readonly |\.)CATEGORIES(?:: [^=]+)? = ', text).start():]
    for m in re.finditer(r'\{\s*id: "(\w+)",\s*name: "(?:§.)?([^"]+)",', body):
        cat = m.group(1)
        names[cat] = m.group(2)
        start = body.index('offers: [', m.end()) + len('offers: ')
        block = braced(body, start)
        for o in re.finditer(r'Offers\.sell\(ItemIds\.(\w+), "[^"]*", (\d+)(?:, (\d+))?\)', block):
            item = ITEM_IDS.get(o.group(1), o.group(1))
            out.setdefault(item, []).append(dict(category=cat, price=int(o.group(2)), amount=int(o.group(3) or 1), rarity=rarity(item), barter=None))
        for o in re.finditer(r'Offers\.barter\(\s*\[(.*?)\],\s*ItemIds\.(\w+),\s*"[^"]*"(?:,\s*(\d+))?\s*\)', block, re.S):
            item = ITEM_IDS.get(o.group(2), o.group(2))
            cost = [(c.group(1) or ITEM_IDS.get(c.group(2), c.group(2)), int(c.group(3)))
                    for c in re.finditer(r'item: (?:"([^"]+)"|ItemIds\.(\w+)), amount: (\d+)', o.group(1))]
            out.setdefault(item, []).append(dict(category=cat, price=0, amount=int(o.group(3) or 1), rarity=rarity(item), barter=cost))
    return out, names


def traders():
    """[dict(id, name, categories, greetings)] from Trader.TYPES"""
    out = []
    for m in re.finditer(r'\{ id: "(\w+)", name: "([^"]+)", categories: \[([^\]]*)\], greetings: \[(.*?)\] \}', src('npcs/Trader')):
        out.append(dict(id=m.group(1), name=m.group(2), categories=re.findall(r'"(\w+)"', m.group(3)), greetings=re.findall(r'"([^"]+)"', m.group(4))))
    return out


STOCK_CHANCE = {'Common': 85, 'Rare': 45, 'OP': 15}
# `const NAME: ReadonlySet<string> = new Set([...]);` (TypeScript) or `var NAME = /* @__PURE__ */ new Set([...]);` (bundle)
SET_RE = r'(?:const|var|let) %s(?:: [^=]+)? = (?:/\* @__PURE__ \*/ )?new Set\(\[(.*?)\]\);'


class Finder:
    """everything that gives an item: traders (price, stock chance), containers / crates / bags (chance), bosses,
    zombie drops, crafting"""

    def __init__(self, zombie_list):
        self.tables, self.sources = loot_tables_ts(), loot_sources()
        self.offers, self.cat_names = trade_offers()
        self.trader_list, self.recipes, self.boss = traders(), recipes(), boss_loot()
        self.zombies = zombie_list

    def find(self, item_id):
        res = dict(traders=[], loot=[], bosses=[], zombies=[], craft=self.recipes.get(item_id))
        for o in self.offers.get(item_id, []):
            who = [t['name'] for t in self.trader_list if o['category'] in t['categories']]
            res['traders'].append(dict(o, category_name=self.cat_names.get(o['category'], o['category']), who=who, stock=STOCK_CHANCE[o['rarity']]))
        for label, rolls in self.sources:
            p = sum(chance * share for table, chance in rolls for i, share, _a, _b in self.tables.get(table, []) if i == item_id)
            if p > 0:
                res['loot'].append((label, p))
        for bid, loot in self.boss.items():
            for kind in ('jackpot', 'bonus'):
                if any(pr['item'] == item_id for pr in loot[kind]):
                    res['bosses'].append((bid, kind))
        for z in self.zombies:
            for i, c, _n in z['drops']:
                if i == item_id:
                    res['zombies'].append((z['id'], c))
            for i, c in z['extra_drops']:
                if i == item_id:
                    res['zombies'].append((z['id'], c))
        return res

    def rarity(self, item_id, find):
        if find['traders']:
            return find['traders'][0]['rarity']
        return 'OP' if any(k == 'jackpot' for _, k in find['bosses']) else 'Rare'


# ------------------------------------------------------------------------------------------------ weapons
def bp_items():
    out = {}
    for f in glob.glob(os.path.join(BP, 'items', '**', '*.json'), recursive=True):
        try:
            d = jload(f)['minecraft:item']
            out[d['description']['identifier']] = d.get('components', {})
        except (ValueError, KeyError):
            pass
    return out


def mod_catalog():
    text = src('weapons/mods/WeaponModCatalog')
    letters = {1: 'e', 2: 't', 3: 'f', 4: 'i', 5: 's'}               # make_weapon_mods.py MODS (bones mod_<letter>)
    mods = []
    for m in re.finditer(r'\{ id: (\d+), key: "(\w+)", name: "(\w+)", part: "([^"]+)", partLabel: "([^"]+)", scrap: (\d+), color: "[^"]*", effect: "([^"]+)" \}', text):
        mods.append(dict(id=int(m.group(1)), key=m.group(2), name=m.group(3), part=m.group(4), part_name=m.group(5),
                         scrap=int(m.group(6)), effect=m.group(7), letter=letters[int(m.group(1))]))
    moddable = {}
    for m in re.finditer(r'"olivares_zomblocks:(\w+)": \{ index: (\d+), name: "([^"]+)" \}', text):
        moddable[m.group(1)] = int(m.group(2))
    signatures = [dict(weapon=m.group(1), mod=int(m.group(2)), text=m.group(3))
                  for m in re.finditer(r'\{ weapon: "olivares_zomblocks:(\w+)", mod: (\d+), text: "([^"]+)" \}', text)]
    costs = [(int(a), int(b)) for a, b in re.findall(r'\{ tape: (\d+), scrap: (\d+) \}', text)]
    bonus = constant_number('REINFORCE_BONUS', 'weapons/mods/WeaponModCatalog')
    # shuriken mods (Fabricator, shurikens in hand; src/weapons/mods/ShurikenMods.ts): every hit, script only
    fab = src('workshop/FabricatorCatalog')
    ids = [int(x) for x in re.search(r'FAB_SHURIKEN_MODS = \[([\d, ]+)\]', fab).group(1).split(',')]
    effects = dict(re.findall(r'\[ModId\.(\w+)\]: "([^"]+)"', src('weapons/mods/ShurikenMods')))
    shuriken = dict(mods=[dict(m, effect=effects.get(m['name'], m['effect'])) for m in mods if m['id'] in ids],
                    batch=int(re.search(r'FAB_SHURIKEN_BATCH = (\d+)', fab).group(1)),
                    scrap=int(re.search(r'FAB_SHURIKEN_SCRAP = (\d+)', fab).group(1)))
    return dict(mods=mods, moddable=moddable, signatures=signatures, reinforce=costs, reinforce_bonus=bonus, shuriken=shuriken)


def weapons(finder):
    """the guidebook weapons + their numbers (damage, uses), where to find them, mods"""
    items = bp_items()
    mods = mod_catalog()
    out = []
    for w in D.WEAPONS:
        iid = NS + w['id']
        comp = items.get(iid, {})
        dmg = comp.get('minecraft:damage')
        dmg = dmg.get('value') if isinstance(dmg, dict) else dmg
        damage = w.get('damage') or (str(dmg) if dmg is not None else '-')
        durability = comp.get('minecraft:durability', {}).get('max_durability')
        stack = comp.get('minecraft:max_stack_size', 1)
        stack = stack.get('value', 1) if isinstance(stack, dict) else stack
        if w.get('uses'):
            uses = w['uses']
        elif w['kind'] == 'Spray':
            uses = 'tank, 10 s of use'
        elif durability:
            uses = '%d hits' % durability
        elif stack > 1:
            uses = 'stacks of %d' % stack
        else:
            uses = 'unlimited'
        find = finder.find(iid)
        out.append(dict(id=w['id'], item=iid, name=w['name'], kind=w['kind'], special=w['special'], text=w['text'], tip=w['tip'],
                        tip_title=w.get('tip_title', 'Tip'), model=w['model'], damage=damage, uses=uses, durability=durability,
                        find=find, rarity=finder.rarity(iid, find), moddable=w['id'] in mods['moddable'],
                        signatures=[s for s in mods['signatures'] if s['weapon'] == w['id']]))
    return out


# ------------------------------------------------------------------------------------------------ towns and lairs
def lairs():
    """the boss lairs of towns/TownCatalog in catalog order: [dict(id, name, boss, boss_name, tip)] (tip: guidebook)"""
    text = src('towns/TownCatalog')
    heads = list(re.finditer(r'"id": "(\w+)",\s*"structure": "[^"]+",\s*"name": "([^"]+)"', text))
    tips = {e['name']: e['text'] for e in getattr(D, 'BOSS_LAIRS', [])}
    out = []
    for n, h in enumerate(heads):
        block = text[h.end():heads[n + 1].start() if n + 1 < len(heads) else len(text)]
        m = re.search(r'"boss": "olivares_zomblocks:(\w+)",\s*"bossName": "([^"]+)"', block)
        if m:
            out.append(dict(id=h.group(1), name=h.group(2), boss=m.group(1), boss_name=m.group(2), tip=tips.get(h.group(2), '')))
    return out
