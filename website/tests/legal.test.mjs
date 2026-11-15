import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {renderLegal, legalPages} from '../scripts/legal.mjs';
const render = (source, template, options = {}) => renderLegal(source, template, {...legalPages[0], ...options});

const metadata = '---\nstatus: draft\nrevised: 2026-11-14\n---\n';
const template = '{{ROBOTS}}{{STATUS}} {{REVISION}}<nav>{{TOC}}</nav><article>{{CONTENT}}</article>';

test('draft is readable locally but cannot be built for production', () => {
  const source = metadata + '# Privacy\n\n## Your data\n\nOn your Mac.\n';
  const html = render(source, template);
  assert.match(html, /noindex, nofollow/);
  assert.doesNotMatch(html, /draft|not yet effective/i);
  assert.match(html, /href="#your-data"/);
  assert.match(html, /id="your-data"/);
  assert.throws(() => render(source, template, {production: true}), /draft/);
});

test('Markdown cannot inject HTML or executable links into the page', () => {
  const html = render(metadata + '# Privacy\n\n<script>alert(1)</script>\n\n[bad](javascript:alert(1))\n\n## A & B\n', template);
  assert.doesNotMatch(html, /<script>|href="javascript:/);
  assert.match(html, /&lt;script&gt;/);
  assert.match(html, /A &amp; B/);
});

test('repeated headings have unique working fragment links', () => {
  const html = render(metadata + '# Privacy\n\n## Data\n\nOne.\n\n## Data\n\nTwo.\n', template);
  assert.match(html, /href="#data-2"/);
  assert.match(html, /id="data-2"/);
});

test('publication needs an effective date and resolved drafting notes', () => {
  const source = metadata.replace('draft', 'published') + '# Privacy\n';
  assert.throws(() => render(source, template, {production: true}), /effective date/);
  const ready = source.replace('revised: 2026-11-14', 'revised: 2026-11-14\neffective: 2026-11-14');
  assert.doesNotMatch(render(ready, template, {production: true}), /noindex/);
  assert.throws(() => render(ready + '\nDraft note: unresolved.\n', template), /draft notes/);
  assert.throws(() => render(ready + '\nContact placeholder\n', template), /draft notes/);
});

for (const page of legalPages) {
  test(`${page.slug} build uses its own canonical Markdown, metadata, and links`, async () => {
    const source = await readFile(new URL(`../../legal/${page.slug}.md`, import.meta.url), 'utf8');
    const actualTemplate = await readFile(new URL('../templates/legal.html', import.meta.url), 'utf8');
    const output = await readFile(new URL(`../dist/${page.slug}/index.html`, import.meta.url), 'utf8');
    assert.equal(output, renderLegal(source, actualTemplate, page));
    assert.equal(await readFile(new URL(`../dist/${page.slug}.md`, import.meta.url), 'utf8'), source);
    assert.ok(output.includes(`href="https://lune.computer/${page.slug}"`));
    assert.ok(output.includes(`href="/${page.slug}.md"`));
    assert.ok(output.includes(`/commits/main/legal/${page.slug}.md`));
    assert.doesNotMatch(output, /\{\{[A-Z]+\}\}/);
  });
}

test('legal page identity cannot escape its URL or HTML context', () => {
  assert.throws(() => render(metadata + '# Test', template, {slug: '../elsewhere'}), /slug/);
  const html = render(metadata + '# Test', '<title>{{TITLE}}</title><meta content="{{DESCRIPTION}}">', {
    title: '<script>bad</script>', description: '" onload="bad',
  });
  assert.doesNotMatch(html, /<script>|content="" onload/);
  assert.match(html, /&lt;script&gt;/);
});
