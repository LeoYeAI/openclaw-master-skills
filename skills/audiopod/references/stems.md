# Stem Separation Reference

## All Modes

| Mode | Stems | Output | Use Case |
|------|-------|--------|----------|
| single | 1 | Specified stem only | Vocal isolation, drum extraction |
| two | 2 | vocals + instrumental | Karaoke tracks |
| four | 4 | vocals, drums, bass, other | Standard remixing |
| six | 6 | + guitar, piano | Full instrument separation |
| producer | 8 | + kick, snare, hihat | Beat production |
| studio | 12 | + cymbals, sub_bass, synth | Professional mixing |
| mastering | 16 | Maximum detail | Forensic analysis |

## Single Stem Options

`stem` parameter: vocals, drums, bass, guitar, piano, other

## API Endpoints

- **Submit job:** `POST /api/v1/stem-extraction/api/extract` (multipart form: `url` or `file`, `mode`, optional `stem`)
- **Check status:** `GET /api/v1/stem-extraction/status/{JOB_ID}`
- **List modes:** `GET /api/v1/stem-extraction/modes`
- **List jobs:** `GET /api/v1/stem-extraction/jobs?skip=0&limit=50&status=COMPLETED`
- **Get job:** `GET /api/v1/stem-extraction/jobs/{JOB_ID}`
- **Delete job:** `DELETE /api/v1/stem-extraction/jobs/{JOB_ID}`

## Response Format

```json
{
  "id": 1234,
  "status": "COMPLETED",
  "download_urls": {
    "vocals": "https://...",
    "drums": "https://...",
    "bass": "https://...",
    "other": "https://..."
  },
  "quality_scores": {
    "vocals": 0.95,
    "drums": 0.88
  }
}
```
