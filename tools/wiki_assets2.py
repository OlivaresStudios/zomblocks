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
MANNEQUIN = 'textures/entity/olivares_zombie/survivor_student'


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


# example hologram screens (card + status strip, as seen in game): (file name, card texture, status texture)
FAB = 'textures/entity/olivares_zombie/fabricator/'
GAR = 'textures/entity/olivares_zombie/buggy/garage/'
HOLO_EXAMPLES = {
    'fab_ready': (FAB + 'card_2', FAB + 'status_1'),
    'fab_missing': (FAB + 'card_4', FAB + 'status_6'),
    'fab_working': (FAB + 'card_0', FAB + 'status_13'),
    'fab_reinforce': (FAB + 'card_5', FAB + 'status_8'),
    'fab_remove': (FAB + 'card_9', FAB + 'status_18'),
    'fab_combo': (FAB + 'card_0', FAB + 'combo_1'),
    'gar_buy': (GAR + 'card_00', GAR + 'status_1'),
    'gar_installed': (GAR + 'card_04', GAR + 'status_3'),
    'gar_missing': (GAR + 'card_06', GAR + 'status_7'),
    'gar_paint': (GAR + 'card_22', GAR + 'status_4'),
    'gar_trunk': (GAR + 'card_14', GAR + 'status_5'),
    'gar_repair': (GAR + 'card_33', GAR + 'status_6'),
}


def holo_screen(card, status, k=2):
    a, b = tex_of(card), tex_of(status)
    img = Image.new('RGBA', (max(a.width, b.width) + 8, a.height + b.height + 12), (5, 8, 7, 255))
    img.alpha_composite(a, (4, 4))
    img.alpha_composite(b, (4, a.height + 8))
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def fabricator_bundle(geos, anims):
    """the bench + its amber hologram (Electric card, READY, a katana turning), as in game: panel 1.45 blocks above"""
    ent = W.CLIENT[W.NS + 'fabricator']['desc']
    panel = W.CLIENT[W.NS + 'fabricator_panel']['desc']
    clip = {'loop': True, 'animation_length': 8, 'bones': {}}
    for key in ('float', 'holo'):
        clip['bones'].update(json.loads(json.dumps(anims.get(panel['animations'][key], {}).get('bones', {}))))
    if 'holo' in clip['bones']:
        clip['bones']['holo']['scale'] = 0.417                         # the katana's size on the panel (its weapon index)
    up = [0, 1.45 * 16, 0]

    def layer(geo_key, tex):
        return dict(geo=geo_doc(geos[panel['geometry'][geo_key]]), texture=data_uri(os.path.join(W.RP, tex + '.png')),
                    offset=up, additive=True, anim=clip)
    d = 'textures/entity/olivares_zombie/fabricator/'
    return dict(geo=geo_doc(geos[ent['geometry']['default']]), textures=[data_uri(os.path.join(W.RP, ent['textures']['default'] + '.png'))],
                anims={'bench': anims.get(ent['animations']['bench'], {})}, view=dict(yaw=-0.45, pitch=0.12, zoom=1.05),
                layers=[layer('card', d + 'card_0'), layer('status', d + 'status_1'), layer('h3', d + 'holo_katana')])


def build(out, armor, furniture, containers, renders=True):
    g_, a_ = W.geometries(), W.animations()
    write_bundle(out, 'fabricator', fabricator_bundle(g_, a_))
    for name, (card, status) in HOLO_EXAMPLES.items():
        save(holo_screen(card, status), os.path.join(out, 'img', 'holo', name + '.png'))
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
    for kind in ('trader', 'survivor_ally'):
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
    # buggy: bare, fully loaded, every module alone, every paint
    import make_buggy as MB
    save(M.picture('buggy:@rust', (360, 280)), os.path.join(out, 'img', 'buggy', 'rust.png'))
    save(M.picture('buggy:spikes,turret,rocket,susp,headlights,beacons,radar,trunk@red', (420, 320)), os.path.join(out, 'img', 'buggy', 'full.png'))
    for _id, key, _name, _slot, _bone, _v in MB.MODULES:
        save(M.picture('buggy:%s@rust' % key, (260, 200)), os.path.join(out, 'img', 'buggy', 'm_%s.png' % key))
    for paint in MB.PAINTS:
        save(M.picture('buggy:@%s' % paint, (180, 140)), os.path.join(out, 'img', 'buggy', 'p_%s.png' % paint))
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
    # blocks and deployables (the guidebook pictures)
    for s in W.D.SURVIVAL:
        if s.get('model', '').startswith(('block:', 'entity:')):
            try:
                save(M.picture(s['model'], (240, 240)), os.path.join(out, 'img', 'world', s['id'] + '.png'))
            except Exception as err:                                                   # noqa: BLE001
                print('no picture for', s['id'], err)
