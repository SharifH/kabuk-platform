# KabuK Platform — marketing website

Standalone, static marketing site for **KabuK Platform**, the technology foundation developed by **KabuK Style Inc.** It is deliberately separate from the KabuK Exchange website. KabuK Exchange is the distribution product built on this foundation.

Plain HTML, CSS and vanilla JavaScript with JSON configuration. No framework, no npm, no runtime build. Five languages ship with crawlable URLs: English (`/`), Japanese (`/ja/`), Korean (`/ko/`), Traditional Chinese for Taiwan (`/zh-tw/`) and Arabic RTL (`/ar/`).

> **Pre-launch build.** Contact addresses, the canonical domain and the privacy notice are placeholders, and non-English copy is a draft. See `docs/CHANGELOG.md` → *Unresolved assumptions & placeholders*.

## Run locally

```bash
python3 -m http.server 8000      # from this folder
# open http://localhost:8000/
```

Serve over HTTP (not `file://`). The pages use root-absolute paths, and the form reads `site-config.json` with `fetch`.

## Structure

| Path | What it is |
|---|---|
| `index.html`, `solutions/`, `technology/`, `why-platform/`, `about/`, `contact/`, `privacy/`, `404.html` | English pages (generated) |
| `ja/`, `ko/`, `zh-tw/`, `ar/` | Localized copies of every page (generated) |
| `assets/css/tokens.css` | Design tokens from the KabuK design library (Platform Core theme). See `docs/DESIGN-TOKENS.md` |
| `assets/css/site.css` | Components, layout, diagrams, RTL and reduced motion |
| `assets/js/site.js` | Navigation, language memory, reveals, diagram light cycle, contact form |
| `assets/brand/kabuk-logo.png` | Official KabuK brush mark from the design library, used unaltered |
| `i18n/<locale>.json` | All visible copy. `en.json` is the master |
| `site-config.json` | Links, lead routing, capability status and locales. Editable without code |
| `tools/build.py` | Page generator (Python 3.8+, standard library only) |
| `sitemap.xml`, `robots.txt` | Generated. Both stay closed until the domain is verified |
| `docs/` | Changelog, design tokens, test report, translation review inventory |

## Editing content

1. Change copy in `i18n/en.json`, then in the other locale files (same keys).
2. Change links, routing or statuses in `site-config.json`.
3. Run `python3 tools/build.py` and commit the regenerated HTML.

`python3 tools/build.py --check` exits non-zero if any locale is missing a key, which makes it suitable for CI. A missing key falls back to English and is listed in `docs/TRANSLATION_REVIEW_INVENTORY.md`.

**Why a generator?** It is needed for 35 localized pages with shared header and footer, plus per-language SEO metadata (`hreflang`, canonical, `og:locale`). It is not a deploy step: the output is committed, so any static host serves the folder as-is.

### No-code settings (`site-config.json`)

| Key | Effect | Rebuild? |
|---|---|---|
| `urls.exchange`, `urls.hafh`, `urls.corporate` | Footer and cross-product links | Applied at runtime too; rebuild to update the static HTML |
| `leads.routes.*`, `leads.organizationTypeRoute` | Which inbox each organization type's email is addressed to | No (read at runtime) |
| `capabilityStatus.*` | `core` / `development` / `planned` chips on cards and the Technology page | Yes |
| `locales[].review` | `draft` shows the "draft translation" banner; set `approved` after native review | Yes |
| `site.canonicalBase`, `site.canonicalVerified` | Canonical, hreflang and sitemap URLs. `false` adds `noindex` and a closed `robots.txt` | Yes |

Never put secrets in `site-config.json`, because it is publicly served.

## Contact form

The form is `mailto:` only. It validates fields, routes by organization type, then opens the visitor's email app with a prepared message. The button says **Prepare Inquiry Email**, and the confirmation tells visitors to send the email themselves. It never says "submitted". Preselect fields with `/contact/?type=hotel&interest=pricing`.

See `docs/CHANGELOG.md` → *Proposed production form backend* for the server-side path. It is **not implemented**.

## Deploy

Upload the folder to any static host with directory-index routing (Netlify, Vercel, Cloudflare Pages, S3 website endpoint, GitHub Pages). Before launch:

1. Verify the domain → set `site.canonicalVerified: true` → rebuild.
2. Replace example.com lead addresses.
3. Replace `/privacy/` with legal-approved text.
4. Complete native review → set each locale's `review` to `approved` → rebuild.

Host `404.html` as the not-found page.
