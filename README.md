# Zombie Extraction Wiki

Static wiki for players, generated from the add-on itself: open `public/index.html` (no server needed), or run `serve.bat`.

- `build.bat` (or `python tools/build.py`): rebuilds everything into `public/` (about 40 s, renders included). `--fast`: pages only.
- `tools/wiki_data.py`: reads the add-on (guidebook_data.py, BP entities and loot tables, TypeScript sources, RP client entities, animations, lang). Never writes it.
- `tools/wiki_assets.py`: zombie renders (same renderer as the guidebook), icons, spawn eggs, real boss bars, 3D bundles (`public/models/*.js`) and three.js turned into a classic script.
- `tools/build.py`: the pages (home, zombies, bosses, "coming soon" sections), sidebar, search index.
- `content/*.py`: hand-written texts (boss attacks, phases, strategy). Numbers read in the code: re-check them when a boss changes.
- `web/`: CSS, site script (search, filters, phone menu), 3D viewer (Bedrock geometry + animations, Molang).
- `design/wiki_mockup.html`: the validated mockup.

Everything is in English, PEGI 10, no technical words.
