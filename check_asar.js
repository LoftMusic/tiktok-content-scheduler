const asar = require('asar');
const path = require('path');

const asarPath = 'C:\\Users\\Studio3\\.openclaw\\workspace\\splice-desktop\\dist\\win-unpacked\\resources\\app.asar';
const fs = require('fs');

if (fs.existsSync(asarPath)) {
  console.log('ASAR exists');
  const list = asar.listPackage(asarPath);
  const srcFiles = list.filter(f => f.includes('src') || f.includes('record'));
  console.log('Src/record files in asar:');
  srcFiles.forEach(f => console.log(' ', f));
} else {
  console.log('ASAR not found at:', asarPath);
}
