# Test file for nested item properties

item elixir_of_strength
    type "consumable"
    effect_type "stat_boost"
    effect_value
        stat "attack_power"
        amount 2
    end effect_value
    description "A potent elixir that permanently increases your attack power."
    shop_price 250
end item

item simple_sword
    type "weapon"
    damage 10
end item
