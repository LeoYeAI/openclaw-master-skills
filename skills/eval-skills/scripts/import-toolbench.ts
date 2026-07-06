import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 模拟 ToolBench 数据
const tasks = [];
const tools = ["weather", "calculator", "calendar", "maps", "search", "translator"];

for(let i=0; i<30; i++) {
    const tool = tools[i % tools.length];
    const id = `toolbench_lite_${String(i+1).padStart(3, '0')}`;
    tasks.push({
        id,
        prompt: `Use the ${tool} tool to find the result for query ${i+1}.`,
        expectedOutput: {
            type: "llm_judge",
            criteria: `The answer must use the ${tool} tool correctly.`
        },
        metadata: { source: "toolbench", category: tool }
    });
}

const benchmark = {
    id: "toolbench-lite",
    name: "ToolBench Lite",
    description: "A lightweight version of ToolBench focusing on single-tool instruction following.",
    version: "1.0.0",
    tasks: tasks,
    scoringMethod: "pass_at_k",
    maxLatencyMs: 30000
};

const outPath = path.resolve(__dirname, '../packages/core/src/benchmarks/definitions/toolbench-lite.json');
// Ensure dir
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(benchmark, null, 2));

console.log(`Generated ToolBench benchmark with ${tasks.length} tasks at ${outPath}`);
