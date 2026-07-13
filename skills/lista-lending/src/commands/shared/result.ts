export interface CommandResult {
  exitCode: 0 | 1;
  payload: Record<string, unknown>;
}
