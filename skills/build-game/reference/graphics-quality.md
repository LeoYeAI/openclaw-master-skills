# Advanced 3D Graphics Quality Patterns

Recipes for dramatically improving visual quality in Three.js games. Use these patterns to make games look polished and professional.

## Enhanced Renderer Setup

```javascript
// High-quality renderer config
const renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: 'high-performance',
    stencil: false  // disable if not needed for perf
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
renderer.outputColorSpace = THREE.SRGBColorSpace;
// Enable physically correct lighting
renderer.useLegacyLights = false;
document.body.appendChild(renderer.domElement);
```

## Advanced Post-Processing Stack

```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

// SSAO — ambient occlusion for depth and realism
const ssaoPass = new SSAOPass(scene, camera, window.innerWidth, window.innerHeight);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
composer.addPass(ssaoPass);

// Bloom — glow on bright objects
const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.4,   // strength — subtle for realism, 0.8+ for stylized
    0.3,   // radius
    0.85   // threshold — only bright things glow
);
composer.addPass(bloomPass);

// Color grading via custom shader
const colorGradingShader = {
    uniforms: {
        tDiffuse: { value: null },
        brightness: { value: 0.02 },
        contrast: { value: 1.1 },
        saturation: { value: 1.15 },
        vignetteIntensity: { value: 0.3 },
        vignetteRoundness: { value: 0.8 }
    },
    vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform float brightness, contrast, saturation;
        uniform float vignetteIntensity, vignetteRoundness;
        varying vec2 vUv;
        void main() {
            vec4 color = texture2D(tDiffuse, vUv);
            // Brightness & contrast
            color.rgb += brightness;
            color.rgb = (color.rgb - 0.5) * contrast + 0.5;
            // Saturation
            float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
            color.rgb = mix(vec3(gray), color.rgb, saturation);
            // Vignette
            vec2 uv = vUv * 2.0 - 1.0;
            float vig = 1.0 - dot(uv * vignetteRoundness, uv * vignetteRoundness);
            vig = clamp(pow(vig, 1.5), 0.0, 1.0);
            color.rgb *= mix(1.0 - vignetteIntensity, 1.0, vig);
            gl_FragColor = color;
        }
    `
};
composer.addPass(new ShaderPass(colorGradingShader));

// FXAA anti-aliasing (final pass)
const fxaaPass = new ShaderPass(FXAAShader);
fxaaPass.uniforms['resolution'].value.set(1/window.innerWidth, 1/window.innerHeight);
composer.addPass(fxaaPass);
```

## Advanced Lighting Rig

```javascript
// Key light (sun) — warm, strong directional
const sunLight = new THREE.DirectionalLight(0xfff0dd, 2.5);
sunLight.position.set(40, 60, 30);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(4096, 4096);  // high-res shadows
sunLight.shadow.camera.near = 0.5;
sunLight.shadow.camera.far = 200;
sunLight.shadow.camera.left = -80;
sunLight.shadow.camera.right = 80;
sunLight.shadow.camera.top = 80;
sunLight.shadow.camera.bottom = -80;
sunLight.shadow.bias = -0.0005;
sunLight.shadow.normalBias = 0.02;  // reduces shadow acne on curved surfaces
scene.add(sunLight);

// Fill light — cool toned, opposite side, no shadow
const fillLight = new THREE.DirectionalLight(0x8899cc, 0.6);
fillLight.position.set(-30, 20, -20);
scene.add(fillLight);

// Hemisphere light — sky/ground ambient color
const hemiLight = new THREE.HemisphereLight(0x88bbff, 0x445522, 0.5);
scene.add(hemiLight);

// Ambient — very low, just prevents total black
const ambient = new THREE.AmbientLight(0x202030, 0.3);
scene.add(ambient);

// Rim/back light for character highlighting (optional)
const rimLight = new THREE.DirectionalLight(0xffeedd, 0.8);
rimLight.position.set(-20, 30, -40);
scene.add(rimLight);
```

### Dynamic Time-of-Day Lighting

```javascript
const TIMES = {
    dawn:    { sun: 0xffaa66, sunI: 1.5, hemiSky: 0xff9966, hemiGnd: 0x332211, ambient: 0x553322, fog: 0xdd9966, exposure: 0.9 },
    day:     { sun: 0xfff4e6, sunI: 2.5, hemiSky: 0x88bbff, hemiGnd: 0x445522, ambient: 0x404060, fog: 0x88aacc, exposure: 1.2 },
    sunset:  { sun: 0xff6633, sunI: 2.0, hemiSky: 0xff7744, hemiGnd: 0x221111, ambient: 0x442222, fog: 0xcc6644, exposure: 1.0 },
    night:   { sun: 0x4466aa, sunI: 0.5, hemiSky: 0x112244, hemiGnd: 0x000011, ambient: 0x111133, fog: 0x0a0a2e, exposure: 0.6 },
};

