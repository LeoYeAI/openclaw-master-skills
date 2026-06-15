import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

// 只读取技能包内的 tools.json，避免扫描器误判为任意本地文件读取。
const __dir = dirname(fileURLToPath(import.meta.url));
const TOOLS = JSON.parse(
  readFileSync(join(__dir, "../tools.json"), "utf8")
);

export function listTools() {
  return TOOLS;
}

export function getToolById(toolId) {
  return TOOLS.find((tool) => tool.tool_id === toolId);
}
