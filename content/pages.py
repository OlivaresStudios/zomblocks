"""Hand-written texts of the wiki pages (English, for players, no technical words). Rules and numbers were read in the
add-on code on 05/10/2026 (zombie_BP/src); prices, odds, lists, health... are NOT written here: the build reads them.
Re-check these texts when the matching system changes."""

ARMOR_INTRO = ('Armor in Zomblocks is worn like vanilla armor and shows in 3D on you. Each piece protects you; '
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
# longer texts of the special blocks (the guidebook 'Blocks' group gives the names, icons and short lines)
BLOCK_TEXTS = {
    'electric_fence': 'Zaps and shocks every zombie that touches it (3 damage, x2 if the zombie is wet). Survivors get a '
                      'small shock too. Right click: on / off. Built at the Fabricator, 4 at a time.',
    'barricade': 'Planks and fragile glass slow the horde down, but zombies stuck in front of them bash them to pieces. '
                 'Duct tape patches a crack.',
    'unstable_floor': 'Cracks under every step and collapses after a moment. It rebuilds itself after a minute. Lure heavy '
                      'zombies on it.',
    'elevator': 'Stand on it and jump to go up to the next elevator block, sneak to go down. Zombies cannot use it.',
    'barbed_wire': 'Zombies crossing it are slowed down a lot and lose 1 health per second (bosses are not slowed). It '
                   'wears out as they cross it and finally snaps: right click it with duct tape to make it like new.',
    'glue_puddle': 'Put it on the ground: zombies walking in it are stuck (very slow). It dries up after about 30 seconds. '
                   'Built at the Fabricator, 4 at a time.',
    'sprinkler': 'Soaks every zombie within 4 blocks: wet zombies take double electric damage. It also puts out burning '
                 'survivors. Put it next to an electric fence. Built at the Fabricator.',
    'manhole': 'Zombies climb out of it while a survivor is around (never more than 4 nearby). Right click it with duct tape '
               'to seal it for good.',
}
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
                           'chapter. It has a page for every zombie, weapon and item. Hold it in your hand: it is also a '
                           'radio whose compass points to the nearest town.'),
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
    ('fab_build', 'Without a melee weapon in hand: the build cards, here 4 Glue Puddles.'),
]
GARAGE_EXAMPLES = [
    ('gar_buy', 'A module you do not own yet: TO BUY, sneak + punch to pay.'),
    ('gar_installed', 'Already on the buggy: sneak + punch removes it (you keep it).'),
    ('gar_missing', 'Not enough items: the action bar lists what is missing.'),
    ('gar_paint', 'Dye cards show the painted buggy; APPLIED is the current paint.'),
    ('gar_trunk', 'The Big Trunk needs the Trunk first.'),
    ('gar_repair', 'Service: repair the hull with a wrench, or pack the buggy up.'),
]

# ------------------------------------------------------------------------------------------------ mechanics & combos
# Read in the code on 08/10/2026 (props/GasColumn.ts, core/Explosions.ts, props/VirusBarrel.ts, props/OxygenTank.ts,
# status/Electricity.ts, blocks/ElectricFence.ts, status/StatusEffects.ts, zombies/Lures.ts, props/*.ts, items/Survival.ts).
MECHANICS_INTRO = ('The systems of Zomblocks talk to each other: water carries electricity, explosions set off other '
                   'explosions, frost makes zombies brittle, noise pulls the horde. Here are the tricks worth knowing.')
