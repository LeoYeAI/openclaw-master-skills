# Procedural Asset Recipes

Build all game characters and objects from Three.js primitives. Use `THREE.Group` to combine parts. Target 15-25 primitives per character for detail. Use `MeshStandardMaterial` with `flatShading: true` for a cohesive low-poly aesthetic.

## Color Palettes by Theme

### Forest / Nature
```
ground: 0x4a7c3f, darkGrass: 0x3a6b2f, tree: 0x2d5a1e, trunk: 0x8B4513,
flowers: [0xff6b9d, 0xffd93d, 0x6bcb77], rocks: [0x808080, 0x696969, 0x909090],
sky: 0x87CEEB, water: 0x4a90d9
```

### Desert
```
sand: 0xd4a574, darkSand: 0xc4956a, rock: 0xa0522d, cactus: 0x228B22,
sky: 0xf4e9d8, sun: 0xffd700, mesa: 0xcd853f
```

### Space / Sci-Fi
```
hull: 0x4a5568, accent: 0x00d4ff, engine: 0xff6b35, glass: 0x88ccff,
stars: 0xffffff, nebula: [0x6b21a8, 0x1e40af, 0xbe123c], laser: 0x00ff88
```

### Urban / City
```
building: [0x6b7280, 0x4b5563, 0x374151], road: 0x374151,
sidewalk: 0x9ca3af, window: 0xffd700, car: [0xef4444, 0x3b82f6, 0xf59e0b],
sky: 0x1e3a5f
```

### Cartoon / Playful
```
primary: 0xff6b6b, secondary: 0x4ecdc4, accent: 0xffe66d,
ground: 0x95e06c, sky: 0x74b9ff, cloud: 0xffffff, shadow: 0xdfe6e9
```

## Humanoid Character (20+ parts)

```javascript
function createHumanoid({ bodyColor = 0x4a90d9, skinColor = 0xffdbac, height = 1.8 } = {}) {
    const g = new THREE.Group();
    const mat = (color) => new THREE.MeshStandardMaterial({ color, flatShading: true });

    // Torso (2 parts: chest + waist)
    const chest = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.4, 0.3), mat(bodyColor));
    chest.position.y = 1.15;
    const waist = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.25, 0.28), mat(bodyColor));
    waist.position.y = 0.85;

    // Head
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 6), mat(skinColor));
    head.position.y = 1.55;

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.03, 6, 4);
    const eyeMat = mat(0x222222);
    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.06, 1.57, 0.15);
    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.06, 1.57, 0.15);

    // Arms (upper + lower each)
    const armGeo = new THREE.CylinderGeometry(0.05, 0.05, 0.3, 6);
    const leftUpperArm = new THREE.Mesh(armGeo, mat(bodyColor));
    leftUpperArm.position.set(-0.35, 1.1, 0);
    const leftLowerArm = new THREE.Mesh(armGeo, mat(skinColor));
    leftLowerArm.position.set(-0.35, 0.8, 0);
    const rightUpperArm = new THREE.Mesh(armGeo, mat(bodyColor));
    rightUpperArm.position.set(0.35, 1.1, 0);
    const rightLowerArm = new THREE.Mesh(armGeo, mat(skinColor));
    rightLowerArm.position.set(0.35, 0.8, 0);

    // Hands
    const handGeo = new THREE.SphereGeometry(0.05, 6, 4);
    const leftHand = new THREE.Mesh(handGeo, mat(skinColor));
    leftHand.position.set(-0.35, 0.62, 0);
    const rightHand = new THREE.Mesh(handGeo, mat(skinColor));
    rightHand.position.set(0.35, 0.62, 0);

    // Legs (upper + lower each)
    const legGeo = new THREE.CylinderGeometry(0.07, 0.06, 0.35, 6);
    const leftUpperLeg = new THREE.Mesh(legGeo, mat(0x2c3e50));
    leftUpperLeg.position.set(-0.12, 0.55, 0);
    const leftLowerLeg = new THREE.Mesh(legGeo, mat(0x2c3e50));
    leftLowerLeg.position.set(-0.12, 0.22, 0);
    const rightUpperLeg = new THREE.Mesh(legGeo, mat(0x2c3e50));
    rightUpperLeg.position.set(0.12, 0.55, 0);
    const rightLowerLeg = new THREE.Mesh(legGeo, mat(0x2c3e50));
    rightLowerLeg.position.set(0.12, 0.22, 0);

    // Feet
    const footGeo = new THREE.BoxGeometry(0.1, 0.06, 0.16);
    const leftFoot = new THREE.Mesh(footGeo, mat(0x333333));
    leftFoot.position.set(-0.12, 0.03, 0.03);
    const rightFoot = new THREE.Mesh(footGeo, mat(0x333333));
    rightFoot.position.set(0.12, 0.03, 0.03);

    g.add(chest, waist, head, leftEye, rightEye,
          leftUpperArm, leftLowerArm, rightUpperArm, rightLowerArm,
          leftHand, rightHand,
          leftUpperLeg, leftLowerLeg, rightUpperLeg, rightLowerLeg,
          leftFoot, rightFoot);

    g.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
    return g;
}
```

