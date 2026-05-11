# Local Profile Descriptions

Use this file only when a **specific named profile / 曲线** is already known and family-level taxonomy is not enough.

This file is not a profile-name cookbook.
Its purpose is narrower:

- clarify what a named profile is trying to do,
- provide a concise expectation for what “normal” looks like,
- and reduce misreadings when family-level guidance is too coarse.

If family mapping alone is sufficient, prefer:
- `profile-mapping.md`
- `profile-families.md`

If the question is mainly about machine-side execution semantics, prefer:
- `analysis-protocol.md`

---

## Blooming espresso
- **Family:** Blooming
- **Intent:** Use a meaningful wetting and bloom structure before the main extraction, especially for lighter or more difficult coffees.
- **Normal expression:** A staged setup should be visible before the main shot. Compared with straight espresso, it will often look more segmented, more delayed, and more structurally extended.
- **Do not misread:** Do not judge it by straight-shot timing or opening behavior. Delayed main extraction, long total time, or a visible bloom-related pause do not automatically mean failure.
- **Source note:** Adapted from the community profile description.

## IUIUIU Classic
- **Family:** Fill-and-soak / staged all-rounder
- **Intent:** Use a staged fill and soak structure to prepare the puck before the main extraction, aiming for a broadly adaptable all-round profile rather than a highly specialized one.
- **Normal expression:** A fill → soak → extraction structure is part of the intended expression. The setup phases are not just dead time before the “real” shot begins.
- **Do not misread:** Do not treat the soak as wasted time, and do not expect the shot to behave like a direct pressure-led classic profile from the opening seconds.
- **Source note:** Adapted from the community profile description.

## Extractamundo Dos!
- **Family:** Turbo / allongé
- **Intent:** An IUIUIU next-gen take on the turbo shot, aimed at light roasts and a fast, open extraction rather than a classic dense structure.
- **Normal expression:** Goal time is around 15–20 seconds. Version 1.0 is described as a fast 8 ml/s fill until 4.5 bar, a quick soak until about 6 g in the cup, then a 3 ml/s flow profile with a 6 bar pressure limit.
- **Do not misread:** Do not treat the fast fill, quick soak, or low-pressure finish as a gusher by default; but if those defining stages never clearly appear, do not call it a clean Extractamundo expression just because it looks broadly turbo-like.
- **Source note:** Adapted closely from the published community profile description.

## Adaptive
- **Family:** Adaptive / resistance-led
- **Intent:** Let the extraction phase adapt to puck resistance while using a pressurized bloom stage to help maintain puck integrity, with the goal of broader tolerance to changing puck conditions and grind settings.
- **Normal expression:** It will not always look like one rigid canonical graph. The more relevant question is whether it establishes a coherent and stable extraction under the current puck conditions.
- **Do not misread:** Do not assume that adaptation means every outcome is automatically correct. It is more forgiving than a rigid profile, but it still needs sensible grind, puck prep, and taste-aware dialing.
- **Source note:** Adapted from the community profile description.

## Allonge
- **Family:** Turbo / allongé
- **Intent:** A direct allongé-style profile aimed at a long-ratio, flow-led extraction that favors a more open presentation than classic espresso.
- **Normal expression:** Expect a longer-ratio shot with a flow-led main extraction and naturally tapering pressure under puck resistance. It should not be judged by classic dense-shot expectations.
- **Do not misread:** Do not assume that a longer ratio, lighter body, or naturally declining pressure means the shot is failing if that is the intended style.
- **Source note:** Revised from supplied JSON structure plus community clarification that this is the non-blooming allongé variant.

## Blooming Allonge
- **Family:** Turbo / allongé
- **Intent:** A blooming-setup variant of allongé that adds a deliberate hold/bloom stage before the main long-ratio extraction while keeping the broader allongé-style cup intent.
- **Normal expression:** Expect a staged structure: initial fill/setup, a visible bloom/hold phase, then a return to flow-led allongé extraction. Compared with plain Allonge, it may present as a slightly more staged and somewhat fuller version of the same broader style.
- **Do not misread:** Do not treat the bloom/hold phase as failure or choking, and do not judge the shot by classic espresso timing or body expectations.
- **Source note:** Revised from supplied JSON and the Espresso Aficionados-style blooming-allongé clarification.

