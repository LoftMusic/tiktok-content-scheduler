# Force switch using Endpoints
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Collections.Generic;

[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {
    int NotImpl1();
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
}

[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {
    int Activate(ref Guid id, int clsCtx, IntPtr activationParams, out IAudioClient client);
}

[Guid("F8679F50-850A-41CF-9C72-430F290290C8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioClient {
    int Initialize(int shareMode, int flags, long hnsBufferDuration, long hnsPeriodicity, ref WAVEFORMATEX format, IntPtr audioSessionGuid);
    int GetServiceSessionGuid(out Guid guid);
}

[StructLayout(LayoutKind.Sequential, Pack=2)]
public struct WAVEFORMATEX {
    public short wFormatTag;
    public short nChannels;
    public int nSamplesPerSec;
    public int nAvgBytesPerSec;
    public short nBlockAlign;
    public short wBitsPerSample;
    public short cbSize;
}

public class AudioSwitcher {
    [DllImport("ole32.dll")]
    public static extern int CoCreateInstance(ref Guid clsid, IntPtr pUnkOuter, int dwClsContext, ref Guid iid, out IntPtr ppv);
    
    public static void SetDefaultDevice(string deviceId) {
        Guid CLSID_MMDeviceEnumerator = new Guid("BCDE0395-E52F-467C-8E3D-C4579291692E");
        Guid IID_IMMDeviceEnumerator = new Guid("A95664D2-9614-4F35-A746-DE8DB63617E6");
        
        IntPtr pDeviceEnumerator;
        CoCreateInstance(ref CLSID_MMDeviceEnumerator, IntPtr.Zero, 1, ref IID_IMMDeviceEnumerator, out pDeviceEnumerator);
        
        IMMDeviceEnumerator enumerator = (IMMDeviceEnumerator)Marshal.GetObjectForIUnknown(pDeviceEnumerator);
        
        // We need to enumerate and find the device
        Console.WriteLine("Device ID to set: " + deviceId);
    }
}
"@
