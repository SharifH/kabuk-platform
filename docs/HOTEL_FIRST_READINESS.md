# Hotel-first update: readiness and claims review

Source copy: `01_KabuK_Platform_Website_Copy.md` (2026-10-15, "Proposed copy, subject to commercial/product approval"). Implementation brief: `03_Claude_Prompt_Platform_Website.md`. Branch: `feat/hotel-first-messaging` (PR #2). **Not deployed.**

Nothing in this repository (code, config or docs) proves that any hotel-facing capability is live. Every status below is therefore taken from the copy document's own flags, not from product evidence.

## 1. Claims / readiness matrix

Statuses marked "confirmed" were signed off by the site owner on 2026-10-16. All others still come from the copy document's own flags.

| Capability or claim | Status | How it is shown | Control |
|---|---|---|---|
| **Single onboarding** covers all KabuK products, subject to eligibility | Confirmed | Hero note, "One Onboarding, Multiple Opportunities", FAQ (activation still depends on eligibility, readiness, terms and approval) | Copy |
| One onboarding → HafH | **Pilot** (confirmed) | Chip "Pilot" | `channelStatus.hafh` |
| One onboarding → KabuK Exchange | **Pilot** (confirmed) | Chip "Pilot" | `channelStatus.exchange` |
| One onboarding → Omakastay | **Planned** | Chip "Planned", dashed card; "Prepare to reach…" | `channelStatus.omakastay` |
| Omakastay target markets | Travelers from **North America and Europe** (confirmed) | Diagram, Solutions ecosystem, About | Copy |
| KabuK Exchange distributor types (agencies, OTAs, wholesalers, travel apps, membership platforms) | Available (confirmed) | Diagram downstream list, Solutions | Copy |
| Distribution visibility (who sells inventory, booking attribution) | **Available** (confirmed) | Visible; coverage qualifier kept | Copy |
| Commercial and inventory controls | **Available** (confirmed) | Visible; "supported … according to your agreements" kept | Copy |
| Clearer operational insight | **Available** (confirmed) | Visible | Copy |
| **Rate transparency** / discrepancy indicators | **Not available** (confirmed) → Coming soon | Chip on the Rate Transparency pillar and the two rate benefit cards; FAQ answers "Not yet"; "rate" removed from visibility claims elsewhere | `modules.rateTransparency` |
| Market intelligence / comparable properties | **Planned** | Coming soon module and benefit card; register interest | `modules.marketInsights` |
| White-label solutions | **Planned**; packages will be a mix of no-cost and low-cost (confirmed) | Coming soon module and benefit card; "planned low-cost and no-cost packages"; no prices | `modules.whiteLabel` |
| Brand promise "We build around hotels…" | Confirmed | Why hero | Copy |
| KabuK Platform is a **product** of KabuK Style Inc. | Confirmed | Footer "A KabuK Style Inc. product." in all locales | Copy |
| **No setup fee for hotels** | Confirmed | Notice under the Home onboarding steps; first Solutions FAQ item (all locales) | Copy |
| Partner login | n/a | Not added; `urls.adminConsole` is a placeholder | n/a |

`module_state()` in `tools/build.py` treats any value other than `comingSoon` (including `live`) as hidden.

## 2. Open items

1. **Other hotel fees:** the site now says there is no setup fee and that "commercial terms for individual channels are reviewed with you during onboarding". Confirm that this second sentence is accurate.
2. **White-label pricing:** the site says only "planned low-cost and no-cost packages". Specific prices, scope and eligibility are still to be announced.

## 3. Copy I wrote that is not in the source document

Bridging copy is needed where the source has no text for an existing component. Please review:

| Location | Text |
|---|---|
| Home, Coming soon section | "Coming soon" / "What we're building next for hotels." / "These capabilities are planned and not yet available. Register your interest and we will share details once scope, coverage, and terms are confirmed." |
| Home, audience | "KabuK Platform also supports other travel businesses:" (+ links to the other three segments) |
| Solutions, benefits heading | "What KabuK Platform is designed to give your hotel." |
| Solutions, FAQ heading | "Questions hotels ask." |
| Solutions, `#hotels` row | Title, body and topics rewritten for hotel-first framing |
| Ecosystem diagram | "One hotel onboarding and connectivity foundation for KabuK channels." and the caption ("Illustrative only… Placement in every channel is not guaranteed.") |
| About family | Fourth card "Consumer travel products: HafH · Omakastay"; Platform role "Hotel platform and technology foundation" |
| Why "not" list | Adds "Not a wholesaler", "Not a channel manager", and "Not a universally available standalone SaaS suite" (from the source guardrails) |
| Contact | Hero "Connect your property." + lead; interests "Hotel onboarding & distribution", "Market insights (coming soon)", "White-label solutions (coming soon)" |
| Common | Status chips "Subject to eligibility", "Pilot", "Coming soon"; footer tagline |

## 4. Outstanding placeholders (unchanged by this update, still blocking launch)

- ~~Lead inboxes~~ Resolved: all `leads.routes.*` now point to `network@kabuk.com`.
- `site.canonicalBase` (`kabukplatform.com`) is unverified, so the site still ships `noindex` and a closed `robots.txt`.
- `urls.*` are marked TODO for verification. No Omakastay URL exists, so the site has no link to it.
- The privacy notice is a draft.
- The ja, ko, zh-TW and ar translations were accepted by the site owner "for now" (2026-10-16) without native review. The draft-translation banner stays on until a locale's `review` is set to `approved`. The 113 new or changed strings per locale were drafted for this update and have **not** had native review. Reviewer flags:
  - **zh-TW:** footer now 旗下產品 (product). 物業 for "property" in the header CTA may read as real estate in Taiwan; 住宿設施 is an option. "Your Control." is rendered 您做主.
  - **ko:** "Your Control." is rendered 당신의 관리 (literal). "Subject to eligibility" (자격 요건에 따라 제공) is long for a chip.
  - **ja:** "Subject to eligibility" is 対象条件あり. HafH is described as 旅のサブスクリプション会員. "Booking attribution" is 予約の帰属.
  - **ar:** "Your Control" is rendered قرارك ("your decision"). "Onboarding" is الإعداد throughout.
  - **All locales:** Omakastay now targets travelers from North America and Europe (北米および欧州 / 북미 및 유럽 / 北美與歐洲 / أمريكا الشمالية وأوروبا).

## 5. Source section → implementation map

| Source section | Where | Component |
|---|---|---|
| Hero | Home | `.hero` + compact architecture diagram (existing) |
| Hotel-first difference (6) | Home `#ben-title`; Solutions `#benefits` | `benefit_cards()` (`.card` grid) |
| Signature ecosystem | Home `#ecosystem`; Solutions `#ecosystem` | `eco_diagram()` (new, light background) |
| Transparency and control | Home | `.pillars` + `.scope-note` qualifier |
| Market intelligence / White-label | Home `#market-insights`, `#white-label` | `gated_modules()` (new) |
| Rate transparency (not available) | Home control pillar 02, benefit 03 on Home and Solutions | per-item Coming soon chip (`CONTROL_MODULES`, `BENEFIT_MODULES`) |
| How onboarding works | Home | `.steps` (existing) |
| Audience / hotel groups | Home | `.split` |
| Closing CTA | All pages | `cta_band()` (now with a secondary action) |
| Hotel benefits page / FAQ | Solutions | page hero + `<details>` FAQ (new) |
| Ecosystem page | Solutions `#ecosystem` (no new route) | |
| Transparency & Insights page | **Not built** (optional, gated by readiness) | |
| White-label page | **Not built** (optional; must not be published as live) | |
| Suggested nav | **Not adopted.** The existing routes and nav are kept; two anchors were added to the Solutions menu | |
