import OpenAI from "openai";

export interface EmbeddingConfig {
  model?: string;  // Default: "text-embedding-3-small"
  apiKey?: string; // Read from env if not provided
}

export interface SearchCandidate {
  id: string;
  text: string;
  metadata?: Record<string, unknown>;
}

export interface SearchResult extends SearchCandidate {
  score: number;
}

export class EmbeddingSearcher {
  private client: OpenAI;
  private model: string;
  private cache: Map<string, number[]> = new Map();

  constructor(config: EmbeddingConfig = {}) {
    const apiKey = config.apiKey ?? process.env.OPENAI_API_KEY;
    if (!apiKey) {
        // Fallback or throw? 
        // Throwing here might be too aggressive if user doesn't use semantic search.
        // But if they construct this class, they likely intend to use it.
        // Let's allow empty and fail on call if needed, or assume OpenAI client handles it.
    }
    this.client = new OpenAI({ apiKey: apiKey });
    this.model = config.model ?? "text-embedding-3-small";
  }

  async embed(text: string): Promise<number[]> {
    if (this.cache.has(text)) return this.cache.get(text)!;
    
    try {
        const response = await this.client.embeddings.create({
          model: this.model,
          input: text,
        });
        const vector = response.data?.[0]?.embedding;
        if (!vector) {
            throw new Error("No embedding returned");
        }
        this.cache.set(text, vector);
        return vector;
    } catch (error) {
        throw new Error(`Embedding failed: ${(error as Error).message}`);
    }
  }

  cosineSimilarity(a: number[], b: number[]): number {
    let dot = 0, normA = 0, normB = 0;
    for (let i = 0; i < a.length; i++) {
      // @ts-ignore
      dot += a[i] * b[i];
      // @ts-ignore
      normA += a[i] * a[i];
      // @ts-ignore
      normB += b[i] * b[i];
    }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  async search(query: string, candidates: SearchCandidate[], topK = 10): Promise<SearchResult[]> {
    const queryVec = await this.embed(query);
    const results = await Promise.all(
      candidates.map(async (c) => ({
        ...c,
        score: this.cosineSimilarity(queryVec, await this.embed(c.text)),
      }))
    );
    return results.sort((a, b) => b.score - a.score).slice(0, topK);
  }
}
