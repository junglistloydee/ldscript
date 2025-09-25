# ================================================================= #
# Item Definitions                                                  #
# ================================================================= #

# --- SHIELDS ---
item wooden_shield
    name "wooden shield"
    type "shield"
    defense 3
    description "A basic wooden shield, light but offers some protection."
    price 10
end item

item iron_shield
    name "iron shield"
    type "shield"
    defense 7
    description "A solid iron shield, providing good protection against attacks."
    price 25
end item

item gleaming_shield
    name "gleaming shield"
    type "shield"
    defense 5
    description "A sturdy metal shield, offering good protection."
    price 20
end item

# --- ARMOR ---
item set_of_rusted_plate_armor
    name "set of rusted plate armor"
    type "armor"
    subtype "body_armor"
    defense 10
    description "Heavy, but rusty. Might still offer some protection."
    price 50
end item

item shimmering_cloak
    name "shimmering cloak"
    type "armor"
    subtype "cloak"
    defense 3
    description "A light cloak that seems to ripple like water, offering a small magical defense."
    price 20
end item

item leather_jerkin
    name "leather jerkin"
    type "armor"
    subtype "body_armor"
    defense 4
    description "A simple leather vest, better than nothing."
    price 15
end item

item chainmail_tunic
    name "chainmail tunic"
    type "armor"
    subtype "body_armor"
    defense 7
    description "A tunic made of interlocking metal rings, decent protection."
    price 30
end item

item hooded_cloak
    name "hooded cloak"
    type "armor"
    subtype "cloak"
    defense 2
    description "A simple cloth cloak with a hood, good for hiding."
    price 10
end item

item enchanted_cloak
    name "enchanted cloak"
    type "armor"
    subtype "cloak"
    defense 5
    description "A cloak woven with faint magic, providing decent protection."
    price 40
end item

item goblin-skin_vest
    name "goblin-skin vest"
    type "armor"
    subtype "body_armor"
    defense 2
    description "Crude, smelly, but might offer minimal protection."
    price 6
end item

item amulet_of_protection
    name "Amulet of Protection"
    type "armor"
    subtype "cloak"
    defense 1
    description "A silver amulet that provides a small but permanent boost to your defense."
    price 300
end item


# --- WEAPONS ---
item battle-worn_axe
    name "battle-worn axe"
    type "weapon"
    damage 14
    description "A sturdy axe with many notches, seen better days."
    price 20
end item

item wooden_sword
    name "wooden sword"
    type "weapon"
    damage 2
    description "A simple wooden sword. Better than your fists."
    price 5
end item

item ornate_longsword
    name "ornate longsword"
    type "weapon"
    damage 22
    description "A finely crafted longsword, sharp and gleaming."
    price 45
end item

item steel_sword
    name "steel sword"
    type "weapon"
    damage 20
    description "A well-balanced steel sword, sharp and deadly."
    price 40
end item

item great_halberd
    name "great halberd"
    type "weapon"
    damage 25
    description "A long polearm with a sharp blade, perfect for keeping enemies at bay."
    price 45
end item

item greatsword_of_shadows
    name "greatsword of shadows"
    type "weapon"
    damage 30
    description "A massive sword that seems to absorb light, its blade dark and menacing."
    price 100
end item

item enchanted_staff
    name "enchanted staff"
    type "weapon"
    damage 16
    description "A staff imbued with magical energy, capable of channeling spells."
    price 50
end item

item mystic_wand
    name "mystic wand"
    type "weapon"
    damage 12
    description "A slender wand that glows faintly, used for casting minor spells."
    price 25
end item

item chipped_sword
    name "chipped sword"
    type "weapon"
    damage 12
    description "A basic, worn sword. Better than nothing."
    price 15
end item

item heavy_iron_mace
    name "heavy iron mace"
    type "weapon"
    damage 18
    description "A blunt, heavy weapon that could crush bones."
    price 30
end item

item ancient_staff
    name "ancient staff"
    type "weapon"
    damage 14
    description "A gnarled wooden staff, pulsing faintly with magical energy."
    price 25
end item

item enchanted_crossbow
    name "enchanted crossbow"
    type "weapon"
    damage 22
    description "A finely crafted crossbow that fires bolts with deadly accuracy."
    price 40
end item

item poisoned_dagger
    name "poisoned dagger"
    type "weapon"
    damage 15
    description "A short blade with a faint green sheen. Looks dangerous."
    price 25
end item

item well-preserved_elven_bow
    name "well-preserved elven bow"
    type "weapon"
    damage 16
    description "An elegant bow, perfectly balanced. Requires arrows, but we'll ignore that for now!"
    price 30
