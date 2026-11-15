import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {renderPrivacy} from '../scripts/privacy.mjs';

const metadata = '---\nstatus: draft\nrevised: 2026-11-14\n---\n';
const template = '{{ROBOTS}}{{STATUS}} {{REVISION}}<nav>{{TOC}}</nav><article>{{CONTENT}}</article>';

test('draft is readable locally but cannot be built for production', () => {
  const source = metadata + '# Privacy\n\n## Your data\n\nOn your Mac.\n';
  const html = renderPrivacy(source, template);
  assert.match(html, /noindex, nofollow/);
  assert.doesNotMatch(html, /draft|not yet effective/i);
  assert.match(html, /href="#your-data"/);
  assert.match(html, /id="your-data"/);
  assert.throws(() => renderPrivacy(source, template, {production: true}), /draft/);
});

test('Markdown cannot inject HTML or executable links into the page', () => {
  const html = renderPrivacy(metadata + '# Privacy\n\n<script>alert(1)</script>\n\n[bad](javascript:alert(1))\n\n## A & B\n', template);
  assert.doesNotMatch(html, /<script>|href="javascript:/);
  assert.match(html, /&lt;script&gt;/);
  assert.match(html, /A &amp; B/);
});

test('repeated headings have unique working fragment links', () => {
  const html = renderPrivacy(metadata + '# Privacy\n\n## Data\n\nOne.\n\n## Data\n\nTwo.\n', template);
  assert.match(html, /href="#data-2"/);
  assert.match(html, /id="data-2"/);
});

test('publication needs an effective date and resolved drafting notes', () => {
  const source = metadata.replace('draft', 'published') + '# Privacy\n';
  assert.throws(() => renderPrivacy(source, template, {production: true}), /effective date/);
  const ready = source.replace('revised: 2026-11-14', 'revised: 2026-11-14\neffective: 2026-11-14');
  assert.doesNotMatch(renderPrivacy(ready, template, {production: true}), /noindex/);
  assert.throws(() => renderPrivacy(ready + '\nDraft note: unresolved.\n', template), /draft notes/);
  assert.throws(() => renderPrivacy(ready + '\nContact placeholder\n', template), /draft notes/);
});

test('build uses the exact canonical Markdown and current template', async () => {
  const source = await readFile(new URL('../../legal/privacy.md', import.meta.url), 'utf8');
  const actualTemplate = await readFile(new URL('../templates/privacy.html', import.meta.url), 'utf8');
  const output = await readFile(new URL('../dist/privacy/index.html', import.meta.url), 'utf8');
  assert.equal(output, renderPrivacy(source, actualTemplate));
  assert.equal(await readFile(new URL('../dist/privacy.md', import.meta.url), 'utf8'), source);
  assert.doesNotMatch(output, /\{\{[A-Z]+\}\}/);
});
