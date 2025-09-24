# Example of a cutscene

define hero as "Sir Reginald"

cutscene intro
    say "A new adventure begins for {hero}."
    say "The mountains loom in the distance."
end cutscene

say "The story starts now."
play cutscene intro
say "The first chapter is over."
