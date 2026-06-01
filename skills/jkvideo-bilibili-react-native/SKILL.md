---
name: jkvideo-bilibili-react-native
description: Expert skill for building and extending JKVideo, a React Native Bilibili-like client with DASH playback, danmaku, WBI signing, and live streaming
triggers:
  - build a bilibili react native app
  - add DASH video playback to expo
  - implement danmaku bullet comments
  - WBI signature bilibili API
  - react native live streaming with websocket danmaku
  - expo video player with multiple quality levels
  - bilibili API integration typescript
  - react native download manager with LAN sharing

---

# JKVideo Bilibili React Native Client

> Skill by [ara.so](https://ara.so) — Daily 2026 Skills collection.

JKVideo is a full-featured third-party Bilibili client built with React Native 0.83 + Expo SDK 55. It supports DASH adaptive streaming, real-time danmaku (bullet comments), WBI API signing, QR code login, live streaming with WebSocket danmaku, and a download manager with LAN QR sharing.

---

## Installation & Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- For Android: Android Studio + SDK
- For iOS: macOS + Xcode 15+

### Quick Start (Expo Go — no compilation)
```bash
git clone https://github.com/tiajinsha/JKVideo.git
cd JKVideo
npm install
npx expo start
```
Scan the QR with Expo Go app. Note: DASH 1080P+ requires Dev Build.

### Dev Build (Full Features — Recommended)
```bash
npm install
npx expo run:android   # Android
npx expo run:ios       # iOS (macOS + Xcode required)
```

### Web with Image Proxy
```bash
npm install
npx expo start --web
# In a separate terminal:
node scripts/proxy.js   # Starts proxy on port 3001 to bypass Bilibili referer restrictions
```

### Install APK Directly (Android)
Download from [Releases](https://github.com/tiajinsha/JKVideo/releases/latest) — enable "Install from unknown sources" in Android settings.

---

## Project Structure

```
app/
  index.tsx            # Home (PagerView hot/live tabs)
  video/[bvid].tsx     # Video detail (playback + comments + danmaku)
  live/[roomId].tsx    # Live detail (HLS + real-time danmaku)
  search.tsx           # Search page
  downloads.tsx        # Download manager
  settings.tsx         # Settings (quality, logout)

components/            # UI: player, danmaku overlay, cards
hooks/                 # Data hooks: video list, streams, danmaku
services/              # Bilibili API (axios + cookie interceptor)
store/                 # Zustand stores: auth, download, video, settings
utils/                 # Helpers: format, image proxy, MPD builder
```

---

## Key Technology Stack

| Layer | Technology |
|---|---|
| Framework | React Native 0.83 + Expo SDK 55 |
| Routing | expo-router v4 (file-system, Stack nav) |
| State | Zustand |
| HTTP | Axios |
| Storage | @react-native-async-storage/async-storage |
| Video | react-native-video (DASH MPD / HLS / MP4) |
| Fallback | react-native-webview (HTML5 video injection) |
| Paging | react-native-pager-view |
| Icons | @expo/vector-icons (Ionicons) |

---

## WBI Signature Implementation

Bilibili requires WBI signing for most API calls. JKVideo implements pure TypeScript MD5 with 12h nav cache.

```typescript
// utils/wbi.ts — pure TS MD5, no external crypto deps
const MIXIN_KEY_ENC_TAB = [
  46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
  27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13
];

function getMixinKey(rawKey: string): string {
  return MIXIN_KEY_ENC_TAB
    .map(i => rawKey[i])
    .join('')
    .slice(0, 32);
}

export async function signWbi(
  params: Record<string, string | number>,
  imgKey: string,
  subKey: string
): Promise<Record<string, string | number>> {
  const mixinKey = getMixinKey(imgKey + subKey);
  const wts = Math.floor(Date.now() / 1000);
  const signParams = { ...params, wts };

  // Sort params alphabetically, filter special chars
  const query = Object.keys(signParams)
    .sort()
    .map(k => {
      const val = String(signParams[k]).replace(/[!'()*]/g, '');
      return `${encodeURIComponent(k)}=${encodeURIComponent(val)}`;
    })
    .join('&');

  const wRid = md5(query + mixinKey); // pure TS md5
  return { ...signParams, w_rid: wRid };
}

// Fetch and cache nav keys (12h TTL)
export async function getWbiKeys(): Promise<{ imgKey: string; subKey: string }> {
  const cached = await AsyncStorage.getItem('wbi_keys');
  if (cached) {
    const { keys, ts } = JSON.parse(cached);
    if (Date.now() - ts < 12 * 3600 * 1000) return keys;
  }
  const res = await api.get('/x/web-interface/nav');
  const { img_url, sub_url } = res.data.data.wbi_img;
  const imgKey = img_url.split('/').pop()!.replace('.png', '');
  const subKey = sub_url.split('/').pop()!.replace('.png', '');
  const keys = { imgKey, subKey };
  await AsyncStorage.setItem('wbi_keys', JSON.stringify({ keys, ts: Date.now() }));
  return keys;
}
```

---

## Bilibili API Service

```typescript
// services/api.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const api = axios.create({
  baseURL: 'https://api.bilibili.com',
  timeout: 15000,
  headers: {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com',
  },
});

// Inject SESSDATA cookie from store
api.interceptors.request.use(async (config) => {
  const sessdata = await AsyncStorage.getItem('SESSDATA');
  if (sessdata) {
    config.headers['Cookie'] = `SESSDATA=${sessdata}`;
  }
  return config;
});

// Popular video list (WBI signed)
export async function getPopularVideos(pn = 1, ps = 20) {
  const { imgKey, subKey } = await getWbiKeys();
  const signed = await signWbi({ pn, ps }, imgKey, subKey);
  const res = await api.get('/x/web-interface/popular', { params: signed });
  return res.data.data.list;
}

// Video stream info (DASH)
export async function getVideoStream(bvid: string, cid: number, qn = 80) {
  const { imgKey, subKey } = await getWbiKeys();
  const signed = await signWbi(
    { bvid, cid, qn, fnval: 4048, fnver: 0, fourk: 1 },
    imgKey, subKey
  );
  const res = await api.get('/x/player/wbi/playurl', { params: signed });
  return res.data.data;
}

// Live stream URL
export async function getLiveStreamUrl(roomId: number) {
  const res = await api.get('/room/v1/Room/playUrl', {
    params: { cid: roomId, quality: 4, platform: 'h5' },
    baseURL: 'https://api.live.bilibili.com',
  });
  return res.data.data.durl[0].url; // HLS m3u8
}
```

---

## DASH MPD Builder

ExoPlayer needs a local MPD file. JKVideo generates it from Bilibili's DASH response:

```typescript
// utils/buildDashMpd.ts
export function buildDashMpdUri(dashData: BiliDashData): string {
  const { duration, video, audio } = dashData;

  const videoAdaptations = video.map((v) => `
    <AdaptationSet mimeType="video/mp4" segmentAlignment="true">
      <Representation id="${v.id}" bandwidth="${v.bandwidth}"
        codecs="${v.codecs}" width="${v.width}" height="${v.height}">
        <BaseURL>${escapeXml(v.baseUrl)}</BaseURL>
        <SegmentBase indexRange="${v.segmentBase.indexRange}">
          <Initialization range="${v.segmentBase.initialization}"/>
        </SegmentBase>
      </Representation>
    </AdaptationSet>`).join('');

  const audioAdaptations = audio.map((a) => `
    <AdaptationSet mimeType="audio/mp4" segmentAlignment="true">
      <Representation id="${a.id}" bandwidth="${a.bandwidth}" codecs="${a.codecs}">
        <BaseURL>${escapeXml(a.baseUrl)}</BaseURL>
        <SegmentBase indexRange="${a.segmentBase.indexRange}">
          <Initialization range="${a.segmentBase.initialization}"/>
        </SegmentBase>
      </Representation>
    </AdaptationSet>`).join('');

  const mpd = `<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
  mediaPresentationDuration="PT${duration}S" minBufferTime="PT1.5S">
  <Period duration="PT${duration}S">
    ${videoAdaptations}
    ${audioAdaptations}
  </Period>
</MPD>`;

  // Write to temp file, return file:// URI for ExoPlayer
  const path = `${FileSystem.cacheDirectory}dash_${Date.now()}.mpd`;
  FileSystem.writeAsStringAsync(path, mpd);
  return path;
}
```

---

## Video Player Component

```typescript
// components/VideoPlayer.tsx
import Video from 'react-native-video';
import { WebView } from 'react-native-webview';
import { useVideoStore } from '../store/videoStore';

interface VideoPlayerProps {
  bvid: string;
  cid: number;
  autoPlay?: boolean;
}

export function VideoPlayer({ bvid, cid, autoPlay = false }: VideoPlayerProps) {
  const [mpdUri, setMpdUri] = useState<string | null>(null);
  const [useFallback, setUseFallback] = useState(false);
  const { setCurrentVideo } = useVideoStore();

  useEffect(() => {
    loadStream();
  }, [bvid, cid]);

  async function loadStream() {
    try {
      const stream = await getVideoStream(bvid, cid);
      if (stream.dash) {
        const uri = await buildDashMpdUri(stream.dash);
        setMpdUri(uri);
      } else {
        setUseFallback(true);
      }
    } catch {
      setUseFallback(true);
    }
  }

  if (useFallback) {
    // WebView fallback for Expo Go / Web
    return (
      <WebView
        source={{ uri: `https://www.bilibili.com/video/${bvid}` }}
        allowsInlineMediaPlayback
        mediaPlaybackRequiresUserAction={false}
      />
    );
  }

  return (
    <Video
      source={{ uri: mpdUri! }}
      style={{ width: '100%', aspectRatio: 16 / 9 }}
      controls
      paused={!autoPlay}
      resizeMode="contain"
      onLoad={() => setCurrentVideo({ bvid, cid })}
    />
  );
}
```

---

## Danmaku System

### Video Danmaku (XML timeline sync)

```typescript
// hooks/useDanmaku.ts
export function useDanmaku(cid: number) {
  const [danmakuList, setDanmakuList] = useState<Danmaku[]>([]);

  useEffect(() => {
    fetchDanmaku(cid);
  }, [cid]);

  async function fetchDanmaku(cid: number) {
    const res = await api.get(`/x/v1/dm/list.so?oid=${cid}`, {
      responseType: 'arraybuffer',
    });
    // Parse XML danmaku
    const xml = new TextDecoder('utf-8').decode(res.data);
    const items = parseXmlDanmaku(xml); // parse <d p="time,...">text</d>
    setDanmakuList(items);
  }

  return danmakuList;
}

