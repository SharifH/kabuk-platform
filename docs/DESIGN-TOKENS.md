# Design tokens — KabuK Platform website

Source of truth: the **KabuK Platform** design system in the KabuK design library (`tokens.json` v1, README, themes). Theme: **Platform Core**, with **KabuK Dark** for selective dark sections and **Architecture Blueprint** rules for diagrams. Implemented in `assets/css/tokens.css`.

## Color

| Token | Light | Dark (`.theme-dark`) | Use |
|---|---|---|---|
| `--background` | `#FAFAF8` Warm White | `#111111` | Page ground |
| `--surface` | `#FFFFFF` | `#1A1A1A` | Cards, form, diagram frames |
| `--text` | `#111827` Ink | `#F5F5F3` | Body, headings |
| `--text-secondary` | `#667085` Slate | `#A3A3A3` | Leads, captions (≥4.5:1 on both grounds) |
| `--border` / `--border-strong` | `#E4E7EC` / `#D0D0CC` | `#333` / `#444` | Structure; borders over shadows |
| `--brand` | `#38C3E2` KabuK Blue | same | KabuK Bar, active markers, pulses. **Never text on light** (2.1:1) |
| `--brand-strong` | `#176B87` Deep Blue | `#38C3E2` | Links, eyebrows, network emphasis |
| `--action-primary` | `#176B87` + white label | `#38C3E2` + ink label | Primary buttons |
| `--brand-soft` / `--brand-subtle` | `#D9F3F8` / `#F1FBFD` | `#164E63` / `#0E2A33` | Chips, info notices, selected states |
| `--shell` | `#111827` | — | Footer (the "ink shell") |
| Semantic `success / warning / critical / info` + `-soft` / `-on-soft` | design library values | design library values | Status only, always with text |

Proportion target (Platform Core): ~65% light grounds, ~20% ink and neutrals, ~10% KabuK Blue family, ~5% semantic.

### Diagram roles

| Token | Meaning |
|---|---|
| `--diagram-platform` (ink) | KabuK Platform and internal services |
| `--diagram-network` (Deep Blue) + `--diagram-network-fill` | KabuK Exchange / distribution network |
| `--diagram-third-party` (slate, dashed) | Partners, PMS/CRS/channel managers |
| `--diagram-pulse` (KabuK Blue) | Animated connection pulses |

## Typography

Inter + Noto Sans JP (design library). Derived per-locale fallbacks: Noto Sans KR, Noto Sans TC and Noto Sans Arabic. Weights: 400 body, 500 labels, 600 headings and buttons. Never 800/900.

| Token | Value |
|---|---|
| `--type-display … --type-micro` | Design library UI scale (48/56 → 11/16) |
| `--web-hero-size` | `clamp(36px, 5.2vw, 64px)`, a **web extension** for marketing heroes |
| `--web-h2-size` | `clamp(28px, 3.2vw, 40px)`, a web extension |
| `--web-lead-size` | `clamp(16px, 1.5vw, 19px)` |

CJK and Arabic get taller line-heights (1.75 / 1.8) and no negative tracking.

## Space, shape, surface, motion

- Spacing `--space-4 … --space-96`. Section rhythm `--web-section-y: clamp(64px, 9vw, 120px)`. Content max width `1200px`, gutter `clamp(16px, 4vw, 48px)`.
- Radius: `sm 4` (pills, diagram tags) · `md 6` (buttons, inputs, nodes) · `lg 8` (cards) · `xl 12` (diagram frame) · `pill` (status chips only).
- Shadows: `--shadow-card` on the diagram frame only; `--shadow-modal` on dropdown menus.
- Strokes: hairline 1px, **KabuK Bar 3px**, focus 2px (`--focus-ring`, 2px offset), icon 1.5px.
- Motion: `--duration-fast 120ms` (hover/press), `--duration-base 200ms` (menus). Web extensions are `--duration-reveal 480ms` (staggered reveals, 70ms step) and `--duration-pulse 3.2s` (connection pulses). `prefers-reduced-motion: reduce` removes every animation and transition, shows all content, hides pulses and stops the node light cycle.

## Components

| Component | Class | Design library source |
|---|---|---|
| Button | `.btn .btn-primary / .btn-secondary / .btn-link` | Button (6px radius, explicit verbs, never pills) |
| Status chip | `.chip .chip-core / -development / -planned` | StatusChip (dot + text) |
| Section heading | `.section-head` (KabuK Bar via `::before`) | SectionHeading, once per section |
| Card | `.card` | Card (flat, 1px border, 8px radius) |
| Text field | `.field .input / .select / .textarea` | TextField (visible label, error replaces hint, `aria-invalid`) |
| Footer | `.site-footer` | AppShell ink shell, with the mark inverted until an official reversed asset exists |
| Notice | `.notice`, `.notice-info` | Warning/info soft grounds |

## Responsive behaviour

Breakpoints: **1080px** (nav collapses; hero stacks; 4-up grids → 2), **860px** (relationship diagram stacks vertically with vertical pulses; split layouts stack), **560px** (single column; full-width CTAs). Verified at 375, 768 and 1440px with no horizontal scroll.
