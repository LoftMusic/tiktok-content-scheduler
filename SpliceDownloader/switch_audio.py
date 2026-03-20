# Audio Device Switcher using AudioDeviceCmdlets
# Call from Python with: switch_audio.py [action]
# Actions: save, switch, restore

import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_ps(script):
    """Run PowerShell script and return output"""
    result = subprocess.run(
        ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', script],
        capture_output=True, text=True, timeout=30,
        cwd=SCRIPT_DIR
    )
    return result.stdout.strip(), result.stderr.strip()

def get_current_devices():
    """Get current output and input device IDs"""
    script = """
Import-Module AudioDeviceCmdlets
$p = Get-AudioDevice -Playback
$r = Get-AudioDevice -Recording
Write-Output "$($p.ID)|$r.ID"
"""
    output, _ = run_ps(script)
    if '|' in output:
        parts = output.split('|')
        return parts[0].strip(), parts[1].strip()
    return None, None

def switch_to_vac():
    """Switch both output and input to VAC"""
    script = """
Import-Module AudioDeviceCmdlets

# Get current first
$p = Get-AudioDevice -Playback
$r = Get-AudioDevice -Recording
Write-Output "ORIGINAL:$($p.ID)|$r.ID"

# Switch playback to VAC (Index 2)
Set-AudioDevice -Index 2

# Switch recording to VAC (Index 5)  
# Use Set-AudioDevice to set recording device
Get-AudioDevice -List | Where-Object { $_.Index -eq 5 } | Set-AudioDevice

Start-Sleep -Milliseconds 300

# Verify
$p2 = Get-AudioDevice -Playback
$r2 = Get-AudioDevice -Recording
Write-Output "SWITCHED:$($p2.ID)|$r2.ID"
"""
    output, err = run_ps(script)
    print(output)
    if err:
        print(f"Error: {err}")
    return output

def restore_devices(original_output_id, original_input_id):
    """Restore original output and input devices"""
    script = f"""
Import-Module AudioDeviceCmdlets

# Find device by ID and switch to it
Get-AudioDevice -List | Where-Object {{ $_.ID -eq "{original_output_id}" }} | Set-AudioDevice
Get-AudioDevice -List | Where-Object {{ $_.ID -eq "{original_input_id}" }} | Set-AudioDevice

Start-Sleep -Milliseconds 300

$p = Get-AudioDevice -Playback
$r = Get-AudioDevice -Recording
Write-Output "RESTORED:$($p.Name)|$r.Name"
"""
    output, _ = run_ps(script)
    print(output)

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if action == "save":
        out_id, in_id = get_current_devices()
        print(f"Output: {out_id}")
        print(f"Input: {in_id}")
        
    elif action == "switch":
        print("Switching to VAC...")
        switch_to_vac()
        
    elif action == "restore":
        if len(sys.argv) > 3:
            out_id = sys.argv[2]
            in_id = sys.argv[3]
            restore_devices(out_id, in_id)
        else:
            print("Usage: switch_audio.py restore <output_id> <input_id>")
            
    else:
        # Status
        out_id, in_id = get_current_devices()
        print(f"Current Output ID: {out_id}")
        print(f"Current Input ID: {in_id}")
