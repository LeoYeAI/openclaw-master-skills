# Trigger Tests / 触发测试用例

Test cases to verify the skill triggers correctly (and does not trigger for out-of-scope requests).

## Should trigger (10 cases)

1. "帮我把这个录音转成文字" — Chinese transcription request
2. "Transcribe this audio file for me" — English transcription request
3. "用豆包把这段音频转写一下" — Explicit Doubao mention
4. "I have an M4A recording, can you convert it to text?" — Format-specific transcription
5. "帮我用火山引擎识别这段语音" — Volcengine mention
6. "Please transcribe the meeting recording at /tmp/meeting.mp3" — File path with transcription
7. "这个粤语录音能转文字吗" — Cantonese dialect mention
8. "I need speaker diarization for this audio" — Speaker diarization feature
9. "把这个 5 小时的会议录音转成文本" — Long audio transcription
10. "Use Seed-ASR to transcribe this file" — Model name mention

## Should NOT trigger (7 cases)

1. "帮我做一个实时语音识别的 demo" — Real-time/streaming ASR (out of scope)
2. "Can you convert this text to speech?" — TTS (text-to-speech, opposite direction)
3. "I need live captioning for my video stream" — Live captioning (out of scope)
4. "帮我用 Whisper 转写这段音频" — Different ASR provider (Whisper)
5. "Translate this Chinese text to English" — Translation, not transcription
6. "帮我录一段语音" — Voice recording, not transcription
7. "Generate subtitles in real-time for my livestream" — Real-time subtitles (out of scope)
