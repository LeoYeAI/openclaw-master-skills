# Three.js Engine Patterns by Game Type

## Importmap (use in every game)

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
```

## Common Setup (All Games)

**IMPORTANT**: For advanced graphics patterns (sky dome, water, terrain, environment maps, SSAO, color grading, procedural textures, toon shading, trails), see `graphics-quality.md`.

```javascript
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';

// Renderer — high quality defaults
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

// Post-processing — full quality stack
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

// SSAO for ambient occlusion depth
const ssaoPass = new SSAOPass(scene, camera, window.innerWidth, window.innerHeight);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
composer.addPass(ssaoPass);

// Bloom
const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight), 0.35, 0.3, 0.85
);
composer.addPass(bloomPass);

// Color grading (contrast, saturation, vignette) — see graphics-quality.md for full shader
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
        uniform float brightness, contrast, saturation, vignetteIntensity, vignetteRoundness;
        varying vec2 vUv;
        void main() {
            vec4 color = texture2D(tDiffuse, vUv);
            color.rgb += brightness;
            color.rgb = (color.rgb - 0.5) * contrast + 0.5;
            float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
            color.rgb = mix(vec3(gray), color.rgb, saturation);
            vec2 uv = vUv * 2.0 - 1.0;
            float vig = 1.0 - dot(uv * vignetteRoundness, uv * vignetteRoundness);
            color.rgb *= mix(1.0 - vignetteIntensity, 1.0, clamp(pow(vig, 1.5), 0.0, 1.0));
            gl_FragColor = color;
        }
    `
};
composer.addPass(new ShaderPass(colorGradingShader));

// FXAA final pass
const fxaaPass = new ShaderPass(FXAAShader);
fxaaPass.uniforms['resolution'].value.set(1/window.innerWidth, 1/window.innerHeight);
composer.addPass(fxaaPass);

// 4-light rig: key + fill + hemisphere + ambient
const sunLight = new THREE.DirectionalLight(0xfff0dd, 2.5);
sunLight.position.set(40, 60, 30);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(4096, 4096);
sunLight.shadow.camera.near = 0.5;
sunLight.shadow.camera.far = 200;
sunLight.shadow.camera.left = -80;
sunLight.shadow.camera.right = 80;
sunLight.shadow.camera.top = 80;
sunLight.shadow.camera.bottom = -80;
sunLight.shadow.bias = -0.0005;
sunLight.shadow.normalBias = 0.02;

const fillLight = new THREE.DirectionalLight(0x8899cc, 0.6);
fillLight.position.set(-30, 20, -20);

const hemiLight = new THREE.HemisphereLight(0x88bbff, 0x445522, 0.5);
const ambientLight = new THREE.AmbientLight(0x202030, 0.3);
scene.add(sunLight, fillLight, hemiLight, ambientLight);

// Fog — match to sky dome horizon color
scene.fog = new THREE.FogExp2(0x88aacc, 0.008);

// Environment map for PBR reflections (see graphics-quality.md for full implementation)
// createEnvironmentMap(scene, renderer);  // makes all metallic surfaces reflect

// Sky dome (see graphics-quality.md for createSkyDome shader)
// scene.add(createSkyDome(0x0066cc, 0xccddee, 0xffffaa));
```

## FPS / Shooter Pattern

```javascript
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

// Camera
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 1.7, 0); // Eye height

// Controls
const controls = new PointerLockControls(camera, document.body);
document.addEventListener('click', () => controls.lock());

// Movement with velocity and friction
const velocity = new THREE.Vector3();
const direction = new THREE.Vector3();
const keys = { w: false, a: false, s: false, d: false, space: false };
const SPEED = 25, FRICTION = 8, JUMP_FORCE = 12, GRAVITY = 30;
let onGround = true;

function updatePlayer(delta) {
    velocity.x -= velocity.x * FRICTION * delta;
    velocity.z -= velocity.z * FRICTION * delta;
    velocity.y -= GRAVITY * delta;
    direction.z = Number(keys.w) - Number(keys.s);
    direction.x = Number(keys.d) - Number(keys.a);
    direction.normalize();
    if (keys.w || keys.s) velocity.z -= direction.z * SPEED * delta;
    if (keys.a || keys.d) velocity.x -= direction.x * SPEED * delta;
    if (keys.space && onGround) { velocity.y = JUMP_FORCE; onGround = false; }
    controls.moveRight(-velocity.x * delta);
    controls.moveForward(-velocity.z * delta);
    camera.position.y += velocity.y * delta;
    if (camera.position.y < 1.7) { camera.position.y = 1.7; velocity.y = 0; onGround = true; }
    // View bob
    if (onGround && (keys.w || keys.a || keys.s || keys.d)) {
        camera.position.y += Math.sin(performance.now() * 0.008) * 0.03;
    }
}

// Raycaster shooting
const raycaster = new THREE.Raycaster();
raycaster.far = 200;
function shoot() {
    raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
    const hits = raycaster.intersectObjects(enemies, true);
    if (hits.length > 0) { /* damage enemy, spawn particles, floating damage number */ }
    shakeIntensity = 0.1; // screen shake
}

// Screen shake system
let shakeIntensity = 0;
function applyScreenShake(delta) {
    if (shakeIntensity > 0) {
        camera.rotation.x += (Math.random() - 0.5) * shakeIntensity;
        camera.rotation.y += (Math.random() - 0.5) * shakeIntensity;
        shakeIntensity *= 0.85;
        if (shakeIntensity < 0.001) shakeIntensity = 0;
    }
}
```

