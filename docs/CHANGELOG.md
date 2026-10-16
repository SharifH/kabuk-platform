# Changelog — KabuK Platform website

## 1.1.0 — 2026-10-16 (unreleased; pending commercial/product approval)

### Changed — hotel-first positioning
Copy from `01_KabuK_Platform_Website_Copy.md`, applied per `03_Claude_Prompt_Platform_Website.md`. Routes, navigation behaviour, the contact form, localization and the design system are unchanged. Claims and readiness are tracked in `docs/HOTEL_FIRST_READINESS.md`.

- **Home:** new hero ("Your Hotel. Your Inventory. Your Control."), six hotel benefits, the hotel → Platform → HafH / Omakastay / KabuK Exchange ecosystem diagram, transparency and control with a data-coverage qualifier, gated Coming soon modules (market intelligence, white-label), onboarding steps and the hotel audience. The value pillars and capability cards were removed; that content remains on Why and Technology.
- **Solutions:** hotel-benefits hero, six benefits (`#benefits`), a controls and transparency FAQ (`#faq`), the distribution ecosystem (`#ecosystem`), then the existing segment rows under their former heading. The dark KabuK Exchange note was replaced by the ecosystem section.
- **Why, About, Contact:** hotel-first hero and lead copy. About adds a fourth family card for consumer products (HafH and Omakastay, the latter planned). The Contact form adds the interests hotel onboarding, market insights and white-label.
- **Global:** the header CTA is "Connect Your Property" (`/contact/?type=hotel&interest=onboarding`), the Solutions menu adds Hotel benefits and Distribution ecosystem, the closing CTA has primary and secondary actions, and the footer tagline changed. SEO titles and descriptions were updated for Home, Solutions, Why, About and Contact.
- **Config:** new `channelStatus` and `modules` keys. Unknown module values (including `live`) are treated as hidden.
- **i18n:** 113 new or changed strings per locale were drafted for ja, ko, zh-TW and ar. They are unreviewed, like the rest of those locales.

### Changed — owner sign-off (2026-10-16)
- HafH and KabuK Exchange channel status changed to `pilot`.
- Rate transparency is not available yet, so it is now gated by the new `modules.rateTransparency` (`comingSoon`): Coming soon chips, the FAQ answers "Not yet", and "rate" was removed from visibility claims in meta descriptions, the control lead, and the Solutions hero and hotel topics.
- Omakastay now targets travelers from North America and Europe.
- The white-label copy now mentions planned no-cost and low-cost packages. No prices are given.
- Footer: KabuK Platform is "a KabuK Style Inc. product".
- Inquiry email: all `leads.routes` now point to `network@kabuk.com`, replacing the `example.com` placeholders. `tools/qa_test.py` expectations were updated to match.
- Single onboarding covering all KabuK products, subject to eligibility: confirmed. The existing copy already says this, so it is unchanged.
- **No setup fee for hotels** (confirmed): added as a notice under the Home onboarding steps and as the first Solutions FAQ item, in all locales.

### Fixed
- Contact select options were taken from each locale's own dictionary, so an option missing from a translation was silently dropped instead of reported. They now follow the English keys.

## 1.0.1 — 2026-10-14

### Fixed
- **No CSS, JS or logo on GitHub Pages** (`https://sharifh.github.io/kabuk-platform/`). Pages were generated with root-absolute paths (`/assets/css/site.css`), which a project site resolves against the domain root, where they 404. `tools/build.py` now writes page-relative paths (`assets/…`, `../assets/…`, `../../assets/…`). `site.js` resolves `site-config.json` from `<html data-root>`, the stored-language redirect is subpath-aware, and `404.html` uses `<base href>` from the new `site.deployBasePath` setting. Verified with the site served under `/kabuk-platform/` locally: every page styled and no asset 404s. Also verified at the root: 24/24 tests pass.
- Added `.nojekyll` for GitHub Pages.

## 1.0.0-rc (pre-launch) — 2026-10-14

Implements `CLAUDE_CODE_KABUK_PLATFORM_IMPLEMENTATION_PROMPT.md`, using `KABUK_PLATFORM_COPY_RECOMMENDATIONS.md` as the editorial reference and the **KabuK Platform design system** (KabuK design library) for all visual decisions. The KabuK Exchange source was not touched.

### Audit of the starter (before)