function lerpLighting(from, to, t) {
    const c = (a, b) => new THREE.Color(a).lerp(new THREE.Color(b), t);
    sunLight.color.copy(c(from.sun, to.sun));
    sunLight.intensity = THREE.MathUtils.lerp(from.sunI, to.sunI, t);
    hemiLight.color.copy(c(from.hemiSky, to.hemiSky));
    hemiLight.groundColor.copy(c(from.hemiGnd, to.hemiGnd));
    ambient.color.copy(c(from.ambient, to.ambient));
    scene.fog.color.copy(c(from.fog, to.fog));
    scene.background.copy(scene.fog.color);
    renderer.toneMappingExposure = THREE.MathUtils.lerp(from.exposure, to.exposure, t);
}
```

## Advanced Materials

### PBR Material Presets

```javascript
// Glossy metal (gold, chrome, copper)
const goldMat = new THREE.MeshStandardMaterial({
    color: 0xffd700, metalness: 1.0, roughness: 0.15
});
const chromeMat = new THREE.MeshStandardMaterial({
    color: 0xdddddd, metalness: 1.0, roughness: 0.05, envMapIntensity: 1.5
});

// Rough stone / concrete
const stoneMat = new THREE.MeshStandardMaterial({
    color: 0x888888, metalness: 0.0, roughness: 0.9, flatShading: true
});

// Glossy plastic
const plasticMat = new THREE.MeshStandardMaterial({
    color: 0xff3344, metalness: 0.0, roughness: 0.3
});

// Ice
const iceMat = new THREE.MeshPhysicalMaterial({
    color: 0xaaddff, metalness: 0.0, roughness: 0.1,
    transmission: 0.6, thickness: 1.5, ior: 1.31,
    transparent: true, opacity: 0.85
});

// Glass / crystal
const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, metalness: 0.0, roughness: 0.0,
    transmission: 0.95, thickness: 0.5, ior: 1.5,
    transparent: true
});

// Water surface
const waterMat = new THREE.MeshPhysicalMaterial({
    color: 0x006688, metalness: 0.1, roughness: 0.1,
    transmission: 0.4, thickness: 2.0, ior: 1.33,
    transparent: true, opacity: 0.8
});

// Emissive glow (lava, neon, magic)
const lavaMat = new THREE.MeshStandardMaterial({
    color: 0xff4400, emissive: 0xff2200, emissiveIntensity: 2.0,
    metalness: 0.0, roughness: 0.7
});
const neonMat = new THREE.MeshStandardMaterial({
    color: 0x00ffaa, emissive: 0x00ffaa, emissiveIntensity: 3.0,
    metalness: 0.0, roughness: 0.5
});

// Skin / organic (subsurface approximation)
const skinMat = new THREE.MeshStandardMaterial({
    color: 0xffccaa, metalness: 0.0, roughness: 0.65
});

// Snow
const snowMat = new THREE.MeshStandardMaterial({
    color: 0xf0f4ff, metalness: 0.0, roughness: 0.8,
    emissive: 0x223344, emissiveIntensity: 0.05  // slight cold glow
});

// Wood
const woodMat = new THREE.MeshStandardMaterial({
    color: 0x8B6914, metalness: 0.0, roughness: 0.75, flatShading: true
});

