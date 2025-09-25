# ================================================================= #
# Dialog Definitions                                                #
# ================================================================= #

dialog stranger_main
    say "Heh heh heh... Welcome, stranger."
    option "I'd like to see what you have for sale."
        dialog shop_menu
            shop stranger
            say "You have {gold} gold. What would you like to do?"
            option "Buy a healing potion"
                buy 1 healing_potion from stranger
                start dialog shop_menu
            end option
            option "Buy a large healing potion"
                buy 1 large_healing_potion from stranger
                start dialog shop_menu
            end option
            option "Nevermind, I'm done trading."
                start dialog stranger_main
            end option
        end dialog
        start dialog shop_menu
    end option
    option "Goodbye."
        say "Come back anytime!"
    end option
end dialog

dialog a_grizzled_old_hermit_main
    say "The hermit rasps, 'I've seen many things in my time. The darkness here is not to be trifled with.'"
    option "Tell me a tale."
        say "'If you seek knowledge, I might have a tale or two to share.'"
    end option
    option "Goodbye."
        say "'Be careful out there.'"
    end option
end dialog

dialog a_spectral_merchant_main
    say "The merchant offers, 'A rare artifact for a handful of gold? Or perhaps... a hint?'"
    option "What kind of hint?"
        say "'The walls themselves have secrets. Look closely.'"
    end option
    option "Goodbye"
        say "'Farewell... for now.'"
    end option
end dialog

dialog a_lost_adventurer_main
    say "The adventurer groans, 'I thought I could handle this dungeon... but I was wrong.'"
    if has healing_potion
        say "'If you find any healing potions, please... I need them more than you do.'"
    end
    option "Hang in there."
        say "'I'll try...'"
    end option
end dialog

dialog grumpy_guard_main
    say "Hmph. Another adventurer..."
    option "Are you the one offering a quest?"
        if quest any_foe_i is not_started
            say "The monsters in these tunnels have been getting bolder. Clear out 5 enemies, any enemies will do. Are you interested?"
            option "accept quest"
                set quest any_foe_i to active
                say "Quest 'Any Foe I' accepted!"
            end option
            option "decline"
                say "Hmph. Suit yourself."
            end option
        end
        if quest any_foe_i is active
            say "Still haven't dealt with those monsters? You've defeated {any_foe_i_current_count} out of 5 so far."
        end
        if quest any_foe_i is complete_ready
            say "You've proven yourself! You defeated enough enemies."
            option "turn in any foe i"
                set quest any_foe_i to completed
                increase stat gold by 50
                increase stat xp by 25
                give 1 small_backpack
                say "Thanks for your help with those monsters. The tunnels are a bit safer now."
            end option
        end
        if quest any_foe_i is completed
            say "Thanks for your help with those monsters. The tunnels are a bit safer now."
        end
    end option
    option "Goodbye."
        say "'Watch yourself.'"
    end option
end dialog

dialog veteran_explorer_main
    say "The dungeon never truly ends, does it?"
    if quest any_foe_i is completed
        option "I'm looking for more work."
            if quest any_foe_ii is not_started
                say "You handled the early threats well, I heard. The deeper parts of the dungeon need clearing. Eliminate 10 more enemies. Are you up to the challenge?"
                option "accept quest"
                    set quest any_foe_ii to active
                    say "Quest 'Any Foe II' accepted!"
                end option
                option "decline"
                    say "A wise choice, perhaps. The risks are greater now."
                end option
            end
            if quest any_foe_ii is active
                say "Keep fighting, adventurer! You've defeated {any_foe_ii_current_count} out of 10 so far."
            end
            if quest any_foe_ii is complete_ready
                say "You've faced many foes and emerged victorious!"
                option "turn in any foe ii"
                    set quest any_foe_ii to completed
                    increase stat gold by 100
                    increase stat xp by 75
                    give 1 chainmail_tunic
                    say "Well done, warrior. Your efforts have made a significant impact."
                end option
            end
            if quest any_foe_ii is completed
                say "Well done, warrior. Your efforts have made a significant impact."
            end
        end option
    else
        say "You seem too green for my tasks. Perhaps assist the guard first?"
    end
    option "Farewell."
        say "'May your path be safe.'"
    end option
end dialog

dialog sobbing_woman_main
    say "Oh, woe is me! My wedding is ruined!"
    option "What's wrong?"
      if quest the_unfit_bridesmaid is not_started
        say "My bridesmaid... she's not fit for the job! Please, can you find the one who is clearly not supposed to be a bridesmaid? I'll reward you handsomely."
        option "accept quest"
          set quest the_unfit_bridesmaid to active
          say "Quest 'The Unfit Bridesmaid' accepted!"
        end option
        option "decline"
          say "Oh, what will I do?"
        end option
      end
      if quest the_unfit_bridesmaid is active
        say "Have you found the... unfit bridesmaid yet? Please hurry!"
      end
      if quest the_unfit_bridesmaid is complete_ready
        say "You found him! Oh, thank you, thank you! Please, let me reward you."
        option "turn in The Unfit Bridesmaid"
          set quest the_unfit_bridesmaid to completed
          increase stat gold by 150
          increase stat xp by 200
          give 1 enchanted_cloak
          say "You've saved my wedding! Thank you, brave adventurer."
        end option
      end
      if quest the_unfit_bridesmaid is completed
          say "Thank you again for your help!"
      end
    end option
    option "I can't help you."
        say "..."
    end option
end dialog

dialog a_man_in_a_dress_main
  say "Uh... I can explain."
  if quest the_unfit_bridesmaid is active
    set quest the_unfit_bridesmaid to complete_ready
  end
  option "You don't have to."
    say "Thanks..."
  end option
end dialog