import { SdkError, toSdkError } from './errors.js';

function isHuman(): boolean {
  return process.argv.includes('--human');
}

export function outputSuccess(data: Record<string, unknown>): void {
  if (isHuman()) {
    for (const [key, value] of Object.entries(data)) {
      if (typeof value === 'object' && value !== null) {
        console.log(`${key}:`);
        for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
          console.log(`  ${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`);
        }
      } else {
        console.log(`${key}: ${value}`);
      }
    }
    return;
  }
  console.log(JSON.stringify({ ok: true, data }));
}

export function outputError(err: SdkError): never {
  if (isHuman()) {
    console.log(`Error [${err.code}]: ${err.message}`);
  } else {
    console.log(JSON.stringify({ ok: false, error: err.code, message: err.message }));
  }
  process.exit(1);
}

export function wrapCommand<T extends (...args: any[]) => Promise<void>>(fn: T): T {
  const wrapped = async (...args: any[]) => {
    try {
      await fn(...args);
    } catch (err) {
      outputError(toSdkError(err));
    }
  };
  return wrapped as unknown as T;
}