# (anchor, title, colour, intro, [combo]); combo = (name, [item icons], text, note or None)
MECHANICS = [
    ('explosions', 'Explosions', 'var(--red)', 'Gas, barrels and tanks are waiting to be set off. Survivors and allies are '
     'only pushed by them, never hurt (except by the plague of a virus barrel).', [
        ('Gas Column + Lighter', ['gas_column', 'lighter'],
         'Step 1: hit the gas column once (a melee hit or any projectile): it starts leaking gas for 30 seconds and pushes '
         'back everything around it.\nStep 2: while it leaks, set it on fire with a Lighter (from up to 4 blocks), the '
         'Flamethrower or any projectile.\nBOOM: 14 damage in a 6 block radius, a huge knock back, and every zombie caught '
         'in it burns for 5 seconds.',
         'A lighter does nothing to a gas column that is not leaking: break it open first. After 30 seconds of leaking it '
         'is empty and will not explode any more.'),
        ('Speaker + Gas Column', ['portable_speaker', 'gas_column'],
         'Place a Portable Speaker next to a gas column: for 15 seconds every zombie within 20 blocks gathers around it. '
         'Break the column open, step back, light it.', None),
        ('Chain reactions', ['grenade_launcher', 'virus_barrel', 'oxygen_tank'],
         'Every explosion sets off the explosive props in its radius: gas columns (even unbroken ones), virus barrels and '
         'oxygen tanks. The Boom Launcher (12 damage in 4.5 blocks), Fireworks, virus bombs and exploding zombies all '
         'count. Line them up: one shot clears the street, and unlocks the Chain Reaction achievement.', None),
        ('Virus Barrel', ['virus_barrel'],
         'Two melee hits, one projectile, a flame or an explosion and it bursts: 10 damage in 5 blocks, and every zombie '
         'it hits catches the plague. The plague hurts for 6 seconds and jumps to the nearest zombie, up to 3 times. A '
         'toxic cloud stays for a few seconds.',
         'Stand back: survivors within 3 blocks of the burst get +15 infection.'),
        ('Oxygen Tank', ['oxygen_tank'],
         'Hit the valve (or catch it in an explosion): it shoots off and bounces around for 2.5 seconds, ramming every '
         'zombie on its way (4 damage each), then bursts. Hit 3 zombies with one tank for the Pinball Wizard achievement.',
         None),
    ]),
    ('water', 'Water + electricity', 'var(--blue)', 'A wet zombie takes double electric damage and stays shocked twice as '
     'long. Water also puts out burning zombies: do not soak the ones you set on fire.', [
        ('How to soak them', ['water_pistol', 'garden_hose', 'water_flask', 'sprinkler'],
         'Water Pistol and Garden Hose: wet for 10 seconds. A splash of the Water Flask: 10 seconds, 3 blocks around. The '
         'Sprinkler soaks everything within 4 blocks every second. The buggy\'s Water Cannon: 10 seconds. A zombie '
         'standing in water is always wet.', None),
        ('Electric Fence + Sprinkler', ['electric_fence', 'sprinkler'],
         'The fence zaps whatever touches it twice a second: 3 damage and a short shock to a zombie. Next to a sprinkler '
         'the zombies are always wet: 6 damage every zap. Survivors only get a small shock. Right click the fence to '
         'switch it on or off.', None),
        ('Garden Hose + Electric Bomb', ['garden_hose', 'electric_bomb'],
         'The Electric Bomb shocks every zombie within 4.5 blocks, 7 blocks if it lands in water: 3 damage and 2.5 seconds '
         'of shock, both doubled on wet zombies.', None),
        ('Water Pistol + Taser Gun', ['water_pistol', 'taser_gun'],
         'The taser paralyses a zombie for 3 seconds. Soaked, it stays paralysed 6 seconds and takes double damage.', None),
        ('Water Cannon + Electric Aura', ['rusty_buggy'],
         'Two buggy modules that love each other: the Water Cannon soaks the zombies, the Electric Aura (every 2 seconds, '
         '10 blocks around the buggy) then hits them twice as hard.', None),
    ], ),
    ('frost', 'Freeze & shatter', 'var(--blue)', 'Frost builds up on a zombie until it is frozen solid for 3 seconds. A '
     'frozen zombie takes 50% more damage from melee hits.', [
        ('Freeze, then hit', ['freeze_blaster', 'baseball_bat'],
         'The Freezing Blaster adds frost with every puff of nitrogen. Once the zombie is frozen, switch to your strongest '
         'melee weapon. Keep 3 zombies frozen at once for the Ice Age achievement.', None),
        ('Frost mod', ['ice_pack'],
         'A melee weapon with the Frost mod adds a big chunk of frost on half of your hits: three of them freeze a zombie. '
         'On the Hockey Stick, every puck freezes a common zombie at once, even after a bounce.', None),
        ('Stay warm', ['hot_soup', 'instant_noodles', 'hot_chocolate'],
         'Frost works on you too. Hot Soup (30 s), Instant Noodles (20 s) and Hot Chocolate (45 s) keep you warm: no '
         'frost while it lasts.', None),
    ]),
    ('lures', 'Lures', 'var(--yellow)', 'Zombies walk to noise and light. Pull a horde away from you, or into a trap. '
     'Bosses never fall for it.', []),
    ('traps', 'Traps & gadgets', 'var(--green)', 'Things to place, throw and switch on before the horde arrives.', []),
    ('tricks', 'Did you know?', 'var(--purple)', 'Small things that make a big difference.', []),
]
# lures: (icon, name, how far, how long)
LURES = [
    ('sound_decoy', 'Sound Decoy (thrown)', '16 blocks', '3 s'),
    ('portable_speaker', 'Portable Speaker (placed)', '20 blocks', '15 s'),
    ('flare', 'Flare (thrown, also lights up)', '32 blocks', '20 s'),
    ('birthday_cake', 'Birthday Cake (when you place it)', '20 blocks', '10 s'),
    ('fireworks', 'Fireworks (where the rocket bursts)', '16 blocks', '4 s'),
    ('air_horn', 'Air Horn (zombies within 7 blocks are stunned instead)', '7 to 32 blocks', '3 s'),
    ('rusty_buggy', 'Buggy Warning Lights module', '25 blocks', 'while installed'),
]
LURES_NOTE = ('Firefighter zombies put flares out with their water jet, and the Warden\'s whistle switches off fences and '
              'gadgets around him for 15 seconds.')
