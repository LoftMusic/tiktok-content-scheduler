import sys
print(sys.version)
import pkgutil
pkgs = [p.name for p in pkgutil.iter_modules()]
print('sounddevice:', 'sounddevice' in pkgs)
print('numpy:', 'numpy' in pkgs)
print('pyaudio:', 'pyaudio' in pkgs)
print('pygame:', 'pygame' in pkgs)
print('all pkgs:', sorted(pkgs))