## Londinium
- **Family:** Lever-like / declining-pressure
- **Intent:** Simulate the extraction style of a Londinium R lever machine, favoring smoothness, body, and a slightly syrupy classic lever expression.
- **Normal expression:** It should be judged against lever-style integration and declining pressure, rather than turbo-style openness or blooming-style staging.
- **Do not misread:** Do not treat healthy declining pressure as automatic collapse. In this profile, a smooth lever-like decline is often part of the intended character.
- **Source note:** Adapted from the community profile description.

## Flimsy Light 0.3 (Gaggia)
- **Family:** Turbo / allongé
- **Intent:** A light-roast turbo-style profile aimed at a fast, open extraction style rather than a dense traditional espresso format.
- **Normal expression:** Expect a relatively fast, open shot that should not be judged by classic dense-shot expectations.
- **Do not misread:** Do not treat a successful fast shot as failed just because it is less dense or less traditional in presentation than classic espresso.
- **Source note:** Adapted from the community profile description.

## Flimsy Light 0.3 (Silvia)
- **Family:** Turbo / allongé
- **Intent:** A Silvia-specific variant of Flimsy Light, adjusted because testing showed the Silvia benefits from a different early exit behavior.
- **Normal expression:** Expect the same broad turbo-style direction as the Gaggia version, but with an important early difference: a 1 bar exit matters on Silvia because the 3 g exit on phase 1 can otherwise be hit before phase 2 reaches 2 bar.
- **Do not misread:** Do not judge Silvia execution directly by Gaggia-specific transition expectations, and do not ignore the significance of the early 1 bar exit in the published Silvia variant.
- **Source note:** Adapted closely from the published community profile description.

## FlimsyLC - ULC RUN v1.0
- **Family:** Turbo / allongé
- **Intent:** The Ultra Low Contact RUN profile pushes the broader LC idea further toward low contact, high clarity, and lower traditional intensity.
- **Normal expression:** Expect a 1:2.5 to 1:3 style shot, typically about 12–15 seconds for ULC, with lower contact and lower traditional intensity than LC. Like LC RUN, it is intended to be used after temperature stabilization on the PREP profile so the shot starts hotter and cools over extraction.
- **Do not misread:** Do not treat the lighter presentation as automatic failure if the profile is clearly aiming for very low-contact clarity; but do not ignore that this RUN profile is meant to be paired with PREP and that ULC is intentionally more extreme than LC.
- **Source note:** Adapted closely from the published community profile description.

## Funky Town v2
- **Family:** Turbo / allongé
- **Intent:** A hybrid profile for difficult funky or highly processed coffees, blending soup/turbo clarity with a denser traditional espresso body.
- **Normal expression:** Expect low pressure — ideally below 4 bar and sometimes not even above 2 — with a 1:2.5 to 1:3 ratio, a grind coarser than traditional espresso but finer than soup/turbo, and a brew temperature starting around 80°C that can be raised if the cup tastes bland.
- **Do not misread:** Do not force this profile into either a strict traditional-espresso frame or an ultra-thin clarity-only frame; the point is the hybrid result.
- **Source note:** Adapted closely from the published community profile description.

## IUIUIU Classic [ZA]
- **Family:** Fill-and-soak / staged all-rounder
- **Intent:** A variant of IUIUIU Classic that leans more heavily on flow while using pressure more as a ceiling than as a mandatory target.
- **Normal expression:** Expect a staged extraction that remains more flow-led than a classic pressure-first profile. Failing to hit the pressure ceiling is not automatically a problem.
- **Do not misread:** Do not treat sub-ceiling pressure as failure by itself.
- **Source note:** Adapted conservatively from the community profile description.

