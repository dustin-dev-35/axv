// Verify the live AXV site against the publication acceptance criteria.
//
// Usage:
//   node scripts/verify-live-site.mjs <base-url> [post-slug]
//
// Exits 0 only when every check passes. Prints a table, because a deploy that is
// up but wrong is the failure this exists to catch: a canonical URL pointing at
// a hostname that does not resolve, a section that silently stopped rendering,
// or a missing alternatives section all leave a green build and a dead page.
//
// Dependency-free on purpose. A check that needs a package is a check that does
// not get run at the moment it is needed.

const SECTION_IDS = [
  'tldr',
  'what-advanced',
  'how-it-works',
  'roads-not-taken',
  'evidence-strength',
  'what-axv-did',
  'links',
];

const base = (process.argv[2] || '').replace(/\/+$/, '');
const slug = process.argv[3] || 'overlapping-eval-windows-are-not-independent-tests';

if (!base) {
  console.error('usage: node scripts/verify-live-site.mjs <base-url> [post-slug]');
  process.exit(2);
}

const results = [];
const check = (name, ok, detail = '') => results.push({ name, ok: !!ok, detail });

async function get(path) {
  const url = `${base}${path}`;
  const res = await fetch(url, { redirect: 'follow', headers: { 'user-agent': 'axv-verify' } });
  const text = res.ok ? await res.text() : '';
  return { url, status: res.status, ok: res.ok, text };
}

const post = await get(`/posts/${slug}/`);

check('post page loads', post.ok, `${post.status} ${post.url}`);

if (post.ok) {
  for (const id of SECTION_IDS) {
    // An anchor with nothing after it resolves to an empty target, so what
    // follows the anchor is checked, not just the anchor. The block may be a
    // heading or a paragraph: the TL;DR section is a paragraph, the rest are
    // headings, and both are content a reader must be able to arrive at.
    const re = new RegExp(`<a id="${id}"[^>]*></a>\\s*<(h2|h3|p|ul|ol|blockquote|pre)[\\s>]`);
    const ok = re.test(post.text);
    check(`section ${id}`, ok, ok ? 'anchor resolves to content' : 'anchor resolves to nothing');
  }

  // Analytics: the whole point of the alternatives section is measuring whether
  // readers reach it, so an absent snippet is a real failure, not a cosmetic one.
  check('section analytics present', post.text.includes('axv_section_reached'), 'PostHog event wiring');

  // A canonical URL on a hostname that does not resolve is a published error
  // that a 200 cannot detect, so it is compared here rather than trusted.
  const canonical = post.text.match(/<link rel="canonical" href="([^"]+)">/);
  const canonicalOrigin = canonical ? new URL(canonical[1]).origin : '';
  check(
    'canonical URL points at the site being served',
    canonicalOrigin === base,
    canonical ? `${canonical[1]} (origin ${canonicalOrigin})` : 'no canonical link'
  );
}

const whitepaper = await get('/whitepaper/');
check('white paper page loads', whitepaper.ok, `${whitepaper.status} ${whitepaper.url}`);

const index = await get('/');
check('front page loads', index.ok, `${index.status} ${index.url}`);

const sitemap = await get('/sitemap.xml');
check(
  'sitemap lists the post and the white paper',
  sitemap.ok && sitemap.text.includes(`/posts/${slug}/`) && sitemap.text.includes('/whitepaper/'),
  sitemap.ok ? 'parsed' : `${sitemap.status}`
);

const width = Math.max(...results.map((r) => r.name.length));
for (const r of results) {
  console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${r.name.padEnd(width)}  ${r.detail}`);
}

const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} checks passed against ${base}`);
process.exit(failed.length ? 1 : 0);