// Fabric / cloth
const fabricMat = new THREE.MeshStandardMaterial({
    color: 0x3344aa, metalness: 0.0, roughness: 0.95
});
```

### Procedural Textures via Canvas

```javascript
function createNoiseTexture(width = 256, height = 256, scale = 20, color1 = [60,120,60], color2 = [40,90,30]) {
    const canvas = document.createElement('canvas');
    canvas.width = width; canvas.height = height;
    const ctx = canvas.getContext('2d');
    const imageData = ctx.createImageData(width, height);
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const i = (y * width + x) * 4;
            // Simple value noise
            const nx = x / scale, ny = y / scale;
            const n = (Math.sin(nx * 1.3 + ny * 0.7) * Math.cos(nx * 0.8 - ny * 1.1) + 1) * 0.5;
            const t = n * n; // sharpen
            imageData.data[i]   = color1[0] + (color2[0] - color1[0]) * t;
            imageData.data[i+1] = color1[1] + (color2[1] - color1[1]) * t;
            imageData.data[i+2] = color1[2] + (color2[2] - color1[2]) * t;
            imageData.data[i+3] = 255;
        }
    }
    ctx.putImageData(imageData, 0, 0);
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    return tex;
}

// Usage: ground with procedural grass
const grassTex = createNoiseTexture(256, 256, 15, [50, 130, 40], [30, 80, 20]);
grassTex.repeat.set(40, 40);
const groundMat = new THREE.MeshStandardMaterial({ map: grassTex, roughness: 0.85 });
```

### Normal Map from Noise (bump detail without geometry)

```javascript
function createNoiseNormalMap(size = 256, bumpStrength = 2.0) {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext('2d');
    const img = ctx.createImageData(size, size);
    // Generate height field
    const heights = new Float32Array(size * size);
    for (let i = 0; i < heights.length; i++) {
        const x = i % size, y = Math.floor(i / size);
        heights[i] = (Math.sin(x * 0.15) * Math.cos(y * 0.12) + Math.sin(x * 0.08 + y * 0.1)) * 0.5;
    }
    // Convert height field to normal map
    for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
            const i = (y * size + x) * 4;
            const l = heights[y * size + ((x - 1 + size) % size)];
            const r = heights[y * size + ((x + 1) % size)];
            const u = heights[((y - 1 + size) % size) * size + x];
            const d = heights[((y + 1) % size) * size + x];
            const dx = (l - r) * bumpStrength;
            const dy = (u - d) * bumpStrength;
            img.data[i]     = (dx * 0.5 + 0.5) * 255;
            img.data[i + 1] = (dy * 0.5 + 0.5) * 255;
            img.data[i + 2] = 200; // z component
            img.data[i + 3] = 255;
        }
    }
    ctx.putImageData(img, 0, 0);
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    return tex;
}

// Usage: add surface detail to a flat material
const stoneNormal = createNoiseNormalMap(256, 3.0);
stoneNormal.repeat.set(8, 8);
const detailedStoneMat = new THREE.MeshStandardMaterial({
    color: 0x889988, roughness: 0.8, normalMap: stoneNormal, normalScale: new THREE.Vector2(1, 1)
});
```

## Environment Cubemap (Reflections)

```javascript
// Procedural environment map using PMREMGenerator (gives all materials realistic reflections)
function createEnvironmentMap(scene, renderer) {
    const pmremGenerator = new THREE.PMREMGenerator(renderer);
    pmremGenerator.compileEquirectangularShader();

    // Create a simple gradient sky scene for the env map
    const envScene = new THREE.Scene();
    const envGeo = new THREE.SphereGeometry(500, 32, 32);
    const envMat = new THREE.ShaderMaterial({
        side: THREE.BackSide,
        uniforms: {
            topColor: { value: new THREE.Color(0x0077ff) },
            bottomColor: { value: new THREE.Color(0xffffff) },
            offset: { value: 20 },
            exponent: { value: 0.6 }
        },
        vertexShader: `
            varying vec3 vWorldPos;
            void main() {
                vec4 wp = modelMatrix * vec4(position, 1.0);
                vWorldPos = wp.xyz;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 topColor, bottomColor;
            uniform float offset, exponent;
            varying vec3 vWorldPos;
            void main() {
                float h = normalize(vWorldPos + offset).y;
                gl_FragColor = vec4(mix(bottomColor, topColor, max(pow(max(h, 0.0), exponent), 0.0)), 1.0);
            }
        `
    });
    envScene.add(new THREE.Mesh(envGeo, envMat));

    const envMap = pmremGenerator.fromScene(envScene, 0.04).texture;
    scene.environment = envMap;  // all PBR materials now get reflections
    pmremGenerator.dispose();
    return envMap;
}

