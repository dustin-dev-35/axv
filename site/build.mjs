// AXV static site build.
//
// One dependency-free script. No framework, no client-side router, no bundler:
// the site is text, and a reader without JavaScript must still get the argument.
//
// Source of truth for post text is posts/<slug>.md and whitepaper/10-years.md.
// Output is site/_site/. The push of this repository is the publication.

import { readFileSync, writeFileSync, readdirSync, mkdirSync, rmSync, existsSync, copyFileSync } from 'node:fs';
import { join, dirname, basename, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, '..');
const outDir = join(here, '_site');

// Set in the Netlify environment. Absent locally and in a build with no key:
// analytics is then simply absent, which is correct. A key is a publishable
// project key, never a secret, and never a reader identifier.
const posthogKey = process.env.POSTHOG_KEY || '';
const posthogHost = process.env.POSTHOG_HOST || 'https://us.i.posthog.com';

/* ---------------------------------------------------------------- markdown */

const escapeHtml = (s) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const slugify = (s) =>
  s
    .toLowerCase()
    .replace(/[`*_~]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');

function inline(src) {
  const codes = [];
  let text = src.replace(/`([^`]+)`/g, (_, c) => {
    codes.push(c);
    return `\u0000${codes.length - 1}\u0000`;
  });

  text = escapeHtml(text);
  // <https://...> and bare autolinks
  text = text.replace(/&lt;(https?:\/\/[^\s&]+)&gt;/g, (_, u) => `<a href="${u}">${u}</a>`);
  // [label](href)
  text = text.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, label, href) => {
    const external = /^https?:\/\//.test(href);
    const rel = external ? ' target="_blank" rel="noopener noreferrer"' : '';
    return `<a href="${href}"${rel}>${label}</a>`;
  });
  text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/(^|[\s(])\*([^*\n]+)\*/g, '$1<em>$2</em>');
  text = text.replace(/~~([^~]+)~~/g, '<del>$1</del>');

  return text.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${escapeHtml(codes[Number(i)])}</code>`);
}

function splitRow(line) {
  return line
    .replace(/^\s*\|/, '')
    .replace(/\|\s*$/, '')
    .split('|')
    .map((c) => c.trim());
}

const isTableDivider = (line) => /^\s*\|?[\s:-]*-[\s:|-]*\|[\s:|-]*$/.test(line) && line.includes('-');

function renderMarkdown(src, { collectSections = [] } = {}) {
  const lines = src.replace(/\r\n/g, '\n').split('\n');
  const out = [];
  const usedIds = new Map();
  let currentSection = null;

  const flushParagraph = (buffer) => {
    if (!buffer.length) return;
    out.push(`<p>${inline(buffer.join(' '))}</p>`);
  };

  for (let i = 0; i < lines.length; ) {
    const line = lines[i];

    if (!line.trim()) {
      i += 1;
      continue;
    }

    // Fenced code
    if (/^```/.test(line)) {
      const lang = line.slice(3).trim();
      const body = [];
      i += 1;
      while (i < lines.length && !/^```/.test(lines[i])) body.push(lines[i++]);
      i += 1;
      out.push(
        `<pre><code${lang ? ` class="language-${lang}"` : ''}>${escapeHtml(body.join('\n'))}</code></pre>`
      );
      continue;
    }

    // A section anchor written as raw HTML: <a id="roads-not-taken"></a>
    const anchor = line.match(/^\s*<a id="([A-Za-z0-9_-]+)"><\/a>\s*$/);
    if (anchor) {
      const id = anchor[1];
      collectSections.push(id);
      out.push(`<a id="${id}" class="section-anchor" data-section-id="${id}"></a>`);
      i += 1;
      continue;
    }

    // Heading
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      flushParagraph([]);
      const depth = heading[1].length;
      const text = heading[2].trim();
      let id = slugify(text.replace(/<[^>]+>/g, ''));
      const count = usedIds.get(id) || 0;
      usedIds.set(id, count + 1);
      if (count) id = `${id}-${count}`;
      out.push(`<h${depth} id="${id}">${inline(text)}</h${depth}>`);
      i += 1;
      continue;
    }

    // Table
    if (line.trim().startsWith('|') && isTableDivider(lines[i + 1] || '')) {
      const header = splitRow(line);
      i += 2;
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) rows.push(splitRow(lines[i++]));
      const head = header.map((c) => `<th>${inline(c)}</th>`).join('');
      const body = rows
        .map((r) => `<tr>${header.map((_, c) => `<td>${inline(r[c] || '')}</td>`).join('')}</tr>`)
        .join('\n');
      out.push(`<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>\n${body}\n</tbody></table></div>`);
      continue;
    }

    // Unordered list
    if (/^\s*[-*]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ''));
        i += 1;
      }
      out.push(`<ul>\n${items.map((it) => `  <li>${inline(it)}</li>`).join('\n')}\n</ul>`);
      continue;
    }

    // Ordered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ''));
        i += 1;
      }
      out.push(`<ol>\n${items.map((it) => `  <li>${inline(it)}</li>`).join('\n')}\n</ol>`);
      continue;
    }

    // Blockquote
    if (/^\s*>\s?/.test(line)) {
      const body = [];
      while (i < lines.length && /^\s*>\s?/.test(lines[i])) {
        body.push(lines[i].replace(/^\s*>\s?/, ''));
        i += 1;
      }
      out.push(`<blockquote>${renderMarkdown(body.join('\n'), { collectSections })}</blockquote>`);
      continue;
    }

    // Paragraph
    const buffer = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !/^(#{1,6})\s+/.test(lines[i]) &&
      !/^```/.test(lines[i]) &&
      !/^\s*[-*]\s+/.test(lines[i]) &&
      !/^\s*\d+\.\s+/.test(lines[i]) &&
      !/^\s*>\s?/.test(lines[i]) &&
      !/^\s*<a id="/.test(lines[i]) &&
      !(lines[i].trim().startsWith('|') && isTableDivider(lines[i + 1] || ''))
    ) {
      buffer.push(lines[i++]);
    }
    flushParagraph(buffer);
  }

  return out.join('\n');
}