// components/DanmakuOverlay.tsx — 5-lane floating display
const LANE_COUNT = 5;

export function DanmakuOverlay({ danmakuList, currentTime }: Props) {
  const activeDanmaku = danmakuList.filter(
    d => d.time >= currentTime - 0.1 && d.time < currentTime + 0.1
  );

  return (
    <View style={StyleSheet.absoluteFillObject} pointerEvents="none">
      {activeDanmaku.map((d, i) => (
        <DanmakuItem
          key={d.id}
          text={d.text}
          color={d.color}
          lane={i % LANE_COUNT}
        />
      ))}
    </View>
  );
}
```

### Live Danmaku (WebSocket)

```typescript
// hooks/useLiveDanmaku.ts
const LIVE_WS = 'wss://broadcastlv.chat.bilibili.com/sub';

export function useLiveDanmaku(roomId: number) {
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(LIVE_WS);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send join room packet
      const body = JSON.stringify({ roomid: roomId, uid: 0, protover: 2 });
      ws.send(buildPacket(body, 7)); // op=7: enter room
      startHeartbeat(ws);
    };

    ws.onmessage = async (event) => {
      const packets = await decompressPacket(event.data);
      packets.forEach(packet => {
        if (packet.op === 5) {
          const msg = JSON.parse(packet.body);
          handleCommand(msg);
        }
      });
    };

    return () => ws.close();
  }, [roomId]);

  function handleCommand(msg: any) {
    switch (msg.cmd) {
      case 'DANMU_MSG':
        setMessages(prev => [{
          type: 'danmaku',
          text: msg.info[1],
          user: msg.info[2][1],
          isGuard: msg.info[7] > 0, // 舰长标记
        }, ...prev].slice(0, 200));
        break;
      case 'SEND_GIFT':
        setMessages(prev => [{
          type: 'gift',
          user: msg.data.uname,
          gift: msg.data.giftName,
          count: msg.data.num,
        }, ...prev].slice(0, 200));
        break;
    }
  }

  return messages;
}
```

---

## Zustand State Stores

```typescript
// store/videoStore.ts
import { create } from 'zustand';

