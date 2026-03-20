const { spawn } = require('child_process');

const PYTHON_EXE = 'C:\\Program Files\\Maxon Cinema 4D 2024\\resource\\modules\\python\\libs\\win64\\python.exe';
const SCRIPT = 'C:\\Users\\Studio3\\openclaw\\workspace\\splice-desktop\\src\\record.py';

console.log('Testing Python spawn...');
console.log('PYTHON_EXE:', PYTHON_EXE);
console.log('SCRIPT:', SCRIPT);

const args = ['--device', '29', '--samplerate', '44100', '--channels', '2', '--blocksize', '4410'];
const proc = spawn(PYTHON_EXE, [SCRIPT, ...args], {
  stdio: ['ignore', 'pipe', 'pipe']
});

let ready = false;

proc.stderr.on('data', (data) => {
  const msg = data.toString().trim();
  console.log('STDERR:', msg);
  if (msg.startsWith('READY')) {
    ready = true;
    console.log('GOT READY!');
    setTimeout(() => {
      proc.kill();
      process.exit(0);
    }, 1000);
  }
});

proc.stdout.on('data', (data) => {
  // Audio data received
  if (!ready) return;
  console.log('Got audio chunk:', data.length, 'bytes');
});

proc.on('error', (err) => {
  console.error('SPAWN ERROR:', err);
});

proc.on('close', (code) => {
  console.log('Process closed with code:', code);
});

setTimeout(() => {
  console.log('Timeout reached');
  proc.kill();
  process.exit(1);
}, 5000);