/* ------------------------------------------------------------- front matter */

// Deliberately minimal: scalars and "- " lists. AXV front matter is ours, so
// a full YAML parser would be a dependency with no user.
function parseFrontMatter(raw) {
  const match = raw.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) return { data: {}, body: raw };
  const data = {};
  let key = null;
  for (const line of match[1].split('\n')) {
    const item = line.match(/^\s*-\s+(.*)$/);
    if (item && key) {
      data[key] = Array.isArray(data[key]) ? [...data[key], unquote(item[1])] : [unquote(item[1])];
      continue;
    }
    const pair = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!pair) continue;
    key = pair[1];
    data[key] = unquote(pair[2]);
  }
  return { data, body: raw.slice(match[0].length) };
}

const unquote = (v) => v.trim().replace(/^["']|["']$/g, '');

/* ------------------------------------------------------------------ layout */

const STYLES = `
:root{--ink:#14161a;--muted:#5b6470;--line:#e3e7ec;--bg:#fdfdfc;--accent:#1a4f8a;--code:#f4f6f8}
@media (prefers-color-scheme:dark){:root{--ink:#e8eaed;--muted:#9aa4b1;--line:#2a2f36;--bg:#101215;--accent:#7fb2f0;--code:#1a1e24}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:44rem;margin:0 auto;padding:2.5rem 1.25rem 5rem}
header.site{border-bottom:1px solid var(--line);margin-bottom:2rem;padding-bottom:1rem}
header.site a{color:var(--ink);text-decoration:none;font-weight:600}
nav.toc{font-size:.95rem;color:var(--muted)}
nav.toc ol{padding-left:1.2rem}
h1{font-size:1.9rem;line-height:1.25;margin:0 0 1rem}
h2{font-size:1.3rem;margin:2.5rem 0 .75rem;padding-top:.5rem;border-top:1px solid var(--line)}
h3{font-size:1.08rem;margin:1.75rem 0 .5rem}
p,li{margin:0 0 1rem}
a{color:var(--accent)}
code{background:var(--code);padding:.1em .35em;border-radius:4px;font-size:.88em;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:var(--code);padding:1rem;border-radius:6px;overflow:auto;font-size:.85rem;line-height:1.5}
pre code{background:none;padding:0}
blockquote{border-left:3px solid var(--line);margin:0 0 1rem;padding-left:1rem;color:var(--muted)}
.table-wrap{overflow-x:auto;margin:0 0 1.25rem}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border:1px solid var(--line);padding:.45rem .6rem;text-align:left;vertical-align:top}
th{background:var(--code)}
.meta{color:var(--muted);font-size:.95rem;margin:0 0 1.5rem}
.meta strong{color:var(--ink)}
.section-anchor{display:block;height:0;overflow:hidden}
ul,ol{padding-left:1.3rem}
ul.post-list{list-style:none;padding-left:0}
ul.post-list li{margin:0 0 1.5rem;padding-bottom:1.25rem;border-bottom:1px solid var(--line)}
ul.post-list .meta{display:block}
footer.site{border-top:1px solid var(--line);margin-top:3rem;padding-top:1rem;color:var(--muted);font-size:.9rem}
`.trim();

// Reader events carry a post slug and a section id. Nothing else, ever:
// no email, no name, no comment body, no reader identifier.
const ANALYTICS = posthogKey
  ? `<script>window.AXV={key:${JSON.stringify(posthogKey)},host:${JSON.stringify(
      posthogHost
    )}};</script>
<script src="${posthogHost}/static/array.js"></script>
<script>
(function(){
  if(!window.posthog||!window.AXV)return;
  posthog.init(window.AXV.key,{api_host:window.AXV.host,autocapture:false,capture_pageview:false});
  var slug=document.body.dataset.postSlug||'index';
  var depths={};
  posthog.capture('axv_post_viewed',{post_slug:slug,referrer:document.referrer||null});
  var order=Array.prototype.slice.call(document.querySelectorAll('[data-section-id]'));
  order.forEach(function(el){
    new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(!e.isIntersecting)return;
        var id=el.dataset.sectionId;
        if(depths[id])return;
        depths[id]=order.indexOf(el)+1;
        posthog.capture('axv_section_reached',{post_slug:slug,section_id:id,depth:depths[id]});
      });
    },{rootMargin:'0px 0px -20% 0px'}).observe(el);
  });
})();
</script>`
  : '';

function page({ title, description, body, postSlug = '', nav = '', extraHead = '' }) {
  const slugAttr = postSlug ? ` data-post-slug="${escapeHtml(postSlug)}"` : '';
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(title)} · AXV</title>
${description ? `<meta name="description" content="${escapeHtml(description)}">` : ''}
<link rel="canonical" href="${escapeHtml(siteUrl)}/${postSlug ? `posts/${postSlug}/` : ''}">
<meta property="og:title" content="${escapeHtml(title)}">
${description ? `<meta property="og:description" content="${escapeHtml(description)}">` : ''}
<meta property="og:type" content="article">
<style>${STYLES}</style>
${extraHead}
</head>
<body${slugAttr}>
<div class="wrap">
<header class="site"><a href="/">AXV</a>${nav}</header>
${body}
<footer class="site">AXV reads arXiv papers in ML and AI and names the roads not taken. Every claim traces to a memo and a run.</footer>
</div>
${ANALYTICS}
</body>
</html>
`;
}

let siteUrl = 'https://axv.sh';

function readDoc(path) {
  const raw = readFileSync(path, 'utf8');
  const { data, body } = parseFrontMatter(raw);
  return { data, body };
}

function write(relPath, contents) {
  const target = join(outDir, relPath);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, contents);
}

// The description is the first real prose paragraph, which in a post comes after the
// title and the Paper/Read metadata block. Reaching into the header block instead
// ships "Paper: <title> - <authors> [arXiv:...]" as the meta description, raw
// markdown link syntax and all.
function firstParagraphText(markdownBody, limit = 200) {
  const paragraphs = markdownBody
    .replace(/^\s*<a id="[^"]+"><\/a>\s*$/gm, '')
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);

  const prose = paragraphs.find((p) => {
    if (/^#{1,6}\s/.test(p)) return false; // heading
    if (/^\*\*(Paper|Read):\*\*/.test(p)) return false; // header metadata block
    return true;
  });

  if (!prose) return '';

  const flat = prose
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1') // [label](href) -> label
    .replace(/<((?:https?:\/\/)[^>\s]+)>/g, '$1') // <url> -> url
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/[*_`>]/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  if (flat.length <= limit) return flat;
  const cut = flat.slice(0, limit - 1);
  const lastSpace = cut.lastIndexOf(' ');
  return `${(lastSpace > limit * 0.6 ? cut.slice(0, lastSpace) : cut).trimEnd()}…`;
}

