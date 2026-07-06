# Animation Shader - Standalone Workflow

> This is the standalone workflow for the Animation Shader skill. Use this when **no external workflow skill** (e.g., OpenSpec, SpecKit) is available. If a workflow skill is active, ignore this file and use the SKILL.md as a domain knowledge reference instead.

## Workflow

1.  Analyze the user's visual goal (e.g., "I want a glowing outline").
2.  **Determine the Approach (Mandatory):**
    *   **Step 2a: Select Base Present:** You **MUST** first identify the overall style. If the user uses general terms like "anime", "toon", "animation shader", or "character shader", map this to a **Present** (e.g., **Basic Anime**) from SKILL.md to establish the foundation. **Do not skip this step.**
    *   **Step 2b: Identify Specific Features:** Extract specific requirements (e.g., "Shadow Texture", "Rim Light") and map them to the **Feature List** in SKILL.md.
    *   **Step 2c: Merge Requirements:** The final feature list is the combination of **ALL features from the selected Present** PLUS the **Specific Features** identified.
        *   *Example:* User asks for "Animation shader with Shadow Texture".
        *   *Action:* Select **Basic Anime** (Base) + **Shadow Texture** (Specific).
        *   *Result:* [3-Tone Shading, Outline, Base Color] (from Basic Anime) + [Shadow Texture].
3.  Consult the **Feature List** in SKILL.md to find relevant techniques and documentation for the identified features. **You must address EVERY item in the final feature list from Step 2 (including both Base Present features and Specific Features).** If a feature is not found in the **Feature List**, check the **Details Features Document** for corresponding details. If it is still not found, implement it based on your own knowledge.
4.  Read the specific reference files identified. **You MUST read ALL reference files listed under each identified feature in the Feature List. Do not select just one file; read them all to gain a complete understanding.**
5.  Propose a solution or shader configuration based on the documentation.
6.  (Optional) If shader variants are needed, read the **Variants & Optimization** reference documents and generate the variant shaders.
7.  (Optional) If code/shader graph editing is needed, guide the user or generate the code.

---

## Example Workflow Executions

### Example 1: Basic Anime (Standard)

*   **Scenario:** User wants "Animation shader with Shadow Texture".
*   **Determine the Approach (Step 2):**
    *   **Base Present:** **Basic Anime**
    *   **Specific Features:** **Shadow Texture**
    *   **Final Feature List:** [3-Tone Shading, Outline, Base Color] (from Basic Anime) + [Shadow Texture].
*   **Identified Features:**
    Read ALL files in the final feature list.
    1.  **Base Color** (from Basic Anime Preset) -> File:
        *   `references/lilToon/Details/01_Base_Main.md`
        *   `references/PoiyomiShaders/Details/01_Base_Main.md`
        *   `references/ToonShadingCollection/Details/03_Diffuse.md`
    2.  **3-Tone Shading** (from Basic Anime Preset) -> File:
        *   `references/lilToon/Details/02_Lighting_Shadows.md`
        *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`
        *   `references/UnityChanToonShaderVer2/Details/01_DoubleShade.md`
        *   `references/ToonShadingCollection/Details/09_Lighting_Shadows.md`
    3.  **Outline** (from Basic Anime Preset) -> File:
        *   `references/lilToon/Details/08_Outline.md`
        *   `references/PoiyomiShaders/Details/05_Outline.md`
        *   `references/RToon/Details/03_Outline.md`
        *   `references/UnityChanToonShaderVer2/Details/03_Outline.md`
        *   `references/ToonShadingCollection/Details/02_Outline.md`
    4.  **Shadow Texture** (Specific Request) -> File:
        *   `references/RToon/Details/02_ShadowT.md`
*   **Action:** You must call `read_file` for **ALL** of these files before writing any code.
*   **Propose a solution or shader configuration based on the documentation.**

---

### Example 2: Stylized Sketch (Artistic)

*   **Scenario:** User wants "Monochrome manga style with hatching shadows".
*   **Determine the Approach (Step 2):**
    *   **Base Present:** **Stylized Sketch**
    *   **Specific Features:** None (The request maps entirely to the preset).
    *   **Final Feature List:** [Color Adjustments, Sketchy Outline, Hatching, Halftone Overlay, Sketch / Paper Overlay] (from Stylized Sketch).
*   **Identified Features:**
    Read ALL files in the final feature list.
    1.  **Color Adjustments** (Desaturated/Monochrome) -> File:
        *   `references/lilToon/Details/01_Base_Main.md`
        *   `references/PoiyomiShaders/Details/01_Base_Main.md`
    2.  **Sketchy Outline** -> File:
        *   `references/SToon/Details/02_Outline.md`
        *   `references/RToon/Details/03_Outline.md`
    3.  **Hatching** -> File:
        *   `references/SToon/Details/03_Overlays.md`
    4.  **Sketch / Paper Overlay** -> File:
        *   `references/SToon/Details/03_Overlays.md`
*   **Action:** You must call `read_file` for **ALL** of these files before writing any code.

---

### Example 3: Semi-Realistic Toon (High Fidelity)

*   **Scenario:** User wants "Toon & PBR mixed character with shiny gold armor".
*   **Determine the Approach (Step 2):**
    *   **Base Present:** **Semi-Realistic Toon**
    *   **Specific Features:** **MatCap** (for shiny gold armor)
    *   **Final Feature List:** [PBR, Normal Map, Shadow Ramp, Subsurface Scattering, Outline] (from Semi-Realistic Toon) + [MatCap].
*   **Identified Features:**
    Read ALL files in the final feature list.
    1.  **PBR / Normal Map** -> File:
        *   `references/PoiyomiShaders/Details/01_Base_Main.md` (Normal Map)
        *   `references/ToonShadingCollection/Details/06_PBR_Stylization.md` (PBR Theory)
    2.  **Shadow Ramp** -> File:
        *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`
    3.  **Subsurface Scattering (SSS)** (for skin) -> File:
        *   `references/PoiyomiShaders/Details/02_Lighting_Shadows.md`
        *   `references/ToonShadingCollection/Details/07_Stylized_Features.md`
    4.  **MatCap** (Specific Request) -> File:
        *   `references/RToon/Details/04_MatCap_Reflection.md`
        *   `references/lilToon/Details/03_Surface_Reflections.md`
        *   `references/PoiyomiShaders/Details/03_Surface_Reflections.md`
        *   `references/UnityChanToonShaderVer2/Details/04_SpecialFeatures.md`
*   **Action:** You must call `read_file` for **ALL** of these files before writing any code.
