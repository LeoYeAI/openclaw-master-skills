import { loadConfig, getApiUrl, getAgentId } from '../config.js';
import { createHttpClient } from '../client.js';
import { outputSuccess } from '../output.js';

export async function chat(message: string) {
  const config = loadConfig();
  const agentId = getAgentId(config);
  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  const res = await client.post('/chat', { agentId, message });
  const data = res.data.data;

  outputSuccess({ message: data.message });
}
