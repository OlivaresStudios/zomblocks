"""Hand-written boss pages (English, for players: no technical words). Every number was read in the add-on code
(zombie_BP/src/zombies/types/*.ts) on 05/10/2026: re-check it when a boss changes. Health, speed, team and loot are
NOT written here: the build reads them from the add-on.

attacks: (name, what it does, damage label)
takes:   how much of a hit it really takes (armour, shields...)
phases:  optional (title, text) blocks
strategy: list of tips
"""

BOSSES = {
    'zombie_warden': dict(
        lead='The prison warden, 1.7 times bigger than a zombie. He stuns you with his baton, shuts down every gadget '
             'and electric fence around him and throws itchy gas at anyone who keeps their distance.',
        attacks=[
            ('Baton strike', 'A heavy swing (3.3 blocks) that stuns you for 1.5 s.', '9 dmg'),
            ('Lockdown', 'Blows his whistle: every gadget within 14 blocks (decoys, sensors, projectors...) stops for '
                         '15 s and every powered electric fence is switched off. At most every 20 s.', 'no dmg'),
            ('Itchy gas', 'Throws a gas canister 4 to 14 blocks away. The cloud lasts 6 s (3 blocks wide), blinds you '
                          'for 3 s and slows you down hard for 4 s. At most every 8 s.', '1 dmg/s'),
            ('Call the team', 'Whistles for 2 team members every 27 s (never more than 6 around him).', 'x2'),
        ],
        takes='Normal damage: no armour. His bite can infect you.',
        strategy=['Do not build your defence on traps or gadgets: his lockdown switches them off.',
                  'Stay close enough to avoid the gas, but step back after each baton swing: the stun is short.',
                  'Kill the Riot Cops first, their shields block your shots.'],
    ),
    'zombie_zombot': dict(
        lead='A giant robot zombie, about 5 blocks tall. It slams the ground, sweeps everything in front of it and '
             'roars so hard that everyone around is blown away.',
        attacks=[
            ('Ground slam', 'Smashes the floor 2.5 blocks in front of it: everyone within 5 blocks is hit and thrown '
                            'in the air.', '14 dmg'),
            ('Sweep', 'A very wide swing (5.8 blocks) that hits every survivor in front of it at once and knocks '
                      'them far back.', '10 dmg'),
            ('Roar', '4 shock waves in a row: every survivor within 10 blocks is pushed away and the screen shakes. '
                     'Used from up to 16 blocks.', 'push'),
            ('Call the team', 'Calls 2 team members every 27 s (never more than 6 around it).', 'x2'),
        ],
        takes='Its metal plates absorb 40% of every hit (it takes 60%), but explosions deal 120%. It never infects.',
        strategy=['Deal with its team first: the Linebacker and the Pole Vaulter rush you while it slams.',
                  'Keep moving sideways: the sweep covers a huge arc in front of it, not behind.',
                  'Save your explosives (Boom Launcher, Virus Bombs, Explosive Virus Barrel) for it: they hit it '
                  'twice as hard as your melee weapons.'],
    ),
    'zombie_panzer': dict(
        lead='A zombie in a mech suit, about 4 blocks tall, with a rocket launcher, a grappling claw and a jetpack. '
             'It fights from every distance.',
        attacks=[
            ('Rocket salvo', 'Fires 3 rockets in a row from 4 to 24 blocks away. Each one explodes (3 blocks wide).',
             '7 dmg each'),
            ('Grappling claw', 'From 2.5 to 9 blocks: the claw pulls you to it, then it punches you.', '8 dmg'),
            ('Jetpack slam', 'Flies to you from 5 to 16 blocks away and crashes down: everyone within 4 blocks is hit '
                             'and thrown back.', '10 dmg'),
            ('Call the team', 'Calls 2 team members every 27 s (never more than 6 around it).', 'x2'),
        ],
        takes='The suit absorbs 45% of every hit (it takes 55%, with sparks), but explosions deal 140%. It never '
              'infects.',
        strategy=['There is no safe distance: rockets far, claw mid-range, jetpack in between. Use cover against '
                  'the rockets.',
                  'Explosives are by far the best answer to its armour.',
                  'When it lifts off with its jetpack, run sideways: the landing hits a 4 block circle.'],
    ),
    'zombie_mega_mascot': dict(
        lead='A giant inflatable bear (1.7 times bigger than the mascot zombie) that bumps you with its belly and '
             'bounces on you. Pierce it and it deflates.',
        attacks=[
            ('Belly bump', 'A big push with its belly (3.9 blocks) that sends you flying.', '7 dmg'),
            ('Bounce', 'Jumps on you from 3 to 11 blocks away: everyone within 5 blocks of the landing is hit.',
             '9 dmg'),
            ('Call the team', 'Calls 2 team members every 27 s (never more than 6 around it).', 'x2'),
        ],
        phases=[('Inflated', 'Projectiles pierce it: every arrow, dart or pellet deals double damage and makes it leak.'),
                ('Deflated (below half health)', 'It deflates for good: it is slowed down and takes 50% more damage '
                                                 'from everything. Its boss bar shows droopy balloons.')],
        takes='Normal damage, x2 from projectiles while inflated, x1.5 from everything once deflated. It never infects.',
        strategy=['Open with ranged weapons (Slingshot, Dart Launcher, Paintball Rifle): every shot counts double.',
                  'Once it has deflated, switch to your best melee weapon and finish it.',
                  'Watch the bounce: move out of the landing spot as soon as it jumps.'],
    ),
    'zombie_charger': dict(
        lead='A brute with a huge armoured arm (1.9 times bigger than a zombie). It charges in a straight line and '
             'pins survivors against the walls.',
        attacks=[
            ('Arm smash', 'Slams its armoured arm 2.4 blocks in front of it: everyone within 4.6 blocks is hit.',
             '12 dmg'),
            ('Charge', 'From 6 to 22 blocks away, it rushes in a straight line and tackles everyone in its path. '
                       'At most every 7 s.', '11 dmg'),
            ('Call the team', 'Calls 2 team members every 27 s (never more than 6 around it).', 'x2'),
        ],
        phases=[('Stunned', 'If its charge ends in a wall, it is stunned for 3.5 s and takes double damage.')],
        takes='Its arm absorbs 25% of every hit (it takes 75%), x2 while stunned. It never infects.',
        strategy=['Stand in front of a wall when it charges and jump aside at the last moment: it crashes and is '
                  'stunned.',
                  'Hit it as hard as you can during the stun: every hit counts double.',
                  'Do not stay in a long corridor with it: the charge covers 22 blocks.'],
    ),
    'zombie_mother_bloater': dict(
        lead='A giant bloater (1.5 times bigger) that gives birth to her brood and spits slime. Four slime sacs on '
             'her body soak up the damage.',
        attacks=[
            ('Belly slam', 'Slams the ground 1.5 blocks in front of her: everyone within 4.5 blocks is hit and '
                           'pushed back.', '9 dmg'),
            ('Slime volley', 'Spits 3 slime globs at once, from 5 to 18 blocks away. At most every 4.5 s.', 'slime'),
            ('Give birth', 'Calls 2 members of her brood every 27 s (never more than 6 around her).', 'x2'),
        ],
        phases=[('Slime sacs (4)', 'Each sac takes 75% of every hit for her. A sac bursts after about 60 damage; her '
                                   'boss bar shows the sacs left.'),
                ('Death burst', 'When she dies, she swells up and bursts: 3 damage and a strong push within 6 blocks, '
                                'slowness for 4 s and a slime pool on the ground.')],
        takes='25% of every hit while she has sacs, then full damage. Her bite can infect you.',
        strategy=['Burst the 4 sacs first: until then she barely takes any damage.',
                  'Keep the Parasites away from you, they jump on you while she slams.',
                  'When she starts to swell up, step back: the burst throws you away and slows you.'],
    ),
    'zombie_conductor': dict(
        lead='The maestro of the horde (1.7 times bigger than a zombie). He conducts every zombie within 16 blocks '
             'and hides behind 3 music stands.',
        attacks=[
            ('Baton strike', 'A quick strike with his baton (4 blocks).', '9 dmg'),
            ('Allegro', 'For 6 s, every zombie within 16 blocks rushes: faster and stronger.', 'buff'),
            ('Adagio', 'For 6 s, every zombie within 16 blocks holds the line: slower but much more resistant. '
                       'You are slowed down too.', 'buff'),
            ('Call the team', 'Calls 2 team members every 27 s (never more than 6 around him).', 'x2'),
        ],
        phases=[('Music stands (3)', 'He places 3 music stands around him. While one is standing, he takes only 30% '
                                     'damage. When a stand breaks, the others are protected for 6 s.'),
                ('Enraged', 'Once the 3 stands are broken, he takes full damage but plays allegro only.')],
        takes='30% of every hit while a music stand stands, then full damage. He never infects.',
        strategy=['Break his 3 music stands first, one every 6 s.',
                  'During the adagio, fall back: the horde is tough but slow.',
                  'Once he is enraged, stay away from the horde and focus him.'],
    ),
    'zombie_slender': dict(
        lead='Mister Lanky, a very tall and thin shadow (3 blocks). He freezes when you look at him and blinks closer '
             'when you do not. He splits into shadow twins and grabs you from afar.',
        attacks=[
            ('Claw', 'A long claw strike (3.4 blocks): darkness for 3 s and nausea for 5 s.', '10 dmg'),
            ('Endless arm', 'From 3.5 to 7.5 blocks: his arm stretches and grabs you. At most every 6 s.', 'grab'),
            ('Shadow twins', 'Every 30 s he splits into 3 shadow twins that look exactly like him. They only scare '
                             '(darkness) and vanish at the first hit.', 'fake'),
            ('Call the team', 'Calls 2 team members every 27 s (never more than 6 around him).', 'x2'),
        ],
        phases=[('Watched', 'While you look straight at him, he cannot move.'),
                ('Unwatched', 'When you look away, he blinks (teleports) closer, if he is more than 6 blocks away.')],
        takes='Normal damage. The twins vanish at the first hit. His bite can infect you.',
        strategy=['Keep your eyes on him: he cannot move while you stare at him.',
                  'Hit the twins once each: the fakes vanish, the real one stays.',
                  'Play with friends: one keeps staring at him, the others attack.'],
    ),
}
