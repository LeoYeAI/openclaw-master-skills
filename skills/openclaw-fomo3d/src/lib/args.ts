// CLI 参数解析工具

export function hasFlag(args: string[], ...flags: string[]): boolean {
  return flags.some(f => args.includes(f))
}

export function removeFlags(args: string[], ...flags: string[]): string[] {
  return args.filter(a => !flags.includes(a))
}

export function getFlagValue(args: string[], flag: string): string | undefined {
  const idx = args.indexOf(flag)
  if (idx === -1 || idx + 1 >= args.length) return undefined
  return args[idx + 1]
}

export function removeFlagWithValue(args: string[], flag: string): string[] {
  const idx = args.indexOf(flag)
  if (idx === -1) return args
  return [...args.slice(0, idx), ...args.slice(idx + 2)]
}
