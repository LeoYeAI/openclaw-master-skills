# Shading Grade Map

The **Shading Grade Map** (SGM) is an advanced workflow that replaces the two separate "Position Maps" with a single grayscale texture. This allows for more organic and complex shadow shapes.

## 1. Concept
Instead of binary "Shadow Here / No Shadow Here", the SGM defines a **Shading Threshold** per pixel.
*   **White (1.0)**: High resistance to shading. Needs very dark lighting to become a shadow. (e.g., Tips of nose, cheeks).
*   **Black (0.0)**: Low resistance. Becomes shadow very easily. (e.g., Deep folds, neck, underarms).
*   **Gray (0.5)**: Standard behavior.

This allows an artist to "paint" the flow of shadows on the texture. As the light moves, the shadow doesn't just slide linearly; it "fills up" the valleys (dark areas on the SGM) first and retreats from the peaks (white areas) last.

## 2. Properties
*   **`_ShadingGradeMap`**: The grayscale texture controlling the threshold.
*   **`_Tweak_ShadingGradeMapLevel`**: Global offset to make the whole model lighter or darker.
*   **`_BlurLevelSGM`**: Blur the map at runtime to soften the shadow shapes.
*   **`_1st_ShadeColor_Step`** / **`_1st_ShadeColor_Feather`**: Still used to define the base cutoffs.

## 3. Implementation Logic
The core math multiplies the dynamic lighting factor (`HalfLambert`) by the static Grade Map.

**Call Site**: `fragShadingGradeMap` in `UniversalToonBodyShadingGradeMap.hlsl`.

**Pseudo-Code:**
```hlsl
// 1. Sample the Grade Map (with optional blur)
float4 sgm = tex2Dlod(_ShadingGradeMap, float4(uv, 0, _BlurLevelSGM));
float grade = sgm.r;

// 2. Adjust with global tweak
// Only applied if the map isn't purely white
if (grade < 0.95) {
    grade += _Tweak_ShadingGradeMapLevel;
}
grade = saturate(grade);

// 3. Combine with Lighting
// The grade effectively scales the light intensity seen by that pixel.
// High Grade (1.0) -> Keeps HalfLambert high -> Stays Lit.
// Low Grade (0.0) -> Drags HalfLambert to 0 -> Forces Shadow.
float CombinedLight = grade * lerp(HalfLambert, HalfLambert * shadowAttenuation, _Set_SystemShadowsToBase);

// 4. Calculate Shadow Masks
// Similar to Double Shade, but using the CombinedLight value
float shadowMask1 = saturate(
    (1.0 + ( (CombinedLight - (_1st_ShadeColor_Step - _1st_ShadeColor_Feather)) 
    * (0.0 - 1.0) ) // Constant factors replacing Position Map logic
    / (_1st_ShadeColor_Step - (_1st_ShadeColor_Step - _1st_ShadeColor_Feather)))
);

float shadowMask2 = saturate(
    (1.0 + ( (CombinedLight - (_2nd_ShadeColor_Step - _2nd_ShadeColor_Feather)) 
    * (0.0 - 1.0) )
    / (_2nd_ShadeColor_Step - (_2nd_ShadeColor_Step - _2nd_ShadeColor_Feather)))
);

// 5. Final Composition
float3 FinalColor = lerp(_BaseColor, _1st_ShadeColor, shadowMask1);
FinalColor = lerp(FinalColor, _2nd_ShadeColor, shadowMask2);
```

## 4. Advantages
*   **Continuous Flow**: Shadows can expand and contract organically based on the texture gradient.
*   **Simplified Asset**: One texture controls both 1st and 2nd shade distribution.
*   **High Control**: Allows creating specific shadow shapes (like heart-shaped highlights or specific muscle definition) that still react to light movement.