## Animal: Raccoon

```javascript
function createRaccoon() {
    const g = new THREE.Group();
    const mat = (color) => new THREE.MeshStandardMaterial({ color, flatShading: true });

    // Body
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.3, 0.5, 4, 8), mat(0x808080));
    body.rotation.x = Math.PI / 2;
    body.position.set(0, 0.4, 0);

    // Head
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 6), mat(0x909090));
    head.position.set(0, 0.55, 0.4);

    // Snout
    const snout = new THREE.Mesh(new THREE.SphereGeometry(0.1, 6, 4), mat(0xcccccc));
    snout.position.set(0, 0.5, 0.6);
    snout.scale.set(1, 0.8, 1.2);

    // Nose
    const nose = new THREE.Mesh(new THREE.SphereGeometry(0.04, 4, 4), mat(0x222222));
    nose.position.set(0, 0.52, 0.7);

    // Eye mask (dark patches)
    const maskGeo = new THREE.SphereGeometry(0.08, 6, 4);
    const maskMat = mat(0x333333);
    const leftMask = new THREE.Mesh(maskGeo, maskMat);
    leftMask.position.set(-0.1, 0.58, 0.55);
    leftMask.scale.set(1.3, 0.8, 0.5);
    const rightMask = new THREE.Mesh(maskGeo, maskMat);
    rightMask.position.set(0.1, 0.58, 0.55);
    rightMask.scale.set(1.3, 0.8, 0.5);

    // Eyes (white + pupil)
    const eyeWhite = new THREE.SphereGeometry(0.04, 6, 4);
    const leftEyeW = new THREE.Mesh(eyeWhite, mat(0xffffff));
    leftEyeW.position.set(-0.1, 0.6, 0.58);
    const rightEyeW = new THREE.Mesh(eyeWhite, mat(0xffffff));
    rightEyeW.position.set(0.1, 0.6, 0.58);
    const pupilGeo = new THREE.SphereGeometry(0.02, 4, 4);
    const leftPupil = new THREE.Mesh(pupilGeo, mat(0x111111));
    leftPupil.position.set(-0.1, 0.6, 0.62);
    const rightPupil = new THREE.Mesh(pupilGeo, mat(0x111111));
    rightPupil.position.set(0.1, 0.6, 0.62);

    // Ears
    const earGeo = new THREE.ConeGeometry(0.08, 0.12, 4);
    const leftEar = new THREE.Mesh(earGeo, mat(0x808080));
    leftEar.position.set(-0.15, 0.75, 0.35);
    const rightEar = new THREE.Mesh(earGeo, mat(0x808080));
    rightEar.position.set(0.15, 0.75, 0.35);

    // Legs (4)
    const legGeo = new THREE.CylinderGeometry(0.06, 0.05, 0.25, 6);
    const legMat = mat(0x606060);
    const fl = new THREE.Mesh(legGeo, legMat); fl.position.set(-0.15, 0.12, 0.2);
    const fr = new THREE.Mesh(legGeo, legMat); fr.position.set(0.15, 0.12, 0.2);
    const bl = new THREE.Mesh(legGeo, legMat); bl.position.set(-0.15, 0.12, -0.2);
    const br = new THREE.Mesh(legGeo, legMat); br.position.set(0.15, 0.12, -0.2);

    // Tail (striped)
    const tailGroup = new THREE.Group();
    for (let i = 0; i < 6; i++) {
        const seg = new THREE.Mesh(
            new THREE.CylinderGeometry(0.06 - i * 0.006, 0.06 - (i+1) * 0.006, 0.12, 6),
            mat(i % 2 === 0 ? 0x808080 : 0x333333)
        );
        seg.position.set(0, 0.3 + i * 0.08, -0.4 - i * 0.06);
        seg.rotation.x = -0.3 - i * 0.15;
        tailGroup.add(seg);
    }

    g.add(body, head, snout, nose, leftMask, rightMask,
          leftEyeW, rightEyeW, leftPupil, rightPupil,
          leftEar, rightEar, fl, fr, bl, br, tailGroup);

    g.traverse(c => { if (c.isMesh) { c.castShadow = true; } });
    return g;
}
```

## Vehicle (Spaceship)

