# Test: Try to switch audio output to VAC using registry
# Then verify if it worked

$vacID = "SWD\MMDEVAPI\{0.0.1.00000000}.{9C8A1CEB-0B21-4211-9FBB-CDF8D4F02824}"
$regPath = "HKCU:\Software\Microsoft\Multimedia\Sound Mapper"

Write-Host "Before:"
Write-Host (Get-ItemProperty -Path $regPath -Name "Playback").Playback

Write-Host "Setting to VAC..."
Set-ItemProperty -Path $regPath -Name "Playback" -Value $vacID

Write-Host "After:"
Write-Host (Get-ItemProperty -Path $regPath -Name "Playback").Playback

# Notify Windows
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

Write-Host "Done. Check if output changed!"