end item

item ceremonial_dacian_falx
    name "ceremonial dacian falx"
    type "weapon"
    damage 16
    description "A curved sword, sharp and intimidating."
    price 35
end item

item shimmering_illusory_dagger
    name "shimmering, illusory dagger"
    type "weapon"
    damage 5
    description "Looks sharp, but feels insubstantial. Barely effective."
    price 10
end item

# --- KEYS ---
item rusty_key
    name "rusty key"
    type "key"
    key_type "rusty"
    description "An old, corroded iron key."
    price 20
end item

item silver_key
    name "silver key"
    type "key"
    key_type "silver"
    description "A beautifully crafted key, shining faintly."
    price 30
end item

item bone_key
    name "bone key"
    type "key"
    key_type "bone"
    description "A macabre key, intricately carved from a bone."
    price 10
end item

# --- CONSUMABLES ---
item healing_potion
    name "healing potion"
    type "consumable"
    effect_type "heal"
    effect_value 30
    description "A bubbling red liquid that smells faintly of mint."
    price 30
end item

item large_healing_potion
    name "large healing potion"
    type "consumable"
    effect_type "heal"
    effect_value 80
    description "Restores a large amount of health."
    price 60
end item

item super_healing_potion
    name "super healing potion"
    type "consumable"
    effect_type "heal"
    effect_value 200
    description "Restores a very large amount of health."
    price 120
end item

item vial_of_liquid_light
    name "vial of liquid light"
    type "consumable"
    effect_type "heal"
    effect_value 15
    description "A glowing vial containing a viscous, golden fluid."
    price 15
end item

item vial_of_tears_glowing_faintly
    name "vial of tears (glowing faintly)"
    type "consumable"
    effect_type "heal"
    effect_value 20
    description "A small vial filled with luminescent, salty liquid."
    price 20
end item

item dusty_bottle_of_fine_wine
    name "dusty bottle of fine wine"
    type "consumable"
    effect_type "flavor"
    description "A very old, probably spoiled, bottle of wine."
    price 5
end item

item bag_of_cursed_beans
    name "bag of cursed beans"
    type "consumable"
    effect_type "harm"
    effect_value 10
    description "They look delicious, but you feel a sense of dread."
    price 3
end item

item bag_of_endless_peanuts
    name "bag of endless peanuts"
    type "consumable"
    effect_type "flavor"
    description "Always full of peanuts. Not very nutritious."
    price 10
end item

item vial_of_unholy_water
    name "vial of unholy water"
    type "consumable"
    effect_type "harm"
    effect_value 5
    description "Dark and murky water. Smells faintly of brimstone."
    price 5
end item

item pouch_of_potent_smelling_salts
    name "pouch of potent smelling salts"
    type "consumable"
    effect_type "wake_up"
    description "A sharp, invigorating scent. Good for waking up stunned allies."
    price 10
end item

item elixir_of_strength
    name "Elixir of Strength"
    type "consumable"
    effect_type "stat_boost"
    effect_value "attack_power 2"
    description "A potent elixir that permanently increases your attack power."
    price 250
end item

item potion_of_power
    name "Potion of Power"
    type "consumable"
    effect_type "stat_boost"
    effect_value "attack_power 1"
    description "A shimmering potion that permanently increases your attack power."
    price 150
end item

item vitality_draught
    name "Vitality Draught"
    type "consumable"
    effect_type "stat_boost"
    effect_value "max_hp 10"
    description "A thick, red liquid that permanently increases your maximum HP."
    price 200
end item

# --- MISC ---
item gauntlet_of_strength
    name "gauntlet of strength"
    type "equipment"
    effect_type "strength_boost"
    effect_value 5
    description "A heavy gauntlet that makes you feel stronger."
    price 70
end item

item strange-looking_gem
    name "strange-looking gem"
    type "misc"
    description "It pulses with a faint, internal light."
    price 50
end item

item tattered_scroll
    name "tattered scroll"
    type "misc"
    description "Looks like ancient magic, but unreadable without knowledge."
    price 10
end item

item pouch_of_gold_coins
    name "pouch of gold coins"
    type "misc"
    description "A decent amount of gold. Good for... something."
    price 10
end item

item old_leather-bound_book
    name "old leather-bound book"
    type "misc"
    description "Full of forgotten lore, but difficult to read here."
    price 15
end item

item lockpick_set
    name "lockpick set"
    type "misc"
    description "Useful for small locks, but not sturdy dungeon doors."
    price 5
end item