// Call after scene setup:
// createEnvironmentMap(scene, renderer);
```

## Gradient Sky Dome (much better than flat background color)

```javascript
function createSkyDome(topColor = 0x0066cc, bottomColor = 0xccddee, sunColor = 0xffffaa) {
    const skyGeo = new THREE.SphereGeometry(500, 32, 32);
    const skyMat = new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
            topColor: { value: new THREE.Color(topColor) },
            bottomColor: { value: new THREE.Color(bottomColor) },
            sunColor: { value: new THREE.Color(sunColor) },
            sunDirection: { value: new THREE.Vector3(0.4, 0.6, 0.3).normalize() },
            sunSize: { value: 0.03 }
        },
        vertexShader: `
            varying vec3 vWorldPosition;
            void main() {
                vec4 worldPos = modelMatrix * vec4(position, 1.0);
                vWorldPosition = worldPos.xyz;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 topColor, bottomColor, sunColor, sunDirection;
            uniform float sunSize;
            varying vec3 vWorldPosition;
            void main() {
                vec3 dir = normalize(vWorldPosition);
                float h = dir.y * 0.5 + 0.5;
                vec3 sky = mix(bottomColor, topColor, pow(h, 0.8));
                // Sun disc
                float sunDot = max(dot(dir, sunDirection), 0.0);
                sky += sunColor * pow(sunDot, 1.0 / sunSize) * 0.5;
                // Sun glow halo
                sky += sunColor * 0.15 * pow(sunDot, 8.0);
                gl_FragColor = vec4(sky, 1.0);
            }
        `
    });
    return new THREE.Mesh(skyGeo, skyMat);
}
// scene.add(createSkyDome());
```

## Animated Water Plane

```javascript
function createWater(size = 200) {
    const waterGeo = new THREE.PlaneGeometry(size, size, 128, 128);
    const waterMat = new THREE.ShaderMaterial({
        transparent: true,
        uniforms: {
            time: { value: 0 },
            waterColor: { value: new THREE.Color(0x006699) },
            foamColor: { value: new THREE.Color(0xccddee) },
            opacity: { value: 0.75 }
        },
        vertexShader: `
            uniform float time;
            varying vec2 vUv;
            varying float vWaveHeight;
            void main() {
                vUv = uv;
                vec3 pos = position;
                float wave1 = sin(pos.x * 0.05 + time * 1.2) * cos(pos.y * 0.03 + time * 0.8) * 1.5;
                float wave2 = sin(pos.x * 0.12 + pos.y * 0.08 + time * 2.0) * 0.5;
                float wave3 = cos(pos.x * 0.07 - pos.y * 0.05 + time * 0.6) * 0.8;
                pos.z = wave1 + wave2 + wave3;
                vWaveHeight = pos.z;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 waterColor, foamColor;
            uniform float opacity;
            varying vec2 vUv;
            varying float vWaveHeight;
            void main() {
                float foam = smoothstep(1.0, 1.8, vWaveHeight);
                vec3 color = mix(waterColor, foamColor, foam);
                // Edge transparency
                float edge = smoothstep(0.0, 0.05, min(vUv.x, min(vUv.y, min(1.0-vUv.x, 1.0-vUv.y))));
                gl_FragColor = vec4(color, opacity * edge);
            }
        `
    });
    const water = new THREE.Mesh(waterGeo, waterMat);
    water.rotation.x = -Math.PI / 2;
    water.position.y = -0.5;
    water.receiveShadow = true;
    return water;
}