| Area | Starter state | Limitation |
|---|---|---|
| Pages | 7 English pages, hand-duplicated header and footer | Markup drift risk; no shared source |
| Localization | English only | Brief requires en/ja/ko/zh-TW/ar with RTL |
| Brand | Typographic "KabuK Platform" wordmark, 800-weight type, navy and pill-like 9–15px radii, drop shadows, radial gradients | Not aligned with the design library (Inter 600 max, 4–12px radii, borders over shadows, no decorative gradients) |
| Visuals | One flex row "Supply → Exchange → Distributors" with an arrow glyph | Platform shown as a caption, not a foundation; no service architecture; no motion or reduced-motion handling |
| Copy | Partly matched the copy doc; some unqualified claims ("helping travel businesses build and scale") | No maturity labelling (exists / in development / planned) |
| Navigation | Flat links; "Why Platform" label | No Solutions/Technology menus; no mobile menu |
| Accessibility | Skip link hidden off-screen only; no focus styles; no reduced-motion handling | Fails keyboard and focus requirements |
| Contact | mailto with "Open email draft"; single recipient; no consent, region or org type | Brief requires categories, consent and accurate labelling |
| Config | `site-config.json` with example.com addresses | Kept, extended |
| Privacy | Placeholder | Kept, now prominently marked DRAFT |
| SEO | Single canonical per page; no hreflang, sitemap or robots | Added (see below) |

### Added

- **Design system implementation** (`assets/css/tokens.css`): primitives, semantic Light tokens, a `.theme-dark` scope (KabuK Dark) and documented web extensions. Platform Core proportions: Warm White and white surfaces, ink text, KabuK Blue `#38C3E2` for identity marks only (KabuK Bar, active markers, diagram pulses), and Deep Blue `#176B87` for primary actions and links.
- **Lockup**: the official KabuK brush mark (from the design library, unaltered) with a "Platform / by KabuK Style" descriptor. The KabuK Exchange logo is not used anywhere.
- **Visual system 1 — Platform service architecture** (`arch_diagram`): a three-layer diagram. Businesses and products (third parties dashed gray, KabuK Exchange in network blue) sit above KabuK Platform core services (8 nodes, ink outline), which sit above the shared foundation. It has animated connection pulses and a light that cycles across nodes. It is reused in the home hero (compact) and on Technology (full).
- **Visual system 2 — Product relationship** (`rel_diagram`): Supply → KabuK Exchange → Distribution, with **KabuK Platform as a foundation slab beneath Exchange**, not a fourth peer. OTAs and wholesalers are marked "Both sides". PMS, CRS and channel managers appear as connectivity providers, not sellers. A caption states it is illustrative, not live integrations. It is reused on Home, Solutions and About (dark sections), mirrors for Arabic and stacks vertically on mobile.
- **Visual system 3 — Point-to-point vs shared foundation** (Why page), SVG with a flowing-dash animation.
- **Capability status chips**, driven by `site-config.json` → `capabilityStatus`, plus a status legend on Technology (`#status`). Analytics is shown as **In development**, and AI/KAOS workflows as **Planned**.
- **Scope notes** on each Technology domain that turn the copy doc's guardrails into honest public statements. For example: rule-based pricing with no ML optimization; not a licensed payment processor or escrow; no certification claims.
- **Navigation**: Solutions ▾ and Technology ▾ disclosure menus (keyboard, Escape, focus return, click-outside), Why KabuK Platform, About, a language menu and a **Talk to Us** CTA. Below 1080px it becomes a mobile panel with accordions.
- **Footer** per the copy doc §9. KabuK Style Products links (Exchange, HafH, KabuK Style Inc.) come from `site-config.json`. Terms is omitted until approved.
- **Localization**: 5 locales × 7 pages + 404, with per-locale `<html lang/dir>`, title, description, canonical, `hreflang` (+ `x-default`), `og:locale` and locale-specific Noto font families. Arabic is RTL throughout via logical CSS properties, and product names stay in Latin script with `dir="ltr"` isolation. Each translated page carries a draft banner linking to English.
- **Language memory**: an explicit choice is stored in `localStorage` (`kbk-locale`). English pages redirect to the stored locale, and `?lang=en` bypasses this. Crawlers are unaffected. Storage failures are caught.
- **Contact**: name, company, business email, organization type, region, interest area, systems (optional), message and privacy acknowledgement. It has inline localized errors, an error summary and focus management. Routing goes by organization type to `leads.routes` (hotels / tourism / technology / general). Confirmation text follows the copy doc §8 exactly; there is no false "submitted" state.
- **SEO**: per-page titles and descriptions from the copy doc §10, JSON-LD `WebPage`, `sitemap.xml` with hreflang alternates, and `robots.txt`.
- **Pre-launch safety**: while `site.canonicalVerified` is `false`, every page emits `noindex, nofollow` and `robots.txt` disallows crawling.
- **Generator** `tools/build.py` (stdlib only) and generated `docs/TRANSLATION_REVIEW_INVENTORY.md`.

