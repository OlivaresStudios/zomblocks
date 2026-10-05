"""Hand-written texts of the "Weapon mods & Fabricator" page (rules read in zombie_BP/src/workshop/Fabricator.ts,
src/weapons/mods/*.ts and src/items/Wrench.ts on 05/10/2026). Mods, parts, costs, combos and prices come from the add-on."""

INTRO = ('The Fabricator is a workbench that puts a mod on a melee weapon: an electric cable, poison leaves, a lighter, '
         'an ice pack or a box of nails. The mod is drawn on the weapon itself and gives its hits a chance to shock, '
         'poison, burn, freeze or stun. Some weapon + mod pairs are signature combos with a bonus of their own.')

HOW_TO = [
    ('Place it', 'Hold the Fabricator item and right click a block: the workbench appears, with a welding arm and a '
                 'projector. Sneak + right click it with a wrench to pack it up again.'),
    ('Open the panel', 'Right click the workbench with a melee weapon in your hand: an amber hologram opens above it, '
                       'one card per mod, plus Reinforce and Remove Mod, with your weapon turning in 3D.'),
    ('Pick a card', 'Right click: next card. Punch: previous card. The card shows the cost and whether you have the parts.'),
    ('Build', 'Sneak + punch: the welding arm works for 2 seconds, then the parts are used up and the mod is on your weapon '
              '(its name and description change).'),
    ('Change or remove', 'A weapon holds one mod: a new one replaces the old one. Removing a mod is free, but the parts '
                         'are lost.'),
    ('Build blocks', 'Right click the workbench with anything else in your hand: the cards are blocks made from parts '
                     '(Glue Puddle, Sprinkler, Electric Fence, Barbed Wire, bombs, flares, shurikens). Sneak + punch builds them and they '
                     'go to your inventory.'),
    ('Shuriken mods', 'Right click it with shurikens in your hand: Electric, Toxic or Fire for up to 8 shurikens of the '
                      'stack (1 part + 2 scrap). Every hit shocks 2 s, poisons 5 s or sets on fire 4 s; a shuriken you '
                      'pick up again keeps its mod.'),
    ('Close', 'The panel closes when you walk away (6 blocks) or put the weapon away.'),
]

REINFORCE = ('Reinforce makes a weapon last longer: +50% durability per level, 3 levels, no change to its look. It stacks '
             'with the mod.')

WRENCH = ('Worn weapons are repaired with a wrench (3 scrap + 1 stick): right click it to choose a worn weapon. It uses '
          'up the wrench and 1 duct tape (2 if the weapon is more than half worn). Tank weapons (sprays, flamethrower...) '
          'are refilled with canisters instead.')
