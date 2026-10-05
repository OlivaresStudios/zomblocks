"""Hand-written texts of the wiki pages (English, for players, no technical words). Rules and numbers were read in the
add-on code on 05/10/2026 (zombie_BP/src); prices, odds, lists, health... are NOT written here: the build reads them.
Re-check these texts when the matching system changes."""

ARMOR_INTRO = ('Armor in Zombie Extraction is worn like vanilla armor and shows in 3D on you. Each piece protects you; '
               'wear the full set and you also get its set bonus, shown in your action bar when it turns on.')

# set key -> what the bonus really does (Armor Sets code)
ARMOR_BONUS = {
    'biker': 'A zombie bite has half the usual chance to infect you.',
    'sport': 'Sprint into zombies to tackle them: 3 damage and a big push to every zombie in front of you, once a second.',
    'hazmat': 'Toxic clouds, acid and poison do nothing to you, and a bite has only a quarter of the usual chance to infect you.',
    'firefighter': 'You never burn (permanent fire resistance) and explosions deal half damage.',
    'scrap': 'The toughest common set, but it rattles: while you move, every zombie within 10 blocks that hunts by ear hears you.',
    'diving': 'In water: water breathing, conduit power (see and dig underwater) and speed. Snorkel zombies lurking underwater are revealed to you.',
    'electrician': 'Electricity does nothing to you (fences, Live Wire, shocks) and your melee hits shock the zombie, at most every 2 s.',
    'ninja': 'While you sneak, zombies lose track of you. The Blind never hears you, even when you run.',
    'mascot': 'While you walk calmly, zombies think you are one of them. Sprinting or hitting gives you away for 3 s.',
    'exo': 'Resistance, strength and jump boost as long as you wear it. The best set in the game.',
    'astronaut': 'Slow falling, a high jump (jump boost II) and water breathing.',
    'chef': 'Every food you eat also heals you (half its food points) with 3 s of regeneration.',
}

INFECTION_INTRO = ('Some zombies infect you when they hit you. The infection grows by itself, from 1 to 100, and gets '
                   'worse at each stage. At 100 you are Turned, and if you die while you are Turning or Turned, you come '
                   'back as a zombie.')
INFECTION_STAGES = {
    'Infected': 'Now and then you cough (a small green cloud). Nothing else yet: the best time to cure it.',
    'Feverish': 'You are weak all the time and get poisoned for 2 s every 12 s.',
    'Turning': 'Weakness II and slowness. Every 8 s your sight goes dark or blind for a moment and you get poisoned.',
    'Turned': 'Wither and slowness II. Cure it now: if you die, you come back as a zombie.',
}
INFECTION_GROWTH = ('Every bite that infects adds to the level (15 for most zombies). Then the level goes up by 1 every '
                    '3 seconds, 20 per minute: from a first bite to Turning takes under 3 minutes. A bandage stops it for '
                    '45 seconds.')
INFECTION_CURES = [
    ('medicine', 'Medicine', 'Cures the infection completely and gives 6 s of regeneration.'),
    ('first_aid_kit', 'First Aid Kit', 'Full health, removes poison, wither, nausea, slowness and weakness, and the infection goes down by 30.'),
    ('bandage', 'Bandage', '+6 health and the infection is paused for 45 s.'),
    ('pickle_jar', 'Pickle Jar', 'Infection -5, and bites cannot infect you for 60 s.'),
]
INFECTION_OTHER = [
    ('Virus barrels', 'The plague cloud of a burst Explosive Virus Barrel adds 15 to everyone within 3 blocks.'),
    ('Bloaters', 'When a Bloater bursts next to you, 25% chance to be infected (+10).'),
    ('Armor', 'The Biker set halves the chance that a bite infects you; the Hazmat set divides it by 4.'),
]
MONITOR_TEXT = ('A small holographic monitor shows up next to your left hand for 5 seconds every minute while you are '
                'infected, and right away after a bite or a new stage. The bar has 20 segments (one per 5 levels); the '
                'newest one blinks. After a treatment it shows what the treatment did for 3 seconds. It never takes the '
                'place of a totem: with a totem in your off hand, the infection shows in the action bar instead.')

TRADERS_INTRO = ('Traders are survivors who sell gear for scrap. There are 8 kinds of trader; each sells 2 kinds of items. '
                 'Right click a trader: their menu shows what they sell and how much scrap you carry.')