### Changed

- Every page's copy was rewritten from the copy doc. H1: "The technology foundation for connected travel." CTAs: "Talk to Our Team" / "Explore Platform Capabilities". Audience headlines and CTAs follow §5, and the relationship section follows §6.
- "Why Platform" → **Why KabuK Platform**. The CTA says "Talk to Us", and the contact submit button says "Prepare Inquiry Email".
- The privacy page is restructured into a clearly flagged **DRAFT — NOT LEGAL-APPROVED** page that accurately describes current behaviour: no server collection, no analytics cookies, localStorage language memory and Google Fonts.

### Removed

- `styles.css` and `script.js` at the root, replaced by `assets/css/*` and `assets/js/site.js`.
- Decorative gradients, heavy shadows, 800-weight type and the navy palette, which are not part of the design library.

### Decisions requiring approval

1. **Generator script.** The brief allows no build pipeline without justification. `tools/build.py` is an authoring tool only: the output is committed and deploy is static. Justification: 35 localized pages with shared chrome and per-locale SEO.
2. **Logo.** The design library prescribes the official KabuK mark + "Platform" descriptor; the brief suggested a typographic placeholder. Per your choice, the mark is used. A dedicated Platform lockup still needs approval.
3. **Web type scale.** The hero (up to 64px) and section titles (up to 40px) extend the design library's UI `display` 48px for marketing use. Weight stays at 600.
4. **Uppercase eyebrows dropped.** The copy doc shows ALL-CAPS eyebrows, but CSS uppercasing renders "KABUK", which the design library forbids. Eyebrows now use sentence case, as the library's SectionHeading does.

### Unresolved assumptions & placeholders

| Item | Where | Action |
|---|---|---|
| Canonical domain `https://kabukplatform.com` | `site-config.json → site` | Verify ownership, set `canonicalVerified: true`, rebuild |
| Lead inboxes `*@example.com` | `site-config.json → leads.routes` | Replace with monitored KabuK Style inboxes |
| External URLs (Exchange, HafH, kabuk.co.jp) | `site-config.json → urls` | Verify |
| Capability maturity labels | `site-config.json → capabilityStatus` | Product to confirm. Defaults: 5 domains `core`, analytics `development`, AI `planned` |
| Named connectivity types (PMS, CRS, channel managers) | Copy | Generic categories only, no vendor names. Confirm which integrations can be named |
| Business model (internal foundation vs external offering) | Copy says "scope confirmed per engagement" | Confirm with leadership (copy doc §12) |
| Privacy notice, cookie language | `/privacy/` | Legal to supply |
| Google Fonts | All pages | Legal review, or self-host for privacy |
| Team profiles | `/about/` | Editorial intro only. Add approved profiles later |
| Terms page | Footer | Omitted until approved |
| Platform-specific logo and secondary palette | Header/footer | Design to supply. A reversed (white) mark is rendered with a CSS invert until then |
| Translations | `i18n/ja|ko|zh-TW|ar.json` | Native-speaker review; see inventory |
| OG/social image | — | None supplied. Add `og:image` when approved artwork exists |

### Proposed production form backend (NOT implemented)

Replace `mailto:` with a POST to a server-side endpoint, for example a serverless function in front of the CRM:

- Same-origin `POST /api/inquiry` with JSON. Server-side validation mirrors the client rules.
- Spam control: a honeypot field plus a privacy-respecting challenge (for example Turnstile) and rate limiting per IP.
- Store consent text, its version and a timestamp with the lead. Minimise fields and set retention per legal.
- Route by `organizationTypeRoute` on the server. Keep CRM/API credentials in server environment variables only, never in `site-config.json`.
- Only then change the button to **Send Inquiry** and show a success message after a 2xx response.
