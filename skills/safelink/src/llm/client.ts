import Anthropic from "@anthropic-ai/sdk";
import { getConfig } from "../utils/config.js";

export interface GenerateTextParams {
  system: string;
  user: string;
  maxTokens?: number;
}

function joinUrl(base: string, path: string): string {
  return `${base.replace(/\/+$/, "")}/${path.replace(/^\/+/, "")}`;
}

export async function generateText(params: GenerateTextParams): Promise<string> {
  const config = getConfig();
  const maxTokens = params.maxTokens ?? 512;

  if (config.LLM_PROVIDER === "anthropic") {
    const anthropic = new Anthropic({ apiKey: config.ANTHROPIC_API_KEY! });
    const response = await anthropic.messages.create(
      {
        model: config.ANTHROPIC_MODEL,
        max_tokens: maxTokens,
        system: params.system,
        messages: [{ role: "user", content: params.user }],
      },
      { signal: AbortSignal.timeout(30_000) }
    );

    return response.content
      .filter((b) => b.type === "text")
      .map((b) => b.text)
      .join("");
  }

  const url = joinUrl(config.LLM_BASE_URL!, "chat/completions");
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${config.LLM_API_KEY!}`,
    },
    body: JSON.stringify({
      model: config.LLM_MODEL,
      messages: [
        { role: "system", content: params.system },
        { role: "user", content: params.user },
      ],
      max_tokens: maxTokens,
      temperature: 0,
    }),
    signal: AbortSignal.timeout(30_000),
  });

  if (!resp.ok) {
    throw new Error(`LLM provider error ${resp.status}: ${await resp.text()}`);
  }

  const data = (await resp.json()) as {
    choices?: Array<{ message?: { content?: string | Array<{ type?: string; text?: string }> } }>;
  };

  const content = data.choices?.[0]?.message?.content;
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((p) => (typeof p?.text === "string" ? p.text : ""))
      .join("");
  }

  return "";
}
