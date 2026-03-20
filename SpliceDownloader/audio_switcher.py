"""
Audio Device Switcher - Uses Windows Core Audio API
More reliable than registry changes
"""

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IMMDeviceEnumerator, IMMDevice, EDataFlow

class AudioSwitcher:
    def __init__(self):
        self.device_enumerator = AudioUtilities.GetDeviceEnumerator()
        self.original_output = None
        self.original_input = None
    
    def get_all_devices(self):
        """Get all audio devices"""
        devices = []
        for i, device in enumerate(self.device_enumerator.EnumAudioEndpoints(EDataFlow.eAll.value, 1)):
            name = device.FriendlyName
            id = device.id
            flow = device.GetState()
            devices.append({
                'index': i,
                'name': name,
                'id': id,
                'state': flow
            })
        return devices
    
    def get_default_output(self):
        """Get default output device"""
        device = self.device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender.value, 1)
        return {
            'name': device.FriendlyName,
            'id': device.id
        }
    
    def get_default_input(self):
        """Get default input device"""
        device = self.device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eCapture.value, 1)
        return {
            'name': device.FriendlyName,
            'id': device.id
        }
    
    def set_default_output(self, device_id):
        """Set default output device by ID"""
        device = self.device_enumerator.GetDevice(device_id)
        self.device_enumerator.SetDefaultAudioEndpoint(device, EDataFlow.eRender.value, 1)
    
    def set_default_input(self, device_id):
        """Set default input device by ID"""
        device = self.device_enumerator.GetDevice(device_id)
        self.device_enumerator.SetDefaultAudioEndpoint(device, EDataFlow.eCapture.value, 1)
    
    def find_device(self, name_pattern):
        """Find device by name pattern (case insensitive)"""
        for device in self.get_all_devices():
            if name_pattern.lower() in device['name'].lower():
                return device
        return None
    
    def save_current_devices(self):
        """Save current output and input devices"""
        self.original_output = self.get_default_output()['id']
        self.original_input = self.get_default_input()['id']
        print(f"Saved output: {self.get_default_output()['name']}")
        print(f"Saved input: {self.get_default_input()['name']}")
        return self.original_output, self.original_input
    
    def restore_devices(self):
        """Restore original output and input devices"""
        if self.original_output:
            print(f"Restoring output: {self.original_output}")
            self.set_default_output(self.original_output)
        if self.original_input:
            print(f"Restoring input: {self.original_input}")
            self.set_default_input(self.original_input)
    
    def switch_to_vac(self):
        """Switch both output and input to Virtual Audio Cable"""
        # Save current devices first
        self.save_current_devices()
        
        # Find VAC devices
        vac_output = self.find_device("Virtual Audio Cable")
        
        if vac_output:
            print(f"Switching output to: {vac_output['name']}")
            self.set_default_output(vac_output['id'])
            
            # For input, we also use VAC (the same device works for both)
            print(f"Switching input to: {vac_output['name']}")
            self.set_default_input(vac_output['id'])
            
            return True
        else:
            print("Virtual Audio Cable not found!")
            return False


def list_devices():
    """List all audio devices"""
    switcher = AudioSwitcher()
    print("\n=== All Audio Devices ===")
    for dev in switcher.get_all_devices():
        print(f"[{dev['index']}] {dev['name']}")
        print(f"    ID: {dev['id']}")
    print()
    
    print("=== Default Output ===")
    out = switcher.get_default_output()
    print(f"Name: {out['name']}")
    print(f"ID: {out['id']}")
    print()
    
    print("=== Default Input ===")
    inp = switcher.get_default_input()
    print(f"Name: {inp['name']}")
    print(f"ID: {inp['id']}")


if __name__ == "__main__":
    list_devices()
