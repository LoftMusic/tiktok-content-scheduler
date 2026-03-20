const http = require('http');

// The Electron IPC doesn't have a direct HTTP interface, so we can't easily call it externally.
// Let me instead create a standalone test that simulates the exact same code path as the app.

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('=== Standalone test simulating packaged app behavior ===\n');

// These are the EXACT same values the packaged app uses
const app = { isPackaged: true };
const resourcesPath = 'C:\\Users\\Studio3\\.openclaw\\workspace\\splice-desktop\\dist\\win-unpacked\\resources';
const PYTHON_EXE = 'C:\\Program Files\\Maxon Cinema 4D 2024\\resource\\modules\\python\\libs\\win64\\python.exe';
const RECORD_SCRIPT = app.isPackaged
  ? path.join(resourcesPath, 'app', 'src', 'record.py')
  : path.join(__dirname, 'record.py');

console.log('app.isPackaged:', app.isPackaged);
console.log('process.resourcesPath:', resourcesPath);
console.log('PYTHON_EXE:', PYTHON_EXE);
console.log('RECORD_SCRIPT:', RECORD_SCRIPT);
console.log('RECORD_SCRIPT exists:', fs.existsSync(RECORD_SCRIPT));
console.log('PYTHON_EXE exists:', fs.existsSync(PYTHON_EXE));
console.log();

// Simulate AudioEngine.start() exactly
const deviceIndex = 29;
const sampleRate = 44100;
const channels = 2;
const blockSize = Math.floor(sampleRate * 0.1);

const args = [
  RECORD_SCRIPT,
  '--device', String(deviceIndex),
  '--samplerate', String(sampleRate),
  '--channels', String(channels),
  '--blocksize', String(blockSize)
];

console.log('Args:', args);
console.log('\nSpawning Python...');

const proc = spawn(PYTHON_EXE, args, {
  stdio: ['ignore', 'pipe', 'pipe']
});

let ready = false;
let deviceInfo = null;

proc.stderr.on('data', (data) => {
  const msg = data.toString().trim();
  console.log('stderr:', msg.substring(0, 150));
  if (msg.startsWith('DEVICE_INFO:')) {
    deviceInfo = msg;
  }
  if (msg.startsWith('READY')) {
    ready = true;
    console.log('\n*** READY signal received! ***');
    console.log('Device info:', deviceInfo);
  }
});

let audioChunks = 0;
proc.stdout.on('data', (chunk) => {
  if (ready) {
    audioChunks++;
    if (audioChunks <= 3) {
      console.log(`stdout: audio chunk ${audioChunks}, ${chunk.length} bytes`);
    }
  }
});

proc.on('error', (err) => {
  console.error('Process error:', err);
});

proc.on('close', (code) => {
  console.log('\nProcess closed with code:', code, 'ready was:', ready, 'chunks received:', audioChunks);
});

setTimeout(() => {
  if (!ready) {
    console.log('\TIMEOUT - READY was never received!');
  } else {
    console.log('\nSUCCESS - Python spawn works correctly!');
  }
  proc.kill();
  process.exit(0);
}, 5000);
