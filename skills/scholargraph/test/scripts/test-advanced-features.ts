/**
 * 测试高级 API 功能
 */

import ConceptLearner from './concept-learner/scripts/learn';
import PaperAnalyzer from './paper-analyzer/scripts/analyze';
import KnowledgeGraphBuilder from './knowledge-graph/scripts/graph';

// 设置环境变量
// 请在运行前设置你自己的 API key
// process.env.OPENAI_API_KEY = "your-api-key-here";
// process.env.OPENAI_BASE_URL = "https://openrouter.ai/api/v1";
// process.env.OPENAI_MODEL = "deepseek/deepseek-chat";
// process.env.AI_PROVIDER = "openai";

// 或者从环境变量读取
if (!process.env.AI_PROVIDER) {
  console.error('请设置环境变量 AI_PROVIDER 和相应的 API key');
  console.error('例如: AI_PROVIDER=openai OPENAI_API_KEY=your-key bun run test-advanced-features.ts');
  process.exit(1);
}

async function testConceptCompare() {
  console.log('\n=== 测试概念对比 ===\n');

  const learner = new ConceptLearner();
  await learner.initialize();

  const result = await learner.compare('CNN', 'RNN');

  console.log(`对比: ${result.concept1} vs ${result.concept2}\n`);
  console.log('相似点:');
  result.similarities.forEach(s => console.log(`  - ${s}`));

  console.log('\n差异点:');
  result.differences.forEach(d => console.log(`  - ${d}`));

  console.log('\n使用场景:');
  console.log(`  ${result.concept1}:`, result.useCases.preferConcept1);
  console.log(`  ${result.concept2}:`, result.useCases.preferConcept2);
}

async function testPaperCompare() {
  console.log('\n=== 测试论文对比 ===\n');

  const analyzer = new PaperAnalyzer();
  await analyzer.initialize();

  const urls = [
    'https://www.semanticscholar.org/paper/83b90f4a0ae4cc214eb3cc140ccfef9cd99fac05',
    'https://www.semanticscholar.org/paper/1f2a20a6efaf83214861dddae4a38a83ae18fe32'
  ];

  const result = await analyzer.compare(urls);

  console.log('共同主题:');
  result.commonThemes.forEach(t => console.log(`  - ${t}`));

  console.log('\n主要差异:');
  result.differences.forEach(d => console.log(`  - ${d}`));

  console.log('\n综合分析:');
  console.log(result.synthesis);
}

async function testPaperCritique() {
  console.log('\n=== 测试论文批判性分析 ===\n');

  const analyzer = new PaperAnalyzer();
  await analyzer.initialize();

  const result = await analyzer.critique({
    url: 'https://www.semanticscholar.org/paper/83b90f4a0ae4cc214eb3cc140ccfef9cd99fac05',
    focusAreas: ['scalability', 'efficiency']
  });

  console.log('优点:');
  result.strengths.forEach(s => console.log(`  - ${s}`));

  console.log('\n缺点:');
  result.weaknesses.forEach(w => console.log(`  - ${w}`));

  console.log('\n研究空白:');
  result.gaps.forEach(g => console.log(`  - ${g}`));

  console.log('\n改进建议:');
  result.suggestions.forEach(s => console.log(`  - ${s}`));

  console.log('\n总体评价:');
  console.log(result.overallAssessment);
}

async function testGraphPath() {
  console.log('\n=== 测试知识图谱路径查找 ===\n');

  const builder = new KnowledgeGraphBuilder();
  await builder.initialize();

  const concepts = ['Machine Learning', 'Neural Networks', 'Deep Learning', 'CNN', 'Image Recognition'];
  const graph = await builder.build(concepts);

  const path = builder.findPath(graph, 'Machine Learning', 'Image Recognition');

  console.log('学习路径:');
  console.log(path.join(' → '));
}

async function testTopologicalOrder() {
  console.log('\n=== 测试拓扑排序（学习顺序） ===\n');

  const builder = new KnowledgeGraphBuilder();
  await builder.initialize();

  const concepts = ['Machine Learning', 'Neural Networks', 'Deep Learning', 'CNN', 'RNN', 'Transformer'];
  const graph = await builder.build(concepts);

  const order = builder.getTopologicalOrder(graph);

  console.log('推荐学习顺序:');
  order.forEach((concept, i) => console.log(`  ${i + 1}. ${concept}`));
}

// 运行测试
async function main() {
  const args = process.argv.slice(2);
  const test = args[0] || 'all';

  try {
    switch (test) {
      case 'compare-concept':
        await testConceptCompare();
        break;
      case 'compare-paper':
        await testPaperCompare();
        break;
      case 'critique':
        await testPaperCritique();
        break;
      case 'path':
        await testGraphPath();
        break;
      case 'order':
        await testTopologicalOrder();
        break;
      case 'all':
        await testConceptCompare();
        await testPaperCompare();
        await testPaperCritique();
        await testGraphPath();
        await testTopologicalOrder();
        break;
      default:
        console.log('用法: bun run test-advanced-features.ts [compare-concept|compare-paper|critique|path|order|all]');
    }
  } catch (error) {
    console.error('错误:', error);
  }
}

main();
