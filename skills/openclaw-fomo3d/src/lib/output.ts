let jsonMode = false

export function setJsonMode(enabled: boolean): void {
  jsonMode = enabled
}

export function isJsonMode(): boolean {
  return jsonMode
}

function replacer(_key: string, value: unknown): unknown {
  if (typeof value === "bigint") return value.toString()
  return value
}

export function json(data: unknown): void {
  console.log(JSON.stringify(data, replacer, 2))
}

export function log(msg: string): void {
  if (!jsonMode) console.log(msg)
}

export function error(msg: string): void {
  if (jsonMode) {
    console.log(JSON.stringify({ success: false, error: msg }))
  } else {
    console.error(`Error: ${msg}`)
  }
}

export function fatal(msg: string): never {
  error(msg)
  process.exit(1)
}

export function output<T>(data: T, formatter: (d: T) => void): void {
  if (jsonMode) {
    json({ success: true, data })
  } else {
    formatter(data)
  }
}
