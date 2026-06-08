# Video Components

> "Reusable components for Remotion videos."

---

## Animated Backgrounds

```tsx
// AnimatedGradient.tsx
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

export const AnimatedGradient = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const opacity = interpolate(frame, [0, 100], [0.3, 0.8]);

  return (
    <div
      style={{
        width,
        height,
        background: `linear-gradient(${frame * 2}deg, #1a1a2e, #16213e, #0f3460)`,
        opacity,
      }}
    />
  );
};
```

---

## Terminal Window

```tsx
// Terminal.tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';

export const Terminal = ({ text = "npm run dev" }: { text?: string }) => {
  const frame = useCurrentFrame();
  const charsVisible = interpolate(frame, [0, 30], [0, text.length]);

  return (
    <AbsoluteFill style={{ backgroundColor: '#1e1e1e', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{
        backgroundColor: '#2d2d2d',
        borderRadius: 8,
        padding: 20,
        fontFamily: 'monospace',
        fontSize: 24,
        color: '#00ff00',
      }}>
        <div style={{ marginBottom: 10, color: '#ff6b6b' }}>~/project$</div>
        <span>{text.slice(0, Math.floor(charsVisible))}</span>
        <span style={{ animation: 'blink 1s infinite' }}>_</span>
      </div>
    </AbsoluteFill>
  );
};
```

---

## Feature Card

```tsx
// FeatureCard.tsx
import { interpolate, useCurrentFrame } from 'remotion';

export const FeatureCard = ({
  title,
  description,
  icon,
  delay = 0,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  delay?: number;
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + 30], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      transform: `translateY(${interpolate(progress, [0, 1], [50, 0])})px`,
      opacity: progress,
      backgroundColor: 'white',
      borderRadius: 12,
      padding: 24,
      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
    }}>
      <div style={{ fontSize: 32, marginBottom: 12 }}>{icon}</div>
      <h3 style={{ margin: '0 0 8px 0' }}>{title}</h3>
      <p style={{ margin: 0, color: '#666' }}>{description}</p>
    </div>
  );
};
```

---

## Stats Display

```tsx
// StatsCounter.tsx
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

export const StatsCounter = ({
  value,
  label,
  delay = 0,
}: {
  value: number;
  label: string;
  delay?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = interpolate(frame, [delay, delay + 60], [0, 1], { extrapolateRight: 'clamp' });
  const currentValue = Math.floor(value * progress);

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        fontSize: 64,
        fontWeight: 'bold',
        background: 'linear-gradient(90deg, #667eea, #764ba2)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}>
        {currentValue}+
      </div>
      <div style={{ fontSize: 18, color: '#666', textTransform: 'uppercase', letterSpacing: 2 }}>
        {label}
      </div>
    </div>
  );
};
```

---

## CTA Button

```tsx
// CTAButton.tsx
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export const CTAButton = ({
  text = "Get Started",
  url = "#",
  delay = 0,
}: {
  text?: string;
  url?: string;
  delay?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame: frame - delay,
    fps,
    from: 0,
    to: 1,
    config: { damping: 12 },
  });

  return (
    <a href={url} style={{
      display: 'inline-block',
      padding: '16px 32px',
      background: 'linear-gradient(90deg, #667eea, #764ba2)',
      color: 'white',
      borderRadius: 8,
      fontSize: 18,
      fontWeight: 'bold',
      textDecoration: 'none',
      transform: `scale(${scale})`,
    }}>
      {text}
    </a>
  );
};
```

---

## Text Reveal Animation

```tsx
// TextReveal.tsx
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

export const TextReveal = ({
  text,
  delay = 0,
}: {
  text: string;
  delay?: number;
}) => {
  const frame = useCurrentFrame();

  return (
    <div style={{ display: 'flex' }}>
      {text.split('').map((char, i) => {
        const charProgress = interpolate(
          frame,
          [delay + i * 3, delay + i * 3 + 20],
          [0, 1],
          { extrapolateRight: 'clamp' }
        );

        return (
          <span
            key={i}
            style={{
              opacity: charProgress,
              transform: `translateY(${interpolate(charProgress, [0, 1], [20, 0])}px)`,
              display: 'inline-block',
            }}
          >
            {char === ' ' ? '\u00A0' : char}
          </span>
        );
      })}
    </div>
  );
};
```

---

*More components to be added as needed.*
