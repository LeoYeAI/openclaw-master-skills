import { loadConfig, saveConfig, getApiUrl, getCluster, SolanaCluster } from '../config.js';
import { outputSuccess } from '../output.js';
import { SdkError } from '../errors.js';

const VALID_CLUSTERS: SolanaCluster[] = ['mainnet-beta', 'devnet'];

export async function configSetCluster(cluster: string) {
  if (!VALID_CLUSTERS.includes(cluster as SolanaCluster)) {
    throw new SdkError('INVALID_CLUSTER', `Invalid cluster "${cluster}". Valid options: ${VALID_CLUSTERS.join(', ')}`);
  }
  const config = loadConfig();
  config.cluster = cluster as SolanaCluster;
  saveConfig(config);
  outputSuccess({ cluster, apiUrl: getApiUrl(config) });
}

export async function configGetCluster() {
  const config = loadConfig();
  outputSuccess({ cluster: getCluster(config), apiUrl: getApiUrl(config) });
}

export async function configResetCluster() {
  const config = loadConfig();
  delete config.cluster;
  saveConfig(config);
  outputSuccess({ cluster: getCluster(config), apiUrl: getApiUrl(config), message: 'Reset to default (mainnet-beta)' });
}