```javascript
function createSpaceship({ color = 0x4a5568, accentColor = 0x00d4ff } = {}) {
    const g = new THREE.Group();
    const mat = (c) => new THREE.MeshStandardMaterial({ color: c, flatShading: true });
    const glow = (c) => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 0.5 });

    // Fuselage
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.4, 3, 8), mat(color));
    body.rotation.x = Math.PI / 2;

    // Cockpit
    const cockpit = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 6), mat(0x88ccff));
    cockpit.position.set(0, 0.15, 0.8);
    cockpit.scale.set(0.8, 0.6, 1.2);

    // Wings
    const wingGeo = new THREE.BoxGeometry(2.5, 0.05, 0.8);
    const wings = new THREE.Mesh(wingGeo, mat(color));
    wings.position.set(0, 0, -0.2);

    // Wing tips
    const tipGeo = new THREE.BoxGeometry(0.2, 0.15, 0.3);
    const leftTip = new THREE.Mesh(tipGeo, mat(accentColor));
    leftTip.position.set(-1.25, 0.05, -0.2);
    const rightTip = new THREE.Mesh(tipGeo, mat(accentColor));
    rightTip.position.set(1.25, 0.05, -0.2);

    // Tail fin
    const tailFin = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.6, 0.5), mat(color));
    tailFin.position.set(0, 0.3, -1.2);

    // Engines (2)
    const engineGeo = new THREE.CylinderGeometry(0.12, 0.15, 0.5, 8);
    const leftEngine = new THREE.Mesh(engineGeo, mat(0x333333));
    leftEngine.rotation.x = Math.PI / 2;
    leftEngine.position.set(-0.5, -0.1, -1.2);
    const rightEngine = new THREE.Mesh(engineGeo, mat(0x333333));
    rightEngine.rotation.x = Math.PI / 2;
    rightEngine.position.set(0.5, -0.1, -1.2);

    // Engine glow
    const glowGeo = new THREE.SphereGeometry(0.1, 6, 4);
    const leftGlow = new THREE.Mesh(glowGeo, glow(0xff6b35));
    leftGlow.position.set(-0.5, -0.1, -1.5);
    const rightGlow = new THREE.Mesh(glowGeo, glow(0xff6b35));
    rightGlow.position.set(0.5, -0.1, -1.5);

    g.add(body, cockpit, wings, leftTip, rightTip, tailFin,
          leftEngine, rightEngine, leftGlow, rightGlow);
    g.traverse(c => { if (c.isMesh) { c.castShadow = true; } });
    return g;
}
```

## Vehicle (Car/Racer)

```javascript
function createCar({ color = 0xef4444 } = {}) {
    const g = new THREE.Group();
    const mat = (c) => new THREE.MeshStandardMaterial({ color: c, flatShading: true });

    // Body
    const body = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.4, 2.4), mat(color));
    body.position.y = 0.35;

    // Cabin
    const cabin = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.35, 1.2), mat(color));
    cabin.position.set(0, 0.7, -0.15);

    // Windshield
    const windshield = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.3, 0.05), mat(0x88ccff));
    windshield.position.set(0, 0.7, 0.45);
    windshield.rotation.x = -0.3;

    // Wheels (4)
    const wheelGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.15, 12);
    const wheelMat = mat(0x222222);
    const positions = [[-0.55, 0.2, 0.7], [0.55, 0.2, 0.7], [-0.55, 0.2, -0.7], [0.55, 0.2, -0.7]];
    positions.forEach(([x, y, z]) => {
        const wheel = new THREE.Mesh(wheelGeo, wheelMat);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(x, y, z);
        g.add(wheel);
    });

    // Headlights
    const lightGeo = new THREE.SphereGeometry(0.06, 6, 4);
    const lightMat = new THREE.MeshStandardMaterial({ color: 0xffffcc, emissive: 0xffffcc, emissiveIntensity: 0.8 });
    const hl = new THREE.Mesh(lightGeo, lightMat); hl.position.set(-0.4, 0.35, 1.2);
    const hr = new THREE.Mesh(lightGeo, lightMat); hr.position.set(0.4, 0.35, 1.2);

    g.add(body, cabin, windshield, hl, hr);
    g.traverse(c => { if (c.isMesh) { c.castShadow = true; } });
    return g;
}
```

## Environment Objects

### Trees (3 types)
```javascript
function createPineTree(height = 4) {
    const g = new THREE.Group();
    const mat = (c) => new THREE.MeshStandardMaterial({ color: c, flatShading: true });
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, height * 0.3, 6), mat(0x8B4513));
    trunk.position.y = height * 0.15;
    for (let i = 0; i < 3; i++) {
        const r = (1.2 - i * 0.3);
        const h = height * 0.3;
        const cone = new THREE.Mesh(new THREE.ConeGeometry(r, h, 7), mat(0x2d5a1e - i * 0x050505));
        cone.position.y = height * 0.3 + i * h * 0.6;
        g.add(cone);
    }
    g.add(trunk);
    g.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
    return g;
}

function createRoundTree(height = 3.5) {
    const g = new THREE.Group();
    const mat = (c) => new THREE.MeshStandardMaterial({ color: c, flatShading: true });
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.18, height * 0.4, 6), mat(0x8B4513));
    trunk.position.y = height * 0.2;
    const canopy = new THREE.Mesh(new THREE.SphereGeometry(height * 0.35, 8, 6), mat(0x4a7c3f));
    canopy.position.y = height * 0.6;
    g.add(trunk, canopy);
    g.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
    return g;
}
```

