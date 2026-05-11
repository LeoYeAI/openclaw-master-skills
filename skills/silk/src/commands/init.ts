import { Keypair } from '@solana/web3.js';
import bs58 from 'bs58';
import { loadConfig, saveConfig, ensureAgentId } from '../config.js';
import { initContacts } from '../contacts.js';
import { outputSuccess } from '../output.js';

export async function init() {
  const config = loadConfig();
  let walletCreated = false;
  let mainWallet = config.wallets.find((w) => w.label === 'main');

  if (!mainWallet) {
    const keypair = Keypair.generate();
    const address = keypair.publicKey.toBase58();
    const privateKey = bs58.encode(keypair.secretKey);

    mainWallet = { label: 'main', address, privateKey };
    config.wallets.push(mainWallet);

    if (config.wallets.length === 1) {
      config.defaultWallet = 'main';
    }

    walletCreated = true;
  }

  const agentIdResult = ensureAgentId(config);
  const contactsCreated = initContacts();

  if (walletCreated || agentIdResult.created) {
    saveConfig(config);
  }

  outputSuccess({
    action: 'init',
    wallet_created: walletCreated,
    wallet_label: 'main',
    wallet_address: mainWallet.address,
    agent_id_created: agentIdResult.created,
    agent_id: agentIdResult.agentId,
    contacts_created: contactsCreated,
    message: (walletCreated || agentIdResult.created || contactsCreated) ? 'Initialization complete' : 'Already initialized',
  });
}