interface VideoState {
  currentVideo: { bvid: string; cid: number } | null;
  isMiniplayer: boolean;
  quality: number; // 80=1080P, 112=1080P+, 120=4K
  setCurrentVideo: (video: { bvid: string; cid: number }) => void;
  setMiniplayer: (val: boolean) => void;
  setQuality: (q: number) => void;
}

export const useVideoStore = create<VideoState>((set) => ({
  currentVideo: null,
  isMiniplayer: false,
  quality: 80,
  setCurrentVideo: (video) => set({ currentVideo: video }),
  setMiniplayer: (val) => set({ isMiniplayer: val }),
  setQuality: (q) => set({ quality: q }),
}));

// store/authStore.ts
interface AuthState {
  sessdata: string | null;
  isLoggedIn: boolean;
  login: (sessdata: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  sessdata: null,
  isLoggedIn: false,
  login: async (sessdata) => {
    await AsyncStorage.setItem('SESSDATA', sessdata);
    set({ sessdata, isLoggedIn: true });
  },
  logout: async () => {
    await AsyncStorage.removeItem('SESSDATA');
    set({ sessdata: null, isLoggedIn: false });
  },
}));
```

---

## QR Code Login

```typescript
// hooks/useQrLogin.ts
export function useQrLogin() {
  const { login } = useAuthStore();
  const [qrUrl, setQrUrl] = useState('');
  const [qrKey, setQrKey] = useState('');
  const pollRef = useRef<ReturnType<typeof setInterval>>();

  async function generateQr() {
    const res = await api.get('/x/passport-login/web/qrcode/generate');
    const { url, qrcode_key } = res.data.data;
    setQrUrl(url);
    setQrKey(qrcode_key);
    startPolling(qrcode_key);
  }

  function startPolling(key: string) {
    pollRef.current = setInterval(async () => {
      const res = await api.get('/x/passport-login/web/qrcode/poll', {
        params: { qrcode_key: key },
      });
      const { code } = res.data.data;
      if (code === 0) {
        // Extract SESSDATA from Set-Cookie header
        const setCookie = res.headers['set-cookie'] ?? [];
        const sessdataCookie = setCookie
          .find((c: string) => c.includes('SESSDATA='));
        const sessdata = sessdataCookie?.match(/SESSDATA=([^;]+)/)?.[1];
        if (sessdata) {
          await login(sessdata);
          clearInterval(pollRef.current);
        }
      }
    }, 2000);
  }

  useEffect(() => () => clearInterval(pollRef.current), []);
  return { qrUrl, generateQr };
}
```

---

## Download Manager + LAN Sharing

```typescript
// store/downloadStore.ts
import * as FileSystem from 'expo-file-system';