item lantern_unlit
    name "lantern (unlit)"
    type "misc"
    description "A simple oil lantern. Needs oil and a spark."
    price 8
end item

item bag_of_rare_herbs
    name "bag of rare herbs"
    type "misc"
    description "A pungent mix of medicinal herbs. Does anyone have any papers?"
    price 15
end item

item mysterious_orb
    name "mysterious orb"
    type "misc"
    description "A smooth, dark orb that feels strangely warm."
    price 75
end item

item wand_of_minor_magic
    name "wand of minor magic"
    type "misc"
    description "A small wooden wand, humming faintly with low-level magic."
    price 40
end item

item collection_of_dried_fungi
    name "collection of dried fungi"
    type "misc"
    description "Various strange mushrooms, some edible, some not."
    price 3
end item

item broken_compass
    name "broken compass"
    type "misc"
    description "Its needle spins wildly, pointing in all directions."
    price 2
end item

item journal_with_unreadable_script
    name "journal with unreadable script"
    type "misc"
    description "The writing shifts and warps before your eyes."
    price 2
end item

item heavy_iron_lever
    name "heavy iron lever"
    type "misc"
    description "Too big to carry easily, but it might be useful somewhere."
    price 8
end item

item cursed_idol
    name "cursed idol"
    type "misc"
    description "A small, unsettling figurine that emanates cold."
    price 15
end item

item bag_of_marbles
    name "bag of marbles"
    type "misc"
    description "Just a bag of ordinary marbles. Why are they here?"
    price 1
end item

item miniature_clockwork_bird
    name "miniature clockwork bird"
    type "misc"
    description "A tiny, intricate metal bird that occasionally chirps."
    price 25
end item

item petrified_eyeball
    name "petrified eyeball"
    type "misc"
    description "A glassy eye, unnervingly realistic."
    price 30
end item

item singing_mushroom
    name "singing mushroom"
    type "misc"
    description "A mushroom that emits a soft, tuneful hum."
    price 10
end item

item stack_of_ancient_coins
    name "stack of ancient coins"
    type "misc"
    description "More valuable than common gold, possibly. Or just heavier."
    price 12
end item

item flawless_diamond
    name "flawless diamond"
    type "misc"
    description "Sparkles brilliantly, could be valuable."
    price 200
end item

item scroll_of_summon_whim
    name "scroll of 'Summon Whim'"
    type "misc"
    description "You have no idea what 'Summon Whim' means. Maybe it summons a whim?"
    price 25
end item

item vial_of_monster_blood
    name "vial of monster blood"
    type "misc"
    description "Thick and black, still faintly warm."
    price 8
end item

item bag_of_holding_small
    name "bag of holding (small)"
    type "misc"
    description "Feels empty, but heavier than it looks. Doesn't expand inventory *yet*."
    price 100
end item

item map_to_nowhere
    name "map to nowhere"
    type "misc"
    description "A detailed map, but all locations are fictional."
    price 5
end item

item broken_telescope
    name "broken telescope"
    type "misc"
    description "The lenses are shattered, but the brass is still good."
    price 15
end item

item shard_of_dark_crystal
    name "shard of dark crystal"
    type "misc"
    description "Absorbs all light around it. Feels cold."
    price 60
end item

item sphere_of_annihilation_dormant
    name "sphere of annihilation (dormant)"
    type "misc"
    description "A tiny black sphere. Best not to touch it too much."
    price 50
end item

item scroll_of_identify_object
    name "scroll of 'Identify Object'"
    type "misc"
    description "Perhaps this could reveal an item's true nature."
    price 30
end item

item mimic-tooth_necklace
    name "mimic-tooth necklace"
    type "misc"
    description "Made from the teeth of a mimic. You hope it's not still alive."
    price 20
end item

item spectral_lantern
    name "spectral lantern"
    type "misc"
    description "Emits light, but seems to pass through solid objects."
    price 30
end item

item chime_of_opening
    name "chime of opening"
    type "misc"
    description "A small bell. You wonder what it opens."
    price 45
end item

item glowing_mushroom
    name "glowing mushroom"
    type "misc"
    description "Radiates a soft, comforting light. Might be edible."
    price 10
end item

item pocket_sundial
    name "pocket sundial"
    type "misc"
    description "Useless underground, but finely crafted."
    price 5
end item

item cursed_coin
    name "cursed coin"
    type "misc"
    description "Feels cold and unlucky. Probably can't get rid of it."
    price 2
end item

item piece_of_chalk_magical
    name "piece of chalk (magical)"
    type "misc"
    description "Leaves glowing marks that slowly fade."
    price 15
