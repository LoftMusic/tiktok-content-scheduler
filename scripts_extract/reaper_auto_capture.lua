-- Reaper Script: Session Guitarist Extract v13 (Fără ReaPack)
-- Extrage MIDI folosind comenzi directe

local reaper = reaper

OUTPUT_FOLDER = "C:\\Users\\ASU\\.openclaw\\workspace\\scripts_extract\\session_guitarist_export"
PATTERN_DURATION = 4

function wait_seconds(seconds)
    local start = reaper.time_precise()
    while reaper.time_precise() - start < seconds do
        reaper.defer(function() end)
    end
end

function ensure_folder(path)
    local f = io.open(path .. "\\_test.txt", "w")
    if f then
        f:close()
        os.remove(path .. "\\_test.txt")
        return true
    else
        os.execute('cmd /c mkdir "' .. path .. '" 2>nul')
        f = io.open(path .. "\\_test.txt", "w")
        if f then
            f:close()
            os.remove(path .. "\\_test.txt")
            return true
        end
        return false
    end
end

function main()
    reaper.ShowConsoleMsg("\n=== EXTRACT MIDI v13 ===\n")
    
    -- 1. Creează folderul
    if not ensure_folder(OUTPUT_FOLDER) then
        reaper.MB("Eroare folder: " .. OUTPUT_FOLDER, "Eroare", 0)
        return
    end
    reaper.ShowConsoleMsg("[OK] Folder: " .. OUTPUT_FOLDER .. "\n")
    
    -- 2. Verifică track
    local track = reaper.GetTrack(0, 0)
    if not track then
        reaper.MB("Fără track!", "Eroare", 0)
        return
    end
    
    -- 3. Arm și record
    reaper.Main_OnCommand(reaper.NamedCommandLookup("_DYNTOGGLETRACKARM"), 0)
    reaper.CSurf_OnRecord()
    wait_seconds(PATTERN_DURATION)
    reaper.CSurf_OnStop()
    
    -- 4. Extrage MIDI folosind comanda din REAPER (nu ReaPack)
    -- Folosim comanda care extrage MIDI din clip
    local cmd_id = reaper.NamedCommandLookup("_EXTRACTMIDI1")
    reaper.ShowConsoleMsg("Comanda ID: " .. tostring(cmd_id) .. "\n")
    
    if cmd_id == 0 then
        -- Încearcă alta comandă
        reaper.ShowConsoleMsg("Încerc comanda alternativă...\n")
        
        -- Extrage MIDI din primul clip de pe track
        local item = reaper.GetTrackMediaItem(track, 0)
        if item then
            reaper.SetMediaItemInfo_Value(item, "B_UISEL", 1)
            
            -- Folosește _TrackExtSendToMIDIFile
            -- Sau _SWS_LISTENMIDICC
            reaper.Main_OnCommand(reaper.NamedCommandLookup("_XSHRWARE_EXTRACTMIDI"), 0)
            
            wait_seconds(2)
            
            reaper.MB(
                "Încearcă manual:\n\n" ..
                "1. Click dreapta pe clip → 'Item properties'\n" ..
                "2. Dă click pe 'Extract MIDI from item'\n" ..
                "3. Salvează în: " .. OUTPUT_FOLDER,
                "Extrage manual",
                0
            )
        end
    else
        reaper.Main_OnCommand(cmd_id, 0)
    end
    
    wait_seconds(2)
    reaper.MB("Finalizat!", "Info", 0)
end

main()