### Rocks
```javascript
function createRock(size = 1) {
    const geo = new THREE.DodecahedronGeometry(size, 0);
    // Deform vertices for organic look
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        pos.setX(i, pos.getX(i) + (Math.random() - 0.5) * size * 0.3);
        pos.setY(i, pos.getY(i) * (0.5 + Math.random() * 0.3));
        pos.setZ(i, pos.getZ(i) + (Math.random() - 0.5) * size * 0.3);
    }
    geo.computeVertexNormals();
    const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
        color: 0x808080, flatShading: true, roughness: 0.9
    }));
    mesh.castShadow = true; mesh.receiveShadow = true;
    return mesh;
}
```

### Buildings
```javascript
function createBuilding({ width = 4, height = 8, depth = 4, color = 0x6b7280 } = {}) {
    const g = new THREE.Group();
    const mat = (c) => new THREE.MeshStandardMaterial({ color: c, flatShading: true });
    const body = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), mat(color));
    body.position.y = height / 2;
    g.add(body);
    // Windows
    const winMat = new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0xffd700, emissiveIntensity: 0.3 });
    const winGeo = new THREE.PlaneGeometry(0.4, 0.5);
    for (let floor = 0; floor < Math.floor(height / 1.5); floor++) {
        for (let col = 0; col < Math.floor(width / 1.2); col++) {
            const win = new THREE.Mesh(winGeo, winMat);
            win.position.set(
                -width/2 + 0.8 + col * 1.2,
                1 + floor * 1.5,
                depth/2 + 0.01
            );
            g.add(win);
        }
    }
    g.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
    return g;
}
```

## Weapons

```javascript
function createGun() {
    const g = new THREE.Group();
    const mat = (c) => new THREE.MeshStandardMaterial({ color: c, flatShading: true, metalness: 0.6 });
    // Barrel
    const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.025, 0.5, 8), mat(0x333333));
    barrel.rotation.x = Math.PI / 2;
    barrel.position.z = 0.25;
    // Body
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.08, 0.3), mat(0x444444));
    // Grip
    const grip = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.12, 0.06), mat(0x5c3a1e));
    grip.position.set(0, -0.08, -0.05);
    grip.rotation.x = 0.3;
    // Magazine
    const mag = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.1, 0.04), mat(0x333333));
    mag.position.set(0, -0.08, 0.05);
    g.add(barrel, body, grip, mag);
    return g;
}
```

## Animal: Tiger

```javascript
function createTiger() {
    const g = new THREE.Group();
    const mat = (color) => new THREE.MeshStandardMaterial({ color, flatShading: true });
    const orange = 0xe88830, black = 0x222222, white = 0xf0e6d0;

    // Body (larger than raccoon)
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.4, 0.8, 4, 8), mat(orange));
    body.rotation.x = Math.PI / 2; body.position.set(0, 0.6, 0);
    // Belly
    const belly = new THREE.Mesh(new THREE.CapsuleGeometry(0.35, 0.6, 4, 8), mat(white));
    belly.rotation.x = Math.PI / 2; belly.position.set(0, 0.5, 0);

    // Head
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), mat(orange));
    head.position.set(0, 0.75, 0.6); head.scale.set(1, 0.9, 1.1);
    // Cheeks/mane
    const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.15, 6, 4), mat(white));
    cheekL.position.set(-0.2, 0.7, 0.7); cheekL.scale.set(1, 1.2, 0.8);
    const cheekR = new THREE.Mesh(new THREE.SphereGeometry(0.15, 6, 4), mat(white));
    cheekR.position.set(0.2, 0.7, 0.7); cheekR.scale.set(1, 1.2, 0.8);
    // Snout
    const snout = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 4), mat(white));
    snout.position.set(0, 0.68, 0.85); snout.scale.set(1, 0.7, 1);
    const nose = new THREE.Mesh(new THREE.SphereGeometry(0.05, 4, 4), mat(0xff6677));
    nose.position.set(0, 0.72, 0.95);
    // Eyes (fierce)
    const eyeGeo = new THREE.SphereGeometry(0.05, 6, 4);
    const lEye = new THREE.Mesh(eyeGeo, mat(0xeedd00)); lEye.position.set(-0.12, 0.82, 0.8);
    const rEye = new THREE.Mesh(eyeGeo, mat(0xeedd00)); rEye.position.set(0.12, 0.82, 0.8);
    const pupGeo = new THREE.SphereGeometry(0.025, 4, 4);
    const lPup = new THREE.Mesh(pupGeo, mat(black)); lPup.position.set(-0.12, 0.82, 0.85);
    const rPup = new THREE.Mesh(pupGeo, mat(black)); rPup.position.set(0.12, 0.82, 0.85);
    // Ears
    const earGeo = new THREE.ConeGeometry(0.08, 0.12, 4);
    const lEar = new THREE.Mesh(earGeo, mat(orange)); lEar.position.set(-0.2, 1.0, 0.5);
    const rEar = new THREE.Mesh(earGeo, mat(orange)); rEar.position.set(0.2, 1.0, 0.5);

    // Stripes (black markings on body)
    for (let i = 0; i < 5; i++) {
        const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.05, 0.08), mat(black));
        stripe.position.set(0, 0.7 + (Math.random()-0.5)*0.15, -0.2 + i * 0.2);
        stripe.rotation.z = (Math.random()-0.5) * 0.3;
        g.add(stripe);
    }

    // Legs (muscular)
    const legGeo = new THREE.CylinderGeometry(0.08, 0.07, 0.4, 6);
    const legM = mat(orange);
    const fl = new THREE.Mesh(legGeo, legM); fl.position.set(-0.2, 0.2, 0.35);
    const fr = new THREE.Mesh(legGeo, legM); fr.position.set(0.2, 0.2, 0.35);
    const bl = new THREE.Mesh(legGeo, legM); bl.position.set(-0.2, 0.2, -0.35);
    const br = new THREE.Mesh(legGeo, legM); br.position.set(0.2, 0.2, -0.35);
    // Paws
    const pawGeo = new THREE.SphereGeometry(0.07, 5, 4);
    const pawM = mat(0xd47828);
    [fl, fr, bl, br].forEach(leg => {
        const paw = new THREE.Mesh(pawGeo, pawM);
        paw.position.copy(leg.position); paw.position.y = 0.02;
        g.add(paw);
    });

    // Tail (long, curving)
    const tailGroup = new THREE.Group();
    for (let i = 0; i < 8; i++) {
        const seg = new THREE.Mesh(
            new THREE.CylinderGeometry(0.05 - i*0.004, 0.05 - (i+1)*0.004, 0.12, 6),
            mat(i % 3 === 0 ? black : orange)
        );
        seg.position.set(0, 0.5 + i * 0.04, -0.6 - i * 0.08);
        seg.rotation.x = -0.2 - i * 0.1;
        tailGroup.add(seg);
    }

    // Fangs
    const fangGeo = new THREE.ConeGeometry(0.02, 0.06, 4);
    const fangM = mat(0xeeeeee);
    const lFang = new THREE.Mesh(fangGeo, fangM); lFang.position.set(-0.04, 0.6, 0.9); lFang.rotation.x = Math.PI;
    const rFang = new THREE.Mesh(fangGeo, fangM); rFang.position.set(0.04, 0.6, 0.9); rFang.rotation.x = Math.PI;

    g.add(body, belly, head, cheekL, cheekR, snout, nose,
          lEye, rEye, lPup, rPup, lEar, rEar,
          fl, fr, bl, br, tailGroup, lFang, rFang);
    g.traverse(c => { if (c.isMesh) { c.castShadow = true; } });
    return g;
}
```