end item

item set_of_skeleton_keys
    name "set of skeleton keys"
    type "misc"
    description "A set of master keys. Perhaps some locks aren't so simple."
    price 80
end item

item crystal_ball_cracked
    name "crystal ball (cracked)"
    type "misc"
    description "You see blurry, fleeting images when you look into it."
    price 25
end item

item vial_of_liquid_shadow
    name "vial of liquid shadow"
    type "misc"
    description "A swirling darkness in a bottle. Feels cold."
    price 70
end item

item golden_idol_of_a_forgotten_god
    name "golden idol of a forgotten god"
    type "misc"
    description "An ornate statue of a deity you've never heard of."
    price 150
end item

item piece_of_a_shattered_mirror_that_shows_glimpses_of_other_realms
    name "piece of a shattered mirror that shows glimpses of other realms"
    type "misc"
    description "You see impossible landscapes in its broken surface."
    price 40
end item

item perfectly_spherical_black_stone
    name "perfectly spherical black stone"
    type "misc"
    description "Feels unnaturally smooth and heavy."
    price 30
end item

item quill_pen_that_writes_by_itself
    name "quill pen that writes by itself"
    type "misc"
    description "When placed on paper, it scribbles nonsense rapidly."
    price 10
end item

item small_intricately_carved_wooden_box_empty
    name "small, intricately carved wooden box (empty)"
    type "misc"
    description "It feels like it should contain something important."
    price 10
end item

item piece_of_petrified_wood
    name "piece of petrified wood"
    type "misc"
    description "Heavy and hard, a remnant of a long-dead forest."
    price 5
end item

item strange_glowing_seed
    name "strange, glowing seed"
    type "misc"
    description "Pulsates with a soft, green light. Maybe plant it?"
    price 20
end item

item bundle_of_dried_flowers_with_a_faint_magical_aura
    name "bundle of dried flowers (with a faint magical aura)"
    type "misc"
    description "They smell faintly of forgotten spells."
    price 8
end item

item single_polished_fang
    name "single, polished fang"
    type "misc"
    description "Too large for any normal animal. From what beast?"
    price 25
end item

item rusted_musical_instrument
    name "rusted musical instrument"
    type "misc"
    description "A lute, but its strings are broken and it's covered in rust."
    price 10
end item

item set_of_weighted_dice
    name "set of weighted dice"
    type "misc"
    description "These always roll sixes. Cheating tools for a rogue."
    price 15
end item

item vial_of_concentrated_darkness
    name "vial of concentrated darkness"
    type "misc"
    description "A tiny bottle containing pure, unmoving blackness."
    price 50
end item

item single_large_feather_from_an_unknown_bird
    name "single, large feather from an unknown bird"
    type "misc"
    description "Soft and iridescent, unlike any bird you know."
    price 10
end item

item pouch_of_strange_metallic_dust
    name "pouch of strange, metallic dust"
    type "misc"
    description "It shimmers faintly. Possibly magical components."
    price 15
end item

item broken_locket_with_a_faded_portrait
    name "broken locket with a faded portrait"
    type "misc"
    description "You can barely make out the smiling face of a stranger."
    price 5
end item

item half-eaten_petrified_apple
    name "half-eaten, petrified apple"
    type "misc"
    description "Rock hard, but you can still see bite marks."
    price 2
end item

item small_buzzing_insect_trapped_in_amber
    name "small, buzzing insect trapped in amber"
    type "misc"
    description "The insect still vibrates faintly within its prison."
    price 20
end item

item set_of_arcane_symbols_etched_onto_bone_fragments
    name "set of arcane symbols etched onto bone fragments"
    type "misc"
    description "They seem to hum with a quiet energy."
    price 35
end item

item piece_of_solidified_dream
    name "piece of solidified dream"
    type "misc"
    description "It's translucent and wavers. You almost remember something."
    price 40
end item

item pair_of_enchanted_spectacles
    name "pair of enchanted spectacles"
    type "misc"
    description "Everything looks slightly sharper and more colorful through them."
    price 60
end item

item single_perfectly_preserved_rose_ancient
    name "single, perfectly preserved rose (ancient)"
    type "misc"
    description "Its petals are still vibrant, defying the ages."
    price 15
end item

item scroll_with_a_riddle
    name "scroll with a riddle"
    type "misc"
    description "A piece of parchment with a challenging enigma."
    price 5
end item

item small_unidentifiable_creature_in_a_jar
    name "small, unidentifiable creature in a jar"
    type "misc"
    description "It squarts with too many legs and eyes. Best left sealed."
    price 15
