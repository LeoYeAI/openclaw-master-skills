# Procedural Audio Recipes (Web Audio API)

All sounds are generated procedurally — no external audio files needed. Always handle the autoplay policy by creating/resuming AudioContext on first user interaction.

## Audio Context Setup

```javascript
let audioCtx = null;
function getAudioContext() {
    if (!audioCtx) audioCtx = new AudioContext();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    return audioCtx;
}

// Call on first click/keypress:
// document.addEventListener('click', () => getAudioContext(), { once: true });
```

## Master Volume + Reverb

```javascript
function createAudioBus() {
    const ctx = getAudioContext();
    const masterGain = ctx.createGain();
    masterGain.gain.value = 0.5;
    masterGain.connect(ctx.destination);

    // Simple reverb via convolver
    const convolver = ctx.createConvolver();
    const rate = ctx.sampleRate;
    const length = rate * 1.5;
    const impulse = ctx.createBuffer(2, length, rate);
    for (let ch = 0; ch < 2; ch++) {
        const data = impulse.getChannelData(ch);
        for (let i = 0; i < length; i++) {
            data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, 2.5);
        }
    }
    convolver.buffer = impulse;
    const reverbGain = ctx.createGain();
    reverbGain.gain.value = 0.15;
    convolver.connect(reverbGain);
    reverbGain.connect(masterGain);

    return { masterGain, convolver, reverbGain };
}
```

## Sound Recipes

### Gunshot
```javascript
function playGunshot() {
    const ctx = getAudioContext();
    const t = ctx.currentTime;
    // Noise burst
    const bufferSize = ctx.sampleRate * 0.1;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
    const noise = ctx.createBufferSource();
    noise.buffer = buffer;
    // Bandpass filter
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(1000, t);
    filter.frequency.exponentialRampToValueAtTime(300, t + 0.1);
    filter.Q.value = 1;
    // Envelope
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.8, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.1);
    noise.connect(filter).connect(gain).connect(ctx.destination);
    noise.start(t);
    noise.stop(t + 0.12);
}
```

### Explosion
```javascript
function playExplosion() {
    const ctx = getAudioContext();
    const t = ctx.currentTime;
    // Low noise
    const bufferSize = ctx.sampleRate * 0.6;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
    const noise = ctx.createBufferSource();
    noise.buffer = buffer;
    const lpf = ctx.createBiquadFilter();
    lpf.type = 'lowpass';
    lpf.frequency.setValueAtTime(800, t);
    lpf.frequency.exponentialRampToValueAtTime(50, t + 0.5);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(1.0, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.6);
    noise.connect(lpf).connect(gain).connect(ctx.destination);
    // Sine sweep down
    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(150, t);
    osc.frequency.exponentialRampToValueAtTime(20, t + 0.5);
    const oscGain = ctx.createGain();
    oscGain.gain.setValueAtTime(0.5, t);
    oscGain.gain.exponentialRampToValueAtTime(0.01, t + 0.5);
    osc.connect(oscGain).connect(ctx.destination);
    noise.start(t); noise.stop(t + 0.65);
    osc.start(t); osc.stop(t + 0.55);
}
```

### Jump
```javascript
function playJump() {
    const ctx = getAudioContext();
    const t = ctx.currentTime;
    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(300, t);
    osc.frequency.exponentialRampToValueAtTime(600, t + 0.15);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.3, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.15);
    osc.connect(gain).connect(ctx.destination);
    osc.start(t); osc.stop(t + 0.18);
}
```

### Coin / Pickup
```javascript
function playPickup() {
    const ctx = getAudioContext();
    const t = ctx.currentTime;
    // Two ascending tones
    [0, 0.08].forEach((offset, i) => {
        const osc = ctx.createOscillator();
        osc.type = 'sine';
        osc.frequency.value = 880 + i * 440;
        const gain = ctx.createGain();
        gain.gain.setValueAtTime(0.3, t + offset);
        gain.gain.exponentialRampToValueAtTime(0.01, t + offset + 0.12);
        osc.connect(gain).connect(ctx.destination);
        osc.start(t + offset); osc.stop(t + offset + 0.15);
    });
}
```

### Hit / Damage Taken
```javascript
function playHit() {
    const ctx = getAudioContext();
    const t = ctx.currentTime;
    // Short noise burst
    const bufferSize = ctx.sampleRate * 0.08;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
    const noise = ctx.createBufferSource();
    noise.buffer = buffer;
    const lpf = ctx.createBiquadFilter();
    lpf.type = 'lowpass';
    lpf.frequency.value = 2000;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.6, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.08);
    noise.connect(lpf).connect(gain).connect(ctx.destination);
    // Low thud
    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = 80;
    const oscGain = ctx.createGain();
    oscGain.gain.setValueAtTime(0.5, t);
    oscGain.gain.exponentialRampToValueAtTime(0.01, t + 0.1);
    osc.connect(oscGain).connect(ctx.destination);
    noise.start(t); noise.stop(t + 0.1);
    osc.start(t); osc.stop(t + 0.12);
}
```

