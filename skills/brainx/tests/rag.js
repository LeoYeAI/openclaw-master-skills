require('dotenv/config');
const rag = require('../lib/openai-rag');

(async () => {
  const mem = {
    id: `test_${Date.now()}`,
    type: 'note',
    content: 'PostgreSQL connection uses DATABASE_URL on localhost. pgvector is enabled.',
    context: 'brainx-v5',
    tier: 'warm',
    agent: 'coder',
    importance: 5,
    tags: ['test']
  };

  await rag.storeMemory(mem);
  const res = await rag.search('how do we connect to postgres?', { limit: 5, minSimilarity: 0.1 });
  console.log(res.map(r => ({ id: r.id, sim: r.similarity, content: r.content })).slice(0, 3));
})();
