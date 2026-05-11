#!/usr/bin/env node

import { access } from 'node:fs/promises';

export async function pathExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}