## LMD 9-8 v1.5
- **Family:** Lever-like / declining-pressure
- **Intent:** Designed for medium to medium-dark beans, this profile uses a pressure-targeted extraction body first, then transitions to a flow-defined finish to reduce the overextraction that can be common with darker beans.
- **Normal expression:** Expect flow-driven PI until about 2 bar, a short soak that transitions after about 6 seconds or less based on weight and pressure drop, then an extraction climb to 9 bar over about 5 seconds, a controlled drop to 8 bar over about 4 seconds, and only then a transition toward a more flow-defined finish. After about 10 seconds, or after a 3-bar pressure drop, flow increases to finish the shot.
- **Do not misread:** Intermediate phases may be short or skipped because the profile includes “save the shot” transition conditions; but a broadly lever-like graph alone is not enough if the intended 9→8→flow-defined structure never clearly appears.
- **Source note:** Adapted closely from the published community profile description.

## LMD Single v1.1
- **Family:** Lever-like / declining-pressure
- **Intent:** Designed for medium to medium-dark beans in a 7 g single basket, this is a small-puck LMD variant that transitions from a pressure target to a flow-defined finish under very tight flow limits.
- **Normal expression:** Expect flow-driven PI until about 1.2 bar, no soak, then a climb to 7 bar, a controlled 1-bar decline over about 3 seconds, and only then a transition to the flow-defined finish as puck resistance allows. It is fine if pressure tapers off toward the end.
- **Do not misread:** Do not read the late taper as collapse by default, but also do not invent a soak stage that the published profile explicitly says is absent.
- **Source note:** Adapted closely from the published community profile description.

## Leva 6 v0.9
- **Family:** Lever-like / declining-pressure
- **Intent:** Emulate a spring lever whose pressure decline depends on pumped water rather than elapsed time, using multiple declining pressure phases from 6 bar.
- **Normal expression:** Preinfusion starts with fast flow and slows as pressure rises; the last preinfusion phase is a pressure drop starting from 3 bar, stopping after about 10 seconds or 10 g in the cup. Main extraction then rises to 6 bar and continues declining, with flow in the main phases limited to 4 ml/s and output after reaching 4 bar expected to be about 60 g.
- **Do not misread:** Do not judge the declining main extraction as collapse by default, and do not ignore that this profile is highly dependent on accurate pump-flow calibration.
- **Source note:** Adapted closely from the published community profile description.

## Leva 9 SINGLE v0.9
- **Family:** Lever-like / declining-pressure
- **Intent:** Emulate a spring lever in a smaller beverage format, using incremental pressure phases that decline from 9 bar based on pumped water rather than elapsed time.
- **Normal expression:** Preinfusion starts with fast flow and slows as pressure rises; the last preinfusion phase is a 3 bar hold, stopping after about 7 seconds or 10 g in the cup. Main extraction rises to 9 bar and continues declining, with flow in the main phases limited to 1.5 ml/s and output after reaching 6 bar expected to be about 20 g.
- **Do not misread:** Do not treat the controlled decline or tight flow-limited finish as automatic failure, and do not ignore that this profile is highly dependent on accurate pump-flow calibration.
- **Source note:** Adapted closely from the published community profile description.

## Leva 9 v0.9
- **Family:** Lever-like / declining-pressure
- **Intent:** Emulate a spring lever by using multiple incremental pressure phases whose decline is tied to pumped water, starting from 9 bar.
- **Normal expression:** Preinfusion starts with fast flow and slows as pressure rises; the last preinfusion phase is a 3 bar hold, stopping after about 7 seconds or 10 g in the cup. Main extraction rises to 9 bar and continues declining, with flow in the main phases limited to 3 ml/s and output after reaching 6 bar expected to be about 40 g.
- **Do not misread:** Do not evaluate it by fixed-pressure espresso expectations, and do not ignore that this profile is highly dependent on accurate pump-flow calibration.
- **Source note:** Adapted closely from the published community profile description.

