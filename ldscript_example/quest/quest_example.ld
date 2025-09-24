# Example of a quest

quest find_artifact "The Lost Artifact"
    description "An ancient artifact is hidden in the ruins."
    state inactive
end quest

say "Checking quest status for the first time."
if quest find_artifact is inactive
    say "The 'Find the Lost Artifact' quest is inactive."
end
if quest find_artifact is active
    say "The 'Find the Lost Artifact' quest is active."
end

say "Activating the quest now."
set quest find_artifact to active

say "Checking quest status for the second time."
if quest find_artifact is inactive
    say "This should not be printed."
end
if quest find_artifact is active
    say "The 'Find the Lost Artifact' quest is now active."
end
