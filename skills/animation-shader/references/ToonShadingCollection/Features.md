# Toon Shading Knowledge Base

This documentation serves as a comprehensive collection and analysis of Toon Shading techniques (NPR - Non-Photorealistic Rendering). It aggregates knowledge on various styles, implementation techniques, and artistic controls used in modern anime-style rendering.

## Overview
Unlike specific shader documentation (like lilToon or Poiyomi), this knowledge base focuses on **concepts, algorithms, and artistic principles**. It covers everything from basic cel-shading logic to advanced post-processing and pipeline optimizations.

## Table of Contents

### 1. Fundamentals
*   **[Art Styles (画风概述)](Details/01_ArtStyles.md)**: Analysis of Western vs. Japanese styles, and the evolution of "Cel-Shading".
*   **[Outlines (描边)](Details/02_Outline.md)**: Techniques for geometric (inverted hull) and post-process outlines, including inner edge handling.

### 2. Lighting & Shading
*   **[Diffuse Shading (漫反射)](Details/03_Diffuse.md)**: Ramp shading, face SDF shading, and half-lambert techniques.
*   **[Specular & Hair (高光)](Details/04_Specular.md)**: Stylized highlights, anisotropic hair shading (Angel Ring).
*   **[Environment & Rim (环境与边缘光)](Details/05_Environment.md)**: MatCaps, reflections, and rim lighting logic.
*   **[Lighting & Shadows (打光与投影)](Details/09_Lighting_Shadows.md)**: Handling multiple light sources, shadow maps, and stylized shadow control.

### 3. Advanced Stylization
*   **[PBR & Painting Styles (PBR与绘画风)](Details/06_PBR_Stylization.md)**: Integrating NPR with PBR workflows, and simulating hand-painted strokes.
*   **[Special Features & Materials (特殊部位与材质)](Details/07_Stylized_Features.md)**: Eyes, skin, translucency, and material analysis.
*   **[Post-Processing (后处理)](Details/08_PostProcessing.md)**: Screen-space effects for toon rendering.

### 4. Production Pipeline
*   **[Animation & VFX (动画与特效)](Details/10_Animation_VFX.md)**: Facial expressions, FOV correction, and stylized VFX.
*   **[Modeling & Pipeline (建模与管线)](Details/11_Modeling_Pipeline.md)**: Modeling best practices for toon shading and pipeline optimization techniques.
