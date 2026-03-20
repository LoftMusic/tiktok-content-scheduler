# Get device IDs
$vacID = "SWD\MMDEVAPI\{0.0.1.00000000}.{9C8A1CEB-0B21-4211-9FBB-CDF8D4F02824}"
$speakersID = "SWD\MMDEVAPI\{0.0.0.00000000}.{3D271FDD-D980-4054-85B7-033392FDF973}"

# Current setting
$current = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Multimedia\Sound Mapper' -Name 'Playback' -ErrorAction SilentlyContinue
Write-Host "Before: $($current.Playback)"

# Switch to VAC (Line 1)
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Multimedia\Sound Mapper' -Name 'Playback' -Value $vacID -ErrorAction SilentlyContinue
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Multimedia\Sound Mapper' -Name 'FrontBack' -Value $vacID -ErrorAction SilentlyContinue

# Refresh
$new = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Multimedia\Sound Mapper' -Name 'Playback' -ErrorAction SilentlyContinue
Write-Host "After: $($new.Playback)"

# Try to notify Windows
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Audio {
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern void SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
    public const int HWND_BROADCAST = 0xffff;
    public const int WM_SETTINGCHANGE = 0x001A;
    public static void Refresh() {
        UIntPtr result;
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "Audio", 2, 1000, out result);
    }
}
"@

[Audio]::Refresh()
Write-Host "Done! Output switched to Line 1 (Virtual Audio Cable)"
