-- VST Batch Renderer for REAPER
-- Extract samples from BANDA CORRIDOS VST
-- Run via: reaper.exe -execscript "vst_batch_render.lua" "project.rpp"

-- Configuration
VST_PATH = "C:\\Program Files\\VSTPlugins\\BANDA CORRIDOS VST\\Banda Corridos Vst.vst3"
OUTPUT_DIR = "C:\\Samples\\BANDA_CORRIDOS_EXTRACTED"
SAMPLE_RATE = 44100
BIT_DEPTH = 24
RENDER_DURATION = 4.0 -- seconds per instrument

-- Get list of .mse files from instruments folder
function get_instruments()
    local instruments = {}
    local folder = "C:\\Program Files\\VSTPlugins\\BANDA CORRIDOS VST\\Banda Corridos Vst.instruments"
    
    local handle = reaper.EnumerateFiles(folder, 0)
    while handle do
        local filename = reaper.GetFileNameFromAnyPath(handle)
        if filename:match("%.mse$") then
            local name = filename:match("(.+)%.mse$")
            table.insert(instruments, name)
        end
        handle = reaper.EnumerateFiles(folder, handle)
    end
    
    table.sort(instruments)
    return instruments
end

-- Main render function
function main()
    reaper.ClearConsole()
    reaper.ShowConsoleMsg("VST Batch Renderer\n")
    reaper.ShowConsoleMsg("==================\n\n")
    
    local instruments = get_instruments()
    
    if #instruments == 0 then
        reaper.ShowConsoleMsg("ERROR: No .mse instruments found!\n")
        return
    end
    
    reaper.ShowConsoleMsg("Found " .. #instruments .. " instruments\n\n")
    
    -- Create output directory
    os.execute('mkdir "' .. OUTPUT_DIR .. '" 2>nul')
    
    -- Save current project
    local initial_proj = reaper.GetProjectName(0, "")
    
    for i, instrument in ipairs(instruments) do
        reaper.ShowConsoleMsg(string.format("[%d/%d] Processing: %s\n", i, #instruments, instrument))
        
        -- Create new project
        reaper.Main_OnCommand(40025, 0) -- New project
        
        -- Add track with VST
        reaper.Main_OnCommand(40001, 0) -- Add new track
        local track = reaper.GetTrack(0, 0)
        
        -- Add VST to track
        local take = reaper.GetActiveTake(track)
        if not take then
            take = reaper.TakeOnTrack(track, -1)
        end
        
        -- Insert VST FX
        reaper.TrackFX_AddByName(track, VST_PATH, false, -1)
        
        -- TODO: Set program (if VST supports program changes)
        -- This depends on the VST's parameter structure
        
        -- Set record arm for rendering
        reaper.SetMediaTrackInfo_Value(track, "I_RECARM", 1)
        
        -- Set project sample rate
        reaper.SetProjectSampleRate(SAMPLE_RATE)
        
        -- Render to file
        local output_file = OUTPUT_DIR .. "\\" .. instrument .. ".wav"
        
        reaper.MarkItemRender(track, false)
        
        -- Set play position to start
        reaper.SetEditCurPos(0, false, false)
        
        -- Render selection/project
        local render_cfg = "--renderfile \"" .. output_file .. "\""
        reaper.Main_OnCommand(41822, 0) -- Render project to file
        
        reaper.ShowConsoleMsg("  -> Saved: " .. output_file .. "\n")
    end
    
    reaper.ShowConsoleMsg("\nDone!\n")
end

-- Run
main()
