import {cp, mkdir, readFile, rm, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {renderPrivacy} from './privacy.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = join(root, 'dist');
const source = await readFile(join(root, '../legal/privacy.md'), 'utf8');
const template = await readFile(join(root, 'templates/privacy.html'), 'utf8');
// Validate before touching a previous successful build.
const html = renderPrivacy(source, template, {production: process.argv.includes('--production')});
await rm(output, {recursive: true, force: true});
await cp(join(root, 'public'), output, {recursive: true});
await mkdir(join(output, 'privacy'), {recursive: true});
await writeFile(join(output, 'privacy/index.html'), html);
await writeFile(join(output, 'privacy.md'), source);
console.log('Built website/dist, including /privacy from legal/privacy.md');
