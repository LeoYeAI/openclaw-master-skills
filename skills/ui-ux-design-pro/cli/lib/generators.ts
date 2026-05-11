// --- Constants ---

export const ADD_RATIOS: Record<string, number> = {
  'minor-second': 1.067,
  'major-second': 1.125,
  'minor-third': 1.2,
  'major-third': 1.25,
  'perfect-fourth': 1.333,
  'augmented-fourth': 1.414,
  'perfect-fifth': 1.5,
  'golden': 1.618,
};

export const HARMONY_OFFSETS: Record<string, number[]> = {
  complementary: [180],
  analogous: [-30, 30],
  triadic: [120, 240],
  tetradic: [90, 180, 270],
  'split-complementary': [150, 210],
  monochromatic: [],
};

const PRESETS: Record<string, { primary: string; neutral: string; radius: number; font: string }> = {
  fintech: { primary: '#2563EB', neutral: '#64748B', radius: 8, font: 'Inter' },
  healthcare: { primary: '#059669', neutral: '#6B7280', radius: 12, font: 'Source Sans Pro' },
  ecommerce: { primary: '#DC2626', neutral: '#78716C', radius: 8, font: 'Poppins' },
  saas: { primary: '#7C3AED', neutral: '#6B7280', radius: 12, font: 'Inter' },
  education: { primary: '#2563EB', neutral: '#9CA3AF', radius: 16, font: 'Nunito' },
  gaming: { primary: '#EF4444', neutral: '#374151', radius: 4, font: 'Orbitron' },
  luxury: { primary: '#1E293B', neutral: '#94A3B8', radius: 0, font: 'Playfair Display' },
  startup: { primary: '#8B5CF6', neutral: '#6B7280', radius: 12, font: 'DM Sans' },
};

// --- Color Utils ---

export function hexToHsl(hex: string): [number, number, number] {
  hex = hex.replace(/^#/, '');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }
    h /= 6;
  }

  return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
}

export function hslToHex(h: number, s: number, l: number): string {
  l /= 100;
  const a = s * Math.min(l, 1 - l) / 100;
  const f = (n: number) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color).toString(16).padStart(2, '0');
  };
  return `#${f(0)}${f(8)}${f(4)}`.toUpperCase();
}

// --- Generators ---

export function generatePalette(baseHex: string, harmony: string = 'triadic', count: number = 5) {
  const [h, s, l] = hexToHsl(baseHex);
  const colors = [{ hex: baseHex.toUpperCase(), role: 'base', hsl: `hsl(${h}, ${s}%, ${l}%)` }];
  const offsets = HARMONY_OFFSETS[harmony] || [];

  for (const offset of offsets) {
    const newH = (h + offset + 360) % 360;
    const hex = hslToHex(newH, s, l);
    colors.push({ hex, role: `+${offset}°`, hsl: `hsl(${Math.round(newH)}, ${s}%, ${l}%)` });
  }

  if (harmony === 'monochromatic') {
    for (let i = 1; i < count; i++) {
        const newL = Math.max(10, Math.min(95, l + (i - Math.floor(count / 2)) * 12));
        const hex = hslToHex(h, s, newL);
        colors.push({ hex, role: `L${Math.round(newL)}`, hsl: `hsl(${h}, ${s}%, ${Math.round(newL)}%)` });
    }
  }

  while (colors.length < count) {
    const idx = colors.length - 1;
    const color = colors[idx];
    if (!color) break;
    const existingH = hexToHsl(color.hex)[0];
    const lighterL = Math.min(95, l + 20);
    colors.push({
      hex: hslToHex(existingH, s, lighterL),
      role: 'light variant',
      hsl: `hsl(${existingH}, ${s}%, ${lighterL}%)`
    });
  }

  return colors.slice(0, count);
}

export function generateTypographyScale(basePx: number = 16, ratio: number = 1.25, steps: number = 8) {
  const scale = [];
  const stepNames = ['xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl'];

  for (let i = -2; i < steps - 2; i++) {
    const sizePx = basePx * Math.pow(ratio, i);
    const name = (i + 2 < stepNames.length) ? stepNames[i + 2]! : `step-${i + 2}`;
    const lh = i >= 0 ? Math.max(1.1, 1.5 - (i * 0.05)) : 1.6;
    
    scale.push({
      name,
      px: parseFloat(sizePx.toFixed(2)),
      rem: parseFloat((sizePx / 16).toFixed(4)),
      lineHeight: parseFloat(lh.toFixed(2)),
      ratioStep: i,
    });
  }
  return scale;
}

export function generateColorScale(hex: string, name: string) {
  const [h, s, _] = hexToHsl(hex);
  const lightnessSteps: Record<number, number> = {
    50: 97, 100: 94, 200: 86, 300: 77, 400: 66,
    500: 50, 600: 41, 700: 35, 800: 27, 900: 20, 950: 12,
  };
  const tokens: Record<string, string> = {};
  for (const [step, l] of Object.entries(lightnessSteps)) {
    tokens[`--color-${name}-${step}`] = `hsl(${h}, ${s}%, ${l}%)`;
  }
  return tokens;
}

export function generateAllTokens(primary: string, neutral: string, radius: number, font: string) {
  const tokens: Record<string, string> = {};
  
  Object.assign(tokens, generateColorScale(primary, 'primary'));
  Object.assign(tokens, generateColorScale(neutral, 'neutral'));
  
  // Spacing (simplified for brevity, complete list from Python script)
  const base = 4;
  [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64].forEach(k => {
     tokens[`--spacing-${k}`] = k === 0 ? '0px' : (`${base * k}px`);
  });
  tokens['--spacing-px'] = '1px';

  // Typography Tokens
  tokens['--font-family-heading'] = `'${font}', system-ui, sans-serif`;
  tokens['--font-family-body'] = `'${font}', system-ui, sans-serif`;
  tokens['--font-family-mono'] = `'JetBrains Mono', 'Fira Code', monospace`;
  
  // Type Scale (Interpreted from generate_typography_tokens in Python)
  const typeScale = generateTypographyScale(16, 1.25, 12); // Generate enough steps
  typeScale.forEach(s => {
      // Map names to tokens like --font-size-xl
      if (['xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl'].includes(s.name)) {
          tokens[`--font-size-${s.name}`] = `${s.rem}rem`;
      }
  });

  // Radius
  tokens[`--radius-sm`] = `${Math.max(radius - 4, 2)}px`;
  tokens[`--radius-md`] = `${radius}px`;
  tokens[`--radius-lg`] = `${radius + 4}px`;
  tokens[`--radius-full`] = `9999px`;

  // Shadows
  tokens['--shadow-sm'] = '0 1px 2px 0 rgb(0 0 0 / 0.05)';
  tokens['--shadow-md'] = '0 4px 6px -1px rgb(0 0 0 / 0.1)';
  tokens['--shadow-lg'] = '0 10px 15px -3px rgb(0 0 0 / 0.1)';
  
  return tokens;
}
