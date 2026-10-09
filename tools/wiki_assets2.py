"""Renders and 3D bundles of the second half of the wiki: armor on a survivor, traders, allies, buggy, furniture,
containers, infection monitor screens, blocks and deployables. Same renderer as the guidebook."""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import wiki_data as W
from wiki_assets import INK, data_uri, save

M = W.M
G = M.G
MANNEQUIN = 'textures/olivares/zomblocks/entity/npcs/survivor_student'


def tex_of(path):
    return Image.open(os.path.join(W.RP, path + '.png')).convert('RGBA')


def geo_doc(g):
    return {'format_version': '1.12.0', 'minecraft:geometry': [json.loads(json.dumps(g))]}


def render_layers(layers, yaw=28, pitch=10, box=(300, 340), max_scale=10.0, outline=INK):
    """like make_guidebook.render_model, for several (geometry, texture) drawn together (a survivor + armor pieces)"""
    quads = []
    for geo, tex in layers:
        desc = geo['minecraft:geometry'][0]['description']
        tw, th = desc.get('texture_width'), desc.get('texture_height')
        if tw and th and tex.size[0] > tw:
            tex = tex.resize((tw, th), Image.BOX)
        quads += G.collect_quads(geo, tex)
    Q = np.array([q[0] for q in quads], dtype=float)
    N = np.array([q[2] for q in quads], dtype=float)
    C = np.array([q[1][:3] for q in quads], dtype=float)
    P = Q.reshape(-1, 3)
    yw, pt = math.radians(yaw), math.radians(pitch)
    fwd = np.array([math.sin(yw) * math.cos(pt), -math.sin(pt), math.cos(yw) * math.cos(pt)])
    right = np.cross(fwd, [0, 1.0, 0]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    light = np.array([0.35, 1.0, -0.55]); light /= np.linalg.norm(light)
    xs, ys = P @ right, P @ up
    scale = min((box[0] - 4) / max(1e-6, xs.max() - xs.min()), (box[1] - 4) / max(1e-6, ys.max() - ys.min()), max_scale)
    W_, H_ = int((xs.max() - xs.min()) * scale) + 4, int((ys.max() - ys.min()) * scale) + 4
    img = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    sx = ((Q @ right) - xs.min()) * scale + 2
    sy = (ys.max() - (Q @ up)) * scale + 2
    shade = 0.62 + 0.38 * np.maximum(0.0, N @ light)
    shade = np.where(N @ fwd > 0, shade * 0.8, shade)
    cols = np.minimum(255, (C * shade[:, None]).astype(int))
    for i in np.argsort(-(Q @ fwd).mean(axis=1), kind='stable'):
        c = (int(cols[i, 0]), int(cols[i, 1]), int(cols[i, 2]), 255)
        dr.polygon(list(zip(sx[i].tolist(), sy[i].tolist())), fill=c, outline=c)
    a = np.array(img)[:, :, 3] > 0
    grown = np.array(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
    arr = np.array(img)
    arr[grown & ~a] = outline
    return Image.fromarray(arr)


def write_bundle(out, key, bundle):
    path = os.path.join(out, 'models', key + '.js')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('(window.WIKI_MODELS = window.WIKI_MODELS || {})[%s] = %s;\n' % (json.dumps(key), json.dumps(bundle, separators=(',', ':'))))


def entity_render(geometry, texture, geos, box=(300, 300), yaw=30, pitch=20):
    return render_layers([(geo_doc(geos[geometry]), tex_of(texture))], yaw, pitch, box)


# example hologram panels as seen in game (make_fabricator.py / make_buggy_garage.py layouts, 8 texels per unit):
# the Fabricator: combo strip above the card, the card, the status strip under it, then the bar of 3 buttons
# (< PREV, the action, NEXT >); the garage: the category tabs left of the card, the status over the bottom of the
# card, the buttons under it. Textures by index: fabricator cards 0-4 the mods (electric, toxic, fire, frost, spiked),
# 5-8 Reinforce, 9 Remove, 10-17 the build cards, 18-20 the shuriken mods, 21 Close; statuses 1 READY, 2-6 missing a
# mod part, 13 working, 18 ready to remove; bars 0 WORKING, 1 BUILD, 2 BUILD (off), 3 REMOVE, 5 CLOSE. Garage cards
# 00-05 weapons, 06-10 mobility, 11-15 utility, 16 repair, 17 pack up; statuses 1 TO BUY, 3 INSTALLED, 4 NEEDS THE
# TRUNK, 5 READY, 6 MISSING ITEMS; bars 0 BUY, 1 BUY (off), 3 REMOVE, 4 REPAIR, 6 PACK UP; tabs_<category>.
FAB = 'textures/olivares/zomblocks/entity/props/fabricator/'
GAR = 'textures/olivares/zomblocks/entity/props/buggy/garage/'
HOLO_EXAMPLES = {
    'fab_ready': ('fab', dict(card=2, status=1, bar=1)),
    'fab_missing': ('fab', dict(card=4, status=6, bar=2)),
    'fab_working': ('fab', dict(card=0, status=13, bar=0)),
    'fab_combo': ('fab', dict(card=0, status=1, bar=1, combo=1)),
    'fab_reinforce': ('fab', dict(card=5, status=1, bar=1)),
    'fab_remove': ('fab', dict(card=9, status=18, bar=3)),
    'fab_build': ('fab', dict(card=10, status=1, bar=1)),
    'fab_close': ('fab', dict(card=21, status=0, bar=5)),
    'gar_buy': ('gar', dict(card=0, status=1, bar=0, tab=0)),
    'gar_installed': ('gar', dict(card=4, status=3, bar=3, tab=0)),
    'gar_missing': ('gar', dict(card=6, status=6, bar=1, tab=1)),
    'gar_trunk': ('gar', dict(card=14, status=4, bar=1, tab=2)),
    'gar_repair': ('gar', dict(card=16, status=5, bar=4, tab=3)),
    'gar_pack': ('gar', dict(card=17, status=5, bar=6, tab=3)),
}


def holo_screen(kind, p, k=2):
    """one panel of the Fabricator ('fab') or of the buggy garage ('gar') on a dark background, x k"""
    if kind == 'fab':
        card, bar = tex_of(FAB + 'card_%d' % p['card']), tex_of(FAB + 'bar_%d' % p['bar'])
        status = tex_of(FAB + 'status_%d' % p['status'])
        img = Image.new('RGBA', (card.width + 16, 24 + 4 + card.height + 4 + 24 + 8 + bar.height + 16), (5, 8, 7, 255))
        y = 8
        if p.get('combo') is not None:
            img.alpha_composite(tex_of(FAB + 'combo_%d' % p['combo']), (8, y))
        y += 28
        img.alpha_composite(card, (8, y))
        y += card.height + 4
        img.alpha_composite(status, (8, y))
        img.alpha_composite(bar, (8, y + 32))
    else:
        card, bar = tex_of(GAR + 'card_%02d' % p['card']), tex_of(GAR + 'bar_%d' % p['bar'])
        status, tabs = tex_of(GAR + 'status_%d' % p['status']), tex_of(GAR + 'tabs_%d' % p['tab'])
        x = 8 + tabs.width + 8
        img = Image.new('RGBA', (x + card.width + 8, 8 + card.height + 8 + bar.height + 8), (5, 8, 7, 255))
        img.alpha_composite(tabs, (8, 8))
        img.alpha_composite(card, (x, 8))
        img.alpha_composite(status, (x, 8 + card.height - status.height))
        img.alpha_composite(bar, (x, 8 + card.height + 8))
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def fabricator_bundle(geos, anims):
    """the bench + its amber hologram (Electric card, READY, BUILD, a katana turning), as in game: the panel
    Fabricator.PANEL_HEIGHT blocks above"""
    ent = W.CLIENT[W.NS + 'fabricator']['desc']
    panel = W.CLIENT[W.NS + 'fabricator_panel']['desc']
    clip = {'loop': True, 'animation_length': 8, 'bones': {}}
    for key in ('float', 'holo'):
        clip['bones'].update(json.loads(json.dumps(anims.get(panel['animations'][key], {}).get('bones', {}))))
    if 'holo' in clip['bones']:
        clip['bones']['holo']['scale'] = 0.417                         # the katana's size on the panel (its weapon index)
    up = [0, W.constant_number('PANEL_HEIGHT', 'workshop/Fabricator') * 16, 0]

    def layer(geo_key, tex):
        return dict(geo=geo_doc(geos[panel['geometry'][geo_key]]), texture=data_uri(os.path.join(W.RP, tex + '.png')),
                    offset=up, additive=True, anim=clip)
    d = 'textures/olivares/zomblocks/entity/props/fabricator/'
    return dict(geo=geo_doc(geos[ent['geometry']['default']]), textures=[data_uri(os.path.join(W.RP, ent['textures']['default'] + '.png'))],
                anims={'bench': anims.get(ent['animations']['bench'], {})}, view=dict(yaw=-0.45, pitch=0.12, zoom=1.35),
                layers=[layer('card', d + 'card_0'), layer('status', d + 'status_1'), layer('buttons', d + 'bar_1'), layer('h3', d + 'holo_katana')])


def build(out, armor, furniture, containers, renders=True):
    g_, a_ = W.geometries(), W.animations()
    write_bundle(out, 'fabricator', fabricator_bundle(g_, a_))
    for name, (kind, p) in HOLO_EXAMPLES.items():
        save(holo_screen(kind, p), os.path.join(out, 'img', 'holo', name + '.png'))
    geos, anims = W.geometries(), W.animations()
    human = W.CLIENT[W.NS + 'survivor_ally']['desc']
    walk = {k: anims[v] for k, v in human.get('animations', {}).items() if v in anims and k in ('walk', 'idle', 'move')}
    # armor: a survivor wearing the set (image + 3D with the pieces as layers)
    for s in armor:
        layers = [(geo_doc(geos[human['geometry']['default']]), tex_of(MANNEQUIN))]
        layers += [(geo_doc(geos[p['geometry']]), tex_of(p['texture'])) for p in s['pieces']]
        if renders:
            save(render_layers(layers, 28, 8, (300, 360)), os.path.join(out, 'img', 'armor', s['key'] + '.png'))
            save(render_layers(layers, 208, 8, (300, 360)), os.path.join(out, 'img', 'armor', s['key'] + '_back.png'))
        write_bundle(out, 'armor_' + s['key'], dict(
            geo=layers[0][0], textures=[data_uri(os.path.join(W.RP, MANNEQUIN + '.png'))], anims=walk,
            layers=[dict(geo=geo_doc(geos[p['geometry']]), texture=data_uri(os.path.join(W.RP, p['texture'] + '.png'))) for p in s['pieces']]))
    # furniture: every colour + 3D
    for f in furniture:
        if not f['geometry']:
            continue
        if renders:
            for k, skin in enumerate(f['skins']):
                save(entity_render(f['geometry'], skin, geos), os.path.join(out, 'img', 'furniture', '%s_%d.png' % (f['id'], k)))
        write_bundle(out, 'f_' + f['id'], dict(geo=geo_doc(geos[f['geometry']]), anims={},
                                               textures=[data_uri(os.path.join(W.RP, s + '.png')) for s in f['skins']]))
    if not renders:
        return
    # traders and allies
    for kind in ('trader', 'survivor_ally', 'survivor'):
        d = W.CLIENT[W.NS + kind]['desc']
        for k in range(len([t for t in d['textures'] if t.startswith('skin_')])):
            save(render_layers([(geo_doc(geos[d['geometry']['default']]), tex_of(d['textures']['skin_%d' % k]))], 28, 10, (260, 320)),
                 os.path.join(out, 'img', 'npc', '%s_%d.png' % (kind, k)))
    # containers
    for c in containers:
        ce = W.CLIENT.get(W.NS + c['id'])
        if ce:
            d = ce['desc']
            tex = d['textures'].get('skin_0') or list(d['textures'].values())[0]
            save(entity_render(d['geometry']['default'], tex, geos, (240, 240)), os.path.join(out, 'img', 'world', c['id'] + '.png'))
    # buggy: bare, fully loaded, every module alone (bare rust only: the paints are gone since 08/10/2026)
    import make_buggy as MB
    save(M.picture('buggy:@rust', (360, 280)), os.path.join(out, 'img', 'buggy', 'rust.png'))
    save(M.picture('buggy:spikes,turret,rocket,susp,headlights,beacons,radar,trunk@rust', (420, 320)), os.path.join(out, 'img', 'buggy', 'full.png'))
    for _id, key, _name, _slot, _bone, _v in MB.MODULES:
        save(M.picture('buggy:%s@rust' % key, (260, 200)), os.path.join(out, 'img', 'buggy', 'm_%s.png' % key))
    # infection monitor screens
    import make_infection_monitor as IM

    def panel(state):
        im = IM.composite(state).crop((20, 20, 20 + IM.TW, 20 + IM.TH)).convert('RGBA')
        a = np.array(im)
        a[..., 3] = np.where(np.array(IM.glass_texture())[..., 3] > 0, 255, 0)
        return Image.fromarray(a)
    for i, level in enumerate((20, 50, 85, 100)):
        save(panel(dict(level=level)), os.path.join(out, 'img', 'monitor', 'stage_%d.png' % i))
    save(panel(dict(level=50, paused=True)), os.path.join(out, 'img', 'monitor', 'paused.png'))
    for i, m in enumerate(IM.MESSAGES):
        save(panel(dict(msg=i)), os.path.join(out, 'img', 'monitor', m[0] + '.png'))
    # special blocks (guidebook group 'Blocks'): the older ones like the guidebook, the new ones from their geometry
    old = {'electric_fence': 'block:electric_fence_on', 'barricade': 'block:barricade_0',
           'unstable_floor': 'block:unstable_floor_0', 'elevator': 'block:elevator_side'}
    first = {'barbed_wire': 'barbed_wire_0', 'glue_puddle': 'glue_puddle', 'sprinkler': 'sprinkler', 'manhole': 'manhole'}
    for b in W.D.BLOCKS:
        key = b['icon']
        try:
            if key in old:
                im = M.picture(old[key], (240, 240))
            else:
                geo = json.load(open(os.path.join(W.RP, 'models/blocks/olivares/zomblocks/%s.geo.json' % key), encoding='utf-8'))
                im = M.render_model(geo, tex_of('textures/olivares/zomblocks/blocks/' + first[key]), 30, 22, box=(240, 240), max_scale=12)
            save(im, os.path.join(out, 'img', 'world', key + '.png'))
        except Exception as err:                                                   # noqa: BLE001
            print('no picture for', key, err)
    # blocks and deployables (the guidebook pictures)
    for s in W.D.SURVIVAL:
        if s.get('model', '').startswith(('block:', 'entity:')):
            try:
                save(M.picture(s['model'], (240, 240)), os.path.join(out, 'img', 'world', s['id'] + '.png'))
            except Exception as err:                                                   # noqa: BLE001
                print('no picture for', s['id'], err)
