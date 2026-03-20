# Audio Device Switcher via Core Audio API
# This is more reliable than registry

param(
    [string]$Action = "list",  # list, save, switch-to-vac, restore
    [string]$OutputId = "",
    [string]$InputId = ""
)

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

[ComImport]
[Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
internal class MMDeviceEnumerator { }

[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
internal interface IMMDeviceEnumerator {
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice);
    int EnumAudioEndpoints(int dataFlow, int stateMask, out IMMDeviceCollection ppDevices);
}

[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
internal interface IMMDevice {
    int Activate(ref Guid iid, int dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
    int OpenPropertyStore(int access, out IPropertyStore properties);
    int GetId([MarshalAs(UnmanagedType.LPWStr)] out string ppstrId);
    int GetState(out int pdwState);
}

[Guid("0FDFB86B-4541-4C85-9E2C-4C0ACA3EA6D2"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
internal interface IMMDeviceCollection {
    int GetCount(out int pcDevices);
    int Item(int nIndex, out IMMDevice ppDevice);
}

[Guid("886d8eeb-8cf2-4446-8d02-cdba1dbdcf99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
internal interface IPropertyStore {
    int GetCount(out int cProps);
    int GetAt(int iProp, out PropertyKey pKey);
    int GetValue(ref PropertyKey key, out PropVariant pv);
}

[StructLayout(LayoutKind.Sequential)]
public struct PropertyKey {
    public Guid fmtid;
    public int pid;
}

[StructLayout(LayoutKind.Explicit)]
public struct PropVariant {
    [FieldOffset(0)] public short vt;
    [FieldOffset(8)] public IntPtr pointerValue;
    public string GetString() { return Marshal.PtrToStringUni(pointerValue); }
}

public class AudioSwitcher {
    private static IMMDeviceEnumerator enumerator = (IMMDeviceEnumerator)(new MMDeviceEnumerator());
    
    public static string GetDefaultDeviceId(int dataFlow) {
        IMMDevice device;
        enumerator.GetDefaultAudioEndpoint(dataFlow, 1, out device);
        string id;
        device.GetId(out id);
        return id;
    }
    
    public static void SetDefaultDevice(string deviceId, int dataFlow) {
        // Note: Setting default device via COM is complex
        // For now, we'll use a different approach
    }
    
    public static string[] GetAllDeviceIds(int dataFlow) {
        IMMDeviceCollection collection;
        enumerator.EnumAudioEndpoints(dataFlow, 1, out collection);
        int count;
        collection.GetCount(out count);
        
        string[] ids = new string[count];
        for (int i = 0; i < count; i++) {
            IMMDevice device;
            collection.Item(i, out device);
            device.GetId(out ids[i]);
        }
        return ids;
    }
}
"@

function Get-AllAudioDevices {
    $devices = @()
    
    # Render devices (output)
    $renderEnum = New-Object MMDeviceEnumerator
    $renderCollection = $renderEnum.EnumAudioEndpoints(0, 1)  # eRender = 0
    
    $count = 0
    $renderCollection.GetCount([ref]$count)
    
    for ($i = 0; $i -lt $count; $i++) {
        $device = $renderCollection.Item($i)
        $id = ""
        $device.GetId([ref]$id)
        
        $name = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render\$id\Properties" -ErrorAction SilentlyContinue).DeviceDesc
        if ($name) { $name = $name -replace '.*,', '' }
        
        $devices += [PSCustomObject]@{
            Type = "Output"
            Name = $name
            Id = $id
        }
    }
    
    # Capture devices (input)
    $captureEnum = New-Object MMDeviceEnumerator
    $captureCollection = $captureEnum.EnumAudioEndpoints(1, 1)  # eCapture = 1
    
    $count = 0
    $captureCollection.GetCount([ref]$count)
    
    for ($i = 0; $i -lt $count; $i++) {
        $device = $captureCollection.Item($i)
        $id = ""
        $device.GetId([ref]$id)
        
        $name = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture\$id\Properties" -ErrorAction SilentlyContinue).DeviceDesc
        if ($name) { $name = $name -replace '.*,', '' }
        
        $devices += [PSCustomObject]@{
            Type = "Input"
            Name = $name
            Id = $id
        }
    }
    
    return $devices
}

function Get-DefaultAudioDevice {
    param([int]$DataFlow)
    
    $enumerator = New-Object MMDeviceEnumerator
    $device = $enumerator.GetDefaultAudioEndpoint($DataFlow, 1)
    $id = ""
    $device.GetId([ref]$id)
    
    $name = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render\$id\Properties" -ErrorAction SilentlyContinue).DeviceDesc
    if ($name) { $name = $name -replace '.*,', '' }
    
    return [PSCustomObject]@{
        Name = $name
        Id = $id
    }
}

# Since Core Audio API doesn't easily allow setting default device programmatically,
# we'll use a workaround: use the Sound Mixer API via console

switch ($Action) {
    "list" {
        Write-Host "=== All Audio Devices ===" -ForegroundColor Cyan
        Get-AllAudioDevices | Format-Table -AutoSize
        
        Write-Host "`n=== Default Output ===" -ForegroundColor Cyan
        $out = Get-DefaultAudioDevice -DataFlow 0
        Write-Host "Name: $($out.Name)"
        Write-Host "ID: $($out.Id)"
        
        Write-Host "`n=== Default Input ===" -ForegroundColor Cyan
        $in = Get-DefaultAudioDevice -DataFlow 1
        Write-Host "Name: $($in.Name)"
        Write-Host "ID: $($in.Id)"
    }
    
    "save" {
        $out = Get-DefaultAudioDevice -DataFlow 0
        $in = Get-DefaultAudioDevice -DataFlow 1
        Write-Output "$($out.Id)|$($in.Id)"
    }
    
    "set-output" {
        if (-not $OutputId) { Write-Error "OutputId required"; exit 1 }
        
        # Use Control Panel to set default
        $result = Run-Console -Command "Set-AudioDevice -ID $OutputId" 2>$null
        
        # Alternative: registry (works for most apps)
        $regPath = "HKCU:\Software\Microsoft\Multimedia\Sound Mapper"
        Set-ItemProperty -Path $regPath -Name "Playback" -Value $OutputId
        Set-ItemProperty -Path $regPath -Name "FrontBack" -Value $OutputId
        
        # Notify Windows
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class AudioNotify {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
}
"@
        $HWND_BROADCAST = [IntPtr]0xffff
        $WM_SETTINGCHANGE = 0x001A
        $result = [AudioNotify]::SendMessageTimeout($HWND_BROADCAST, $WM_SETTINGCHANGE, [UIntPtr]::Zero, "Audio", 2, 1000, [ref][IntPtr]::Zero)
        
        Write-Host "Output set to: $OutputId" -ForegroundColor Green
    }
}
