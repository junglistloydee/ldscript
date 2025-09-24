# Example of a dialog tree

define playerName as "Jules"
say "Welcome, {playerName}."

dialog blacksmith_convo
    say "Hello there, traveler. What brings you to my forge?"

    option "I'm looking for a weapon."
        say "I have many fine weapons. What kind are you looking for?"
        dialog weapon_choice
            option "A sword."
                say "An excellent choice."
            end option
            option "A bow."
                say "For a ranger, I see."
            end option
        end dialog
        start dialog weapon_choice
    end option

    option "Just looking around."
        say "Feel free to browse. Let me know if you see anything you like."
    end option

    option "I need a shield."
        say "A shield is a warrior's best friend. Here is my finest."
    end option
end dialog

start dialog blacksmith_convo

say "Your conversation with the blacksmith has ended."