TRADERS_HOW = [
    ('Their stock is rolled once', 'Every trader rolls its stock the first time it is met: each common offer has a '
                                   '{Common}% chance to be there, each rare offer {Rare}% and each OP offer only {OP}%. '
                                   'Two traders of the same kind never sell exactly the same things: visit them all.'),
    ('Rare and OP offers', 'In the menu, rare offers are written in blue and OP offers in purple with a star.'),
    ('Scrap', 'Scrap is the money of the apocalypse. Zombies drop it, containers and supply crates hold it, and the barter '
              'trades 4 rotten flesh for 2 scrap.'),
    ('Barter', 'Some offers cost items instead of scrap: 3 bandages make a first aid kit, a golf club and a baseball bat '
               'make a katana...'),
]

ALLIES_INTRO = ('Allies are survivors who follow you, fight the zombies and pick things up for you. Hire one from a Camp '
                'Guard, or recruit a free survivor you meet.')
ALLIES_HOW = [
    ('Recruit', 'Right click a survivor and choose Recruit: they follow you and fight. The Camp Guard trader also sells '
                'one (Hire Help).'),
    ('Their menu', 'Right click your ally: health, status, their bag, the items you can heal them with, and Part ways.'),
    ('The bag', 'Every zombie your ally kills has a {chance}% chance to leave them something (never scrap). The bag holds '
                '{bag} things; buy them from the menu for scrap.'),
    ('Downed', 'An ally at 0 health is down. Sneak within {radius} blocks of them for {revive:g} seconds to revive them. '
               'Nobody comes within {bleed} seconds? They retreat and leave.'),
    ('Part ways', 'Ends the alliance: they stay where they are as a free survivor (same name, look and bag). You can '
                  'recruit them again later.'),
    ('Find them', 'Hold a Whistle: the action bar becomes a compass pointing to your nearest ally. A Walkie-Talkie calls '
                  'your allies to you.'),
]

BUGGY_INTRO = ('The Rusty Buggy is a two-seat vehicle with a fuel tank, a dashboard and a holographic garage to upgrade '
               'it with weapons, wheels, lights, a trunk and paint.')
BUGGY_HOW = [
    ('Get one', 'The Tinkerer sells the Rusty Buggy item; toolboxes and supply crates rarely hold one. Right click a block '
                'with it to place the buggy.'),
    ('Drive', 'Right click the buggy to get in (2 seats). Look to steer, move forward to drive. Sneak to get out.'),
    ('Fuel', 'A new buggy has a third of a tank. A full tank lasts about {range} blocks; right click the buggy with a Fuel '
             'Canister to add half a tank. The fuel gauge and a bar of lights are on the dashboard.'),
    ('Ram', 'Hitting a zombie at speed rams it: 1 damage, 6 with the Spiked Bumper. Bosses are never affected by the buggy '
            'or its modules.'),
    ('Hull', 'The hull ({hull} points) takes half of the zombie hits meant for the riders, and every hit on the buggy. At '
             '0 the buggy is wrecked: repair it in the garage with a wrench.'),
    ('Modules', 'Modules only work while someone sits in the buggy, except the Warning Lights. One weapon per slot '
                '(front, roof, rear) plus the trunk; everything else stacks. A module bought once is yours for good.'),
]
GARAGE_HOW = [
    ('Open the garage', 'Right click the buggy with a wrench: a holographic garage opens over it, one card per module, '
                        'dye or service.'),
    ('Browse', 'Right click: next card. Punch: previous card. Sneak + right click: next category.'),
    ('Buy, install, remove', 'Sneak + punch. The card shows the cost and whether you own it already. While you browse, '
                             'the module blinks on the buggy.'),
]

WORLD_INTRO = 'Everything you can search, use and avoid around the world.'
CONTAINERS_TEXT = ('Right click a container: after 1 second of searching, its loot pops out and it stays open. It restocks '
                   '{restock} minutes later. Each one looks a little different. A vase is smashed instead of opened.')
SUPPLY_DROP = ('A Walkie-Talkie calls your allies to you. With no ally around, it calls a supply drop instead, once a day: '
               'a supply crate falls from the sky under a parachute next to you.')
