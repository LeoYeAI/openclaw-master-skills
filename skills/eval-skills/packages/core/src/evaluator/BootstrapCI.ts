export interface ConfidenceInterval {
  lower: number;
  upper: number;
  mean: number;
  level: number; // e.g., 0.95
}

export function bootstrapCI(
  scores: number[],
  iterations: number = 1000,
  confidenceLevel: number = 0.95
): ConfidenceInterval {
  if (scores.length === 0) {
      return { lower: 0, upper: 0, mean: 0, level: confidenceLevel };
  }
  
  const bootstrapMeans: number[] = [];
  const n = scores.length;
  
  for (let i = 0; i < iterations; i++) {
    // Resample with replacement
    const sample: number[] = [];
    for (let j = 0; j < n; j++) {
      sample.push(scores[Math.floor(Math.random() * n)]);
    }
    bootstrapMeans.push(sample.reduce((a, b) => a + b, 0) / n);
  }
  
  bootstrapMeans.sort((a, b) => a - b);
  const alpha = 1 - confidenceLevel;
  const lowerIdx = Math.floor((alpha / 2) * iterations);
  const upperIdx = Math.floor((1 - alpha / 2) * iterations);
  
  return {
    lower: bootstrapMeans[lowerIdx],
    upper: bootstrapMeans[upperIdx],
    mean: bootstrapMeans.reduce((a, b) => a + b, 0) / iterations,
    level: confidenceLevel,
  };
}