## Elemental Spirit / Creature (customizable)

```javascript
function createElementalSpirit({ type = 'fire', size = 0.8 } = {}) {
    const g = new THREE.Group();
    const colors = {
        fire:     { primary: 0xff6b35, secondary: 0xffaa00, glow: 0xff4400 },
        water:    { primary: 0x4a90d9, secondary: 0x88ccff, glow: 0x2266ff },
        ice:      { primary: 0xaaddff, secondary: 0xffffff, glow: 0x66ccff },
        earth:    { primary: 0x8B6914, secondary: 0x6b8e23, glow: 0xaa8833 },
        electric: { primary: 0xffd700, secondary: 0xffff88, glow: 0xffee00 },
        dark:     { primary: 0x4a0080, secondary: 0x8833cc, glow: 0x6600aa },
        light:    { primary: 0xffffcc, secondary: 0xffffff, glow: 0xffffaa },
        air:      { primary: 0xcceecc, secondary: 0xeeffee, glow: 0xaaddaa },
    };
    const c = colors[type] || colors.fire;
    const mat = (color) => new THREE.MeshStandardMaterial({ color, flatShading: true });
    const glow = (color) => new THREE.MeshStandardMaterial({ color, flatShading: true, emissive: color, emissiveIntensity: 0.6 });

    // Core body (orb-like with floating fragments)
    const core = new THREE.Mesh(new THREE.SphereGeometry(size * 0.4, 8, 6), glow(c.primary));
    core.position.y = size;
    // Inner glow
    const inner = new THREE.Mesh(new THREE.SphereGeometry(size * 0.25, 6, 4), glow(c.glow));
    inner.position.y = size;
    // Eyes (two glowing dots)
    const eyeGeo = new THREE.SphereGeometry(size * 0.06, 4, 4);
    const eyeMat = glow(0xffffff);
    const lEye = new THREE.Mesh(eyeGeo, eyeMat); lEye.position.set(-size*0.12, size*1.05, size*0.35);
    const rEye = new THREE.Mesh(eyeGeo, eyeMat); rEye.position.set(size*0.12, size*1.05, size*0.35);

    // Floating fragments orbiting the core
    const fragments = new THREE.Group();
    for (let i = 0; i < 6; i++) {
        const frag = new THREE.Mesh(
            new THREE.OctahedronGeometry(size * (0.08 + Math.random() * 0.06), 0),
            mat(Math.random() > 0.5 ? c.primary : c.secondary)
        );
        const angle = (i / 6) * Math.PI * 2;
        const radius = size * (0.5 + Math.random() * 0.2);
        frag.position.set(Math.cos(angle) * radius, size + (Math.random()-0.5) * size * 0.4, Math.sin(angle) * radius);
        fragments.add(frag);
    }

    // Wispy trails (type-specific)
    if (type === 'fire' || type === 'electric') {
        for (let i = 0; i < 3; i++) {
            const wisp = new THREE.Mesh(new THREE.ConeGeometry(size*0.08, size*0.4, 4), glow(c.secondary));
            wisp.position.set((Math.random()-0.5)*size*0.3, size*0.4 - i*0.15, (Math.random()-0.5)*size*0.3);
            wisp.rotation.x = Math.PI; // point downward
            g.add(wisp);
        }
    }

    // Point light for ambient glow
    const light = new THREE.PointLight(c.glow, 0.8, size * 5);
    light.position.y = size;
    g.add(core, inner, lEye, rEye, fragments, light);

    // Animation data stored on group
    g.userData = { fragments, bobPhase: Math.random() * Math.PI * 2, spinSpeed: 0.5 + Math.random() * 0.5 };
    g.traverse(ch => { if (ch.isMesh) ch.castShadow = true; });
    return g;
}

// Call each frame to animate spirits:
function animateSpirit(group, time) {
    const { fragments, bobPhase, spinSpeed } = group.userData;
    // Bob up and down
    group.position.y = Math.sin(time * 2 + bobPhase) * 0.15;
    // Spin fragments
    if (fragments) fragments.rotation.y = time * spinSpeed;
}
```

