# Hotel-first update: readiness and claims review

Source copy: `01_KabuK_Platform_Website_Copy.md` (2026-10-15, "Proposed copy, subject to commercial/product approval"). Implementation brief: `03_Claude_Prompt_Platform_Website.md`. Branch: `feat/hotel-first-messaging`. **Not deployed.**

Nothing in this repository (code, config or docs) proves that any hotel-facing capability is live. Every status below is therefore taken from the copy document's own flags, not from product evidence.

## 1. Claims / readiness matrix

| Capability or claim | Copy flag | Status used on site | How it is shown | Control |
|---|---|---|---|---|
| One onboarding → HafH | `[VERIFY live eligibility and onboarding flow]` | Unknown → **eligible** | Chip "Subject to eligibility" | `channelStatus.hafh` |
| One onboarding → Omakastay | `[PLANNED]` | **Planned** | Chip "Planned", dashed card; "Prepare to reach…" | `channelStatus.omakastay` |
| One onboarding → KabuK Exchange | `[VERIFY actual distribution activation]` | Unknown → **eligible** | Chip "Subject to eligibility" | `channelStatus.exchange` |
| Distribution visibility (who sells inventory, booking attribution) | none (calibrated copy) | Unknown | Copy says "where information is available", plus a coverage qualifier | Copy only |
| Rate transparency / discrepancy indicators | none (calibrated copy) | Unknown | "available rate information", "supported channels" | Copy only |
| Commercial and inventory controls | none (calibrated copy) | Unknown | "supported … according to your agreements and connected systems" | Copy only |
| Market intelligence / comparable properties | `[PLANNED / VERIFY]`, `[PLANNED / CONFIG]` | **Planned** | Coming soon module and benefit card; register-interest CTA | `modules.marketInsights` |
| White-label solutions | `[PLANNED / VERIFY COMMERCIAL PACKAGES]` | **Planned** | Coming soon module and benefit card; "Register Interest" | `modules.whiteLabel` |
| Hotel-first onboarding and support | none | Process claim | Onboarding steps, "A Partner That Listens" | Copy only |
| Partner login | "only if applicable" | Not added | `urls.adminConsole` is a placeholder and not public | n/a |

No module was hidden before this change, so none was activated. The two new modules ship as `comingSoon`. `module_state()` in `tools/build.py` treats any other value, including `live`, as hidden, so a config typo can never publish them as live.

## 2. Claims requiring business approval before launch

1. **HafH and KabuK Exchange shown as "Subject to eligibility".** Confirm that hotels can actually be onboarded to each today. Otherwise set them to `planned` or `pilot`.
2. **"One onboarding relationship. Multiple paths to demand"** and "One Onboarding, Multiple Opportunities". This needs a real shared onboarding flow across the channels.
3. **Transparency and controls copy** (Distribution Visibility, Rate Transparency, Commercial & Inventory Controls, Clearer Operational Insight, "Know Who Sells Your Inventory"). The section is visible and has no status chip. Product must confirm what hotels can see and control today. If none of it is live, these items should be gated like the modules.
4. **Omakastay positioning:** "AI travel concierge for U.S. and inbound travelers". Confirm the target markets and that it may be named publicly.
5. **KabuK Exchange downstream list** (travel agencies, OTAs, wholesalers, travel apps, membership platforms). Confirm that each category is a real participating distributor type.
6. **White-label "accessible" packages.** I deliberately dropped "low-cost and no-cost" from the source copy, following the source's own rule not to publish "free" or "no-cost" until approved. The FAQ question "Are white-label tools free?" stays because its answer makes no promise.
7. **Brand promise "We build around hotels—not the other way around"** (Why hero) and "designed around hotel needs rather than distributor requirements".
8. **Footer "A KabuK Style Inc. company".** Confirm whether KabuK Platform is a company or a product of KabuK Style Inc. The zh-TW draft currently says 旗下公司 (subsidiary company).
9. **Hotel onboarding fee terms:** the site states none. The KBKX distributor no-setup-fee policy was not carried over.

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

- `leads.routes.*` are `example.com` addresses, so hotel inquiries currently go nowhere.
- `site.canonicalBase` (`kabukplatform.com`) is unverified, so the site still ships `noindex` and a closed `robots.txt`.
- `urls.*` are marked TODO for verification. No Omakastay URL exists, so the site has no link to it.
- The privacy notice is a draft.
- The ja, ko, zh-TW and ar translations are drafts. The 113 new or changed strings per locale were drafted for this update and have **not** had native review. Reviewer flags:
  - **zh-TW:** 物業 for "property" in the header CTA may read as real estate in Taiwan; 住宿設施 is an option. "Your Control." is rendered 您做主.
  - **ko:** "Your Control." is rendered 당신의 관리 (literal). "Subject to eligibility" (자격 요건에 따라 제공) is long for a chip.
  - **ja:** "Subject to eligibility" is 対象条件あり. HafH is described as 旅のサブスクリプション会員. "Booking attribution" is 予約の帰属.
  - **ar:** "Your Control" is rendered قرارك ("your decision"). "Onboarding" is الإعداد throughout.
  - **All locales:** "inbound travelers" is kept neutral (インバウンド / 인바운드 / 入境 / الوافدين) rather than "visiting Japan". Confirm the intended market.

## 5. Source section → implementation map

| Source section | Where | Component |
|---|---|---|
| Hero | Home | `.hero` + compact architecture diagram (existing) |
| Hotel-first difference (6) | Home `#ben-title`; Solutions `#benefits` | `benefit_cards()` (`.card` grid) |
| Signature ecosystem | Home `#ecosystem`; Solutions `#ecosystem` | `eco_diagram()` (new, light background) |
| Transparency and control | Home | `.pillars` + `.scope-note` qualifier |
| Market intelligence / White-label | Home `#market-insights`, `#white-label` | `gated_modules()` (new) |
| How onboarding works | Home | `.steps` (existing) |
| Audience / hotel groups | Home | `.split` |
| Closing CTA | All pages | `cta_band()` (now with a secondary action) |
| Hotel benefits page / FAQ | Solutions | page hero + `<details>` FAQ (new) |
| Ecosystem page | Solutions `#ecosystem` (no new route) | |
| Transparency & Insights page | **Not built** (optional, gated by readiness) | |
| White-label page | **Not built** (optional; must not be published as live) | |
| Suggested nav | **Not adopted.** The existing routes and nav are kept; two anchors were added to the Solutions menu | |