LURE_COMBOS = [
    ('Flare + Barbed Wire', ['flare', 'barbed_wire'],
     'Throw a flare behind a line of barbed wire: every zombie within 32 blocks walks through it, slowed down and hurt '
     'every second.', None),
    ('Air Horn + Fan Propeller', ['air_horn', 'fan_propeller'],
     'Call the horde with the horn, then switch the fan on: they are blown far away. Even better near a cliff.', None),
]
# traps & gadgets: (icon, name, text)
TRAPS = [
    ('light_projector', 'Light Projector', 'Right click to switch it on. Zombies in its 11 block beam slow down, then catch '
                                           'fire after 4 seconds.'),
    ('fan_propeller', 'Fan Propeller', 'Right click: an 8 second storm that blows zombies far away. Push them off a cliff '
                                       'or onto a trap.'),
    ('motion_sensor', 'Motion Sensor', 'Marks every zombie passing within 12 blocks and beeps to warn you, even when you '
                                       'are 64 blocks away.'),
    ('banana', 'Banana Peel', 'Eat a banana, keep the peel. Throw it at a zombie or drop it on its path: it slips, takes '
                              '2 damage and stays down for 2.5 seconds.'),
    ('bowling_ball', 'Bowling Ball', '6 damage on impact, then it rolls on and knocks down every zombie on its way. Five '
                                     'at once: STRIKE!'),
    ('shopping_cart', 'Shopping Cart', 'Hit it to shove it into the horde: the faster it goes, the harder it rams.'),
    ('net_launcher', 'Net Launcher', 'Pins a zombie to the ground for 3 seconds (a boss for 1 second).'),
    ('unstable_floor', 'Unstable Floor', 'Collapses under anyone who steps on it, zombies included, and the cracks spread '
                                         'to the next blocks. It rebuilds after a minute.'),
    ('glue_puddle', 'Glue Puddle', 'Zombies in it barely move (bosses are only slowed). It dries after 30 seconds.'),
    ('barbed_wire', 'Barbed Wire', 'Slows zombies a lot and hurts them every second; survivors are only slowed. It wears '
                                   'out as they cross it.'),
]
# did you know: (icon, title, text)
TRICKS = [
    ('ninja_helmet', 'Sneak past the Blind', 'The Blind hunt by ear and never notice a survivor who sneaks. Sprinting is '
                                             'heard 14 blocks away, a melee hit 8, a weapon\'s right click 20.'),
    ('barricade', 'Bashing', 'A zombie stuck in front of a barricade, weak glass or furniture soon starts bashing it. The '
                             'Lumberjack and the Zomboni smash through at once.'),
    ('fire_axe', 'Fire Axe', 'One hit smashes a barricade or a weak glass block (they take 4 and 3 hits otherwise).'),
    ('flashlight', 'Flashlight', 'Its beam dazzles and pushes back Night Creepers and the Blind, but it makes noise.'),
    ('fire_extinguisher', 'Doused', 'A Firefighter zombie\'s jet soaks you: your flamethrower and lighter will not light '
                                    'for 4 seconds.'),
    ('chewing_gum', 'Chewing Gum', 'Your next melee hit glues the zombie in place for 2 seconds.'),
    ('spicy_chili', 'Spicy Chili', 'Your next left click breathes fire on the zombies in front of you.'),
    ('lucky_coin', 'Lucky Coin', 'Keep it in your inventory: 35% chance of a bonus drop from every zombie you kill.'),
    ('combat_umbrella_open', 'Combat Umbrella', 'Open, it slows your fall like a small parachute.'),
    ('shopping_crate', 'Thrown furniture', 'Carry a piece of furniture and attack: it hits for 3 damage plus 2 per weight '
                                           'point.'),
]