## Third-Person Pattern

**IMPORTANT**: WASD must move the player relative to CAMERA facing, not world axes. The camera orbits with mouse drag. This is the standard third-person feel (like every modern 3D game).

```javascript
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);

// Camera orbit state
let cameraYaw = 0;       // horizontal orbit angle (radians)
let cameraPitch = 0.4;   // vertical angle (0 = level, positive = looking down)
const cameraDistance = 10;
const cameraPitchMin = 0.1, cameraPitchMax = 1.2;
const cameraTarget = new THREE.Vector3();
let isDragging = false;

// Mouse drag to orbit camera
document.addEventListener('mousedown', (e) => { if (e.button === 0 || e.button === 2) isDragging = true; });
document.addEventListener('mouseup', () => { isDragging = false; });
document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    cameraYaw -= e.movementX * 0.005;
    cameraPitch = THREE.MathUtils.clamp(cameraPitch + e.movementY * 0.005, cameraPitchMin, cameraPitchMax);
});
document.addEventListener('contextmenu', e => e.preventDefault()); // prevent right-click menu

function updateCamera(delta) {
    // Spherical coords around player
    const desiredPos = new THREE.Vector3(
        player.position.x + Math.sin(cameraYaw) * Math.cos(cameraPitch) * cameraDistance,
        player.position.y + Math.sin(cameraPitch) * cameraDistance + 2,
        player.position.z + Math.cos(cameraYaw) * Math.cos(cameraPitch) * cameraDistance
    );
    camera.position.lerp(desiredPos, 8 * delta);
    cameraTarget.lerp(player.position.clone().add(new THREE.Vector3(0, 1.5, 0)), 10 * delta);
    camera.lookAt(cameraTarget);
}

// WASD movement RELATIVE TO CAMERA (not world axes!)
function updatePlayer(delta) {
    const inputZ = Number(!!keys['KeyW']) - Number(!!keys['KeyS']);  // forward/back
    const inputX = Number(!!keys['KeyD']) - Number(!!keys['KeyA']);  // strafe

    if (inputX !== 0 || inputZ !== 0) {
        // Get camera's forward direction projected onto XZ plane
        const camForward = new THREE.Vector3(-Math.sin(cameraYaw), 0, -Math.cos(cameraYaw)).normalize();
        const camRight = new THREE.Vector3(camForward.z, 0, -camForward.x);

        // Combine into world-space movement direction
        const moveDir = camForward.multiplyScalar(inputZ).add(camRight.multiplyScalar(inputX)).normalize();

        // Rotate character to face movement direction
        const targetAngle = Math.atan2(moveDir.x, moveDir.z);
        player.rotation.y = THREE.MathUtils.lerp(player.rotation.y, targetAngle, 10 * delta);

        // Move
        player.position.addScaledVector(moveDir, speed * delta);
    }
}
```

### Top-down / Isometric Third-Person (for maze, puzzle, strategy games)

For games viewed from above (mazes, puzzles, etc.), use a fixed or semi-fixed camera:

