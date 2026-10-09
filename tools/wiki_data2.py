"""More wiki data read from the add-on (never written): armor, traders, allies, buggy, containers, furniture,
achievements, infection. Same rules as wiki_data.py."""
import os
import re

from wiki_data import (BP, CLIENT, D, ITEM_IDS, NS, RP, SET_RE, TS, braced, bp_items, classes, constant_number, drop_calls, jload,
                       loot_tables_ts, src, statement_block, trade_offers)

# ------------------------------------------------------------------------------------------------ armor
ARMOR_SLOTS = {'helmet': 'Head', 'chest': 'Chest', 'legs': 'Legs', 'boots': 'Feet'}
PRICE_FACTOR = {'helmet': 1, 'chest': 1.6, 'legs': 1.3, 'boots': 1}
OP_SETS = ('exo', 'astronaut')


def js_round(x):
    return int(x + 0.5)


def armor_specs():
    out = []
    pat = r'\[ArmorSet\.(\w+)\]: \{ name: "([^"]+)", pieces: \[([^\]]*)\], bonus: "([^"]+)", price: (\d+), names: \{([^}]*)\} \}'
    for m in re.finditer(pat, src('items/ArmorSets')):
        names = dict(re.findall(r'(\w+): "([^"]+)"', m.group(6)))
        out.append(dict(key=m.group(1).lower(), name=m.group(2), pieces=re.findall(r'"(\w+)"', m.group(3)), bonus=m.group(4),
                        price=int(m.group(5)), names=names))
    return out


def armor_sets_full(finder):
    items = bp_items()
    gb = {a['armor']: a for a in D.ARMOR}
    out = []
    for s in armor_specs():
        pieces = []
        for p in s['pieces']:
            iid = '%s%s_%s' % (NS, s['key'], p)
            comp = items.get(iid, {})
            att = jload(os.path.join(RP, 'attachables', 'olivares', 'zomblocks', 'armor', '%s_%s.player.json' % (s['key'], p)))
            att = att['minecraft:attachable']['description']
            pieces.append(dict(piece=p, item=iid, name=s['names'].get(p, p), slot=ARMOR_SLOTS[p],
                               protection=comp.get('minecraft:wearable', {}).get('protection', 0),
                               durability=comp.get('minecraft:durability', {}).get('max_durability'),
                               price=js_round(s['price'] * PRICE_FACTOR[p]), geometry=att['geometry']['default'],
                               texture=att['textures']['default'], find=finder.find(iid)))
        out.append(dict(s, pieces=pieces, text=gb.get(s['key'], {}).get('text', s['bonus']),
                        protection=sum(p['protection'] for p in pieces), op=s['key'] in OP_SETS))
    return out


# ------------------------------------------------------------------------------------------------ traders
def trade_rarity():
    """the rarity rule of TradeOffers.ts (rarityOf): OP / rare item lists and armor set prefixes"""
    text = src('npcs/TradeOffers')

    def items(name):
        m = re.search(SET_RE % name, text, re.S)
        return {ITEM_IDS.get(x, x) for x in re.findall(r'ItemIds\.(\w+)', m.group(1))} if m else set()

    def prefixes(name):
        m = re.search(r'(?:const|var|let) %s = \[(.*?)\]' % name, text)
        return re.findall(r'"(\w+)"', m.group(1)) if m else []
    op_items, rare_items, op_sets, rare_sets = items('OP_ITEMS'), items('RARE_ITEMS'), prefixes('OP_SETS'), prefixes('RARE_SETS')

    def rarity(item):
        name = item.split(':')[-1]
        if item in op_items or any(name.startswith(p) for p in op_sets):
            return 'OP'
        if item in rare_items or any(name.startswith(p) for p in rare_sets):
            return 'Rare'
        return 'Common'
    return rarity


