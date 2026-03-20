const { ipcMain, BrowserWindow } = require('electron');

// We need to find the window and send IPC directly
// But we can't easily do this from an external script...

// Instead, let's just verify that the paths work in the packaged context
const path = require('path');
const fs = require('fs');
const { app } = require('electron');

console.log('Testing RECORD_SCRIPT path resolution in packaged context...');
const resourcesPath = 'C:\\Users\\Studio3\\.openclaw\\workspace\\splice-desktop\\dist\\win-unpacked\\resources';
const RECORD_SCRIPT = path.join(resourcesPath, 'app', 'src', 'record.py');
console.log('RECORD_SCRIPT:', RECORD_SCRIPT);
console.log('Exists:', fs.existsSync(RECORD_SCRIPT));

// Now actually try to spawn
const { spawn } = require('child_process');
const PYTHON_EXE = 'C:\\Program Files\\Maxon Cinema 4D 2024\\resource\\modules\\python\\libs\\win64\\python.exe';
const proc = spawn(PYTHON_EXE, [RECORD_SCRIPT, '--device', '29', '--samplerate', '44100', '--channels', '2', '--blocksize', '4410'], {
  stdio: ['ignore', 'pipe', 'pipe']
});
let ready = false;
proc.stderr.on('data', (data) => {
  const msg = data.toString().trim();
  console.log('Python:', msg.substring(0, 100));
  if (msg.includes('READY')) ready = true;
});
proc.on('close', (code) => console.log('Closed:', code));
setTimeout(() => { proc.kill(); console.log('Done'); }, 4000);
