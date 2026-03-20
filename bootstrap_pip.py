import ensurepip
print("ensurepip:", ensurepip.__file__)
# Bootstrap pip
ensurepip.bootstrap()
# Verify pip is available
import subprocess
result = subprocess.run(["pip", "--version"], capture_output=True, text=True)
print("pip:", result.stdout.strip())