def trade_categories():
    """[dict(id, name, offers=[dict(item, label, price, amount, rarity, barter)])] in the trader menu order"""
    rarity = trade_rarity()
    text = src('npcs/TradeOffers')
    body = text[re.search(r'(?:static readonly |\.)CATEGORIES(?:: [^=]+)? = ', text).start():]
    specs = {s['key']: s for s in armor_specs()}
    heads = list(re.finditer(r'\{\s*id: "(\w+)",\s*name: "(?:§.)?([^"]+)",', body))
    out = []
    for n, m in enumerate(heads):
        block = body[m.end():heads[n + 1].start() if n + 1 < len(heads) else len(body)]
        rows = []
        for o in re.finditer(r'Offers\.sell\(ItemIds\.(\w+), "([^"]*)", (\d+)(?:, (\d+))?\)', block):
            item = ITEM_IDS.get(o.group(1), o.group(1))
            rows.append(dict(item=item, label=o.group(2), price=int(o.group(3)), amount=int(o.group(4) or 1), barter=None,
                             rarity=rarity(item)))
        for o in re.finditer(r'Offers\.armor\(\[([^\]]*)\]\)', block):
            for key in re.findall(r'ArmorSet\.(\w+)', o.group(1)):
                s = specs[key.lower()]
                for p in s['pieces']:
                    item = '%s%s_%s' % (NS, s['key'], p)
                    rows.append(dict(item=item, label=s['names'].get(p, p), price=js_round(s['price'] * PRICE_FACTOR[p]), amount=1,
                                     barter=None, rarity=rarity(item)))
        for o in re.finditer(r'Offers\.barter\(\s*\[(.*?)\],\s*ItemIds\.(\w+),\s*"([^"]*)"(?:,\s*(\d+))?', block, re.S):
            cost = [(c.group(1) or ITEM_IDS.get(c.group(2), c.group(2)), int(c.group(3)))
                    for c in re.finditer(r'item: (?:"([^"]+)"|ItemIds\.(\w+)), amount: (\d+)', o.group(1))]
            item = ITEM_IDS.get(o.group(2), o.group(2))
            rows.append(dict(item=item, label=o.group(3), price=0, amount=int(o.group(4) or 1), barter=cost, rarity=rarity(item)))
        if m.group(1) == 'hire':
            p = re.search(r'Offers\.scrap\((\d+)\)', block)
            rows.append(dict(item=NS + 'walkie_talkie', label='Survivor Ally', price=int(p.group(1)) if p else 20, amount=1,
                             barter=None, rarity='Common', ally=True))
        out.append(dict(id=m.group(1), name=m.group(2), offers=rows))
    return out


def stock_chances():
    m = re.search(r'Rarity\.Common\]: ([\d.]+), \[Rarity\.Rare\]: ([\d.]+), \[Rarity\.Op\]: ([\d.]+)', src('npcs/Trader'))
    return dict(Common=round(float(m.group(1)) * 100), Rare=round(float(m.group(2)) * 100), OP=round(float(m.group(3)) * 100))


def skins_of(entity):
    d = CLIENT[NS + entity]['desc']['textures']
    return [d['skin_%d' % i] for i in range(len([k for k in d if k.startswith('skin_')]))]


# ------------------------------------------------------------------------------------------------ allies
def allies():
    am = src('npcs/AllyMenu')
    ent = jload(os.path.join(BP, 'entities', 'olivares', 'zomblocks', 'npcs', 'survivor_ally.json'))['minecraft:entity']['components']
    remedies = [dict(item=ITEM_IDS.get(m.group(1)), label=m.group(2), heal=int(m.group(3)), regen=int(m.group(4)) / 20)
                for m in re.finditer(r'\{ item: ItemIds\.(\w+), label: "([^"]+)", heal: (\d+), regenTicks: (\d+) \}', am)]
    finds = [(t, int(w), int(p)) for t, w, p in re.findall(r'\[Loot\.(\w+), (\d+), (\d+)\]', am)]
    return dict(health=ent.get('minecraft:health', {}).get('value', 30), damage=ent.get('minecraft:attack', {}).get('damage'),
                bag=int(constant_number('BAG_SIZE', 'npcs/AllyMenu')), loot_chance=constant_number('LOOT_CHANCE', 'npcs/AllyMenu'),
                bleed_out=int(constant_number('BLEED_OUT_MS')) // 1000,          # npcs/SurvivorAlly, now npcs/Downed
                revive=constant_number('REVIVE_TICKS') / 20,
                revive_radius=int(constant_number('REVIVE_RADIUS')),
                remedies=remedies, finds=finds, skins=skins_of('survivor_ally'))


