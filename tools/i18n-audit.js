const fs = require('fs');
const src = fs.readFileSync('js/app.js', 'utf8');
const locales = ['en', 'hi', 'mr', 'gu'];
const keys = {};
for (let i = 0; i < locales.length; i++) {
  const loc = locales[i];
  const start = src.indexOf(`${loc}: {`);
  const end = i < locales.length - 1
    ? src.indexOf(`${locales[i + 1]}: {`)
    : src.indexOf('};', start);
  const block = src.slice(start, end);
  keys[loc] = new Set();
  for (const m of block.matchAll(/'([^']+)':/g)) keys[loc].add(m[1]);
}
const en = [...keys.en].sort();
for (const loc of ['hi', 'mr', 'gu']) {
  const missing = en.filter((k) => !keys[loc].has(k));
  console.log(`${loc} missing: ${missing.length}`);
  missing.forEach((k) => console.log('  ' + k));
}
console.log('EN total:', en.length);