end item

item sphere_of_liquid_mercury
    name "sphere of liquid mercury"
    type "misc"
    description "A heavy, silvery ball of shifting liquid metal."
    price 80
end item

item small_iron_birdcage_empty_and_bent
    name "small, iron birdcage (empty and bent)"
    type "misc"
    description "It's rusty and clearly hasn't held a bird in ages."
    price 5
end item

item piece_of_a_shattered_stained-glass_window
    name "piece of a shattered stained-glass window"
    type "misc"
    description "Shows a fragment of a beautiful, religious scene."
    price 12
end item

item key_that_seems_to_constantly_shift_shape
    name "key that seems to constantly shift shape"
    type "misc"
    description "You can't quite grasp its form, let alone use it on a lock."
    price 20
end item

item miniature_statue_of_a_grotesque_beast
    name "miniature statue of a grotesque beast"
    type "misc"
    description "An unsettling carving, but strangely detailed."
    price 25
end item

item set_of_exquisite_silver_cutlery_bloodstained
    name "set of exquisite silver cutlery (bloodstained)"
    type "misc"
    description "Fine dining instruments, now tarnished by grim use."
    price 50
end item

item ring_that_whispers_ancient_secrets
    name "ring that whispers ancient secrets"
    type "misc"
    description "You hear faint, unintelligible whispers when you hold it to your ear."
    price 5
end item

item single_perfectly_symmetrical_leaf
    name "single, perfectly symmetrical leaf"
    type "misc"
    description "Seems to radiate natural perfection."
    price 10
end item

item small_plush_doll_with_button_eyes
    name "small, plush doll with button eyes"
    type "misc"
    description "It looks innocent, but you feel a prickle of unease."
    price 3
end item

item scroll_of_minor_illusion
    name "scroll of 'Minor Illusion'"
    type "misc"
    description "A basic spell scroll. Creates simple illusions."
    price 20
end item

item bag_containing_only_lint
    name "bag containing only lint"
    type "misc"
    description "Just pocket lint. Very disappointing."
    price 0
end item

item perfectly_normal_rock_that_seems_out_of_place
    name "perfectly normal rock (that seems out of place)"
    type "misc"
    description "It's just a rock. But why is it here?"
    price 0
end item

# --- BACKPACKS ---
item small_backpack
    name "small backpack"
    type "backpack"
    effect_type "increase_slots"
    effect_value 2
    description "A sturdy backpack that adds a few more inventory slots."
    price 60
end item

item medium_backpack
    name "medium backpack"
    type "backpack"
    effect_type "increase_slots"
    effect_value 4
    description "A spacious backpack that offers considerably more storage."
    price 120
end item

item large_backpack
    name "large backpack"
    type "backpack"
    effect_type "increase_slots"
    effect_value 6
    description "A huge backpack, almost magically large, for the serious adventurer."
    price 180
end item

# --- WINNING ITEMS ---
item amulet_of_yendor
    name "Amulet of Yendor"
    type "winning_item"
    description "A legendary artifact, shimmering with pure magical energy."
end item

item crown_of_eldoria
    name "Crown of Eldoria"
    type "winning_item"
    description "The crown of an ancient elven kingdom, radiating nobility."
end item

item scepter_of_the_serpent_king
    name "Scepter of the Serpent King"
    type "winning_item"
    description "A scepter topped with a coiled serpent, glowing faintly."
end item

item orb_of_divine_light
    name "Orb of Divine Light"
    type "winning_item"
    description "A pure orb of light, dispelling all shadows around it."
end item

item heart_of_the_mountain
    name "Heart of the Mountain"
    type "winning_item"
    description "A colossal crystal, pulsing with the very essence of the earth."
end item

item starfall_shard
    name "Starfall Shard"
    type "winning_item"
    description "A fragment of a fallen star, humming with cosmic power."
end item

item soulstone_of_the_ancients
    name "Soulstone of the Ancients"
    type "winning_item"
    description "A gem that seems to contain countless tiny souls, whispering silently."
end item

item codex_of_cosmic_understanding
    name "Codex of Cosmic Understanding"
    type "winning_item"
    description "An ancient book, its pages filled with the secrets of the universe."
end item

item chronos_crystal
    name "Chronos Crystal"
    type "winning_item"
    description "A crystal that subtly distorts time around it, causing a strange déjà vu."
end item

item blade_of_infinite_echoes
    name "Blade of Infinite Echoes"
    type "winning_item"
    description "A sword that hums with the memory of every blow it has ever struck."
end item