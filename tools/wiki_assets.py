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
    for sub, src in (('items', 'textures/items/olivares_zombie'), ('eggs', 'textures/items/olivares_zombie/eggs')):
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