## Dragon

```javascript
function createDragon({ color = 0x882222, wingColor = 0xaa4444, size = 1 } = {}) {
    const g = new THREE.Group();
    const mat = (c) => new THREE.MeshStandardMaterial({ color: c, flatShading: true });
    const s = size;

    // Body
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.4*s, 1.0*s, 4, 8), mat(color));
    body.rotation.x = Math.PI / 2; body.position.set(0, 0.8*s, 0);
    // Belly (lighter)
    const belly = new THREE.Mesh(new THREE.CapsuleGeometry(0.35*s, 0.8*s, 4, 8), mat(0xcc8866));
    belly.rotation.x = Math.PI / 2; belly.position.set(0, 0.7*s, 0);

    // Head
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.4*s, 0.35*s, 0.5*s), mat(color));
    head.position.set(0, 1.0*s, 0.7*s);
    // Snout
    const snout = new THREE.Mesh(new THREE.BoxGeometry(0.3*s, 0.2*s, 0.35*s), mat(color));
    snout.position.set(0, 0.9*s, 1.0*s);
    // Nostrils (glowing)
    const nostrilGeo = new THREE.SphereGeometry(0.04*s, 4, 4);
    const nostrilMat = new THREE.MeshStandardMaterial({ color: 0xff4400, emissive: 0xff4400, emissiveIntensity: 0.8 });
    const lN = new THREE.Mesh(nostrilGeo, nostrilMat); lN.position.set(-0.08*s, 0.95*s, 1.2*s);
    const rN = new THREE.Mesh(nostrilGeo, nostrilMat); rN.position.set(0.08*s, 0.95*s, 1.2*s);
    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.06*s, 6, 4);
    const eyeMat = mat(0xffcc00);
    const lE = new THREE.Mesh(eyeGeo, eyeMat); lE.position.set(-0.18*s, 1.1*s, 0.85*s);
    const rE = new THREE.Mesh(eyeGeo, eyeMat); rE.position.set(0.18*s, 1.1*s, 0.85*s);
    // Horns
    const hornGeo = new THREE.ConeGeometry(0.05*s, 0.25*s, 5);
    const hornMat = mat(0x555555);
    const lH = new THREE.Mesh(hornGeo, hornMat); lH.position.set(-0.15*s, 1.3*s, 0.6*s); lH.rotation.z = 0.3;
    const rH = new THREE.Mesh(hornGeo, hornMat); rH.position.set(0.15*s, 1.3*s, 0.6*s); rH.rotation.z = -0.3;

    // Wings (large triangular)
    const wingShape = new THREE.Shape();
    wingShape.moveTo(0, 0);
    wingShape.lineTo(1.5*s, 0.8*s);
    wingShape.lineTo(1.2*s, -0.3*s);
    wingShape.lineTo(0.6*s, 0.1*s);
    wingShape.lineTo(0, 0);
    const wingGeo = new THREE.ShapeGeometry(wingShape);
    const wingMat = mat(wingColor);
    const lWing = new THREE.Mesh(wingGeo, wingMat);
    lWing.position.set(-0.35*s, 1.0*s, -0.1*s); lWing.rotation.y = Math.PI/2 + 0.3;
    const rWing = new THREE.Mesh(wingGeo, wingMat);
    rWing.position.set(0.35*s, 1.0*s, -0.1*s); rWing.rotation.y = -(Math.PI/2 + 0.3); rWing.scale.x = -1;

    // Legs
    const legGeo = new THREE.CylinderGeometry(0.1*s, 0.08*s, 0.5*s, 6);
    const legM = mat(color);
    const fl = new THREE.Mesh(legGeo, legM); fl.position.set(-0.25*s, 0.25*s, 0.3*s);
    const fr = new THREE.Mesh(legGeo, legM); fr.position.set(0.25*s, 0.25*s, 0.3*s);
    const bl = new THREE.Mesh(legGeo, legM); bl.position.set(-0.25*s, 0.25*s, -0.3*s);
    const br = new THREE.Mesh(legGeo, legM); br.position.set(0.25*s, 0.25*s, -0.3*s);
    // Claws
    const clawGeo = new THREE.ConeGeometry(0.03*s, 0.08*s, 4);
    const clawMat = mat(0x444444);
    [fl, fr, bl, br].forEach(leg => {
        for (let c = -1; c <= 1; c++) {
            const claw = new THREE.Mesh(clawGeo, clawMat);
            claw.position.set(leg.position.x + c*0.04*s, 0.01*s, leg.position.z + 0.06*s);
            claw.rotation.x = 0.3;
            g.add(claw);
        }
    });

    // Tail (long, spiked)
    const tailGroup = new THREE.Group();
    for (let i = 0; i < 8; i++) {
        const seg = new THREE.Mesh(
            new THREE.CylinderGeometry((0.12-i*0.012)*s, (0.12-(i+1)*0.012)*s, 0.18*s, 6),
            mat(color)
        );
        seg.position.set(0, 0.6*s - i*0.04*s, -0.6*s - i*0.12*s);
        seg.rotation.x = -0.15 - i*0.08;
        tailGroup.add(seg);
    }
    // Tail spike
    const spike = new THREE.Mesh(new THREE.ConeGeometry(0.06*s, 0.15*s, 5), mat(0x555555));
    spike.position.set(0, 0.3*s, -1.5*s); spike.rotation.x = -1.2;
    tailGroup.add(spike);

    // Spine ridges
    for (let i = 0; i < 6; i++) {
        const ridge = new THREE.Mesh(new THREE.ConeGeometry(0.03*s, 0.1*s, 4), mat(0x666644));
        ridge.position.set(0, 1.15*s, 0.3*s - i*0.2*s);
        g.add(ridge);
    }

    g.add(body, belly, head, snout, lN, rN, lE, rE, lH, rH,
          lWing, rWing, fl, fr, bl, br, tailGroup);
    g.traverse(c => { if (c.isMesh) { c.castShadow = true; } });
    return g;
}
```