## Low High Low v1.3
- **Family:** Turbo / allongé
- **Intent:** A fast, high-ratio profile aimed at reduced TDS and fewer harsh notes, especially with light roasts and high-extraction baskets.
- **Normal expression:** The published recipe is 17 g in, 60 g out (about 1:3.52). Phase 2 is expected to run around 5–8 g/s and 5–7 bar, and the profile requires scales because its logic depends on weight.
- **Do not misread:** Do not assume the high ratio alone means failure or dilution if the shot is following the intended fast, low-harshness format; but do not ignore that this profile depends on scale-guided execution.
- **Source note:** Adapted closely from the published community profile description.

## LowRider - rc.2
- **Family:** Turbo / allongé
- **Intent:** A very extended allongé-style profile built around a long, low-contact extraction style.
- **Normal expression:** The published method uses 19 g in, about 57 g out at roughly 1:3, with a total shot time around 2:30. The intended cup is unusually smooth for an allongé-style shot, with sparkle of acidity followed by milk-chocolate body and lactose-like finish.
- **Do not misread:** Do not treat its very long format as accidental overrun by default; but also do not judge it by normal espresso timing expectations.
- **Source note:** Adapted closely from the published community profile description.

## Phiynic v1.1
- **Family:** Traditional / straight espresso
- **Intent:** A guided, adjustable pressure-led profile meant to help the user tune a recipe rather than lock them into one fixed shape.
- **Normal expression:** Phase 1 is a fast preinfusion/saturation stage to fill headspace and saturate the puck while reaching a pressure peak. Phase 2 is a pressurized extraction stage whose time, pressure end target, and curve shape are meant to be adjusted. Phase 3 is a taper to stop the shot near the intended ratio and avoid overextraction. The guide suggests starting around 88–90°C and around a 1:2 plus tail-shot style ratio.
- **Do not misread:** Do not treat its adjustability as meaning every outcome is equally intended; the profile still expects coherent changes to phase time, pressure targets, and taper behavior.
- **Source note:** Adapted closely from the published community profile description.

## Salami Shot v0.1
- **Family:** Utility / training
- **Intent:** Support salami-shot training by reproducing a straightforward espresso-style extraction that can be split into sequential cups for taste-learning rather than normal daily brewing.
- **Normal expression:** Expect a repeatable extraction shape suitable for cup-swapping and flavor segmentation, not a profile aimed at an optimized finished cup in itself.
- **Do not misread:** Do not judge it as though it were meant to be a polished endgame brew profile; it is primarily a training tool.
- **Source note:** Adapted from the community profile description.

## Stock - 12 Bar
- **Family:** Traditional / straight espresso
- **Intent:** Mimic the stock Gaggia Classic / Classic Pro experience with a 12-bar spring in a simple direct espresso format.
- **Normal expression:** Target temperature is 93°C. The pump runs at max flow for up to 300 seconds, and the shot is meant to be dialed by time or weight, just like an unmodified stock machine.
- **Do not misread:** Do not treat 12 bar as a pressure target that must be reached; maximum pressure is still limited by the OPV, and predictive scales may be inaccurate because some water can be lost through the OPV.
- **Source note:** Adapted closely from the published community profile description.

## Stock - 9 Bar
- **Family:** Traditional / straight espresso
- **Intent:** Mimic the stock Gaggia Classic / Classic Pro experience with a 9-bar spring in a simple direct espresso format.
- **Normal expression:** Target temperature is 93°C. The pump runs at max flow for up to 300 seconds, and the shot is meant to be dialed by time or weight, just like an unmodified stock machine.
- **Do not misread:** Do not treat 9 bar as a pressure target that must be reached.
- **Source note:** Adapted closely from the published community profile description.

## Tea Mofos Reloaded
- **Family:** Filter-style low-pressure
- **Intent:** A profile used to pull tea through a standard basket.
- **Normal expression:** Expect a filter-style or tea-style preparation rather than an espresso-style one.
- **Do not misread:** Do not apply espresso success criteria to this profile.
- **Source note:** Adapted conservatively from the community profile description.