export const useDownloadStore = create((set, get) => ({
  downloads: [] as Download[],

  startDownload: async (bvid: string, quality: number) => {
    const stream = await getVideoStream(bvid, /* cid */ 0, quality);
    const url = stream.durl?.[0]?.url ?? stream.dash?.video?.[0]?.baseUrl;
    const path = `${FileSystem.documentDirectory}downloads/${bvid}_${quality}.mp4`;

    const task = FileSystem.createDownloadResumable(url, path, {
      headers: { Referer: 'https://www.bilibili.com' },
    }, (progress) => {
      // Update progress in store
      set(state => ({
        downloads: state.downloads.map(d =>
          d.bvid === bvid ? { ...d, progress: progress.totalBytesWritten / progress.totalBytesExpectedToWrite } : d
        ),
      }));
    });

    set(state => ({
      downloads: [...state.downloads, { bvid, quality, path, progress: 0, task }],
    }));
    await task.downloadAsync();
  },
}));

// LAN HTTP server for QR sharing (scripts/proxy.js pattern)
// Built-in HTTP server serves downloaded file, generates QR with local IP
import { createServer } from 'http';
import { networkInterfaces } from 'os';

function getLanIp(): string {
  const nets = networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]!) {
      if (net.family === 'IPv4' && !net.internal) return net.address;
    }
  }
  return 'localhost';
}
```

---

## expo-router Navigation Patterns

```typescript
// app/video/[bvid].tsx
import { useLocalSearchParams } from 'expo-router';

