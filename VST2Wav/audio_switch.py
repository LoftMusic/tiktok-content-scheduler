"""
Audio Device Switcher Helper
Switches default Windows audio output device
"""

import sys
import os
import subprocess
import re

def get_audio_devices():
    """Get list of audio output devices using PowerShell"""
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            'Get-WmiObject Win32_SoundDevice | Select-Object -ExpandProperty Name'
        ], capture_output=True, text=True, timeout=10)
        
        devices = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line:
                devices.append(line)
        return devices
    except Exception as e:
        print(f"Error: {e}")
        return []

def set_default_audio_device(device_name):
    """
    Set default audio device using AudioDeviceCmdlets or manual method
    Returns True if successful
    """
    # Try using AudioDeviceCmdlets if available
    # Otherwise use registry method
    try:
        # Method 1: Using registry to set default communication device
        # This requires the device ID which we need to get first
        
        # Get device ID
        ps_command = f'''
$device = Get-PnpDevice -Class AudioEndpoint -Status OK | Where-Object {{$_.FriendlyName -eq "{device_name}"}}
if ($device) {{
    $deviceID = $device.InstanceId
    $regPath = "HKCU:\\Software\\Microsoft\\Multimedia\\Sound Mapper"
    Set-ItemProperty -Path $regPath -Name "FrontBack" -Value $deviceID
    Set-ItemProperty -Path $regPath -Name "Playback" -Value $deviceID
    Write-Output "SUCCESS"
}} else {{
    Write-Output "DEVICE_NOT_FOUND"
}}
'''
        result = subprocess.run(['powershell', '-Command', ps_command], 
                              capture_output=True, text=True, timeout=30)
        
        if "SUCCESS" in result.stdout:
            return True
    except Exception as e:
        print(f"Method 1 failed: {e}")
    
    return False

def get_current_default_device():
    """Get current default audio device"""
    try:
        result = subprocess.run([
            'powershell', '-Command',
            'Get-WmiObject Win32_SoundDevice | Where-Object {$_.Status -eq "OK"} | Select-Object -First 1 -ExpandProperty Name'
        ], capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: audio_switch.py <device_name|list|get>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "list":
        devices = get_audio_devices()
        for d in devices:
            print(d)
    elif action == "get":
        device = get_current_default_device()
        print(device if device else "Unknown")
    elif action.startswith("set:"):
        device_name = action[4:]
        if set_default_audio_device(device_name):
            print("SUCCESS")
        else:
            print("FAILED")
    else:
        print("Unknown action")