## FlimsyLC - RUN v1.0
- **Family:** Turbo / allongé
- **Intent:** The main Low Contact RUN profile, designed to highlight clarity and acidity while minimizing astringency and harshness through low contact time, declining low temperature, and a longer ratio.
- **Normal expression:** Expect a 1:2.5 to 1:3 style shot, typically about 13–16 seconds for LC, with lower traditional intensity than denser espresso profiles. The RUN profile is intended to be paired with the PREP profile so the shot begins hotter and cools over the course of extraction.
- **Do not misread:** Do not treat lower traditional intensity as automatic failure if the profile is clearly aiming for low-contact clarity; but do not ignore that this RUN profile is meant to be used after temperature stabilization on PREP.
- **Source note:** Adapted closely from the published community profile description.

## Zer0
- **Family:** Turbo / allongé
- **Intent:** A broadly usable profile for many beans and roasts, with the default setup aimed especially at medium and medium-light coffees.
- **Normal expression:** Aim for about 30–40 seconds depending on roast level, with darker roasts tending shorter and a target ratio around 1:3. In the first phase, the goal is not to go above 6 bar, but the shot does not need to actually hit that target; the phase has a hard stop at 15 seconds.
- **Do not misread:** Do not treat failure to hit the early 6 bar target as automatic failure if the broader staged flow logic and target ratio are still coherent.
- **Source note:** Adapted closely from the published community profile description.

## LPD - FISO v2
- **Family:** Lever-like / declining-pressure
- **Intent:** A La Pavoni-inspired profile for darker roasts using a fast-in, slow-out lever-style curve.
- **Normal expression:** Expect a lever-style extraction with a stronger early phase and a declining finish rather than a flat pressure hold.
- **Do not misread:** Do not judge the profile by fixed-pressure espresso expectations, and do not treat the lever-style finish as collapse by default.
- **Source note:** Adapted from the community profile description.

## LPL - FISO v2.2
- **Family:** Lever-like / declining-pressure
- **Intent:** A La Pavoni-inspired light-roast profile using a fast-in, slow-out lever-style curve.
- **Normal expression:** Expect a lever-style shot with more emphasis toward the beginning of the pull and a declining finish rather than a flat classic espresso plateau.
- **Do not misread:** Do not judge it by fixed-pressure expectations, and do not treat the lever-style decline as failure by default.
- **Source note:** Adapted from the community profile description.

## LPL - SISO v2.2
- **Family:** Lever-like / declining-pressure
- **Intent:** A La Pavoni-inspired light-roast profile using a slow-in, slow-out lever-style curve.
- **Normal expression:** Expect a lever-style shot that develops more gradually than the FISO variant while still declining rather than holding flat through the body of the shot.
- **Do not misread:** Do not read its gentler early build and lever-style decline as automatic weakness or failure.
- **Source note:** Adapted from the community profile description.

## Filter 2.1
- **Family:** Filter-style low-pressure
- **Intent:** Use the espresso machine to produce a filter-style coffee rather than an espresso-style cup.
- **Normal expression:** Expect a longer, more dilute brew format judged by filter-style logic rather than espresso density or crema expectations.
- **Do not misread:** Do not apply espresso success criteria to this profile.
- **Source note:** Adapted from the community profile description.

## Adaptive Dark Roast v1
- **Family:** Adaptive / resistance-led
- **Intent:** A dark-roast-oriented Adaptive variant with a firmer initial hold and a gentler extraction phase than the broader Adaptive baseline.
- **Normal expression:** Expect the same broader Adaptive logic, but with a darker-roast-leaning setup.
- **Do not misread:** Do not judge it by the exact graph expectations of the light-roast variant.
- **Source note:** Adapted conservatively from the community profile description.

## Adaptive Light Roast v2
- **Family:** Adaptive / resistance-led
- **Intent:** A light-roast-oriented Adaptive variant with a zero-flow hold after preinfusion and a faster tail-end flow than the regular Adaptive profile.
- **Normal expression:** Expect the same broader Adaptive logic, but with a more explicitly staged light-roast-oriented structure.
- **Do not misread:** Do not judge it by the exact phase structure of the regular Adaptive profile if the shot is still behaving coherently under this variant's intended staging.
- **Source note:** Adapted conservatively from the community profile description.
