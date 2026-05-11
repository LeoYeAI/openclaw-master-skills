# Authentication

## API Key Setup

Get your API key from the [Scrapeless Dashboard](https://app.scrapeless.com).

### Method 1: Config File (Recommended)

```bash
scrapeless-scraping-browser config set apiKey your_api_key_here
```

This stores the key securely in `~/.scrapeless/config.json` with restricted permissions (0600).

### Method 2: Environment Variable

```bash
export SCRAPELESS_API_KEY=your_api_key_here
```

For persistence, add to your shell profile:

```bash
echo 'export SCRAPELESS_API_KEY=your_api_key_here' >> ~/.zshrc
source ~/.zshrc
```

## Configuration Priority

Config file > Environment variable

## Verify Authentication

```bash
# Check if API key is set
scrapeless-scraping-browser config get apiKey

# Test with a simple command
scrapeless-scraping-browser sessions
```

## Security Best Practices

1. Never commit API keys to version control
2. Use config file method for persistent storage
3. Config files are automatically created with user-only permissions
4. Rotate API keys regularly from the Scrapeless Dashboard