/* ------------------------------------------------------------------- build */

rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });

if (process.env.AXV_SITE_URL) siteUrl = process.env.AXV_SITE_URL.replace(/\/+$/, '');

// netlify.toml sets AXV_SITE_URL; a local build falls back to the placeholder.
if (existsSync(join(here, 'CNAME'))) {
  siteUrl = `https://${readFileSync(join(here, 'CNAME'), 'utf8').trim()}`;
}

const posts = [];
const postsDir = join(repoRoot, 'posts');
if (existsSync(postsDir)) {
  for (const file of readdirSync(postsDir).filter((f) => f.endsWith('.md')).sort()) {
    const doc = readDoc(join(postsDir, file));
    posts.push({ slug: doc.data.slug || basename(file, '.md'), ...doc });
  }
}

const whitepaperPath = join(repoRoot, 'whitepaper', '10-years.md');
const hasWhitepaper = existsSync(whitepaperPath);

const nav =
  `<nav class="toc">${posts.length ? `<span> · <a href="/posts/${posts[0].slug}/">Latest post</a>` : ''}${
    hasWhitepaper ? ' · <a href="/whitepaper/">10 Years in 1 Paper</a>' : ''
  }</span>`;

// ---- posts
for (const post of posts) {
  const sections = [];
  const content = renderMarkdown(post.body, { collectSections: sections });
  const description = firstParagraphText(post.body);
  const declared = Array.isArray(post.data.section_ids) ? post.data.section_ids : [];
  const missing = declared.filter((id) => !sections.includes(id));

  const body = `${content}`;
  write(
    `posts/${post.slug}/index.html`,
    page({
      title: post.data.title || post.slug,
      description,
      body,
      postSlug: post.slug,
      nav,
      extraHead: `<meta property="article:published_time" content="${escapeHtml(post.data.read_date || '')}">`,
    })
  );

  if (missing.length) {
    console.error(
      `FAIL ${post.slug}: front matter declares section_ids with no matching anchor: ${missing.join(', ')}`
    );
    process.exitCode = 1;
  } else {
    console.log(`ok   posts/${post.slug}/  (${sections.length} section ids: ${sections.join(', ')})`);
  }
}

