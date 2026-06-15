import { getApiKey, BASE_URL } from "./env.mjs";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

// 加载工具注册表（tools.json 与 scripts/ 同级上一层）
const __dir = dirname(fileURLToPath(import.meta.url));
const TOOLS = JSON.parse(
  readFileSync(join(__dir, "../tools.json"), "utf8")
);

const SEMANTIC_QUERY_ALIASES = {
  "注册号": ["企业基本信息"],
  "工商注册号": ["企业基本信息"],
  "统一社会信用代码": ["企业基本信息"],
  "信用代码": ["企业基本信息"],
  "法人": ["企业基本信息"],
  "法定代表人": ["企业基本信息"],
  "营业期限": ["企业基本信息"],
  "官网": ["企业基本信息"],
  "电话": ["企业基本信息"],
  "邮箱": ["企业基本信息"],
  "股权结构": ["企业股东信息"],
  "股东结构": ["企业股东信息"],
  "董监高": ["企业高级职员"],
  "高管": ["企业高级职员"],
  "对外投资": ["企业对外投资"],
  "工商变更": ["企业工商变更"],
  "法人变更": ["企业工商变更"],
  "地址变更": ["企业工商变更"],
  "被执行": ["被执行人"],
  "执行标的": ["被执行人"],
  "老赖": ["失信被执行人"],
  "失信": ["失信被执行人"],
  "限消": ["限制高消费"],
  "限高": ["限制高消费"],
  "经营异常": ["经营异常"],
  "严重违法": ["严重违法"],
  "行政处罚": ["行政处罚"],
  "处罚机关": ["行政处罚"]
};

function normalizeSearchText(input) {
  return String(input || "")
    .toLowerCase()
    .replace(/[\s"'“”‘’，。、《》【】（）()、:：;；!?！？-]+/g, "")
    .trim();
}

function buildQueryVariants(input) {
  const normalized = normalizeSearchText(input);
  const variants = new Set([normalized]);

  if (normalized.startsWith("企业")) {
    variants.add(normalized.slice(2));
  }
  if (normalized.startsWith("公司")) {
    variants.add(normalized.slice(2));
  }

  for (const variant of [...variants]) {
    if (variant.endsWith("查询")) {
      variants.add(variant.slice(0, -2));
    }
    if (variant.endsWith("信息查询")) {
      variants.add(variant.slice(0, -4));
    }
    for (const [alias, mappedVariants] of Object.entries(SEMANTIC_QUERY_ALIASES)) {
      if (variant.includes(alias)) {
        mappedVariants.forEach((mapped) => variants.add(normalizeSearchText(mapped)));
      }
    }
  }

  return [...variants].filter((item) => item.length >= 2);
}

function buildSearchTerms(input) {
  const text = normalizeSearchText(input);
  const terms = new Set();

  for (const asciiWord of text.match(/[a-z0-9]+/g) || []) {
    terms.add(asciiWord);
  }

  for (const segment of text.match(/[\u4e00-\u9fa5]+/g) || []) {
    for (let size = 2; size <= Math.min(segment.length, 4); size++) {
      for (let i = 0; i <= segment.length - size; i++) {
        const term = segment.slice(i, i + size);
        if (!["企业", "公司", "信息", "查询"].includes(term)) {
          terms.add(term);
        }
      }
    }
  }

  return [...terms];
}

/** 本地关键词匹配，替代后端 /skill/match */
export function discover(query, { limit = 5 } = {}) {
  const queryVariants = buildQueryVariants(query);
  const queryTerms = buildSearchTerms(query);
  const scored = TOOLS.map((tool) => {
    const normalizedName = normalizeSearchText(tool.name);
    const normalizedDescription = normalizeSearchText(tool.description || "");
    const normalizedKeywords = (tool.keywords || [])
      .map((keyword) => normalizeSearchText(keyword))
      .filter(Boolean);
    const normalizedText = normalizeSearchText(
      [tool.name, tool.description, ...(tool.keywords || [])].filter(Boolean).join(" ")
    );

    let similarity = 0;
    for (const variant of queryVariants) {
      if (!variant) continue;
      if (normalizedName === variant) {
        similarity = Math.max(similarity, 1);
      } else if (normalizedKeywords.includes(variant)) {
        similarity = Math.max(similarity, 0.98);
      } else if (normalizedName.includes(variant)) {
        similarity = Math.max(similarity, 0.95);
      } else if (normalizedKeywords.some((keyword) => keyword.includes(variant) || variant.includes(keyword))) {
        similarity = Math.max(similarity, 0.9);
      } else if (normalizedDescription.includes(variant) || normalizedText.includes(variant)) {
        similarity = Math.max(similarity, 0.85);
      }
    }

    if (similarity < 0.85) {
      const hits = queryTerms.filter(
        (term) => normalizedText.includes(term) || normalizedKeywords.some((keyword) => keyword.includes(term))
      );
      const uniqueHits = new Set(hits);
      const overlap =
        queryTerms.length === 0 || uniqueHits.size === 0
          ? 0
          : Math.min(uniqueHits.size / Math.max(Math.min(queryTerms.length, 5), 1), 0.84);
      similarity = Math.max(similarity, overlap);
    }

    return { similarity, tool };
  });

  scored.sort((a, b) => b.similarity - a.similarity);

  return {
    tools: scored
      .filter((s) => s.similarity > 0)
      .slice(0, limit)
      .map(({ similarity, tool }) => ({
        tool_id: tool.tool_id,
        name: tool.name,
        description: tool.description,
        similarity: parseFloat(similarity.toFixed(4)),
        params: tool.params,
      })),
  };
}

/** 直接调用真实 API，替代后端 /gateway/{tool_id} */
export async function call(toolId, params = {}) {
  const apiKey = await getApiKey();
  if (!apiKey) throw new Error("API Key 未配置，请先访问 https://www.riskbird.com/skills，通过页面中部复制按钮获取当前页面展示的公用 Key，并设置环境变量 FN_API_KEY");

  const tool = TOOLS.find((t) => t.tool_id === toolId);
  if (!tool) throw new Error(`未找到工具: ${toolId}`);

  const url = new URL(BASE_URL + tool.endpoint);

  const options = {
    method: tool.method,
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
      "X-API-Key": apiKey,
    },
  };

  if (tool.method === "GET") {
    Object.entries(params).forEach(([k, v]) => {
      if (v != null) url.searchParams.set(k, v);
    });
  } else {
    options.body = JSON.stringify(params);
  }

  const res = await fetch(url.toString(), options);
  const body = await res.json().catch(() => ({ error: "non-JSON response" }));

  if (!res.ok) {
    throw new Error(`API 错误 ${res.status}: ${JSON.stringify(body)}`);
  }

  // 直接透传原始响应，结构为 { code, msg, data, success }
  return body;
}
