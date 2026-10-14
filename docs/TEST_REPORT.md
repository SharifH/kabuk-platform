# Test report — KabuK Platform website

**Date:** 2026-10-14 · **Server:** `python3 -m http.server` (HTTP, not `file://`) · **Browser:** headless Chromium via Playwright.

These are the checks that were run, and nothing more.

## Automated checks

| # | Check | Result |
|---|---|---|
| 1 | JSON validity: `site-config.json`, `i18n/en|ja|ko|zh-TW|ar.json` | Pass (6/6) |
| 2 | `tools/build.py --check`: all 413 strings present in each of 5 locales, 0 English fallbacks | Pass |
| 3 | Every internal `href`/`src` and `#anchor` resolves, across 36 generated pages | Pass (0 broken) |
| 4 | `ja/technology/` has 6 `hreflang` alternates and the correct canonical | Pass |
| 5 | `noindex, nofollow` emitted while the domain is unverified | Pass |
| 6 | Arabic pages render `dir="rtl"` | Pass |
| 7 | No JavaScript errors or console errors (excluding blocked Google Fonts) on 35 pages | Pass |
| 8 | Solutions menu opens with Enter, focus moves into the menu, Escape closes and returns focus | Pass |
| 9 | Skip link is the first Tab stop | Pass |
| 10 | Exchange link resolved from `site-config.json` | Pass |
| 11 | Language menu → 日本語 navigates to `/ja/` | Pass |
| 12 | Stored `ja` preference redirects `/technology/` → `/ja/technology/`; `?lang=en` bypasses it | Pass |
| 13 | `/contact/?type=hotel&interest=pricing` preselects both fields | Pass |
| 14 | Empty submit: 6 inline errors, a visible summary, focus on the first invalid field | Pass |
| 15 | Invalid email shows the specific email error | Pass |
| 16 | Valid submit (real click) shows the mailto confirmation, not "submitted" | Pass |
| 17 | Hotel organization type routes to `leads.routes.hotels` | Pass |
| 18 | Mobile (375px): menu opens, Technology accordion opens, Escape closes the panel | Pass |
| 19 | `prefers-reduced-motion: reduce`: pulses hidden, all reveal content visible, no node light cycling | Pass |
| 20 | JavaScript disabled: content fully visible (reveals are progressive enhancement) | Pass |
| 21 | No horizontal overflow on all 35 pages × 375 / 768 / 1440px (105 combinations) | Pass, after fix B3 |
| 22 | WCAG contrast of 19 key foreground/background pairs (both themes) | Pass. All ≥ 4.5:1; lowest is the warning notice at 4.51:1 |

## Visual review (screenshots in `qa-screenshots/`)

Reviewed: home at 1440 / 768 / 375, Technology, Solutions, Why, About, Contact (default and validation state), Arabic home at 1440 (RTL mirroring of nav, hero, both diagrams and arrow direction), Japanese home at 375, and the reduced-motion home.

## Bugs found and fixed during QA

| ID | Bug | Fix |
|---|---|---|
| B1 | Fixing an invalid field and then clicking submit could lose the click, because clearing the error on blur shifted the button under the pointer | Errors now clear on `input` while typing. Verified with a real click (test 16) |
| B2 | The form error summary showed as an empty yellow bar, because `.notice { display:flex }` overrode `[hidden]` | Global `[hidden] { display:none !important }` |
| B3 | 20px horizontal overflow on `/ja/solutions/` at 375px: a long Japanese CTA on a non-wrapping button | Buttons wrap at ≤560px |
| B4 | CSS uppercasing rendered "KABUK" in eyebrows and labels, which the design library forbids | Sentence-case eyebrows |

## Not tested / limitations

- **Web fonts**: Google Fonts is blocked in the test sandbox, so screenshots use fallback fonts (Inter, Noto and the Arabic face are not rendered). Recheck rendering on a networked machine.
- **Screen readers**: not tested with VoiceOver or NVDA. ARIA patterns were checked structurally only.
- **Real mail clients**: the `mailto:` handoff was verified up to the navigation call, not in an actual mail app.
- **Browsers**: Chromium only. Safari and Firefox were not tested.
- **Translations**: not linguistically verified; they need native-speaker review.
- **Automated a11y scanner** (axe or Lighthouse): not run.