# ------------------------------------------------------------------------------------------------ towns & radio
# Read in the code on 08/10/2026 (towns/Towns.ts, towns/TownRadio.ts, status/InfectionMonitor.ts, spawning/SpawnDirector.ts).
TOWNS_INTRO = ('Five kinds of towns are scattered across the world, each with its own buildings, loot and dangers. Your '
               'Zombie Guidebook is also a radio that leads you to them.')
# town key -> what you find there (zombie_structures/buildings/<town>)
TOWN_TEXTS = {
    'haven_hill': 'A walled settlement on the hills: council house, infirmary, workshop, pantry and houses behind the '
                  'palisade.',
    'ashford': 'The ruins of a city: an abandoned apartment building, a police station and a looted supermarket.',
    'pinecrest': 'A village in the pines with its fire station, a roadside motel and a school.',
    'greywater': 'A flooded town where nature took over: overgrown towers of 6 and 8 floors and an old gas station.',
    'verdance': 'A modern town: a 10 floor white tower, a museum and an airfield hangar.',
}
RADIO_HOW = [
    ('Hold the guidebook', 'Hold the Zombie Guidebook in your main hand: the compass on its cover points to the nearest town '
                           'you have not discovered yet, and the action bar shows the signal, the town and the distance.'),
    ('Read the signal', 'The closer you get, the more bars light up: 4 bars under 250 m, 3 under 600 m, 2 under 1000 m, '
                        '1 beyond. "Weak signal" with a distance: the radio hears a town there but does not know which '
                        'one yet.'),
    ('Discover the town', 'Walk within 72 blocks of its centre. The monitor next to your left hand shows TOWN DISCOVERED '
                          'with the name of the town, with a little jingle.'),
    ('Wait for the next one', 'Right after a discovery the radio loses the signal for about 3 minutes: the needle spins and '
                              'the bar shows "Weak signal". Then it points to the next town you have not found yet.'),
]
TOWN_FACTS = [
    ('More zombies', 'Inside a town up to 10 zombies roam around you by day and 18 at night (4 and 10 in the wild). Town '
                     'zombies like Riot Cops, Firefighters and Mailmen are twice as common there, and the elite Tanks only '
                     'walk the streets of a town at night.'),
    ('Loot', 'Loot chests, searchable trash cans, boxes and bags (they restock after 5 minutes) and furniture in every '
             'house.'),
    ('Manholes', 'Zombies climb out of the manholes in the streets while you are around. Right click one with duct tape to '
                 'seal it for good.'),
    ('Elevators', 'The tall buildings have elevator pads: jump to go up, sneak to go down, right click for the list of '
                  'floors. Zombies cannot use them.'),
]
