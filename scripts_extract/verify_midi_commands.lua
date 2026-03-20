-- Reaper Script: Verify MIDI Commands
-- Verifică ce comenzi MIDI sunt disponibile

local reaper = reaper

function main()
    reaper.ShowConsoleMsg("\n=== VERIFICĂ COMENZI MIDI ===\n\n")
    
    -- Comenzi de verificat
    local commands = {
        "_EXTRACTMIDI1",
        "_XSHRWARE_EXTRACTMIDI",
        "_SWS_LISTENMIDICC",
        "_ TrackExtSendToMIDIFile",
        "_GITHUB_REAPER_EXTRACTMIDI",
        "_ENVELOPE_EXTRACTMIDI",
    }
    
    reaper.ShowConsoleMsg("Verific comenzi:\n")
    
    for i, cmd in ipairs(commands) do
        local cmd_id = reaper.NamedCommandLookup(cmd)
        if cmd_id and cmd_id ~= 0 then
            reaper.ShowConsoleMsg("  ✓ " .. cmd .. " = " .. cmd_id .. "\n")
        else
            reaper.ShowConsoleMsg("  ✗ " .. cmd .. " = NOT FOUND (0)\n")
        end
    end
    
    -- Listează toate comenziile care conțin "MIDI" sau "EXTRACT"
    reaper.ShowConsoleMsg("\nToate comenziile cu 'MIDI' sau 'EXTRACT':\n")
    
    -- Folosim EnumCommands din ReaPack dacă e disponibil
    -- Sau listăm manual cele mai comune
    local common_commands = {
        "_EXTRACTMIDI1",
        "_EXTRACTMIDI2",
        "_EXTRACTMIDI3",
        "_EXTRACTMIDI4",
        "_EXTRACTMIDI5",
        "_EXTRACTMIDI6",
        "_EXTRACTMIDI7",
        "_EXTRACTMIDI8",
        "_EXTRACTMIDI9",
        "_EXTRACTMIDI10",
    }
    
    for i, cmd in ipairs(common_commands) do
        local cmd_id = reaper.NamedCommandLookup(cmd)
        if cmd_id and cmd_id ~= 0 then
            reaper.ShowConsoleMsg("  ✓ " .. cmd .. " = " .. cmd_id .. "\n")
        end
    end
    
    reaper.MB(
        "Verifică consola (F10) pentru rezultate.\n\n" ..
        "Dacă niciuna nu funcționează, ai nevoie de ReaPack/ReaTeam Scripts.",
        "Verificare finalizată",
        0
    )
end

main()
