# Get MMDEVAPI device IDs (used in Sound Mapper registry)
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Collections.Generic;

public class MMDeviceEnumerator {
    [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
    internal class MMDeviceEnumeratorComObject { }

    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("A95664D2-9614-4F35-A746-DE8DB63617E6")]
    internal interface IMMDeviceEnumerator {
        int NotImpl1();
        int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice);
    }

    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("D666063F-1587-4E43-81F1-B948E807363F")]
    internal interface IMMDevice {
        int Activate(ref Guid iid, int dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
    }

    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("306A6A19-B5F8-41F5-A6AF-0472A5046B00")]
    internal interface IPropertyStore {
        int GetCount(out int cProps);
        int GetAt(int iProp, out PropertyKey pKey);
        int GetValue(ref PropertyKey key, out PropVariant pv);
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct PropertyKey {
        public Guid fmtid;
        public int pid;
        public PropertyKey(Guid fmtid, int pid) { this.fmtid = fmtid; this.pid = pid; }
    }

    [StructLayout(LayoutKind.Explicit)]
    public struct PropVariant {
        [FieldOffset(0)] public short vt;
        [FieldOffset(8)] public IntPtr pointerValue;
        public string GetString() { return Marshal.PtrToStringUni(pointerValue); }
    }

    public static string GetDeviceId(int dataFlow) {
        var enumerator = (IMMDeviceEnumerator)(new MMDeviceEnumeratorComObject());
        IMMDevice device;
        enumerator.GetDefaultAudioEndpoint(dataFlow, 1, out device);
        
        Guid propertyStoreGuid = new Guid("886d8eeb-8cf2-4446-8d02-cdba1dbdcf99");
        IPropertyStore propertyStore;
        device.Activate(ref propertyStoreGuid, 1, IntPtr.Zero, out propertyStore);
        
        var pkeyDeviceID = new PropertyKey(new Guid("a45c254e-df1c-4efd-8020-67d146a850e0"), 2);
        PropVariant pv;
        propertyStore.GetValue(ref pkeyDeviceID, out pv);
        
        return pv.GetString();
    }
}
"@

Write-Host "Default Playback Device (MMDEVAPI ID):"
Write-Host ([MMDeviceEnumerator]::GetDeviceId(0))

Write-Host "`nDefault Capture Device (MMDEVAPI ID):"
Write-Host ([MMDeviceEnumerator]::GetDeviceId(1))
