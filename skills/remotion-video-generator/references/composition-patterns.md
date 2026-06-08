# Composition Patterns

> "Advanced composition patterns for complex Remotion videos."

---

## Parallel Sequences

Run multiple scenes simultaneously:

```tsx
<AbsoluteFill>
  <Sequence from={0} durationInFrames={150}>
    <SceneA />
  </Sequence>
  <Sequence from={30} durationInFrames={150}>
    <SceneB />
  </Sequence>
  <Sequence from={60} durationInFrames={150}>
    <SceneC />
  </Sequence>
</AbsoluteFill>
```

---

## Nested Sequences

Scene within a scene:

```tsx
<Sequence from={0} durationInFrames={300}>
  <MainScene>
    <Sequence from={60} durationInFrames={90}>
      <SubScene />
    </Sequence>
  </MainScene>
</Sequence>
```

---

## Conditional Rendering

Show different content based on frame:

```tsx
const frame = useCurrentFrame();

{
  frame < 60 ? <Intro /> : <MainContent />
}
```

---

## Loop Points

Create seamless loops:

```tsx
const loopFrame = frame % 120; // Loop every 4 seconds at 30fps

<AnimatedElement frame={loopFrame} />
```

---

## Shared Animations

Extract common animations:

```tsx
const useSlideIn = (delay: number, from: 'left' | 'right' | 'top' | 'bottom') => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + 30], [0, 1]);

  const offsets = {
    left: [ -200, 0],
    right: [200, 0],
    top: [0, -200],
    bottom: [0, 200],
  };

  return {
    x: from === 'left' || from === 'right' ? interpolate(progress, [0, 1], offsets[from]) : 0,
    y: from === 'top' || from === 'bottom' ? interpolate(progress, [0, 1], offsets[from]) : 0,
    opacity: progress,
  };
};

// Usage
const style = useSlideIn(30, 'right');
<div style={{ transform: `translate(${style.x}px, ${style.y}px)`, opacity: style.opacity }} />
```

---

## Audio Synchronization

Sync visuals to audio:

```tsx
import { useAudio } from 'remotion';

export const AudioSync = () => {
  const audio = useAudio();
  // Visualize audio data
  return <Visualizer data={audio.frequencyData} />;
};
```

---

## Scroll-Linked Animation

Progress based on scroll position:

```tsx
import { useScroll } from 'remotion';

export const ScrollVideo = () => {
  const { scrollY, scrollYProgress } = useScroll();

  const scale = interpolate(scrollYProgress, [0, 1], [1, 1.5]);
  const opacity = interpolate(scrollYProgress, [0.8, 1], [1, 0]);

  return (
    <div style={{ transform: `scale(${scale})`, opacity }}>
      <Content />
    </div>
  );
};
```

---

## Stagger Children

Animate list items one by one:

```tsx
const items = ['First', 'Second', 'Third', 'Fourth'];

{items.map((item, i) => (
  <Sequence key={i} from={i * 15} durationInFrames={60}>
    <div>{item}</div>
  </Sequence>
))}
```

---

## Gesture/Interaction Simulation

Simulate user interactions:

```tsx
export const ClickAnimation = () => {
  const frame = useCurrentFrame();
  const clickProgress = interpolate(frame, [30, 45], [0, 1]);

  return (
    <div>
      <Button scale={1 + clickProgress * 0.1} />
      {clickProgress > 0.5 && (
        <div style={{ opacity: interpolate(clickProgress, [0.5, 1], [0, 1]) }}>
          <Dropdown />
        </div>
      )}
    </div>
  );
};
```

---

## 3D Transforms

Add depth:

```tsx
<div style={{
  transform: `perspective(1000px) rotateY(${frame * 2}deg)`,
}}>
  <Card />
</div>
```

---

## Masking

Create reveal effects:

```tsx
<div style={{
  clipPath: `circle(${interpolate(frame, [0, 60], [0, 150])}% at 50% 50%)`,
}}>
  <Content />
</div>
```

---

## Green Screen / Chroma Key

```tsx
export const ChromaKey = ({ video, color = '#00ff00' }) => {
  return (
    <div style={{ backgroundColor: color, mixBlendMode: 'multiply' }}>
      {video}
    </div>
  );
};
```

---

## Picture-in-Picture

```tsx
<AbsoluteFill>
  <MainContent />
  <div style={{
    position: 'absolute',
    bottom: 20,
    right: 20,
    width: 200,
    borderRadius: 8,
    overflow: 'hidden',
  }}>
    <PIPContent />
  </div>
</AbsoluteFill>
```

---

## Progress Indicator

```tsx
const ProgressBar = ({ progress }: { progress: number }) => {
  return (
    <div style={{
      width: `${progress * 100}%`,
      height: 4,
      background: 'linear-gradient(90deg, #667eea, #764ba2)',
    }} />
  );
};
```

---

## Responsive Scaling

Scale to fit any resolution:

```tsx
const { width, height } = useVideoConfig();
const scale = Math.min(width / 1920, height / 1080);

<div style={{ transform: `scale(${scale})` }}>
  <Content />
</div>
```

---

*More patterns to be added as needed.*
