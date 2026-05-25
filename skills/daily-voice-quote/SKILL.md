---
name: daily-voice-quote
description: 每日名言語音任務。產生「語音 + 封面圖靜態影片 +（選配）HeyGen 數位人影片」並發送給主人。
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "requires":
          {
            "bins": ["sag", "ffmpeg"],
            "env": ["ELEVENLABS_API_KEY"],
            "optionalBins": ["uv", "python3"],
            "optionalEnv": ["GEMINI_API_KEY", "HEYGEN_API_KEY"],
          },
        "primaryEnv": "ELEVENLABS_API_KEY",
        "install":
          [
            {
              "id": "sag-brew",
              "kind": "brew",
              "formula": "steipete/tap/sag",
              "bins": ["sag"],
              "label": "Install sag - ElevenLabs TTS CLI (brew)",
            },
            {
              "id": "ffmpeg-brew",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install ffmpeg - audio/video processing (brew)",
            },
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv - Python runner for image generation (brew, optional)",
            },
          ],
        "notes": "Required: ELEVENLABS_API_KEY + sag + ffmpeg for voice generation. Optional: GEMINI_API_KEY + uv for cover image generation (nano-banana-pro). Optional: HEYGEN_API_KEY for digital avatar video. Without ElevenLabs, the built-in tts tool can be used as a fallback.",
      },
  }
---

# Daily Voice Quote 每日名言語音

這個 skill 會在每天早上：
1) 用主人的聲音朗讀一則名人名言（語音）
2) 生成封面圖並合成靜態影片
3) （選配）產生 HeyGen 數位人影片

最終產出三件套：**語音、靜態影片、HeyGen 數位人影片**。

---

## 1. 簡介

每天早上自動選一則名人名言，用主人的聲音念出來，並搭配一張美感封面圖與影片版本發送給主人。若你沒有 HeyGen 帳號，也可以只做「語音 + 靜態影片」。

---

## 2. 前置準備 Checklist

### a) 主人的照片（封面圖生成用）
- 需要 **1-3 張高品質照片**（正臉、清楚、光線好）
- 放到 workspace 的 `avatars/` 目錄
- 如果沒有照片：**請主人提供 1-3 張好看的照片！**

