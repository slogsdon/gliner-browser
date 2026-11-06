# GLiNER Browser — microsite

Static microsite for [GLiNER Browser](https://github.com/slogsdon/gliner-browser),
served at `https://projects.logsdon.io/gliner-browser/`.

Source revision: `ff41760bd279c71fc2e3a0820a936540c34c11ff` (branch `feature/website`
of `slogsdon/gliner-browser`, HEAD at the time of writing; `git log -1 --format=%cs`
is `2026-09-18`, which is the `lastmod` in `site.json`). All product content on the
site is derived from that revision: `README.md`, `pyproject.toml`,
`agent-skill/gliner-browser/SKILL.md`, and the CLI sources
(`src/gliner_browser/{cli,runtime,resolver}.py`).

## Build

Node 26.12.0, PHP 8.3+, and Composer are required.

```sh
cd website
composer install --no-interaction --prefer-dist
npm install
node scripts/build-site.ts          # SITE_NOINDEX=1 by default: preview, noindex
SITE_NOINDEX=0 node scripts/build-site.ts   # indexable production artifact
```

Output is a physical subtree at `website/dist/<slug>/`, plus `dist/_headers` in
preview builds. Nothing else is written at the `dist/` root: the hub owns
`/robots.txt`, `/sitemap.xml`, and the slashless `/<slug>` redirect.

Packaging (local only; neither command deploys):

```sh
npm ci
npx --no-install cf build --mode microsite
npx --no-install cf build --mode microsite-production
```

## One file drives the site

`site.json` holds the four values the build and the pages need — `slug`, `name`,
`origin`, `lastmod` — plus the `source` URL. `scripts/build-site.ts` validates
them, exports them to the PHP layout as `SITE_SLUG`, `SITE_NAME`, `SITE_ORIGIN`
and `SITE_NOINDEX`, and mounts every emitted URL under `/<slug>/`. The layout
throws if they are missing, so nothing falls back to a hard-coded project name.

`cloudflare.config.ts` keeps the Worker name and route pattern as literals on
purpose: they are the deployment identity, not site content, and the file is
loaded by the Cloudflare CLI outside the build script. Production is
`gliner-browser-microsite` on `projects.logsdon.io/gliner-browser/*`; every other
mode builds `gliner-browser-microsite-preview` with no triggers and workers.dev
enabled.

## What the build asserts

`scripts/build-site.ts` fails the build unless all of the following hold:

- `index.html`, `404.html`, `sitemap.xml`, `assets/site.css`, `assets/tokens.css`,
  `assets/fonts/*` exist and are non-empty.
- No `_redirects`, `robots.txt`, `sitemap.xml`, `index.html`, or `404.html` at the
  `dist/` root; the root holds only `<slug>/` (and `_headers` when `SITE_NOINDEX=1`).
- Every HTML page has exactly one `<h1>`, a unique `<title>` containing the project
  name, a meta description, the skip link, the `main` landmark, and the primary
  `nav`.
- Canonical and `og:url` equal `https://projects.logsdon.io/<slug>/<path>`; the 404
  carries neither and is always noindex.
- The `noindex` meta matches `SITE_NOINDEX`, and the footer links both
  `https://projects.logsdon.io/` and `https://shane.logsdon.io/`.
- No `href`/`src` is root-relative outside `/<slug>/`, and every local link and
  asset target exists in the artifact.
- The sitemap lists exactly the canonical pages, with `lastmod` set to
  `site.json`'s `lastmod`.

The Google Fonts `@import` is stripped from the copied `tokens.css` (fonts are
served locally) and `/assets/` inside the copied CSS is rewritten to
`/<slug>/assets/`.

## Content and design provenance

- Pages: `pages/index.php` is F · Frontispiece (the single entry point, no
  figures). `pages/getting-started.php` is D · Assembly Order: seven numbered
  steps in dependency order — interpreter and platform, first-download
  requirements, install, session and observation, an action on an observed
  element, configuration, then stopping and the safety limits. `pages/404.html.php`
  is G · Recovery.
- No hosted demo, sandbox, or backend is described or linked, because the product
  has none: the CLI, Chromium, and the model run on the reader's machine. The site
  therefore only quotes commands; it does not offer a way to run them here.
- Status qualifiers are kept as the source states them: "Early development. The
  command interface and behavior may change." (README), version 0.1.0
  (`pyproject.toml`), MIT (`LICENSE`), Python `>=3.11,<3.14`, macOS or Linux with
  Windows unsupported because the daemon is a Unix-domain socket.
- `public/assets/tokens.css`, the fonts, `assets/fonts/LICENSES.txt`, and the
  first part of `public/assets/site.css` are copied from the collection hub
  (`projects.logsdon.io`) at its `main`; `design/provenance.json` is copied with
  them and records the personal-site hashes (its paths are hub-relative). The
  appended "Project microsite additions" section was already present in the seeded
  skeleton and is unchanged by this site: prose, code, tables, facts, link lists,
  and the harness block cover every page here. No new colors and no new rule
  weights; everything comes from the tokens.
- `composer.lock` pins `slogsdon/flat-file` to the same reference as the hub
  (`dev-code-highlight`, `3ba5285e424aa376af324db0424f53c33a2c07a5`).
- `package.json` pins the hub's `cf`, `@cloudflare/vite-plugin`, and `vite`
  versions exactly. This site has no client JavaScript.

## Verified here

- `composer install`, `npm install`, and `node scripts/build-site.ts` (preview and
  `SITE_NOINDEX=0`), plus every artifact assertion listed above.
- The absence of out-of-namespace root-relative URLs, the presence of
  `dist/_headers` only in preview builds, and the preview/production indexing
  difference.
- `npx --no-install cf build --mode microsite` and
  `npx --no-install cf build --mode microsite-production` (packaging only). The
  production Worker config was read back and carries the expected name, route
  pattern, and no `domains:` key.

## Not verified here (Unverified)

No product command on the site was executed while building it: the tool was not
installed and no model files were downloaded. The getting-started page states this
above its first step. Every command below is quoted from the source revision.

- `git clone https://github.com/slogsdon/gliner-browser`, `cd gliner-browser`,
  `uv sync`, `uv run playwright install chromium` — from `README.md` (Install).
  Not run: installing the product and downloading PyTorch, Chromium, and the model
  is out of scope for the site build.
- `uv run gliner-browser --help` — from `README.md` (Commands). Not run.
- The quick-start block `start`, `open https://example.com`, `observe`,
  `find "more information link"`, `stop` — from `README.md` (Quick start), quoted
  verbatim on the getting-started page. Not run; the observed-element walkthrough
  is documentation, not an execution.
- `uv run gliner-browser click e4`, `fill e7 person@example.com`,
  `select e9 monthly` and the natural-language variants
  (`click "continue to checkout"`, `fill "email address" person@example.com`) —
  from `README.md` (Quick start). The element IDs are the README's examples, not
  IDs observed here.
- `uv run gliner-browser stop` and `status`; the `already_stopped` response — from
  `README.md` (Commands) and `src/gliner_browser/cli.py`. Read, not exercised.
- `uv --project "$GLINER_BROWSER_PROJECT" run gliner-browser ...` — from
  `README.md` (Configuration). Not run.
- The configuration table (`GLINER_BROWSER_STATE_DIR`, `GLINER_BROWSER_MODEL`,
  `GLINER_BROWSER_TIMEOUT`, defaults `~/.local/state/gliner-browser`,
  `fastino/gliner2.5-multi-v1`, `180`) — from `README.md` (Configuration) and
  `cli.py`. Read, not exercised.
- The `observe` payload description (title, URL, element `id`/`role`/`name`/`tag`/
  `href`, a `total`, `--limit` default 100) and the `find` confidence fields
  (combined, `lexical_confidence`, `gliner_confidence`) — from
  `src/gliner_browser/runtime.py` and `resolver.py`. Read, not exercised.
- Stale-ID behavior ("missing or stale; run observe again") — from `runtime.py`
  (`_element`). Read, not exercised.
- The first semantic lookup loading the model, and the rough one-minute first-call
  wait — from `agent-skill/gliner-browser/SKILL.md` and `resolver.py`
  (`_load` is lazy). Read, not timed; no model files were present or fetched.
- The model download from Hugging Face on first lookup and the checkpoint's
  Apache-2.0 license — from `README.md`. The model card was not fetched.
- The daemon log path and the start-failure message — from `cli.py` (`start`,
  `serve`). Read, not exercised.
- Linux support — the README lists macOS or Linux; neither platform was exercised here.

## Deployment

Not performed from this repository: no `cf deploy`, no `cf previews deploy`, no
Cloudflare API call. Publication is the collection's T09 step and runs through the
hub's own workflow; this repository only produces the artifact and the Worker
configuration. The hub owns the hostname (`projects.logsdon.io`), the sitemap
index, and the slashless redirect; this Worker claims only
`projects.logsdon.io/gliner-browser/*`.
