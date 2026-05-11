# Edge-TTS Skill Distribution

## Overview

This document provides information for distributing the Edge-TTS skill package.

## Package Contents

The distributable package includes:

- `SKILL.md` - Complete skill documentation
- `scripts/` - Node.js scripts for TTS conversion and configuration
- `references/` - Additional documentation and guides
- `dist/` - Distribution artifacts and installation scripts

## Installation Requirements

### System Requirements
- Node.js (v14.0.0 or higher)
- npm (v6.0.0 or higher)
- Internet connection for TTS service
- Approximately 50MB disk space

### Dependencies
The package includes all required dependencies:
- `node-edge-tts` - Microsoft Edge TTS service wrapper
- `commander` - CLI argument parsing

## Installation Instructions

### Method 1: Direct Installation (Recommended)
```bash
# Clone or download the package
git clone https://github.com/clawdbot/edge-tts-skill.git
cd edge-tts-skill

# Install dependencies
npm install

# Test the installation
npm test
```

### Method 2: Manual Installation
```bash
# Create installation directory
mkdir -p /home/user/clawd/skills/public/edge-tts
cd /home/user/clawd/skills/public/edge-tts

# Copy package contents
cp -r /path/to/edge-tts-package/* .

# Install dependencies
npm install

# Run tests
npm test
```

## Usage

### Basic TTS
```javascript
// Simple TTS conversion
tts("Hello, world!")
```

### Advanced Usage
```bash
# Convert text with custom voice
node scripts/tts-converter.js "Hello, world!" --voice en-US-GuyNeural

# List available voices
node scripts/tts-converter.js --list-voices

# Configure default settings
node scripts/config-manager.js --set-voice en-US-AriaNeural
```

## Testing

### Package Validation
```bash
# Run package tests
npm test

# Verify voice list
node scripts/tts-converter.js --list-voices

# Test TTS conversion
node scripts/tts-converter.js "This is a test." --output test.mp3
```

## Voice Testing

Test different voices and preview audio quality at: https://tts.travisvn.com/

## Support

For issues and support, please contact the skill maintainer or visit the official documentation.

## License

MIT License - See LICENSE file for details.