// ---- white paper: one long page, read as a document
if (hasWhitepaper) {
  const doc = readDoc(whitepaperPath);
  const content = renderMarkdown(doc.body);
  write('whitepaper/index.html', page({ title: '10 Years in 1 Paper', description: doc.data.description || '', body: content, nav }));
  console.log('ok   whitepaper/');
}

// ---- index. Authored as HTML, not markdown: the post list is pre-built markup
// and running it through the markdown renderer would escape it into visible tags.
const items = posts
  .map(
    (p) => `  <li>
    <a href="/posts/${p.slug}/">${escapeHtml(p.data.title || p.slug)}</a>
    <span class="meta">${escapeHtml(p.data.read_date || '')} · confidence ${escapeHtml(
      p.data.confidence || 'unknown'
    )} · experiment ${escapeHtml(p.data.experiment_status || 'unknown')}</span>
    <span class="meta">${escapeHtml(firstParagraphText(p.body, 180))}</span>
  </li>`
  )
  .join('\n');

const indexBody = `<h1 id="axv">AXV</h1>
<p>AXV reads arXiv papers in ML and AI, compresses each advancement with the credible
alternative routes and what each one costs, publishes one post per paper, and folds the
corpus into a decade-long white paper.</p>
<p>The thing AXV is after is not the summary of a paper. It is the <strong>roads not
taken</strong>.</p>
<h2 id="posts">Posts</h2>
${posts.length ? `<ul class="post-list">\n${items}\n</ul>` : '<p>No posts published yet.</p>'}
${
  hasWhitepaper
    ? `<h2 id="the-white-paper">The white paper</h2>
<p><a href="/whitepaper/">10 Years in 1 Paper</a> — the living compression of the corpus:
what the decade turned on, what it cost, and what did not work.</p>`
    : ''
}`;

write(
  'index.html',
  page({
    title: 'AXV',
    description: 'AXV reads arXiv papers in ML and AI and names the roads not taken.',
    nav,
    body: indexBody,
  })
);
console.log('ok   index.html');

// ---- sitemap, robots, headers
const urls = [
  `${siteUrl}/`,
  ...posts.map((p) => `${siteUrl}/posts/${p.slug}/`),
  ...(hasWhitepaper ? [`${siteUrl}/whitepaper/`] : []),
];
write('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls
  .map((u) => `  <url><loc>${u}</loc></url>`)
  .join('\n')}\n</urlset>\n`);
write('robots.txt', `User-agent: *\nAllow: /\nSitemap: ${siteUrl}/sitemap.xml\n`);

if (existsSync(join(here, '_headers'))) copyFileSync(join(here, '_headers'), join(outDir, '_headers'));
if (existsSync(join(here, 'assets'))) copyFileSync(join(here, 'assets'), join(outDir, 'assets'), (err) => {
  if (err) console.error(`assets copy failed: ${err.message}`);
});
if (existsSync(join(here, 'CNAME'))) copyFileSync(join(here, 'CNAME'), join(outDir, 'CNAME'));

console.log(
  posthogKey
    ? 'analytics: PostHog key present, section events wired'
    : 'analytics: no POSTHOG_KEY, site builds without analytics (expected locally)'
);