```javascript
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 500);
// Fixed isometric-ish angle
const cameraOffset = new THREE.Vector3(0, 15, 10);

function updateCamera(delta) {
    const desired = player.position.clone().add(cameraOffset);
    camera.position.lerp(desired, 6 * delta);
    camera.lookAt(player.position.x, 0, player.position.z);
}

// WASD moves in screen-relative directions (up=forward on screen, not world-north)
function updatePlayer(delta) {
    const inputZ = Number(!!keys['KeyW']) - Number(!!keys['KeyS']);
    const inputX = Number(!!keys['KeyD']) - Number(!!keys['KeyA']);
    if (inputX !== 0 || inputZ !== 0) {
        // For top-down: W moves "into screen" (negative Z), D moves right (positive X)
        const moveDir = new THREE.Vector3(inputX, 0, -inputZ).normalize();
        const targetAngle = Math.atan2(moveDir.x, moveDir.z);
        player.rotation.y = THREE.MathUtils.lerp(player.rotation.y, targetAngle, 10 * delta);
        player.position.addScaledVector(moveDir, speed * delta);
    }
}
```

## Racing Pattern

```javascript
const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 2000);

const vehicle = {
    position: new THREE.Vector3(), rotation: 0, speed: 0,
    maxSpeed: 80, acceleration: 30, braking: 50,
    turnSpeed: 2.5, friction: 0.98, mesh: null
};

function updateVehicle(delta) {
    if (keys.w) vehicle.speed += vehicle.acceleration * delta;
    if (keys.s) vehicle.speed -= vehicle.braking * delta;
    vehicle.speed *= vehicle.friction;
    vehicle.speed = THREE.MathUtils.clamp(vehicle.speed, -20, vehicle.maxSpeed);
    const turnFactor = Math.min(Math.abs(vehicle.speed) / 30, 1);
    if (keys.a) vehicle.rotation += vehicle.turnSpeed * turnFactor * delta;
    if (keys.d) vehicle.rotation -= vehicle.turnSpeed * turnFactor * delta;
    vehicle.position.x += Math.sin(vehicle.rotation) * vehicle.speed * delta;
    vehicle.position.z += Math.cos(vehicle.rotation) * vehicle.speed * delta;
    vehicle.mesh.position.copy(vehicle.position);
    vehicle.mesh.rotation.y = vehicle.rotation;
}

function updateChaseCamera(delta) {
    const behind = new THREE.Vector3(
        vehicle.position.x - Math.sin(vehicle.rotation) * 12,
        vehicle.position.y + 5,
        vehicle.position.z - Math.cos(vehicle.rotation) * 12
    );
    camera.position.lerp(behind, 4 * delta);
    const lookTarget = vehicle.position.clone().add(
        new THREE.Vector3(Math.sin(vehicle.rotation) * 10, 1, Math.cos(vehicle.rotation) * 10)
    );
    camera.lookAt(lookTarget);
}
```

## Top-Down / RTS / Tower Defense Pattern

```javascript
const frustumSize = 40;
const aspect = window.innerWidth / window.innerHeight;
const camera = new THREE.OrthographicCamera(
    -frustumSize * aspect / 2, frustumSize * aspect / 2,
    frustumSize / 2, -frustumSize / 2, 0.1, 1000
);
camera.position.set(0, 50, 30);
camera.lookAt(0, 0, 0);

// Mouse-to-world raycasting
const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
const raycaster = new THREE.Raycaster();
function getWorldPosition(event) {
    const mouse = new THREE.Vector2(
        (event.clientX / window.innerWidth) * 2 - 1,
        -(event.clientY / window.innerHeight) * 2 + 1
    );
    raycaster.setFromCamera(mouse, camera);
    const target = new THREE.Vector3();
    raycaster.ray.intersectPlane(groundPlane, target);
    return target;
}

// Grid snapping for tower placement
function snapToGrid(pos, gridSize = 2) {
    return new THREE.Vector3(
        Math.round(pos.x / gridSize) * gridSize, 0,
        Math.round(pos.z / gridSize) * gridSize
    );
}
```

## Platformer Pattern

```javascript
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);

function updateCamera(delta) {
    const targetX = player.position.x;
    const targetY = Math.max(player.position.y + 3, 5);
    camera.position.x = THREE.MathUtils.lerp(camera.position.x, targetX, 3 * delta);
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, targetY, 3 * delta);
    camera.position.z = 20;
    camera.lookAt(camera.position.x, camera.position.y - 1, 0);
}

// Double jump
let jumpsRemaining = 2;
function jump() {
    if (jumpsRemaining > 0) {
        velocity.y = JUMP_FORCE;
        jumpsRemaining--;
        onGround = false;
    }
}

// Platform collision
function checkPlatformCollision() {
    const playerBox = new THREE.Box3().setFromObject(playerMesh);
    for (const platform of platforms) {
        if (playerBox.intersectsBox(platform.box)) {
            if (velocity.y <= 0 && player.position.y > platform.mesh.position.y) {
                player.position.y = platform.mesh.position.y + platform.height / 2 + playerHeight / 2;
                velocity.y = 0;
                onGround = true;
                jumpsRemaining = 2;
            }
        }
    }
}
```

