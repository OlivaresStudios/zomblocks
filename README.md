# Zomblocks Wiki

Static wiki for players, generated from the add-on itself: open `public/index.html` (no server needed), or run `serve.bat`.

- `build.bat` (or `python tools/build.py`): rebuilds everything into `public/` (about 40 s, renders included). `--fast`: pages only.
- `tools/wiki_data.py`: reads the add-on (guidebook_data.py, BP entities and loot tables, TypeScript sources, RP client entities, animations, lang). Never writes it.
- `tools/wiki_assets.py`: zombie renders (same renderer as the guidebook), icons, spawn eggs, real boss bars, 3D bundles (`public/models/*.js`) and three.js turned into a classic script.
- `tools/build.py`: home, zombies, bosses, weapons, mods & Fabricator, sidebar, search index; `tools/build2.py`: armor, food & medical, gear, infection, traders, allies, buggy, loot & world, furniture, achievements, first night guide.
- `tools/wiki_data2.py` / `tools/wiki_assets2.py`: data and renders of those pages (armor worn by a survivor in 3D, traders, allies, survivors, buggy modules, furniture colours, containers, infection monitor screens, Fabricator and garage hologram panels).
- `tools/check_links.py`: every link and image of every page exists (must end with "0 broken").
- `content/*.py`: hand-written texts (bosses, Fabricator, every other page in `pages.py`). Numbers read in the code: re-check them when the matching system changes.
- `web/`: CSS, site script (search, filters, phone menu), 3D viewer (Bedrock geometry + animations, Molang).
- `design/wiki_mockup.html`: the validated mockup.
- `tools/build3.py`: Mechanics & combos, Towns & lairs (the 5 towns, Haven Hill, the 8 boss lairs, the guidebook radio; texts in `content/pages.py`).
- `build2.survivors_page`: the townsfolk and hidden survivors; weapon pages play the weapon's own animations (idle, right click, swing).
- `tools/deploy.py`: publishes `public/` to the `gh-pages` branch (GitHub Pages, domain zomblocks.eu in `CNAME`).
- `tools/hostinger_dns.py [--apply]`: points zomblocks.eu (DNS at Hostinger) to GitHub Pages, with the API token in `HOSTINGER_API_TOKEN`.

The add-on documented is the newest package of `../READY TO SEND/<name>_<version>/Content` (resource_packs, behavior_packs);
without it, `../zombie_RP` and `../zombie_BP`. The generator is `../zombie_tools` (or `../CLAUDE_TOOLS`). `ZOMBIE_TOOLS`,
`ZOMBIE_RP`, `ZOMBIE_BP` override them. The packaged BP has no TypeScript: `wiki_data.script_modules()` cuts its bundled
`scripts/**/main.js` back into modules ('items/Loot', 'npcs/Trader'...) and the readers accept both forms. Fonts are self-hosted (`web/fonts`): the site makes no request to Google.

Everything is in English, PEGI 10, no technical words.