## Biome: Snow Mountain Environment

```javascript
function createSnowEnvironment(scene, arenaSize = 80) {
    // Snowy ground
    const groundGeo = new THREE.PlaneGeometry(arenaSize * 3, arenaSize * 3, 40, 40);
    const pos = groundGeo.attributes.position;
    // Terrain height variation
    for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), y = pos.getY(i);
        const height = Math.sin(x * 0.05) * Math.cos(y * 0.05) * 3 + Math.random() * 0.3;
        pos.setZ(i, height);
    }
    groundGeo.computeVertexNormals();
    const ground = new THREE.Mesh(groundGeo, new THREE.MeshStandardMaterial({
        color: 0xe8e8f0, flatShading: true, roughness: 0.8
    }));
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Snow-capped pine trees
    function createSnowPine(height = 4) {
        const g = new THREE.Group();
        const mat = (c) => new THREE.MeshStandardMaterial({ color: c, flatShading: true });
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, height*0.3, 6), mat(0x6b4423));
        trunk.position.y = height * 0.15;
        for (let i = 0; i < 3; i++) {
            const r = 1.2 - i * 0.3;
            const h = height * 0.3;
            const cone = new THREE.Mesh(new THREE.ConeGeometry(r, h, 7), mat(0x2d4a1e));
            cone.position.y = height * 0.3 + i * h * 0.6;
            g.add(cone);
            // Snow cap on each layer
            const snow = new THREE.Mesh(new THREE.ConeGeometry(r * 0.95, h * 0.3, 7), mat(0xffffff));
            snow.position.y = height * 0.3 + i * h * 0.6 + h * 0.35;
            g.add(snow);
        }
        g.add(trunk);
        g.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
        return g;
    }

    // Ice rocks
    function createIceRock(size = 1) {
        const geo = new THREE.DodecahedronGeometry(size, 0);
        const p = geo.attributes.position;
        for (let i = 0; i < p.count; i++) {
            p.setX(i, p.getX(i) + (Math.random()-0.5)*size*0.3);
            p.setY(i, p.getY(i) * (0.5 + Math.random()*0.3));
            p.setZ(i, p.getZ(i) + (Math.random()-0.5)*size*0.3);
        }
        geo.computeVertexNormals();
        const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            color: 0xbbccdd, flatShading: true, roughness: 0.4, metalness: 0.2
        }));
        mesh.castShadow = true; mesh.receiveShadow = true;
        return mesh;
    }

    // Mountain peaks in background
    function createMountain(x, z, height = 20) {
        const geo = new THREE.ConeGeometry(height * 0.6, height, 6);
        const p = geo.attributes.position;
        for (let i = 0; i < p.count; i++) {
            if (p.getY(i) > 0) {
                p.setX(i, p.getX(i) + (Math.random()-0.5) * 3);
                p.setZ(i, p.getZ(i) + (Math.random()-0.5) * 3);
            }
        }
        geo.computeVertexNormals();
        const mountain = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            color: 0x667788, flatShading: true
        }));
        mountain.position.set(x, height/2 - 2, z);
        // Snow cap
        const snowCap = new THREE.Mesh(new THREE.ConeGeometry(height*0.25, height*0.2, 6),
            new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true }));
        snowCap.position.set(x, height - 2, z);
        scene.add(mountain, snowCap);
    }

    // Place environment objects
    for (let i = 0; i < 40; i++) {
        let x, z;
        do { x = (Math.random()-0.5)*arenaSize*2; z = (Math.random()-0.5)*arenaSize*2; }
        while (Math.sqrt(x*x+z*z) < 8);
        const tree = createSnowPine(3 + Math.random() * 3);
        tree.position.set(x, 0, z);
        tree.scale.setScalar(0.8 + Math.random()*0.4);
        scene.add(tree);
    }
    for (let i = 0; i < 20; i++) {
        const rock = createIceRock(0.3 + Math.random()*0.8);
        rock.position.set((Math.random()-0.5)*arenaSize*2, 0, (Math.random()-0.5)*arenaSize*2);
        scene.add(rock);
    }
    // Background mountains
    for (let i = 0; i < 6; i++) {
        const angle = (i/6)*Math.PI*2 + Math.random()*0.5;
        createMountain(Math.cos(angle)*arenaSize*1.5, Math.sin(angle)*arenaSize*1.5, 15 + Math.random()*15);
    }

    // Lighting for snow
    scene.fog = new THREE.FogExp2(0xccddee, 0.008);
    scene.background = new THREE.Color(0xccddee);
}
```

