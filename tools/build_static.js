import { mkdir, cp, rm } from 'node:fs/promises';
import { join } from 'node:path';

const root = process.cwd();
const publicDir = join(root, 'public');
const distDir = join(root, 'dist');

await rm(distDir, { recursive: true, force: true });
await mkdir(distDir, { recursive: true });
await cp(publicDir, distDir, { recursive: true });

console.log('Built static web assets into dist/.');