## Common Utility Patterns

### Particle System (Buffer-based, pooled)
```javascript
function createParticleSystem(count, { color = 0xffaa00, size = 0.3 } = {}) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const lifetimes = new Float32Array(count).fill(-1);
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({
        color, size, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false
    });
    const points = new THREE.Points(geometry, material);
    points.userData = { velocities, lifetimes, maxLife: 1.0 };
    return points;
}

function emitParticles(system, origin, count, speed = 5) {
    const pos = system.geometry.attributes.position.array;
    const { velocities, lifetimes } = system.userData;
    let emitted = 0;
    for (let i = 0; i < lifetimes.length && emitted < count; i++) {
        if (lifetimes[i] <= 0) {
            const i3 = i * 3;
            pos[i3] = origin.x; pos[i3+1] = origin.y; pos[i3+2] = origin.z;
            velocities[i3] = (Math.random()-0.5) * speed;
            velocities[i3+1] = Math.random() * speed;
            velocities[i3+2] = (Math.random()-0.5) * speed;
            lifetimes[i] = system.userData.maxLife;
            emitted++;
        }
    }
}

function updateParticles(system, delta) {
    const pos = system.geometry.attributes.position.array;
    const { velocities, lifetimes } = system.userData;
    for (let i = 0; i < lifetimes.length; i++) {
        if (lifetimes[i] > 0) {
            const i3 = i * 3;
            pos[i3] += velocities[i3] * delta;
            pos[i3+1] += velocities[i3+1] * delta;
            pos[i3+2] += velocities[i3+2] * delta;
            velocities[i3+1] -= 9.8 * delta;
            lifetimes[i] -= delta;
            if (lifetimes[i] <= 0) pos[i3+1] = -999;
        }
    }
    system.geometry.attributes.position.needsUpdate = true;
}
```

### Object Pooling
```javascript
class ObjectPool {
    constructor(factory, initialSize = 20) {
        this.factory = factory;
        this.pool = [];
        this.active = [];
        for (let i = 0; i < initialSize; i++) {
            const obj = factory();
            obj.visible = false;
            this.pool.push(obj);
        }
    }
    get() {
        const obj = this.pool.pop() || this.factory();
        obj.visible = true;
        this.active.push(obj);
        return obj;
    }
    release(obj) {
        obj.visible = false;
        const idx = this.active.indexOf(obj);
        if (idx >= 0) this.active.splice(idx, 1);
        this.pool.push(obj);
    }
}
```

### Instanced Meshes (for many identical objects)
```javascript
function createInstancedTrees(count, area) {
    const trunkGeo = new THREE.CylinderGeometry(0.2, 0.3, 2, 6);
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
    const canopyGeo = new THREE.ConeGeometry(1.5, 3, 6);
    const canopyMat = new THREE.MeshStandardMaterial({ color: 0x2d5a1e, flatShading: true });
    const trunkMesh = new THREE.InstancedMesh(trunkGeo, trunkMat, count);
    const canopyMesh = new THREE.InstancedMesh(canopyGeo, canopyMat, count);
    trunkMesh.castShadow = true; canopyMesh.castShadow = true;
    const dummy = new THREE.Object3D();
    for (let i = 0; i < count; i++) {
        const x = (Math.random() - 0.5) * area;
        const z = (Math.random() - 0.5) * area;
        const scale = 0.8 + Math.random() * 0.6;
        dummy.position.set(x, 1 * scale, z); dummy.scale.setScalar(scale);
        dummy.updateMatrix(); trunkMesh.setMatrixAt(i, dummy.matrix);
        dummy.position.y = 3 * scale;
        dummy.updateMatrix(); canopyMesh.setMatrixAt(i, dummy.matrix);
    }
    return [trunkMesh, canopyMesh];
}
```

