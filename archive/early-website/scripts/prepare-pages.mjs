import { mkdirSync, copyFileSync, writeFileSync, cpSync } from 'node:fs';
try {
  mkdirSync('pages', {recursive:true});
  copyFileSync('collateral/沐仞_品牌与产品原型_2026-10-12.html', 'pages/index.html');
  writeFileSync('pages/.nojekyll', '');
  cpSync('public/history', 'pages/history', {recursive:true});
  console.log('GitHub Pages artifact ready: pages/index.html');
} catch (error) { console.error('Failed to prepare Pages:', error); process.exit(1); }
