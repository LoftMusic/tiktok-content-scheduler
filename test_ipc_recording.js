const { ipcMain, BrowserWindow } = require('electron');
const path = require('path');

// Load the main.js module to access its handlers
const mainJsPath = path.join(__dirname, 'splice-desktop', 'src', 'main.js');
console.log('Loading main.js from:', mainJsPath);

// We can't require() main.js directly since it's not a module
// Instead, let's test the Python spawn path directly

const { spawn } = require('child_process');
const fs = require('fs');

const PYTHON_EXE = 'C:\\Program Files\\Maxon Cinema 4D 2024\\resource\\modules\\python\\libs\\win64\\python.exe';
const RECORD_SCRIPT = 'C:\\Users\\Studio3\\.openclaw\\workspace\\splice-desktop\\src\\record.py';

console.log('PYTHON_EXE exists:', fs.existsSync(PYTHON_EXE));
console.log('RECORD_SCRIPT exists:', fs.existsSync(RECORD_SCRIPT));

// Test spawning
const args = [RECORD_SCRIPT, '--device', '29', '--samplerate', '44100', '--channels', '2', '--blocksize', '4410'];
console.log('Spawning:', PYTHON_EXE, args.join(' '));

const proc = spawn(PYTHON_EXE, args, {
  stdio: ['ignore', 'pipe', 'pipe'],
  cwd: path.dirname(PYTHON_EXE)
});

let ready = false;
proc.stderr.on('data', (data) => {
  console.log('Python:', data.toString().trim().substring(0, 120));
  if (data.toString().includes('READY')) ready = true;
});
proc.stdout.on('data', () => { if (ready) { console.log('AUDIO!'); } });
proc.on('close', (code) => console.log('Closed:', code));
proc.on('error', (err) => console.error('Error:', err));

setTimeout(() => { proc.kill(); console.log('Done'); }, 4000);