## Reference-Image-to-Model Guide

When the user provides a photo or image as reference:

### Workflow
1. **View the image** using the Read tool
2. **Extract visual features:**
   - Dominant colors → map to hex values for materials
   - Body proportions → map to primitive dimensions (height/width ratios)
   - Distinctive features → plan which primitives capture them (stripes = boxes, wings = ShapeGeometry, horns = cones, etc.)
   - Texture/pattern → vertex colors or multi-material sections
   - Pose/stance → default Group rotation and part positions
3. **Choose primitive strategy:**
   - Round/organic shapes → SphereGeometry, CapsuleGeometry
   - Angular/blocky → BoxGeometry
   - Pointed → ConeGeometry
   - Cylindrical → CylinderGeometry
   - Flat/wing-like → ShapeGeometry or PlaneGeometry
   - Irregular/rocky → DodecahedronGeometry with vertex deformation
4. **Build bottom-up:** feet → legs → body → arms → head → details
5. **Target 20-30 primitives** for photo-referenced models (more detail to capture likeness)

### Using Photos as Textures
If the user explicitly wants their image IN the game (not just as reference):
```javascript
// Embed image as base64 data URI
const textureLoader = new THREE.TextureLoader();
const tex = textureLoader.load('data:image/png;base64,<BASE64_DATA>');
const material = new THREE.MeshStandardMaterial({ map: tex });
// Apply to a plane, billboard, or UV-mapped geometry
```

To convert a file to base64 for embedding:
```bash
base64 -w 0 /path/to/image.png
```

### Sprite Billboard (for 2D characters from photos)
```javascript
function createBillboard(base64Data, width = 1, height = 1.5) {
    const tex = new THREE.TextureLoader().load('data:image/png;base64,' + base64Data);
    tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.DoubleSide });
    const geo = new THREE.PlaneGeometry(width, height);
    const mesh = new THREE.Mesh(geo, mat);
    mesh.userData.isBillboard = true;
    return mesh;
}
// Each frame: billboard.lookAt(camera.position);
```

## General Tips
- Always use `flatShading: true` for the low-poly look
- Set `castShadow = true` on all visible objects
- Set `receiveShadow = true` on ground and large surfaces
- Use `emissive` + `emissiveIntensity` for glowing elements (lights, lasers, UI)
- Vary scale slightly (±20%) when placing multiple instances
- Use `THREE.Group` to organize multi-part objects and enable easy transform
- For large crowds, switch to `THREE.InstancedMesh` (see engine-patterns.md)
- When building from reference images, prioritize **silhouette** and **distinctive features** over exact detail
- For any animal not listed: body = CapsuleGeometry, head = SphereGeometry, legs = CylinderGeometry, tail = chained small cylinders, ears = ConeGeometry, eyes = small spheres. Adjust proportions and colors for species.
