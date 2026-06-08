# Storage Reference

## Table of contents
1. Storage areas comparison
2. Basic CRUD operations
3. Quota limits and handling
4. Reactive storage (onChanged)
5. Framework hooks (React, Vue)
6. Storage migration patterns
7. IndexedDB in extensions

## 1. Storage areas comparison

All require `"storage"` permission. All APIs are async (Promise-based in MV3).

| Feature | `storage.local` | `storage.sync` | `storage.session` |
|---------|-----------------|----------------|-------------------|
| Quota | 10 MB (unlimited with permission) | 100 KB total | 10 MB |
| Per-item limit | None | 8,192 bytes | None |
| Max items | None | 512 | None |
| Write ops/hour | None | 1,800 | None |
| Persistence | Until uninstall | Synced via Chrome account | Browser session only |
| Service worker access | Yes | Yes | Yes |
| Content script access | Yes | Yes | No (unless enabled) |
| Popup/options access | Yes | Yes | Yes |
| MV3 only | No | No | Yes (Chrome 102+) |
| `unlimitedStorage` | Yes | No | No |

### When to use which

- **`storage.local`**: large data, caches, tokens, anything that should persist across browser restarts
- **`storage.sync`**: user preferences/settings (syncs to all user's Chrome instances)
- **`storage.session`**: ephemeral state that should survive SW restarts but not browser restarts (computed caches, temporary auth, in-progress operations)

## 2. Basic CRUD operations

```typescript
// === WRITE ===
// Single key
await chrome.storage.local.set({ username: 'alice' });

// Multiple keys (atomic: all succeed or all fail)
await chrome.storage.local.set({
  username: 'alice',
  settings: { theme: 'dark', lang: 'en' },
  lastLogin: Date.now(),
});

// === READ ===
// Single key
const { username } = await chrome.storage.local.get('username');

// Multiple keys
const { username, settings } = await chrome.storage.local.get(['username', 'settings']);

// All keys
const everything = await chrome.storage.local.get(null);

// With defaults (returned if key doesn't exist)
const { theme } = await chrome.storage.local.get({ theme: 'light' });

// === DELETE ===
await chrome.storage.local.remove('username');
await chrome.storage.local.remove(['username', 'settings']);

// Clear everything
await chrome.storage.local.clear();

// === CHECK QUOTA ===
const bytes = await chrome.storage.local.getBytesInUse(null);       // total
const keyBytes = await chrome.storage.local.getBytesInUse('cache'); // specific key
```

## 3. Quota limits and handling

When quota is exceeded, the `set()` call rejects. No partial writes occur.

```typescript
async function safeSet(area: chrome.storage.StorageArea, data: Record<string, unknown>) {
  try {
    await area.set(data);
    return true;
  } catch (err: any) {
    if (err.message?.includes('QUOTA_BYTES')) {
      console.error('Storage quota exceeded. Clearing old data...');
      // Implement eviction strategy
      await evictOldEntries(area);
      try {
        await area.set(data);
        return true;
      } catch { return false; }
    }
    throw err;
  }
}

// LRU eviction for cache entries
async function evictOldEntries(area: chrome.storage.StorageArea) {
  const data = await area.get(null);
  const entries = Object.entries(data)
    .filter(([k]) => k.startsWith('cache:'))
    .sort((a, b) => (a[1] as any).timestamp - (b[1] as any).timestamp);

  // Remove oldest 25%
  const toRemove = entries.slice(0, Math.ceil(entries.length / 4)).map(([k]) => k);
  await area.remove(toRemove);
}
```

For `storage.sync`, also respect per-item and write-rate limits:

```typescript
// Check if value fits in sync storage item limit
function fitsInSyncItem(value: unknown): boolean {
  return new Blob([JSON.stringify(value)]).size <= 8192;
}

// Chunk large values across multiple sync keys
async function setSyncChunked(key: string, value: unknown) {
  const json = JSON.stringify(value);
  const chunkSize = 8000; // leave margin
  const chunks = Math.ceil(json.length / chunkSize);

  const data: Record<string, unknown> = { [`${key}__meta`]: { chunks } };
  for (let i = 0; i < chunks; i++) {
    data[`${key}__${i}`] = json.slice(i * chunkSize, (i + 1) * chunkSize);
  }
  await chrome.storage.sync.set(data);
}
```

## 4. Reactive storage (onChanged)

Storage changes fire events across ALL extension contexts simultaneously.

```typescript
// Listen to all areas
chrome.storage.onChanged.addListener((changes, areaName) => {
  for (const [key, { oldValue, newValue }] of Object.entries(changes)) {
    console.log(`[${areaName}] ${key}: ${oldValue} -> ${newValue}`);
  }
});

// Listen to specific area
chrome.storage.local.onChanged.addListener((changes) => {
  if (changes.theme) {
    applyTheme(changes.theme.newValue);
  }
});

// Use for cross-context state sync (popup updates, content script reacts)
// No need for manual messaging for settings changes!
```

## 5. Framework hooks

### React

```typescript
function useChromeStorage<T>(
  key: string,
  defaultValue: T,
  area: 'local' | 'sync' | 'session' = 'local'
): [T, (v: T | ((prev: T) => T)) => void, boolean] {
  const [value, setValue] = useState<T>(defaultValue);
  const [loading, setLoading] = useState(true);
  const storageArea = chrome.storage[area];

  useEffect(() => {
    // Initial load
    storageArea.get(key).then((result) => {
      if (result[key] !== undefined) setValue(result[key] as T);
      setLoading(false);
    });

    // Reactive updates from other contexts
    const listener = (changes: Record<string, chrome.storage.StorageChange>) => {
      if (changes[key]) setValue(changes[key].newValue as T);
    };
    storageArea.onChanged.addListener(listener);
    return () => storageArea.onChanged.removeListener(listener);
  }, [key, area]);

  const update = useCallback((newValue: T | ((prev: T) => T)) => {
    setValue(prev => {
      const resolved = typeof newValue === 'function'
        ? (newValue as (p: T) => T)(prev) : newValue;
      storageArea.set({ [key]: resolved });
      return resolved;
    });
  }, [key, area]);

  return [value, update, loading];
}

// Usage
function Settings() {
  const [theme, setTheme] = useChromeStorage('theme', 'light', 'sync');
  const [count, setCount] = useChromeStorage('count', 0);

  return (
    <div>
      <select value={theme} onChange={e => setTheme(e.target.value)}>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
      <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
    </div>
  );
}
```

### Vue 3 composable

```typescript
function useChromeStorage<T>(key: string, defaultValue: T, area: 'local' | 'sync' = 'local') {
  const value = ref<T>(defaultValue) as Ref<T>;
  const loading = ref(true);
  const storageArea = chrome.storage[area];

  storageArea.get(key).then((result) => {
    if (result[key] !== undefined) value.value = result[key];
    loading.value = false;
  });

  const listener = (changes: Record<string, chrome.storage.StorageChange>) => {
    if (changes[key]) value.value = changes[key].newValue;
  };
  storageArea.onChanged.addListener(listener);
  onUnmounted(() => storageArea.onChanged.removeListener(listener));

  watch(value, (newVal) => { storageArea.set({ [key]: newVal }); }, { deep: true });

  return { value, loading };
}
```

## 6. Storage migration patterns

Handle data format changes across extension versions:

```typescript
const CURRENT_SCHEMA_VERSION = 3;

chrome.runtime.onInstalled.addListener(async (details) => {
  if (details.reason !== 'update') return;

  const { schemaVersion = 1 } = await chrome.storage.local.get('schemaVersion');

  if (schemaVersion < 2) {
    // v1 -> v2: rename 'prefs' to 'settings'
    const { prefs } = await chrome.storage.local.get('prefs');
    if (prefs) {
      await chrome.storage.local.set({ settings: prefs });
      await chrome.storage.local.remove('prefs');
    }
  }

  if (schemaVersion < 3) {
    // v2 -> v3: move theme from local to sync
    const { settings } = await chrome.storage.local.get('settings');
    if (settings?.theme) {
      await chrome.storage.sync.set({ theme: settings.theme });
      delete settings.theme;
      await chrome.storage.local.set({ settings });
    }
  }

  await chrome.storage.local.set({ schemaVersion: CURRENT_SCHEMA_VERSION });
});
```

## 7. IndexedDB in extensions

For complex data (large blobs, structured queries, indexes), use IndexedDB.
Available in service worker, popup, options, and content scripts.

```typescript
// In service worker (no DOM, but IndexedDB works)
function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('MyExtDB', 1);
    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains('items')) {
        db.createObjectStore('items', { keyPath: 'id' });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
```

Prefer `chrome.storage` for simple key-value data. Use IndexedDB only when you
need indexes, transactions, or binary blob storage.