NOISE_TEXT = ('Some zombies hunt by ear, like the Blind. They hear survivors who walk or sprint (never the ones who sneak), '
              'weapons, explosions, the guitar, popcorn... and walk to the noise. The Ninja set makes you silent; the '
              'Scrap set makes you loud.')
HAZARDS = [
    ('Toxic clouds', 'Virus barrels, virus bombs, the Spitter and the Warden leave clouds that hurt survivors (or zombies) '
                     'inside them. The Hazmat set is immune.'),
    ('Gas column', 'Hit it and it leaks gas; set it on fire and it explodes (6 blocks).'),
    ('Fire', 'Burning zombies spread fire. The Firefighter set never burns, and a full Water Flask puts you out.'),
]

FURNITURE_INTRO = ('Houses are full of furniture you can carry, throw and build barricades with. Every piece comes in '
                   '4 colours.')
FURNITURE_HOW = [
    ('Carry', 'Look at a light piece of furniture and click it to pick it up. Sneak to put it down.'),
    ('Throw', 'Attack while carrying it: it flies and hits the first zombie, 3 damage + 2 per weight point.'),
    ('Break', 'Every piece breaks after a number of hits; zombies that get stuck bash it too. A broken Shopping Crate '
              'spills snacks.'),
    ('Barricade', 'Block doors and corridors with heavy pieces. The Fort Builder achievement asks for 10 pieces.'),
]

ACHIEVEMENTS_INTRO = ('23 achievements to unlock. Open the achievement menu with the Zombie Guidebook: sneak and punch the '
                      'open book.')

FIRST_NIGHT = [
    ('Read the guidebook', 'You get the Zombie Guidebook the first time you join. Use it: a big book floats in front of '
                           'you. Right click turns the page, punch goes back, sneak + right click jumps to the next '
                           'chapter. It has a page for every zombie, weapon and item.'),
    ('Grab a weapon', 'A baseball bat, a golf club or a frying pan is enough for the first zombies. Duffel bags and supply '
                      'crates often hold one; the Brawler and the Camp Guard sell them for 5 scrap.'),
    ('Search everything', 'Trash cans, vases, duffel bags, cardboard boxes and toolboxes can be searched (right click). '
                          'They hold food, scrap, gadgets and tools, and restock after 5 minutes.'),
    ('Collect scrap', 'Zombies drop scrap. Spend it at the traders: each one sells 2 kinds of items and never the same '
                      'stock twice.'),
    ('Do not get bitten', 'Some zombies infect you. A bandage pauses the infection, medicine cures it. Watch the monitor '
                          'next to your left hand: it shows the infection every minute.'),
    ('Find a friend', 'Hire an ally from a Camp Guard (20 scrap) or recruit a free survivor. Allies fight with you and pick '
                      'up loot.'),
    ('Barricade', 'Carry furniture into doorways. Zombies bash what blocks them, so keep an eye on it; duct tape repairs a '
                  'cracked barricade.'),
    ('Know your enemy', 'Read the zombie pages of this wiki: each one tells you how it fights and how to beat it.'),
]

# example hologram screens shown under "How to use" (image name in img/holo, caption)
FAB_EXAMPLES = [
    ('fab_ready', 'You have the lighter and 3 scrap: READY, sneak + punch to build.'),
    ('fab_missing', 'A part is missing: the strip tells you which one.'),
    ('fab_working', 'Building: the welding arm works for 2 seconds.'),
    ('fab_combo', 'On the Electric Guitar the Electric card shows its signature combo.'),
    ('fab_reinforce', 'Reinforce: each level costs more duct tape and scrap.'),
    ('fab_remove', 'Remove Mod: free, but the parts are lost.'),
]
GARAGE_EXAMPLES = [
    ('gar_buy', 'A module you do not own yet: TO BUY, sneak + punch to pay.'),
    ('gar_installed', 'Already on the buggy: sneak + punch removes it (you keep it).'),
    ('gar_missing', 'Not enough items: the action bar lists what is missing.'),
    ('gar_paint', 'Dye cards show the painted buggy; APPLIED is the current paint.'),
    ('gar_trunk', 'The Big Trunk needs the Trunk first.'),
    ('gar_repair', 'Service: repair the hull with a wrench, or pack the buggy up.'),
]