### Engine Hum (looping)
```javascript
function createEngineSound() {
    const ctx = getAudioContext();
    const osc1 = ctx.createOscillator();
    osc1.type = 'sawtooth';
    osc1.frequency.value = 80;
    const osc2 = ctx.createOscillator();
    osc2.type = 'sawtooth';
    osc2.frequency.value = 82; // slight detune for richness
    const lpf = ctx.createBiquadFilter();
    lpf.type = 'lowpass';
    lpf.frequency.value = 200;
    const gain = ctx.createGain();
    gain.gain.value = 0.15;
    osc1.connect(lpf); osc2.connect(lpf);
    lpf.connect(gain).connect(ctx.destination);
    osc1.start(); osc2.start();
    return {
        setSpeed(speed) {
            const freq = 60 + speed * 2;
            osc1.frequency.setTargetAtTime(freq, ctx.currentTime, 0.1);
            osc2.frequency.setTargetAtTime(freq + 2, ctx.currentTime, 0.1);
            lpf.frequency.setTargetAtTime(100 + speed * 5, ctx.currentTime, 0.1);
        },
        stop() { osc1.stop(); osc2.stop(); }
    };
}
```

### Laser / Sci-Fi Shot
```javascript
function playLaser() {
    const ctx = getAudioContext();
    const t = ctx.currentTime;
    const osc = ctx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(1200, t);
    osc.frequency.exponentialRampToValueAtTime(100, t + 0.2);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.3, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.2);
    osc.connect(gain).connect(ctx.destination);
    osc.start(t); osc.stop(t + 0.25);
}
```

### Impact / Thud
```javascript
function playImpact() {
    const ctx = getAudioContext();
    const t = ctx.currentTime;
    const bufferSize = ctx.sampleRate * 0.05;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
    const noise = ctx.createBufferSource();
    noise.buffer = buffer;
    const lpf = ctx.createBiquadFilter();
    lpf.type = 'lowpass';
    lpf.frequency.value = 500;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.7, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.05);
    noise.connect(lpf).connect(gain).connect(ctx.destination);
    noise.start(t); noise.stop(t + 0.07);
}
```

### Simple Background Music (chord loop)
```javascript
function startMusic(bpm = 100) {
    const ctx = getAudioContext();
    const beatDur = 60 / bpm;
    // Chord progression: I - V - vi - IV (in C major)
    const chords = [
        [261.6, 329.6, 392.0],  // C major
        [392.0, 493.9, 587.3],  // G major
        [440.0, 523.3, 659.3],  // A minor
        [349.2, 440.0, 523.3],  // F major
    ];
    let chordIdx = 0;
    const oscs = [];
    const masterGain = ctx.createGain();
    masterGain.gain.value = 0.08;
    masterGain.connect(ctx.destination);

    for (let i = 0; i < 3; i++) {
        const osc = ctx.createOscillator();
        osc.type = i === 0 ? 'triangle' : 'sine';
        const g = ctx.createGain();
        g.gain.value = i === 0 ? 0.5 : 0.3;
        osc.connect(g).connect(masterGain);
        osc.start();
        oscs.push({ osc, gain: g });
    }

    function nextChord() {
        const chord = chords[chordIdx % chords.length];
        const t = ctx.currentTime;
        oscs.forEach((o, i) => {
            o.osc.frequency.setTargetAtTime(chord[i], t, 0.05);
        });
        chordIdx++;
    }
    nextChord();
    const interval = setInterval(nextChord, beatDur * 4 * 1000);
    return { stop() { clearInterval(interval); oscs.forEach(o => o.osc.stop()); } };
}
```

### Spatial Audio (3D positioned sounds)
```javascript
function play3DSound(position, frequency = 440, duration = 0.3) {
    const ctx = getAudioContext();
    if (!ctx.listener.positionX) return; // fallback for old browsers
    const panner = ctx.createPanner();
    panner.panningModel = 'HRTF';
    panner.distanceModel = 'inverse';
    panner.refDistance = 1;
    panner.maxDistance = 100;
    panner.rolloffFactor = 1;
    panner.positionX.value = position.x;
    panner.positionY.value = position.y;
    panner.positionZ.value = position.z;

    const osc = ctx.createOscillator();
    osc.frequency.value = frequency;
    const gain = ctx.createGain();
    const t = ctx.currentTime;
    gain.gain.setValueAtTime(0.5, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + duration);
    osc.connect(gain).connect(panner).connect(ctx.destination);
    osc.start(t); osc.stop(t + duration + 0.05);
}

// Update listener position each frame:
function updateAudioListener(camera) {
    const ctx = getAudioContext();
    if (ctx.listener.positionX) {
        ctx.listener.positionX.value = camera.position.x;
        ctx.listener.positionY.value = camera.position.y;
        ctx.listener.positionZ.value = camera.position.z;
        const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
        const up = new THREE.Vector3(0, 1, 0).applyQuaternion(camera.quaternion);
        ctx.listener.forwardX.value = forward.x;
        ctx.listener.forwardY.value = forward.y;
        ctx.listener.forwardZ.value = forward.z;
        ctx.listener.upX.value = up.x;
        ctx.listener.upY.value = up.y;
        ctx.listener.upZ.value = up.z;
    }
}
```

## Tips
- Always wrap AudioContext creation in a user gesture handler (click/keydown)
- Use `setTargetAtTime` for smooth parameter transitions, `exponentialRampToValueAtTime` for envelopes
- Layer multiple sounds (noise + oscillator) for richer effects
- Keep gain values conservative (0.1-0.5) to prevent clipping
- Use `gain.gain.exponentialRampToValueAtTime(0.01, ...)` (not 0) to avoid errors
- For looping sounds, create once and control with gain nodes rather than re-creating
