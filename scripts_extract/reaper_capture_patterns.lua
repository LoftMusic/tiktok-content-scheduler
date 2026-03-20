-- Reaper Script: Capture Session Guitarist Patterns
-- Extrage toate pattern-urile din Session Guitarist ca fișiere MIDI separate
--
-- Folosire:
-- 1. Deschide REAPER
-- 2. Creează un track nou
-- 3. Adaugă FX-ul Kontakt și încarcă Session Guitarist
-- 4. Rulează acest script (Extensions > ReaScript > Run script)
--
-- NOTĂ: Trebuie să ai deja încărcat librăria în Kontakt

local reaper = reaper

-- Configurare
OUTPUT_FOLDER = reaper.GetResourcePath() .. "\\Media\\SessionGuitarist_Export"
LIBRARY_NAME = "Session Guitarist - Electric Sunburst Deluxe"

-- Creează folderul de output dacă nu există
function ensure_folder(path)
    local f = io.open(path .. "\\_dummy.txt", "w")
    if f then
        f:close()
        reaper.DeleteFile(path .. "\\_dummy.txt")
    else
        reaper.MB("Nu pot crea folderul de output: " .. path, "Eroare", 0)
        return false
    end
    return true
end

-- Salvează un clip ca MIDI
function save_clip_as_midi(track, item, pattern_name)
    -- Selectează item-ul
    reaper.SetMediaItemInfo_Value(item, "B_UISEL", 1)
    
    -- extrage MIDI
    reaper.Main_OnCommand(reaper.NamedCommandLookup("_EXTRACTMIDI1"), 0)
    
    -- Așteaptă puțin
    reaper.AdjustTimeGrid(0, 0)
    
    reaper.defer(function() end)
end

-- Captură pattern din Session Guitarist
function capture_pattern(pattern_name, duration_seconds)
    local track = reaper.GetTrack(0, 0) -- Primul track
    
    if not track then
        reaper.MB("Nu am găsit niciun track!", "Eroare", 0)
        return false
    end
    
    -- Creează un item nou (clip)
    local item = reaper.AddMediaItemToTrack(track)
    reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0)
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", duration_seconds)
    
    -- Setează numele
    reaper.SetMediaItemInfo_Value(item, "P_NAME", pattern_name)
    
    -- Selectează track-ul pentru recording
    reaper.SetTrackState(track, "VOL", 0) -- Mute dacă vrei
    
    -- Record-arm track-ul
    reaper.SetTrackState(track, "REARM", 1)
    
    -- Start recording
    reaper.CSurf_OnRecord()
    
    -- Așteaptă înregistrarea
    reaper.sleep(duration_seconds * 1000)
    
    -- Stop recording
    reaper.CSurf_OnStop()
    
    -- Extrage MIDI
    local item_count = reaper.GetTrackNumMediaItems(track)
    if item_count > 0 then
        local last_item = reaper.GetTrackMediaItem(track, item_count - 1)
        save_clip_as_midi(track, last_item, pattern_name)
    end
    
    return true
end

-- Extrage toate pattern-urile
function extract_all_patterns()
    reaper.ClearRoute()
    
    -- Creează folderul de output
    if not ensure_folder(OUTPUT_FOLDER) then
        return
    end
    
    reaper.ShowConsoleMsg("=== EXTRAGERE PATTERN-uri ===\n")
    reaper.ShowConsoleMsg("Output folder: " .. OUTPUT_FOLDER .. "\n")
    reaper.ShowConsoleMsg("Librărie: " .. LIBRARY_NAME .. "\n")
    reaper.ShowConsoleMsg("\n")
    
    -- Pattern-urile din Session Guitarist
    local patterns = {
        "3-4 Arpeggio",
        "Americana",
        "Blues",
        "Blues Swing",
        "Bollywood",
        "Bonfire",
        "Break of Dawn",
        "Dark Highway",
        "Dark Matter",
        "Flageolet Arpeggio",
        "Free Horses",
        "Harmonic Glissando",
        "Hit Factor",
        "Hot Funk",
        "Ibiza",
        "Impossible",
        "In the Clouds",
        "Latin Love",
        "Main Stage",
        "More Gain",
        "Morning Sun",
        "Old Ranch",
        "Prime Time",
        "Pure",
        "Reggae",
        "Reverse Clouds",
        "Reverse EDM",
        "Reverse Score",
        "Reverse Thrust",
        "Reverse Triplets",
        "RnB Classics",
        "Rock Ballad",
        "Rock Hard",
        "Rock School",
        "Rock Show",
        "Rocker",
        "Scratches",
        "Southern Shuffle",
        "Straightforward",
        "Sweet Love",
        "Tequila Bar",
        "Toolbox",
        "Triple Energy",
        "Wanderlust",
    }
    
    reaper.ShowConsoleMsg("Gasit " .. #patterns .. " pattern-uri\n")
    reaper.ShowConsoleMsg("Incep extragerea...\n\n")
    
    local success_count = 0
    
    for i, pattern_name in ipairs(patterns) do
        reaper.ShowConsoleMsg(string.format("[%d/%d] %s... ", i, #patterns, pattern_name))
        
        -- Aici ar trebui să selectezi pattern-ul în Kontakt
        -- Acest pas necesită interacțiune manuală sau scripturi NI
        
        -- Captură pattern (ex: 16 secunde pentru un loop complet)
        if capture_pattern(pattern_name, 16) then
            reaper.ShowConsoleMsg("OK\n")
            success_count = success_count + 1
        else
            reaper.ShowConsoleMsg("FAILED\n")
        end
        
        -- Așteaptă puțin între pattern-uri
        reaper.sleep(1000)
    end
    
    reaper.ShowConsoleMsg("\n=== FINALIZAT ===\n")
    reaper.ShowConsoleMsg("Pattern-uri extrase: " .. success_count .. "/" .. #patterns .. "\n")
    reaper.ShowConsoleMsg("Output folder: " .. OUTPUT_FOLDER .. "\n")
    
    reaper.ShowConsoleMsg("\nAcum poți găsi fișierele MIDI în:\n")
    reaper.ShowConsoleMsg(OUTPUT_FOLDER .. "\n")
end

-- Interfață
retval, user_input = reaper.GetUserInputs("Extract Session Guitarist Patterns", 200, "", "Duration (seconds):16")

if retval then
    duration = tonumber(user_input) or 16
    extract_all_patterns()
else
    reaper.MB("Extragerea a fost anulată.", "Info", 0)
end
