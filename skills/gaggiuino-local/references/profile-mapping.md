# Profile Mapping

Primary mapping table for official/community Gaggiuino profiles, with local custom profiles kept as a separate supplement.

## Purpose

This file is the **main lookup table** for mapping named profiles to Local profile families.

It is intended to be more publishable and more generally useful than a machine-only inventory.
Use it when you need a quick answer to:
- which family a named profile belongs to,
- whether the profile is a brew profile or a utility profile,
- and what brief rationale supports that placement.

In graph interpretation, profile advice, and quick conceptual lookup, this table can be a first-pass tool.
In real-shot analysis with named profile data, use it as an **interpretation layer**, not as a replacement for profile-specific execution analysis.

## Scope

This file now prioritizes:
1. official/community profiles from `Zer0-bit/gaggiuino` → `community` → `profiles/`
2. a compact family mapping for those profiles
3. a small supplement for local custom profiles

Detailed family definitions live in:
- `references/profile-families.md`

## Family shorthand

- **Traditional** = Traditional / straight espresso
- **Fill-and-soak** = Fill-and-soak / preinfusion-led
- **Blooming** = Blooming
- **Lever-like** = Lever-like / declining pressure
- **Turbo/allongé** = Turbo / allongé / low-pressure fast-flow
- **Filter-style** = Filter-style low-pressure
- **Soup** = Soup / ultra-low-pressure high-flow
- **Adaptive** = Adaptive / resistance-led
- **Utility** = non-brewing / maintenance / calibration / prep

---

## Official / community profile mapping table

| Profile | Family | Type | Short rationale |
|---|---|---|---|
| Adaptive | Adaptive | official/community | Explicitly designed to adapt to grind / resistance conditions |
| Adaptive Dark Roast v1 | Adaptive | official/community | Official dark-roast variant of the Adaptive family with the same resistance-led design intent |
| Adaptive Light Roast v2 | Adaptive | official/community | Official light-roast variant of the Adaptive family with the same adaptive core logic |
| Allonge | Turbo/allongé | official/community | Direct long-ratio flow-led allongé structure with no distinct bloom/hold phase in the supplied JSON variant |
| Blooming Allonge | Turbo/allongé | official/community | Blooming-setup variant of allongé with a distinct hold/bloom phase before the main long-ratio extraction |
| Blooming espresso | Blooming | official/community | Explicit bloom-centered extraction design |
| Extractamundo Dos! | Turbo/allongé | official/community | Source explicitly frames it as a next-gen turbo shot |
| F3.0-LFWStep v1.0 | Filter-style | official/community | Filter 3.0 low-flow step variant |
| F3.0-RFWLinear v1.0 | Filter-style | official/community | Filter 3.0 regular-flow linear variant |
| F3.0-RFWStep v1.0 | Filter-style | official/community | Filter 3.0 regular-flow stepped variant |
| Filter 2.1 | Filter-style | official/community | Canonical filter-expression profile |
| Flimsy Light 0.3 (Gaggia) | Turbo/allongé | official/community | Source explicitly calls it turbo for light roasts |
| Flimsy Light 0.3 (Silvia) | Turbo/allongé | official/community | Same turbo-style light-roast family adapted to Silvia hardware |
| FlimsyLC - PREP v1.0 | Utility | official/community | Prep/helper half of split workflow, not a standalone cup family |
| FlimsyLC - RUN v1.0 | Turbo/allongé | official/community | Source frames LC as turbo-style, clarity-led low-contact extraction with brief soak and low-temp run profile |
| FlimsyLC - ULC RUN v1.0 | Turbo/allongé | official/community | ULC is still source-described as turbo-style, just more extreme, lower-contact, and lower-pressure than LC |
| Funky Town v2 | Turbo/allongé | official/community | Hybrid low-pressure clarity-led profile; still closer to turbo/allongé than traditional, but intentionally denser than a standard turbo |
| IUIUIU Classic | Fill-and-soak | official/community | Explicit staged fill + soak before pressure-led body |
| IUIUIU Classic [ZA] | Fill-and-soak | official/community | Variant of IUIUIU Classic, likely same family |
| LMD 9-8 v1.5 | Lever-like | official/community | Source explicitly transitions from pressure-led extraction into flow-defined finishing with healthy pressure decline |
| LMD Single v1.1 | Lever-like | official/community | Single-basket variant of LMD logic with pressure phase then flow-defined finish |
| LPD - FISO v2 | Lever-like | official/community | Source explicitly describes La Pavoni lever-style fast-in slow-out pressure profile |
| LPL - FISO v2.2 | Lever-like | official/community | Source explicitly describes La Pavoni light-roast lever-style FISO profile |
| LPL - SISO v2.2 | Lever-like | official/community | Source explicitly describes La Pavoni light-roast lever-style SISO profile |
| Leva 6 v0.9 | Lever-like | official/community | Explicit lever-emulation profile |
| Leva 9 SINGLE v0.9 | Lever-like | official/community | Lever-emulation variant for smaller beverage format |
| Leva 9 v0.9 | Lever-like | official/community | Explicit spring-lever emulation with declining pressure |
| Londinium | Lever-like | official/community | Explicit Londinium lever-style simulation |
| Low High Low v1.3 | Turbo/allongé | official/community | Fast high-ratio low/high/low flow design aimed at reduced TDS and light-roast extraction |
| LowRider - rc.2 | Turbo/allongé | official/community | Very long allongé-style low-contact shot with clarity, smoothness, and low-rider flow structure |
| Phiynic v1.1 | Traditional | official/community | Guided, adjustable pressure-led espresso framework for classic concentrated shots; still closer to Traditional than bloom, turbo, or lever-style families |
| Salami Shot v0.1 | Utility | official/community | Primarily tasting / diagnostic profile, not a normal everyday brewing family |
| Stock - 12 Bar | Traditional | official/community | Default straight high-pressure espresso style |
| Stock - 9 Bar | Traditional | official/community | Default straight espresso baseline |
| Tea Mofos Reloaded | Filter-style | official/community | Source explicitly says it works similarly to Filter 3.0 for tea-like extraction |
| Zer0 | Turbo/allongé | official/community | Flow-led, low-pressure, ~1:3 style closer to turbo/allongé than straight espresso |
| [UT] Boiler Off | Utility | official/community | Maintenance / boiler-off utility profile |
| [UT] Cycle 100 | Utility | official/community | Utility / testing / cycling profile |
| [UT] Cycle 130 | Utility | official/community | Utility / testing / cycling profile |
| [UT] PZ Cal 1.3 | Utility | official/community | Calibration profile |
| [UT] Test OPV | Utility | official/community | Testing profile, not beverage family |
| [UT] Tube Fill | Utility | official/community | Explicit tube-fill utility profile |

---

## Local custom profile supplement

These are machine-specific and should not be treated as official/community-backed.

| Profile | Family | Type | Short rationale |
|---|---|---|---|
| HyperEx 2.0 | Turbo/allongé | local custom |  a high-yield low-pressure fast-flow expression closer to turbo/allongé than filter-style |
| HyperEx | Turbo/allongé | local custom |  a high-yield low-pressure fast-flow expression closer to turbo/allongé than filter-style |
| Boiler Off/Flush | Utility | local utility | Current machine idle / flush profile, not brewing taxonomy |
