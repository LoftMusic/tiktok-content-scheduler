const { spawn } = require('child_process');
const path = require('path');

const PYTHON_EXE = 'C:\\Program Files\\Maxon Cinema 4D 2024\\resource\\modules\\python\\libs\\win64\\python.exe';
const SCRIPT = 'C:\\Users\\Studio3\\.openclaw\\workspace\\splice-desktop\\src\\record.py';

console.log('Script exists?', require('fs').existsSync(SCRIPT));

// Script path is absolute - cwd doesn't affect it
const proc = spawn(PYTHON_EXE, [SCRIPT, '--device', '29', '--samplerate', '44100', '--channels', '2', '--blocksize', '4410'], {
  cwd: 'C:\\Users\\Studio3\\.openclaw\\workspace\\splice-desktop',
  stdio: ['ignore', 'pipe', 'pipe']
});

let ready = false;
proc.stderr.on('data', (data) => {
  const msg = data.toString().trim();
  console.log('STDERR:', msg.substring(0, 120));
  if (msg.startsWith('READY')) { ready = true; }
});
proc.stdout.on('data', () => { if (ready) { console.log('Got audio!'); proc.kill(); } });
proc.on('close', (code) => console.log('Close:', code));
proc.on('error', (e) => console.error('Error:', e));
setTimeout(() => { if (!ready) { proc.kill(); console.log('Timeout - no READY'); } }, 5000);
