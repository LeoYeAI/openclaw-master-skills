import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { generateKeypair } from './keygen.js';

describe('keygen', () => {
  it('generates a valid keypair with base64-encoded keys', async () => {
    const keypair = await generateKeypair();

    assert.ok(keypair.privateKey, 'privateKey should be defined');
    assert.ok(keypair.publicKey, 'publicKey should be defined');
    assert.equal(typeof keypair.privateKey, 'string');
    assert.equal(typeof keypair.publicKey, 'string');
  });

  it('generates a 32-byte private key (44 base64 chars)', async () => {
    const keypair = await generateKeypair();
    const privateKeyBytes = Buffer.from(keypair.privateKey, 'base64');
    assert.equal(privateKeyBytes.length, 32, 'private key should be 32 bytes');
    assert.equal(keypair.privateKey.length, 44, 'base64 private key should be 44 chars');
  });

  it('generates a 32-byte public key (44 base64 chars)', async () => {
    const keypair = await generateKeypair();
    const publicKeyBytes = Buffer.from(keypair.publicKey, 'base64');
    assert.equal(publicKeyBytes.length, 32, 'public key should be 32 bytes');
    assert.equal(keypair.publicKey.length, 44, 'base64 public key should be 44 chars');
  });

  it('produces valid base64 encoding', async () => {
    const keypair = await generateKeypair();
    const base64Regex = /^[A-Za-z0-9+/]+=*$/;
    assert.match(keypair.privateKey, base64Regex, 'privateKey should be valid base64');
    assert.match(keypair.publicKey, base64Regex, 'publicKey should be valid base64');
  });

  it('generates unique keypairs on each call', async () => {
    const kp1 = await generateKeypair();
    const kp2 = await generateKeypair();
    assert.notEqual(kp1.privateKey, kp2.privateKey, 'private keys should differ');
    assert.notEqual(kp1.publicKey, kp2.publicKey, 'public keys should differ');
  });

  it('public key matches the publicKeySchema validation (44 chars, valid base64)', async () => {
    const keypair = await generateKeypair();
    // Matches packages/shared/src/schemas/base.ts publicKeySchema
    assert.equal(keypair.publicKey.length, 44);
    assert.match(keypair.publicKey, /^[A-Za-z0-9+/]+=*$/);
  });
});
