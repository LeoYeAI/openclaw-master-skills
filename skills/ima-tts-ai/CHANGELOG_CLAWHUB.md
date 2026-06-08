# Changelog — ima-tts-ai

All notable changes to the **IMA Studio TTS** skill will be documented in this file.

---

## [1.0.0] - 2026

### Added

- Initial ClawHub release
- Text-to-speech via IMA Open API (seed-tts-2.0)
- Flow: query product list → create task → poll until done
- Scripts: `ima_tts_create.py`, `ima_logger.py`
- Support for voice_id, speed and other TTS parameters
- Output: audio URL (mp3/wav)

### Requirements

- IMA API key (ima_*)
- Python 3, requests
