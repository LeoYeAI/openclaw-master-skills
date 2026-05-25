# Hi-Lite

**Search, browse, and rediscover your Kindle highlights — locally, for free.**

Hi-Lite is an [OpenClaw](https://openclaw.org) skill that turns your raw Kindle highlights into a searchable, browsable personal library. No accounts, no subscriptions, no cloud — everything stays on your machine.

## Prerequisites

- [OpenClaw](https://openclaw.org) installed and running

## Installation

**Option A: ClawHub**

```
clawhub install hi-lite
```

**Option B: Git clone**

```bash
git clone https://github.com/gofordylan/hi-lite.git ~/.openclaw/workspace/skills/hi-lite/
```

**Option C: Paste the repo URL** to your OpenClaw assistant and it will install it for you.

## Setup

Tell your OpenClaw assistant:

> Set up hi-lite

This creates the workspace directory at `~/.openclaw/workspace/hi-lite/` with the necessary subdirectories.

### Optional: Enable Semantic Search

For the best search experience, add the highlights directory to your OpenClaw memory search config:

```json
{
  "memorySearch": {
    "extraPaths": ["~/.openclaw/workspace/hi-lite/highlights"]
  }
}
```

This enables hybrid vector + BM25 search across all your highlights. Without it, Hi-Lite still works — it just reads files directly instead of using semantic search.

## Importing Highlights

1. Place your raw Kindle export files into `~/.openclaw/workspace/hi-lite/raw/`
2. Tell your assistant:

> Import my highlights

### Supported Sources

- **My Clippings.txt** — The file from your Kindle device (connect via USB, find it in the `documents` folder)
- **Amazon Read Notebook** — Copy-paste from [read.amazon.com/notebook](https://read.amazon.com/notebook)
- **Bookcision** — JSON or text exports from the [Bookcision](https://readwise.io/bookcision) browser extension
- **Any raw text** — Paste or drop any text with highlights and Hi-Lite will do its best to parse it

## Auto-Fetch from Amazon

Fetch all your Kindle highlights directly from Amazon with a single command — no manual exporting needed.

### Prerequisites

- Python 3.8+
- pip

### First-Time Setup

```bash
pip install "playwright>=1.40.0"
playwright install chromium
```

### Usage

Tell your OpenClaw assistant:

> Fetch my highlights from Amazon

Or:

> /hi-lite fetch

A browser window will open and navigate to Amazon's Kindle notebook. If you're not already logged in, you'll be prompted to sign in manually (the script handles 2FA and CAPTCHA by letting you do it yourself in the real browser). Your session is saved, so future fetches won't require logging in again.

After fetching, Hi-Lite automatically imports the highlights into your library.

### Non-US Amazon Domains

If your Amazon account is on a non-US store (e.g., amazon.co.uk, amazon.de), just mention it to your assistant.

---

## Usage

All interaction happens through natural conversation with your OpenClaw assistant.

### Search

> Find quotes about perseverance

> What did Dostoevsky say about suffering?

> /hi-lite search meaning of life

### Browse

> Show me all my books

> Show me highlights from Antifragile

> What are my most highlighted books?

### Random Quotes

> Give me a random quote

> Surprise me with 5 highlights

> /hi-lite random 3

### Collections

> Make a collection of quotes about courage

> Show my collections

> Add that last quote to my "favorites" collection

## How It Works

Hi-Lite stores everything as plain markdown files:

```
~/.openclaw/workspace/hi-lite/
├── raw/              # Your raw Kindle exports
├── highlights/
│   ├── _index.md     # Master index of all books
│   └── books/        # One markdown file per book
└── collections/      # Themed collections you create
```

Each book gets its own markdown file with YAML frontmatter and blockquoted highlights. This format is human-readable, git-friendly, and optimized for OpenClaw's vector search.

## Privacy

All your data stays on your machine. Hi-Lite is just a set of instructions that teach your local OpenClaw agent how to work with your files. Nothing is sent to any server.

## License

MIT