export default function VideoDetail() {
  const { bvid } = useLocalSearchParams<{ bvid: string }>();
  // ...
}

// Navigate to video
import { router } from 'expo-router';
router.push(`/video/${bvid}`);

// Navigate to live room
router.push(`/live/${roomId}`);

// Navigate back
router.back();
```

---

## Image Proxy (Web)

Bilibili images block direct loading in browsers via Referer header. Use the bundled proxy:

```javascript
// scripts/proxy.js (port 3001)
// Usage in components:
function proxyImage(url: string): string {
  if (Platform.OS === 'web') {
    return `http://localhost:3001/proxy?url=${encodeURIComponent(url)}`;
  }
  return url; // Native handles Referer correctly
}
```

---

## Quality Level Reference

| Code | Quality |
|------|---------|
| 16 | 360P |
| 32 | 480P |
| 64 | 720P |
| 80 | 1080P |
| 112 | 1080P+ (大会员) |
| 116 | 1080P60 (大会员) |
| 120 | 4K (大会员) |

---

## Common Patterns

### Add a New API Endpoint

```typescript
// services/api.ts
export async function getVideoInfo(bvid: string) {
  const { imgKey, subKey } = await getWbiKeys();
  const signed = await signWbi({ bvid }, imgKey, subKey);
  const res = await api.get('/x/web-interface/view', { params: signed });
  return res.data.data;
}
```

### Add a New Screen

```typescript
// app/history.tsx — automatically becomes /history route
import { Stack } from 'expo-router';

export default function HistoryScreen() {
  return (
    <>
      <Stack.Screen options={{ title: '历史记录' }} />
      {/* screen content */}
    </>
  );
}
```

### Create a Zustand Slice

```typescript
// store/settingsStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const useSettingsStore = create(
  persist(
    (set) => ({
      defaultQuality: 80,
      danmakuEnabled: true,
      setDefaultQuality: (q: number) => set({ defaultQuality: q }),
      toggleDanmaku: () => set(s => ({ danmakuEnabled: !s.danmakuEnabled })),
    }),
    {
      name: 'jkvideo-settings',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DASH not playing in Expo Go | Use Dev Build: `npx expo run:android` |
| Images not loading on Web | Run `node scripts/proxy.js` and ensure web uses proxy URLs |
| API returns 412 / risk control | Ensure WBI signature is fresh; clear cached keys via AsyncStorage |
| 4K/1080P+ not available | Login with a Bilibili Premium (大会员) account |
| Live stream fails | App auto-selects HLS; FLV is not supported by ExoPlayer/HTML5 |
| QR code expired | Close and reopen the login modal to regenerate |
| Cookie not persisting | Check AsyncStorage permissions; `SESSDATA` key must match interceptor |
| WebSocket danmaku drops | Increase heartbeat frequency; check packet decompression (zlib) |
| Build fails on iOS | Run `cd ios && pod install` then rebuild |

---

## Known Limitations

- **Dynamic feed / posting / likes** require `bili_jct` CSRF token — not yet implemented
- **FLV live streams** are not supported; app auto-selects HLS fallback
- **Web platform** requires local proxy server for images (Referer restriction)
- **4K / 1080P+** requires logged-in Bilibili Premium account
- **QR code** expires after 10 minutes — reopen modal to refresh

---