# ------------------------------------------------------------------------------------------------ buggy
def buggy_catalog():
    import make_buggy_garage as G
    text = src('vehicles/BuggyCatalog')
    out = []
    for cat in re.finditer(r'name: "(\w+)",\s*cards: (?=\[)', text):
        cards = []
        for c in re.finditer(r'\{ card: \d+, kind: "(\w+)", key: "(\w+)", name: "([^"]+)", id: \d+, cost: \[(.*?)\] \}', braced(text, cat.end())):
            cost = [(i, int(n)) for i, n in re.findall(r'item: "([^"]+)", amount: (\d+)', c.group(4))]
            cards.append(dict(kind=c.group(1), key=c.group(2), name=c.group(3), cost=cost, text=G.MODULE_TEXT.get(c.group(2), ('', None))[0]))
        out.append(dict(name=cat.group(1), cards=cards))
    return out


def buggy_numbers():
    return {k: float(v) for k, v in re.findall(r'(?:static readonly |\bBuggy\.)([A-Z_]+) = ([\d.]+);', src('vehicles/Buggy'))}


# ------------------------------------------------------------------------------------------------ world
def containers():
    text = src('props/Searchable')
    out = []
    for m in re.finditer(r'(\w+): \{ name: "([^"]+)", loot: \[(.*?)\], sound: [\w.]+(, smash: true)? \}', text):
        rolls = [(t, float(c)) for t, c in re.findall(r'\[Loot\.(\w+), ([\d.]+)\]', m.group(3))]
        out.append(dict(id=m.group(1), name=m.group(2), rolls=rolls, smash=bool(m.group(4))))
    out.append(dict(id='supply_crate', name='Supply Crate', rolls=drop_calls(src('props/SupplyCrate')), smash=False))
    restock = int(constant_number('RESTOCK_MS', 'props/Searchable') / 60000)
    return out, loot_tables_ts(), restock


def furniture():
    pat = (r'\{ typeId: "(\w+)", name: "([^"]+)", hits: (\d+), material: FurnitureMaterial\.(\w+), carryable: (\w+), '
           r'weight: (\d+), colors: \[.*?\](?:, loot: Loot\.(\w+))?(?:, lootRolls: \[(\d+), (\d+)\])? \}')
    out = []
    for m in re.finditer(pat, src('furniture/FurnitureCatalog')):
        ce = next((c for k, c in CLIENT.items() if k.split(':')[-1] == m.group(1)), None)
        d = ce['desc'] if ce else None
        skins = [d['textures'][k] for k in sorted(d['textures']) if k.startswith('skin')] if d else []
        out.append(dict(id=m.group(1), name=m.group(2), hits=int(m.group(3)), material=m.group(4), carry=m.group(5) == 'true',
                        weight=int(m.group(6)), loot=m.group(7), rolls=(int(m.group(8) or 1), int(m.group(9) or 1)), geometry=d['geometry']['default'] if d else None, skins=skins,
                        anims={}, kind='furniture'))
    return out


def achievements():
    pat = r'name: "([^"]+)", description: "([^"]+)", goal: (\d+), icon: `\$\{ICONS\d*\}/(\w+)`'
    return [dict(name=m.group(1), text=m.group(2), goal=int(m.group(3)), icon=m.group(4)) for m in re.finditer(pat, src('achievements/Achievements'))]


def infection():
    text = src('status/Infection')
    stages = re.findall(r'name: "([^"]+)",\s*hint: "[^"]*",\s*threshold: (\d+)', text)
    period = int(constant_number('PROGRESSION_PERIOD', 'status/Infection'))
    turned = re.findall(r'"olivares_zomblocks:(\w+)"', re.search(r'TURNED_ZOMBIES(?:: [^=]+)? = \[(.*?)\]', text).group(1))
    return dict(stages=[(n, int(t)) for n, t in stages], seconds_per_level=period / 20, turned=turned)


def bite_severities():
    sev = {}
    for _f, text in TS.items():
        for _name, _parent, body in classes(text):
            tid = re.search(r'typeId = "olivares_zomblocks:(\w+)"', body)
            s = re.search(r'biteSeverity = (\d+)', body)
            if tid and s:
                sev[tid.group(1)] = int(s.group(1))
    return sev