### Floating Damage Numbers
```javascript
const damageNumbers = [];
function spawnDamageNumber(position, amount, color = '#ff4444') {
    const div = document.createElement('div');
    div.textContent = amount;
    div.style.cssText = `position:absolute;color:${color};font-size:24px;font-weight:bold;
        pointer-events:none;text-shadow:0 0 4px #000;z-index:100;`;
    document.body.appendChild(div);
    damageNumbers.push({ el: div, pos: position.clone(), vy: 3, life: 1.0 });
}
function updateDamageNumbers(delta, camera) {
    for (let i = damageNumbers.length - 1; i >= 0; i--) {
        const dn = damageNumbers[i];
        dn.pos.y += dn.vy * delta;
        dn.life -= delta;
        dn.el.style.opacity = dn.life;
        const screen = dn.pos.clone().project(camera);
        dn.el.style.left = ((screen.x + 1) / 2 * window.innerWidth) + 'px';
        dn.el.style.top = ((-screen.y + 1) / 2 * window.innerHeight) + 'px';
        if (dn.life <= 0) { dn.el.remove(); damageNumbers.splice(i, 1); }
    }
}
```

### RPG / Adventure Overworld Pattern
```javascript
// Top-down-ish camera following player character
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 500);
const cameraOffset = new THREE.Vector3(0, 12, 10);

// Player character (third-person visible)
const playerGroup = createPlayerModel(); // procedural character
scene.add(playerGroup);
const playerVel = new THREE.Vector3();
const PLAYER_SPEED = 6;

function updateOverworldPlayer(delta) {
    const inputDir = new THREE.Vector3(
        Number(keys.d || keys.ArrowRight) - Number(keys.a || keys.ArrowLeft),
        0,
        Number(keys.s || keys.ArrowDown) - Number(keys.w || keys.ArrowUp)
    );
    if (inputDir.length() > 0) {
        inputDir.normalize();
        playerGroup.position.addScaledVector(inputDir, PLAYER_SPEED * delta);
        // Face movement direction
        const targetAngle = Math.atan2(inputDir.x, inputDir.z);
        playerGroup.rotation.y = THREE.MathUtils.lerp(playerGroup.rotation.y, targetAngle, 10 * delta);
        // Walk bob
        playerGroup.position.y = Math.abs(Math.sin(performance.now() * 0.01)) * 0.1;
    }
    // Camera follow
    const desiredCamPos = playerGroup.position.clone().add(cameraOffset);
    camera.position.lerp(desiredCamPos, 5 * delta);
    camera.lookAt(playerGroup.position.x, 0, playerGroup.position.z);
}

// NPC interaction (E key)
function checkNPCInteraction() {
    const interactRange = 2.5;
    for (const npc of npcs) {
        const dist = playerGroup.position.distanceTo(npc.mesh.position);
        if (dist < interactRange) {
            // Show interaction prompt
            npc.showPrompt = true;
            if (keys.e) {
                npc.interact();
                keys.e = false; // consume
            }
        } else {
            npc.showPrompt = false;
        }
    }
}

// Zone transition / encounter check
function checkZoneAndEncounters(delta) {
    const zone = getCurrentZone(playerGroup.position);
    // Random encounter in wild zones
    if (zone.encounters && (keys.w || keys.a || keys.s || keys.d)) {
        state.encounterTimer += delta;
        if (state.encounterTimer > 1) { // check every second of movement
            state.encounterTimer = 0;
            const wild = checkWildEncounter(playerGroup.position, zone.biome);
            if (wild) startBattle(state.collection.getFirstAlive(), wild);
        }
    }
}
```

### Transition Effects (mode switches)
```javascript
// Screen fade for mode transitions (overworld → battle, etc.)
const transitionOverlay = document.createElement('div');
transitionOverlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:#000;opacity:0;transition:opacity 0.4s;pointer-events:none;z-index:50;';
document.body.appendChild(transitionOverlay);

function fadeTransition(callback, duration = 0.4) {
    transitionOverlay.style.opacity = '1';
    setTimeout(() => {
        callback();
        setTimeout(() => { transitionOverlay.style.opacity = '0'; }, 50);
    }, duration * 1000);
}

// Usage: fadeTransition(() => { gameMode.switch(MODES.BATTLE); setupBattleScene(); });
```

### Debug: render_game_to_text (from OpenAI pattern)
```javascript
// Expose game state as JSON for debugging/automated testing
window.render_game_to_text = () => JSON.stringify({
    mode: gameState.mode, // 'title' | 'playing' | 'gameover'
    player: { x: player.position.x, y: player.position.y, z: player.position.z, health: player.health },
    enemies: enemies.map(e => ({ x: e.position.x, z: e.position.z, health: e.health, state: e.aiState })),
    score: gameState.score,
    wave: gameState.wave,
    time: gameState.time
});

// Deterministic time stepping for testing
window.advanceTime = (ms) => {
    const steps = Math.max(1, Math.round(ms / (1000 / 60)));
    for (let i = 0; i < steps; i++) update(1 / 60);
    render();
};
```