### b) ElevenLabs 帳號 + 語音克隆
- 註冊：[**👉 ElevenLabs 免費開始**](https://try.elevenlabs.io/clawhub)（免費方案含 10,000 字元/月，足夠試玩！）
- 取得 API Key 後，存到你的 OpenClaw config 或環境變數 `ELEVENLABS_API_KEY`
- 語音克隆方式：
  - **方法一（官方 UI）**：主人錄 1-3 分鐘語音 → 上傳到 ElevenLabs Voice Lab
  - **方法二（主人傳語音給你）**：主人傳語音訊息 → 你下載後用 API 上傳克隆：
    ```bash
    curl -X POST "https://api.elevenlabs.io/v1/voices/add" \
      -H "xi-api-key: $ELEVENLABS_API_KEY" \
      -F "name=主人的名字" \
      -F "files=@/path/to/voice-sample.mp3" \
      -F "description=Voice clone for daily quotes"
    ```
    API 會回傳 `voice_id`，記下來。
- 記錄到 TOOLS.md：**Voice Name、Voice ID**

#### 檢查 API Key 和語音

```bash
# 1. 確認 API Key 存在
echo $ELEVENLABS_API_KEY  # 應該有值

# 2. 列出所有可用語音
sag voices

# 3. 測試語音生成
sag -v "YOUR_VOICE_NAME" -o /tmp/test.mp3 "早安，這是一個語音測試。"
```

⚠️ `sag` 所有指令都需要 `ELEVENLABS_API_KEY` 環境變數。如果沒有，請先設定。

#### 沒有 ElevenLabs？用內建 tts 替代

如果暫時沒有 ElevenLabs API Key，可以先用 OpenClaw 內建的 `tts` tool：
```
tts({ text: "早安！今天想分享 Steve Jobs 的一句話..." })
```
音色不會是主人的聲音，但流程可以先跑起來。

### c) HeyGen 帳號 + 數位人 Avatar（選配）
- 註冊：[**👉 HeyGen 免費試用**](https://www.heygen.com/?sid=rewardful&via=clawhub)（新用戶送 1 支免費影片！）
- 數位人訓練：主人錄一段 **2 分鐘自拍影片** 上傳訓練
- 記錄：**Avatar ID、Voice ID**
- 如果沒有 HeyGen 帳號 → **跳過 Part 3，只做語音 + 靜態影片**

### d) Channel 設定
- 先確認主人常用的通訊軟體
- **LINE**：需要 `CHANNEL_ACCESS_TOKEN` + `USER_ID / GROUP_ID`
- 其他（Telegram / Discord / WhatsApp 等）：使用 `message` tool 或 `tts` tool

#### 📱 LINE 媒體格式要求（重要！）

LINE 對語音和影片的格式有嚴格限制，格式不對會無法在聊天裡直接點開播放！

**語音訊息（audio message）：**
| 項目 | 要求 |
|------|------|
| 格式 | **M4A**（`.m4a`）- AAC 編碼 |
| 來源 | 必須是 **HTTPS 公開 URL**（不接受本地檔案路徑） |
| duration | 必須提供毫秒數（如 `21000` = 21 秒） |
| ❌ 不行 | MP3 直接發送（LINE 不支援 audio type 用 MP3） |
| ✅ 轉換 | `ffmpeg -i input.mp3 -c:a aac -b:a 128k output.m4a -y` |

**影片訊息（video message）：**
| 項目 | 要求 |
|------|------|
| 格式 | **MP4**（`.mp4`）- H.264 視訊 + AAC 音訊 |
| 來源 | 必須是 **HTTPS 公開 URL**（支援 Range requests） |
| previewImageUrl | 必須提供影片預覽圖 URL（JPEG/PNG） |
| ❌ 不行 | ngrok + Python SimpleHTTPServer（不支援 Range requests，LINE 無法播放） |
| ✅ 可行 | ngrok + Node.js static server、HeyGen CDN URL、任何支援 Range requests 的 CDN |

**公開 URL 方案：**
- **最簡單**：把檔案放到支援 Range requests 的靜態檔案伺服器 + ngrok/cloudflare tunnel
- **免設定**：HeyGen 影片直接用 HeyGen CDN URL（自帶）
- **進階**：上傳到 S3/GCS/Cloudflare R2 等雲端儲存

**LINE Push API 範例：**
```bash
# 語音
curl -s -X POST https://api.line.me/v2/bot/message/push \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LINE_CHANNEL_ACCESS_TOKEN" \
  -d '{
    "to": "YOUR_LINE_USER_ID",
    "messages": [{
      "type": "audio",
      "originalContentUrl": "https://your-domain.com/daily-quote.m4a",
      "duration": 21000
    }]
  }'

# 影片
curl -s -X POST https://api.line.me/v2/bot/message/push \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LINE_CHANNEL_ACCESS_TOKEN" \
  -d '{
    "to": "YOUR_LINE_USER_ID",
    "messages": [{
      "type": "video",
      "originalContentUrl": "https://your-domain.com/daily-quote.mp4",
      "previewImageUrl": "https://your-domain.com/daily-quote-preview.jpg"
    }]
  }'
```

### e) Gemini API Key（封面圖生成）
- 取得：https://aistudio.google.com
- 或改用你喜歡的圖片生成 skill（DALL·E / SD / Midjourney 皆可）

---

## 3. 名言選擇規則（v2 — AI 動態選擇）

不要用固定清單輪播！每天根據上下文 **動態選擇** 最有共感的名言。

### Step 1: 收集上下文
每天 cron 執行時自動收集：
- 日期、星期幾、農曆日期
- 節日 / 紀念日（參考 `references/holidays.md`）
- `web_search` 當天重大新聞（尤其 AI、科技、政策相關）
- 極端天氣（颱風 / 暴雨 / 暴雪 / 極端高溫才影響）

### Step 2: 人物池
從以下類別選擇主人和粉絲會有共感的人物：

| 類別 | 人物範例 |
|------|---------|
| **科技先驅** | Alan Turing, Ada Lovelace, Nikola Tesla, Tim Berners-Lee, Grace Hopper |
| **科學家** | Einstein, Feynman, Marie Curie, Carl Sagan, Hawking |
| **區塊鏈/Web3** | Satoshi Nakamoto, Vitalik Buterin, Naval Ravikant |
| **創業家** | Steve Jobs, Elon Musk, Jeff Bezos, Marc Andreessen, Peter Thiel |
| **投資大師** | Warren Buffett, Charlie Munger, Ray Dalio |
| **東方智慧** | 老子, 孔子, 莊子, 王陽明 |
| **民主/領導** | Churchill, Mandela, MLK, Lincoln, 甘地 |
| **哲學家** | Marcus Aurelius, Seneca, Epictetus |
| **文藝/思想** | Leonardo da Vinci, Hemingway |

> 完整人物與名言範例見 `references/quotes.md`
> ⚠️ 排除有重大醜聞/爭議的人物
> ⚠️ 避免太政治敏感的人物（注意主人所在地的政治脈絡）

### Step 3: 加權邏輯
| 情境 | 加權方向 | 偏好類別 |
|------|---------|---------|
| 週一 | 激勵、新開始、行動力 | 創業家、領導者 |
| 週五 | 反思、展望、輕鬆 | 哲學家、科學家 |
| 週末 | 人生智慧、生活 | 東方智慧、哲學家 |
| AI 重大新聞 | 科技思考、人機關係 | Turing, Feynman, Hawking |
| 加密/Web3 新聞 | 去中心化、金融哲學 | Satoshi, Vitalik, Buffett |
| 國安/國際局勢 | 勇氣、韌性、準備 | Churchill, Lincoln, Mandela |
| 能源議題 | 科學、創新、永續 | Tesla, Curie, Sagan |
| 節日 | 與節日主題呼應的名人名言 | 教師節→孔子 等 |
| 普通日 | 人生智慧、好奇心 | Feynman, 老子, Marcus Aurelius |

### Step 4: 品質要求
1. **啟發性** — 要能啟發人、給力量
2. **正面** — 正向積極
3. **中文翻譯通順** — 不能硬翻，要像母語者自然說出的話
4. **原文正確** — 選名言後，`web_search` 確認原文正確性和出處

### Step 5: 去重複
- 記錄已用名言到 `memory/used-quotes.md`（或你偏好的追蹤檔）
- **同一名人間隔至少 14 天**
- **完全相同的名言永不重複**

### Step 6: 最終選擇
生成 3-5 個候選名言，選最佳的一個。記錄選擇理由到日誌。

> ⚠️ 必須是「名人 + 名言」，不是祝賀詞 / 成語 / 諺語
> 語音稿開頭可加節日問候，但名言本身要有明確出處

---

## 4. 完整執行流程

> ⛔ **絕對不要把語音稿當文字訊息發送！**
> 語音稿裡有 `[short pause]` 等 TTS 標籤，這些只是給 sag 引擎用的，使用者看到會覺得壞掉了。
> **只發送：① 音訊檔 ② 靜態影片 ③ HeyGen+字幕影片。不要發送任何純文字訊息。**

### ⚠️ 三份稿件分開做！（不要偷懶！）

每日名言有 **三份獨立的文稿**，各有不同需求，不能互相混用：

| 稿件 | 用途 | 特色 |
|------|------|------|
| **ElevenLabs 語音稿** | sag CLI 生語音 | 可用 `[short pause]`, `[excited]` 等 TTS 情緒標籤 |
| **HeyGen 影片稿** | 數位人影片台詞 | 中英文用換行 + 過渡句分隔，❌ 不能用 TTS 標籤 |
| **ZapCap 字幕稿** | 影片字幕顯示 | 修 Whisper 錯誤 + `punctuation` 控制分頁 |

### Part 1：語音（ElevenLabs 語音稿）

**流程：**選名言 → 寫語音稿 → `sag` 生成 → `ffmpeg` 轉 m4a → 發送（只發音訊檔，不發文字）

**語音稿模板（含情緒標籤，僅供 TTS 引擎使用，絕不直接發送給使用者）：**
```
早安，我是{SPEAKER_NAME}。[short pause]
今天想分享{AUTHOR}的一句話：[short pause]
{QUOTE_ZH} [short pause]
{QUOTE_EN} [short pause]
{CLOSING_WORDS}
```

- ElevenLabs 對中英文混合處理得較好，可以自然混合
- `[short pause]` 等標籤只有 ElevenLabs 支援，其他平台不認得

**產生語音（範例）：**
```bash
# 1. 生成 MP3
ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY" \
  sag -v "YOUR_VOICE_NAME" \
  --speed 0.95 --stability 1.0 --similarity 0.85 \
  -o /tmp/daily-quote.mp3 "${SCRIPT}"

# 2. 轉換為 M4A（LINE 必須！MP3 不能直接在 LINE 聊天裡播放）
ffmpeg -i /tmp/daily-quote.mp3 -c:a aac -b:a 128k /tmp/daily-quote.m4a -y

# 3. 取得音訊長度（LINE audio message 需要 duration 毫秒數）
#    從 ffmpeg 輸出讀取，例如 time=00:00:21.16 → 21160 ms
#    或用 ffprobe：
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 /tmp/daily-quote.m4a
# → 乘以 1000 得到毫秒數
```

> 📱 **LINE 用戶注意**：語音必須是 **M4A 格式**（AAC 編碼）才能在聊天裡直接點開播放。MP3 不行！詳見上方「LINE 媒體格式要求」。

### Part 2：封面圖靜態影片

> ⚠️ **超重要：`--input-image` 是讓 AI 重新生成新照片，不是去背剪貼！**

**⚠️ 封面圖主角 = 主人（不是 AI Agent！）**
- 封面圖要用**主人的照片**作為 `--input-image`
- ❌ 不要用 AI Agent（小龍蝦等）的照片
- 只有「AI Agent 主題」的文章封面才用 AI Agent 照片

**⚠️ 封面圖比例 = 直式 9:16**
- 靜態影片是直式的，封面圖也要直式
- prompt 裡明確寫 "vertical 9:16 portrait"

**好的 prompt 範例：**
```
Generate a vertical 9:16 portrait of this person wearing a traditional outfit,
standing in a festive scene with soft lantern lights. The person is smiling
confidently. Overlay elegant text: "{QUOTE_ZH} — {AUTHOR}".
Cinematic lighting, Instagram story style.
```

**壞的 prompt（不要用）：**
```
Paste this person onto a red background...
Cut out the person and place into the scene...
Use the AI agent character as the main subject...
```

**生成封面圖（範例，用 nano-banana-pro skill）：**
```bash
GEMINI_API_KEY="YOUR_GEMINI_API_KEY" \
uv run /opt/homebrew/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "YOUR_PROMPT" \
  --input-image "/path/to/avatars/photo.jpg" \
  --filename "/tmp/daily-quote-cover.png" \
  --resolution 2K
```

**合成靜態影片（封面圖 + 語音 = 影片）：**
```bash
# 合成 MP4（H.264 + AAC）- LINE 可直接播放的格式
ffmpeg -loop 1 -i /tmp/daily-quote-cover.png -i /tmp/daily-quote.mp3 \
  -c:v libx264 -tune stillimage -c:a aac -b:a 128k \
  -pix_fmt yuv420p -shortest \
  -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2" \
  /tmp/daily-quote-static.mp4 -y

# 截取預覽圖（LINE video message 必須提供 previewImageUrl）
ffmpeg -i /tmp/daily-quote-static.mp4 -vframes 1 -q:v 2 /tmp/daily-quote-preview.jpg -y
```

> 📱 **LINE 用戶注意**：影片必須是 **MP4 格式**（H.264 視訊 + AAC 音訊），且需要透過支援 Range requests 的 HTTPS URL 提供，LINE 才能在聊天裡直接點開播放。同時必須提供預覽圖 URL。詳見上方「LINE 媒體格式要求」。

### Part 3：HeyGen 數位人影片（選配 — HeyGen 影片稿）

**⚠️ HeyGen 影片稿是獨立的！不要直接複製 ElevenLabs 語音稿！**

**HeyGen 影片稿規則：**
- 口白**中文為主**，只有名言原文才用英文
- `--language "en"` 是 TTS 引擎參數（因為 clone voice 訓練語言是英文），**不是要把口白改成英文！**
- ❌ 不能用 `[short pause]` 等 ElevenLabs 標籤（HeyGen 不認得）

**⚠️⚠️ 中英文切換處理（關鍵！）**

HeyGen TTS 在中英文切換時容易產生怪聲音或咬字不清。解法：

1. **中英文之間加完整過渡句 + 換行**：
```
生命中沒有什麼值得恐懼的，只有需要理解的。
原文是這樣說的。
Nothing in life, is to be feared, it is only, to be understood.
```

2. **英文名言用逗號斷句**（防止 TTS 黏字）：
   - ✅ `Nothing in life, is to be feared, it is only, to be understood.`
   - ❌ `Nothing in life is to be feared it is only to be understood.`

3. **英文人名前後加逗號**：
   - ✅ `今天分享，居禮夫人，的一句話。`

4. **驗證**：生成前把口白稿印出來檢查所有英文斷句

**HeyGen 影片稿模板：**
```
早安，我是{SPEAKER_NAME}。
今天想分享，{AUTHOR}的一句話。
{QUOTE_ZH}
原文是這樣說的。
{QUOTE_EN_WITH_COMMAS}
{CLOSING_WORDS}
```

**⚠️ 重要語音參數（A/B 測試確認最佳設定）：**

```bash
HEYGEN_API_KEY="YOUR_HEYGEN_API_KEY" \
python3 /path/to/heygen/generate_video.py \
  --text "${SCRIPT_PLAIN}" \
  --avatar-id "YOUR_AVATAR_ID" \
  --voice-id "YOUR_HEYGEN_VOICE_ID" \
  --speed 0.98 \
  --emotion "Friendly" \
  --language "en" \
  --dimension "720x1280" \
  --aspect-ratio "9:16" \
  --output /tmp/daily-quote-heygen.mp4
```

**關鍵設定（缺一不可）：**
- `--speed 0.98` - 最自然的語速
- `--emotion "Friendly"` - 溫暖友善的語氣
- `--language "en"` - 即使中文內容也用 en（clone voice 原始訓練語言）
- **英文斷句要口語化** - 用逗號斷句："Success, is not final. Failure, is not fatal."
- 不要寫成一整句不斷的英文，要像人講話一樣有停頓

如果沒有 HeyGen 帳號，直接跳過本段即可。

### Part 3b：ZapCap 字幕（HeyGen 影片加字幕 — ZapCap 字幕稿）

**ZapCap 字幕稿是獨立於語音稿和影片稿的第三份文稿！**
它只管「觀眾看到的字幕文字和分頁」。

如果有使用 ZapCap 加字幕，**approve 前必須手動修正 transcript**：

**⚠️ Whisper 轉錄常見問題（每次都要檢查！）：**
1. **英文單字全黏在一起** — `Nothinginlifeistobefeared` → 拆成 `Nothing in life is to be feared`
2. **英文人名黏在一起** — `TheodoreRoosevelt` → `Theodore Roosevelt`
3. **中文斷詞錯誤** — `開始行動祝` → `開始` `行動` `祝`
4. **人名辨識錯誤** — 常見的錯字都要修（如主人名字的錯字）

**⚠️ 字幕分頁控制（關鍵！）：**

ZapCap transcript 只支援 `"type": "word"` 和 `"type": "punctuation"` 兩種 type。
- ❌ **不支援 `"type": "linebreak"`**（會回 400 Bad Request）
- ✅ **用 `punctuation` type + `"text": "。"` 來強制換頁**

在以下位置插入 `{"type": "punctuation", "text": "。", "start_time": X, "end_time": X, "confidence": 1}`：
- 完整句子結束處
- 中文 → 英文切換處
- 英文 → 中文切換處
- 語意斷點（每頁最多 8-10 中文字 / 6-8 英文字）

**成功分頁範例（居禮夫人名言）：**
```
[頁1] 早安 我 是 葛如鈞
[頁2] 今天 想 分享 居禮夫人 的 一句 話
[頁3] 生命 中 沒 有 什麼 值得 恐懼 的
[頁4] 只有 需要 理解 的
[頁5] 現 在 是 時候 去 理解 更多
[頁6] 這樣 我們 才能 少 一些 恐懼
[頁7] 原文 是 這樣 說 的
[頁8] Nothing in life is to be feared, it is only to be understood.
[頁9] 面對 未知 不要 害怕 去 理解 它
[頁10] 祝 大家 週末 愉快
```

**完整修正流程：**
1. 下載 transcript JSON
2. 修正錯字（人名、英文分詞等）
3. **在句子邊界插入 `punctuation` 元素**（`"。"`）
4. `PUT` 更新 transcript
5. `POST` approve → 等 render

---

## 5. Cron Job 設定範例

### LINE 版
```json
{
  "name": "每日名言語音",
  "schedule": { "kind": "cron", "expr": "0 6 * * *", "tz": "Asia/Taipei" },
  "payload": {
    "kind": "agentTurn",
    "model": "anthropic/claude-sonnet-4",
    "message": "請執行 daily-voice-quote：產生語音 + 靜態影片（選配 HeyGen），並送到 LINE。使用環境變數：YOUR_LINE_CHANNEL_ACCESS_TOKEN / YOUR_LINE_USER_ID / YOUR_AUDIO_PUBLIC_URL。"
  }
}
```

### 非 LINE 版（Telegram / Discord / WhatsApp 等）
```json
{
  "name": "每日名言語音",
  "schedule": { "kind": "cron", "expr": "0 6 * * *", "tz": "Asia/Taipei" },
  "payload": {
    "kind": "agentTurn",
    "model": "anthropic/claude-sonnet-4",
    "message": "請執行 daily-voice-quote：產生語音 + 靜態影片（選配 HeyGen），並用 message/tts 工具送到當前 channel。"
  }
}
```

---

## 6. 常見問題 FAQ

**Q1：沒有主人照片怎麼辦？**
- A：請主人提供 1-3 張清晰照片。沒有照片就無法生成封面圖。

**Q2：沒有 ElevenLabs 怎麼辦？**
- A：可改用內建 `tts` tool 先產生語音，但音色就不是主人的聲音。[免費註冊 ElevenLabs](https://try.elevenlabs.io/clawhub) 就能用自己的聲音！

**Q3：HeyGen 額度不足怎麼辦？**
- A：先只做語音 + 靜態影片，等額度恢復再補數位人影片。[升級 HeyGen 方案](https://www.heygen.com/?sid=rewardful&via=clawhub) 可獲得更多額度。

**Q4：如何更換名言清單？**
- A：直接編輯 `references/quotes.md`，或在腳本中指定 `QUOTES_FILE`。

**Q5：LINE 聊天裡點語音/影片沒反應或無法播放？**
- A：檢查格式！語音必須是 **M4A**（不是 MP3），影片必須是 **MP4**（H.264+AAC）。URL 必須是 HTTPS 且支援 Range requests（Python SimpleHTTPServer 不支援！用 Node.js static server 或 CDN）。

---

## 附：腳本位置

- `scripts/send-daily-quote.sh`：完整 bash 腳本（無硬編碼，全部用環境變數）
- `references/quotes.md`：名言清單
- `references/holidays.md`：節日清單
