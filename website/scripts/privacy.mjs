import MarkdownIt from 'markdown-it';

const markdown = new MarkdownIt({html: false, linkify: false, typographer: false});
const escape = markdown.utils.escapeHtml;

export function renderPrivacy(source, template, {production = false} = {}) {
  const match = source.match(/^---\nstatus: (draft|published)\nrevised: (\d{4}-\d{2}-\d{2})(?:\neffective: (\d{4}-\d{2}-\d{2}))?\n---\n/);
  if (!match) throw new Error('Privacy policy requires status and ISO revision date metadata.');
  const [, status, revised, effective] = match;
  for (const date of [revised, effective].filter(Boolean)) {
    if (new Date(date).toISOString().slice(0, 10) !== date) throw new Error('Invalid policy date.');
  }
  if (status === 'published' && (!effective || /\bdraft\b|placeholder/i.test(source))) {
    throw new Error('Published privacy policy must have an effective date and no unresolved draft notes.');
  }
  if (production && status !== 'published') {
    throw new Error('Privacy policy is a draft. Local builds are available; production deployment is blocked.');
  }
  const tokens = markdown.parse(source.slice(match[0].length), {});
  const sections = [];
  const ids = new Set();
  let titles = 0;
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token.type !== 'heading_open') continue;
    const label = tokens[i + 1].content;
    if (token.tag === 'h1') titles++;
    const base = label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'section';
    let id = base;
    for (let suffix = 2; ids.has(id); suffix++) id = `${base}-${suffix}`;
    ids.add(id);
    token.attrSet('id', id);
    if (token.tag === 'h2') sections.push(`<li><a href="#${id}">${escape(label)}</a></li>`);
  }
  if (titles !== 1) throw new Error('Privacy policy must contain exactly one page title.');
  const values = {
    CONTENT: markdown.renderer.render(tokens, markdown.options, {}),
    TOC: sections.join('\n'),
    REVISION: revised,
    STATUS: status === 'published' ? `<span class="status">Effective ${effective}</span>` : '',
    ROBOTS: status === 'draft' ? '<meta name="robots" content="noindex, nofollow">' : '',
  };
  return template.replace(/\{\{([A-Z]+)\}\}/g, (_, key) => {
    if (!(key in values)) throw new Error(`Unknown privacy template field: ${key}`);
    return values[key];
  });
}
