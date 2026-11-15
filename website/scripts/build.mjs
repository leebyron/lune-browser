import {cp, mkdir, readFile, rm, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {renderLegal, legalPages} from './legal.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = join(root, 'dist');
const template = await readFile(join(root, 'templates/legal.html'), 'utf8');
// Validate every document before touching a previous successful build.
const pages = await Promise.all(legalPages.map(async (document) => {
  const source = await readFile(join(root, `../legal/${document.slug}.md`), 'utf8');
  const html = renderLegal(source, template, {...document, production: process.argv.includes('--production')});
  return {...document, source, html};
}));
await rm(output, {recursive: true, force: true});
await cp(join(root, 'public'), output, {recursive: true});
for (const {slug, source, html} of pages) {
  await mkdir(join(output, slug), {recursive: true});
  await writeFile(join(output, slug, 'index.html'), html);
  await writeFile(join(output, `${slug}.md`), source);
}
console.log(`Built website/dist, including ${pages.map(({slug}) => `/${slug}`).join(' and ')} from legal/ Markdown`);
