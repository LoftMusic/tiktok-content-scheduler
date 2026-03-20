const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const PYTHON_EXE = 'C:\\Program Files\\Maxon Cinema 4D 2024\\resource\\modules\\python\\libs\\win64\\python.exe';
const RECORD_SCRIPT = 'C:\\Users\\Studio3\\.openclaw\\workspace\\splice-desktop\\dist\\win-unpacked\\resources\\app\\src\\record.py';

console.log('=== Packaged App Path Test ===');
console.log('PYTHON_EXE:', PYTHON_EXE);
console.log('PYTHON_EXE exists:', fs.existsSync(PYTHON_EXE));
console.log('RECORD_SCRIPT:', RECORD_SCRIPT);
console.log('RECORD_SCRIPT exists:', fs.existsSync(RECORD_SCRIPT));

const args = [RECORD_SCRIPT, '--device', '29', '--samplerate', '44100', '--channels', '2', '--blocksize', '4410'];
console.log('Args:', args);

console.log('\n=== Spawning ===');
const proc = spawn(PYTHON_EXE, args, {
  stdio: ['ignore', 'pipe', 'pipe']
});

let ready = false;
proc.stderr.on('data', (data) => {
  const msg = data.toString().trim();
  console.log('STDERR:', msg.substring(0, 200));
  if (msg.includes('READY')) { ready = true; }
});
proc.stdout.on('data', () => {
  if (ready) console.log('AUDIO CHUNK RECEIVED!');
});
proc.on('close', (code) => console.log('Closed with code:', code));
proc.on('error', (err) => console.error('Error:', err));

setTimeout(() => {
  if (!ready) console.log('TIMEOUT - READY never received');
  proc.kill();
  process.exit(0);
}, 5000);
