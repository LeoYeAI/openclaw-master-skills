export function stringifyJson(payload: unknown): string {
  return JSON.stringify(payload);
}

export function printJson(payload: unknown): void {
  console.log(stringifyJson(payload));
}

export function printErrorJson(payload: unknown): void {
  console.error(stringifyJson(payload));
}

export function exitWithCode(code: number): never {
  process.exit(code);
}
