"""Images and 3D bundles of the wiki, made from the add-on's own models and textures:
- img/z/<id>_<k>.png   a 3/4 render of every zombie variant (same renderer as the guidebook)
- img/items/, img/eggs/ the inventory icons and spawn egg icons, copied from the RP
- img/bossbars/<id>.png the real boss bar of each boss (make_boss_bars.py preview, full health)
- models/<id>.js        the geometry, textures and animations of a zombie for the 3D viewer (a classic script that
                        fills window.WIKI_MODELS: the site also works opened from the disk, without a server)
- vendor/three.js       three.js r160 turned into a classic script (window.THREE), for the same reason
"""
import base64
import io
import json
import os
import shutil

from PIL import Image

import wiki_data as W

M = W.M
INK = (10, 14, 12, 255)


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def zombie_render(z, skin, box=(300, 340), yaw=28, pitch=10):
    geo, texdir = M.rp_model('zombie', z['id'])
    tex = Image.open(os.path.join(W.RP, skin + '.png')).convert('RGBA')
    return M.render_model(geo, tex, yaw, pitch, outline=INK, box=box, max_scale=10)


def npc_render(texture, box=(300, 340)):
    geo, texdir = M.rp_model('npc', 'humanoid')
    return M.render_model(geo, Image.open(os.path.join(texdir, texture + '.png')).convert('RGBA'), 28, 10, outline=INK, box=box, max_scale=10)


def boss_bar(boss_id):
    import make_boss_bars as B
    for key, zid, _name, extras in B.THEMES:
        if zid == boss_id:
            tex = Image.open(os.path.join(W.RP, B.TEX_DIR, key + '.png')).convert('RGBA')
            img = B.bar_preview(tex, 21, extras, extras)
            return img.crop(img.getbbox())
    return None


def data_uri(path):
    with open(path, 'rb') as fh:
        return 'data:image/png;base64,' + base64.b64encode(fh.read()).decode()


def model_bundle(z, geos, anims):
    """what the 3D viewer needs for one zombie"""
    geo = geos[z['geometry']]
    used = {}
    for key, anim_id in z['anims'].items():
        if anim_id in anims:
            used[key] = anims[anim_id]
    return dict(geo={'format_version': '1.12.0', 'minecraft:geometry': [geo]},
                textures=[data_uri(os.path.join(W.RP, s + '.png')) for s in z['skins']], anims=used)


WEAPON_FX = 'animation.olivares_zomblocks.weapon_mods.fx'


def weapon_geo_tex(w):
    """(geometry dict, texture path, render kind) of a weapon: its 3D attachable, or the entity model of thrown ones"""
    if w['model'] == 'attachable':                       # the file itself: M.rp_model strips the mod bones
        geo = json.load(open(W.locate('models/entity/olivares/zomblocks/attachables/%s.geo.json' % w['id']), encoding='utf-8'))
        return geo, W.locate('textures/olivares/zomblocks/attachables/%s.png' % w['id'])
    name = w['model'].split(':', 1)[1]                  # props/ or projectiles/
    geo = json.load(open(W.locate('models/entity/olivares/zomblocks/%s.geo.json' % name), encoding='utf-8'))
    return geo, W.locate('textures/olivares/zomblocks/entity/%s.png' % name)


def weapon_view(w):
    """rest pose of root_item + camera (my yaw = -python yaw, radians) like the guidebook pictures"""
    import math
    if w['model'] != 'attachable':
        return {}, -math.radians(30), 0.35
    if w['kind'] in ('Ranged', 'Spray'):
        return {'root_item': {'rotation': [-90, 0, 0]}}, -math.radians(270), 0.1
    return {'root_item': {'rotation': [0, 0, -30]}}, -math.radians(200), 0.18