// In game loop: waterMesh.material.uniforms.time.value += delta;
```

## Terrain with Height Noise

```javascript
function createTerrain(size = 200, segments = 128, heightScale = 15) {
    const geo = new THREE.PlaneGeometry(size, size, segments, segments);
    geo.rotateX(-Math.PI / 2);
    const posAttr = geo.attributes.position;

    // Multi-octave noise for natural terrain
    function noise2D(x, y) {
        return Math.sin(x * 1.2) * Math.cos(y * 0.8) * 0.5
             + Math.sin(x * 2.3 + y * 1.1) * 0.25
             + Math.cos(x * 0.5 - y * 1.7) * 0.35
             + Math.sin(x * 4.1 + y * 3.3) * 0.1;
    }

    for (let i = 0; i < posAttr.count; i++) {
        const x = posAttr.getX(i);
        const z = posAttr.getZ(i);
        const h = noise2D(x * 0.02, z * 0.02) * heightScale;
        posAttr.setY(i, h);
    }
    geo.computeVertexNormals();

    // Vertex colors based on height (snow peaks, grass valleys)
    const colors = new Float32Array(posAttr.count * 3);
    const grassColor = new THREE.Color(0x44882a);
    const rockColor = new THREE.Color(0x887766);
    const snowColor = new THREE.Color(0xeef0ff);
    for (let i = 0; i < posAttr.count; i++) {
        const y = posAttr.getY(i);
        const normalizedH = (y / heightScale + 1) * 0.5;
        let c;
        if (normalizedH < 0.4) c = grassColor.clone();
        else if (normalizedH < 0.7) c = grassColor.clone().lerp(rockColor, (normalizedH - 0.4) / 0.3);
        else c = rockColor.clone().lerp(snowColor, (normalizedH - 0.7) / 0.3);
        colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const mat = new THREE.MeshStandardMaterial({
        vertexColors: true, roughness: 0.85, metalness: 0.0, flatShading: true
    });
    const terrain = new THREE.Mesh(geo, mat);
    terrain.receiveShadow = true;
    terrain.castShadow = true;
    return terrain;
}
```

## Volumetric Fog / God Rays (Lightweight)

```javascript
// Lightweight volumetric light shafts via post-processing shader
const godRaysShader = {
    uniforms: {
        tDiffuse: { value: null },
        lightPosition: { value: new THREE.Vector2(0.5, 0.7) }, // screen-space sun position
        exposure: { value: 0.2 },
        decay: { value: 0.96 },
        density: { value: 0.8 },
        weight: { value: 0.5 },
        samples: { value: 60 }
    },
    vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform vec2 lightPosition;
        uniform float exposure, decay, density, weight;
        uniform int samples;
        varying vec2 vUv;
        void main() {
            vec2 texCoord = vUv;
            vec2 deltaTexCoord = (texCoord - lightPosition) * density / float(samples);
            vec4 color = texture2D(tDiffuse, texCoord);
            float illuminationDecay = 1.0;
            vec4 rays = vec4(0.0);
            for (int i = 0; i < 60; i++) {
                texCoord -= deltaTexCoord;
                vec4 s = texture2D(tDiffuse, texCoord);
                float lum = dot(s.rgb, vec3(0.299, 0.587, 0.114));
                s *= illuminationDecay * weight * smoothstep(0.6, 1.0, lum);
                rays += s;
                illuminationDecay *= decay;
            }
            gl_FragColor = color + rays * exposure;
        }
    `
};
// Add as ShaderPass after bloom, before FXAA
// Update lightPosition each frame from sun world position projected to screen
```

## Advanced Particle Effects

### Trail System (for projectiles, magic, speed lines)

```javascript
function createTrail(length = 30, width = 0.3, color = 0x00aaff) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(length * 2 * 3);
    const alphas = new Float32Array(length * 2);
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));

    const material = new THREE.ShaderMaterial({
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        uniforms: { color: { value: new THREE.Color(color) } },
        vertexShader: `
            attribute float alpha;
            varying float vAlpha;
            void main() {
                vAlpha = alpha;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 color;
            varying float vAlpha;
            void main() {
                gl_FragColor = vec4(color, vAlpha * 0.8);
            }
        `
    });

    const mesh = new THREE.Mesh(geometry, material);
    const points = Array.from({ length }, () => new THREE.Vector3());

    mesh.userData = {
        update(headPos, cameraPos) {
            // Shift points
            for (let i = points.length - 1; i > 0; i--) points[i].copy(points[i-1]);
            points[0].copy(headPos);
            // Build ribbon facing camera
            const pos = geometry.attributes.position.array;
            const alp = geometry.attributes.alpha.array;
            for (let i = 0; i < length; i++) {
                const t = i / length;
                const a = 1.0 - t;
                const dir = i < length - 1 ? points[i].clone().sub(points[i+1]) : dir;
                const toCamera = cameraPos.clone().sub(points[i]).normalize();
                const right = new THREE.Vector3().crossVectors(dir || new THREE.Vector3(0,1,0), toCamera).normalize().multiplyScalar(width * a);
                const idx = i * 6;
                const p = points[i];
                pos[idx] = p.x + right.x; pos[idx+1] = p.y + right.y; pos[idx+2] = p.z + right.z;
                pos[idx+3] = p.x - right.x; pos[idx+4] = p.y - right.y; pos[idx+5] = p.z - right.z;
                alp[i*2] = alp[i*2+1] = a;
            }
            geometry.attributes.position.needsUpdate = true;
            geometry.attributes.alpha.needsUpdate = true;
        }
    };

    // Build index
    const indices = [];
    for (let i = 0; i < length - 1; i++) {
        const a = i * 2, b = a + 1, c = a + 2, d = a + 3;
        indices.push(a, b, c, b, d, c);
    }
    geometry.setIndex(indices);

    return mesh;
}
```

### GPU-Like Particles with Shader

```javascript
function createAdvancedParticles(maxCount = 500, opts = {}) {
    const {
        baseColor = new THREE.Color(0xff6600),
        endColor = new THREE.Color(0xff0000),
        baseSize = 8.0,
        additive = true
    } = opts;

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(maxCount * 3);
    const velocities = new Float32Array(maxCount * 3);
    const ages = new Float32Array(maxCount).fill(-1);
    const maxAges = new Float32Array(maxCount);
    const sizes = new Float32Array(maxCount);

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('age', new THREE.BufferAttribute(ages, 1));
    geometry.setAttribute('maxAge', new THREE.BufferAttribute(maxAges, 1));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const material = new THREE.ShaderMaterial({
        transparent: true,
        depthWrite: false,
        blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
        uniforms: {
            baseColor: { value: baseColor },
            endColor: { value: endColor },
            baseSize: { value: baseSize }
        },
        vertexShader: `
            attribute float age, maxAge, size;
            varying float vLife;
            uniform float baseSize;
            void main() {
                vLife = age / maxAge;
                vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
                gl_PointSize = size * baseSize * (1.0 - vLife * 0.5) * (300.0 / -mvPos.z);
                gl_Position = projectionMatrix * mvPos;
            }
        `,
        fragmentShader: `
            uniform vec3 baseColor, endColor;
            varying float vLife;
            void main() {
                float dist = length(gl_PointCoord - 0.5) * 2.0;
                if (dist > 1.0) discard;
                float alpha = (1.0 - dist) * (1.0 - vLife);
                vec3 color = mix(baseColor, endColor, vLife);
                gl_FragColor = vec4(color, alpha);
            }
        `
    });

    const system = new THREE.Points(geometry, material);
    system.frustumCulled = false;

    system.userData = {
        velocities, ages, maxAges, sizes,
        emit(origin, count, speed = 5, lifetime = 1.0) {
            let emitted = 0;
            for (let i = 0; i < maxCount && emitted < count; i++) {
                if (ages[i] < 0) {
                    const i3 = i * 3;
                    positions[i3] = origin.x; positions[i3+1] = origin.y; positions[i3+2] = origin.z;
                    velocities[i3] = (Math.random()-0.5) * speed;
                    velocities[i3+1] = Math.random() * speed * 0.8 + speed * 0.2;
                    velocities[i3+2] = (Math.random()-0.5) * speed;
                    ages[i] = 0;
                    maxAges[i] = lifetime * (0.7 + Math.random() * 0.6);
                    sizes[i] = 0.5 + Math.random();
                    emitted++;
                }
            }
        },
        update(delta) {
            for (let i = 0; i < maxCount; i++) {
                if (ages[i] >= 0) {
                    ages[i] += delta;
                    if (ages[i] >= maxAges[i]) { ages[i] = -1; positions[i*3+1] = -9999; continue; }
                    const i3 = i * 3;
                    positions[i3] += velocities[i3] * delta;
                    positions[i3+1] += velocities[i3+1] * delta;
                    positions[i3+2] += velocities[i3+2] * delta;
                    velocities[i3+1] -= 9.8 * delta; // gravity
                }
            }
            geometry.attributes.position.needsUpdate = true;
            geometry.attributes.age.needsUpdate = true;
        }
    };
    return system;
}
```

## Ground Plane with Procedural Texture Variation

```javascript
function createDetailedGround(size = 200, biome = 'grass') {
    const palettes = {
        grass:  { base: [0x3a7a2a, 0x4a9a3a, 0x2d6b1d], accent: 0x8B6914 },
        snow:   { base: [0xe8eeff, 0xd8dff0, 0xf0f4ff], accent: 0x99aabb },
        desert: { base: [0xd4a457, 0xc49640, 0xe0b86b], accent: 0xa07830 },
        rock:   { base: [0x666666, 0x777777, 0x555555], accent: 0x888888 },
    };
    const palette = palettes[biome] || palettes.grass;

    const geo = new THREE.PlaneGeometry(size, size, 100, 100);
    geo.rotateX(-Math.PI / 2);

    // Vertex color variation
    const colors = new Float32Array(geo.attributes.position.count * 3);
    for (let i = 0; i < geo.attributes.position.count; i++) {
        const x = geo.attributes.position.getX(i);
        const z = geo.attributes.position.getZ(i);
        const noise = Math.sin(x * 0.1) * Math.cos(z * 0.08) * 0.5 + 0.5;
        const idx = Math.floor(noise * palette.base.length) % palette.base.length;
        const c = new THREE.Color(palette.base[idx]);
        // Add subtle random variation
        c.r += (Math.random() - 0.5) * 0.03;
        c.g += (Math.random() - 0.5) * 0.03;
        c.b += (Math.random() - 0.5) * 0.03;
        colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const mat = new THREE.MeshStandardMaterial({
        vertexColors: true, roughness: 0.9, metalness: 0.0
    });
    const ground = new THREE.Mesh(geo, mat);
    ground.receiveShadow = true;
    return ground;
}
```

## Grass Blades (instanced billboards)

```javascript
function createGrassField(count = 5000, area = 100) {
    const bladeGeo = new THREE.PlaneGeometry(0.15, 0.8, 1, 3);
    // Bend the blade
    const posAttr = bladeGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
        const y = posAttr.getY(i);
        const bend = (y / 0.8) * (y / 0.8) * 0.15;
        posAttr.setZ(i, bend);
    }

    const grassMat = new THREE.MeshStandardMaterial({
        color: 0x44aa22, side: THREE.DoubleSide, alphaTest: 0.5,
        roughness: 0.8, metalness: 0.0
    });

    const instanced = new THREE.InstancedMesh(bladeGeo, grassMat, count);
    const dummy = new THREE.Object3D();
    const color = new THREE.Color();

    for (let i = 0; i < count; i++) {
        dummy.position.set(
            (Math.random() - 0.5) * area,
            0,
            (Math.random() - 0.5) * area
        );
        dummy.rotation.y = Math.random() * Math.PI;
        dummy.scale.set(0.8 + Math.random() * 0.4, 0.6 + Math.random() * 0.8, 1);
        dummy.updateMatrix();
        instanced.setMatrixAt(i, dummy.matrix);

        // Color variation
        color.setHSL(0.28 + Math.random() * 0.06, 0.6 + Math.random() * 0.2, 0.25 + Math.random() * 0.15);
        instanced.setColorAt(i, color);
    }
    instanced.instanceMatrix.needsUpdate = true;
    instanced.instanceColor.needsUpdate = true;
    instanced.castShadow = true;
    return instanced;
}
```

## Character Outline / Toon Shading

```javascript
// Outline effect via inverted-hull method (add to any character group)
function addOutline(mesh, thickness = 0.03, color = 0x000000) {
    const outlineMat = new THREE.MeshBasicMaterial({
        color, side: THREE.BackSide
    });
    mesh.traverse(child => {
        if (child.isMesh) {
            const outline = child.clone();
            outline.material = outlineMat;
            outline.scale.multiplyScalar(1 + thickness);
            outline.castShadow = false;
            outline.receiveShadow = false;
            child.parent.add(outline);
        }
    });
}

// Toon material (cel shading)
function createToonMaterial(color, steps = 4) {
    const gradientMap = (() => {
        const canvas = document.createElement('canvas');
        canvas.width = steps; canvas.height = 1;
        const ctx = canvas.getContext('2d');
        for (let i = 0; i < steps; i++) {
            const v = Math.floor(((i + 0.5) / steps) * 255);
            ctx.fillStyle = `rgb(${v},${v},${v})`;
            ctx.fillRect(i, 0, 1, 1);
        }
        const tex = new THREE.CanvasTexture(canvas);
        tex.magFilter = THREE.NearestFilter;
        tex.minFilter = THREE.NearestFilter;
        return tex;
    })();
    return new THREE.MeshToonMaterial({ color, gradientMap });
}
```

## Lens Flare (lightweight)

```javascript
function createLensFlare(light, scene) {
    const flareGroup = new THREE.Group();
    const sprite = new THREE.SpriteMaterial({
        color: 0xffffee,
        transparent: true,
        opacity: 0.3,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        depthTest: false
    });

    const sizes = [3, 1.5, 0.8, 0.5, 1.2];
    const offsets = [0, 0.3, 0.5, 0.7, 0.9];

    sizes.forEach((s, i) => {
        const flare = new THREE.Sprite(sprite.clone());
        flare.scale.setScalar(s);
        flare.userData.offset = offsets[i];
        flareGroup.add(flare);
    });
    scene.add(flareGroup);

    return {
        update(camera) {
            const lightScreenPos = light.position.clone().project(camera);
            const visible = lightScreenPos.z < 1 && Math.abs(lightScreenPos.x) < 1.2 && Math.abs(lightScreenPos.y) < 1.2;
            flareGroup.visible = visible;
            if (!visible) return;

            const center = new THREE.Vector3(0, 0, 0);
            flareGroup.children.forEach(flare => {
                const t = flare.userData.offset;
                const pos = light.position.clone().lerp(center, t);
                flare.position.copy(pos);
            });
        }
    };
}
```

## Shadow Quality by Genre

```javascript
// For close-up games (FPS, third-person): high detail
sunLight.shadow.mapSize.set(4096, 4096);
sunLight.shadow.camera.left = sunLight.shadow.camera.bottom = -30;
sunLight.shadow.camera.right = sunLight.shadow.camera.top = 30;

// For large-area games (racing, open world): cascading shadow approach
// Use a shadow camera that follows the player
function updateShadowCamera(playerPos) {
    sunLight.shadow.camera.left = playerPos.x - 40;
    sunLight.shadow.camera.right = playerPos.x + 40;
    sunLight.shadow.camera.top = playerPos.z + 40;
    sunLight.shadow.camera.bottom = playerPos.z - 40;
    sunLight.target.position.copy(playerPos);
    sunLight.position.set(playerPos.x + 40, 60, playerPos.z + 30);
}
```

## Recommended Post-Processing Presets

### Cinematic (realistic games)
```javascript
bloomPass.strength = 0.25;
bloomPass.radius = 0.3;
bloomPass.threshold = 0.9;
colorGrading.contrast = 1.15;
colorGrading.saturation = 1.1;
colorGrading.vignetteIntensity = 0.35;
renderer.toneMappingExposure = 1.1;
```

### Stylized / Vibrant (cartoon, arcade games)
```javascript
bloomPass.strength = 0.5;
bloomPass.radius = 0.4;
bloomPass.threshold = 0.7;
colorGrading.contrast = 1.2;
colorGrading.saturation = 1.3;
colorGrading.vignetteIntensity = 0.2;
renderer.toneMappingExposure = 1.3;
```

### Dark / Horror
```javascript
bloomPass.strength = 0.6;
bloomPass.radius = 0.5;
bloomPass.threshold = 0.5;
colorGrading.contrast = 1.3;
colorGrading.saturation = 0.7;
colorGrading.vignetteIntensity = 0.6;
renderer.toneMappingExposure = 0.7;
```

### Snow / Bright Outdoors
```javascript
bloomPass.strength = 0.35;
bloomPass.radius = 0.3;
bloomPass.threshold = 0.8;
colorGrading.contrast = 1.05;
colorGrading.saturation = 0.95;
colorGrading.vignetteIntensity = 0.15;
renderer.toneMappingExposure = 1.4;
```

## Performance Tips for Graphics

- Use `InstancedMesh` for any object that appears 10+ times (trees, grass, rocks, particles)
- Set `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))` — cap at 2x for 4K displays
- Use `frustumCulled = true` (default) and set appropriate bounding spheres
- Pool particle systems — reuse geometries, don't create/destroy
- Shadow map: 2048x2048 is good default, 4096 for close-up, 1024 for mobile/perf
- Only the most important light casts shadows (usually sunLight)
- Use LOD (Level of Detail) for distant objects:
  ```javascript
  const lod = new THREE.LOD();
  lod.addLevel(highDetailMesh, 0);    // close
  lod.addLevel(medDetailMesh, 30);    // medium distance
  lod.addLevel(lowDetailMesh, 80);    // far
  ```
- Merge static geometries that share materials:
  ```javascript
  import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
  const merged = mergeGeometries(geometries);
  ```