def weapon_render(w, box=(300, 300), mod=None):
    if w['model'] == 'attachable':
        geo, texdir = M.rp_model('weapon', w['id'], mod)
        return M.weapon_render(geo, Image.open(os.path.join(texdir, w['id'] + '.png')), w['kind'], box)
    img = M.picture(w['model'], box)
    k = int(min(box) * 0.7 // max(img.size))                           # small thrown items: scaled up, pixels kept
    return img.resize((img.width * k, img.height * k), Image.NEAREST) if k > 1 else img


def weapon_bundle(w, anims):
    geo, tex = weapon_geo_tex(w)
    rest, yaw, pitch = weapon_view(w)
    bones = {b['name'] for b in geo['minecraft:geometry'][0]['bones']}
    clip = {'loop': True, 'animation_length': 4, 'bones': {}}
    if WEAPON_FX in anims:
        clip['bones'].update({k: v for k, v in anims[WEAPON_FX].get('bones', {}).items() if k in bones})
    for bone, ch in rest.items():
        clip['bones'].setdefault(bone, {}).update(ch)
    mods = sorted({b[4] for b in bones if b.startswith('mod_') and len(b) >= 5})
    return dict(geo=geo, textures=[data_uri(tex)], anims={'show': clip}, view=dict(yaw=yaw, pitch=pitch), mods=mods)


def build_weapons(out, weapons, mods, renders=True):
    anims = W.animations()
    for w in weapons:
        if renders:
            save(weapon_render(w), os.path.join(out, 'img', 'w', w['id'] + '.png'))
            if w['moddable']:
                for m in mods['mods']:
                    save(weapon_render(w, (240, 240), m['letter']), os.path.join(out, 'img', 'w', '%s_%s.png' % (w['id'], m['letter'])))
        path = os.path.join(out, 'models', 'w_' + w['id'] + '.js')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write('(window.WIKI_MODELS = window.WIKI_MODELS || {})[%s] = %s;\n' % (json.dumps('w_' + w['id']), json.dumps(weapon_bundle(w, anims), separators=(',', ':'))))


def three_classic(src, dst):
    """three.module.js has no import and one final export {...}: wrap it so it defines window.THREE"""
    code = open(src, encoding='utf-8').read()
    i = code.rindex('export {')
    body, exports = code[:i], code[i + len('export'):].strip().rstrip(';')
    with open(dst, 'w', encoding='utf-8') as fh:
        fh.write('(function () {\n' + body + '\nwindow.THREE = ' + exports + ';\n})();\n')


def build(out, zombies, renders=True):
    geos, anims = W.geometries(), W.animations()
    # item icons + spawn eggs (copied as they are; shown pixelated)
    for sub, src in (('items', 'textures/olivares/zomblocks/items'), ('eggs', 'textures/olivares/zomblocks/items/eggs')):
        d = os.path.join(out, 'img', sub)
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(os.path.join(W.RP, src)):
            if f.endswith('.png'):
                shutil.copyfile(os.path.join(W.RP, src, f), os.path.join(d, f))
    for z in zombies:
        if renders:
            for k, skin in enumerate(z['skins']):
                save(zombie_render(z, skin), os.path.join(out, 'img', 'z', '%s_%d.png' % (z['id'], k)))
        if z['kind'] == 'boss':
            bar = boss_bar(z['id'])
            if bar:
                save(bar, os.path.join(out, 'img', 'bossbars', z['id'] + '.png'))
        bundle = model_bundle(z, geos, anims)
        path = os.path.join(out, 'models', z['id'] + '.js')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write('(window.WIKI_MODELS = window.WIKI_MODELS || {})[%s] = %s;\n' % (json.dumps(z['id']), json.dumps(bundle, separators=(',', ':'))))
    if renders:
        save(npc_render('trader_medic'), os.path.join(out, 'img', 'npc', 'trader.png'))
        save(npc_render('survivor_hoodie'), os.path.join(out, 'img', 'npc', 'ally.png'))
        geo, texdir = M.rp_model('weapon', 'sledgehammer')
        save(M.weapon_render(geo, Image.open(os.path.join(texdir, 'sledgehammer.png')), 'Melee', (300, 340)), os.path.join(out, 'img', 'misc', 'weapons.png'))
        save(M.picture('buggy:rocket,headlights@rust', (340, 300)), os.path.join(out, 'img', 'misc', 'buggy.png'))
        save(M.picture('entity:fabricator', (300, 320)), os.path.join(out, 'img', 'misc', 'fabricator.png'))
    os.makedirs(os.path.join(out, 'vendor'), exist_ok=True)
    three_classic(os.path.join(W.WIKI, 'web', 'vendor', 'three.module.js'), os.path.join(out, 'vendor', 'three.js'))
