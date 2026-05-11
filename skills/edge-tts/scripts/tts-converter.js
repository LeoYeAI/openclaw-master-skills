#!/usr/bin/env node
/**
 * TTS Converter using node-edge-tts
 *
 * Converts text to speech using Microsoft Edge's online TTS service.
 * Supports multiple voices, languages, speeds, and output formats.
 *
 * Usage:
 *   node tts-converter.js "Your text here" --voice en-US-AriaNeural --rate +10% --output audio.mp3
 */

const { EdgeTTS } = require('node-edge-tts');
const { program } = require('commander');
const fs = require('fs/promises');
const path = require('path');
const os = require('os');

// Constants
const DEFAULT_TIMEOUT_MS = 10000;
const MAX_TEXT_LENGTH = 10000;
const TEMP_DIR = path.join(os.tmpdir(), 'edge-tts-temp');

// Default voice configurations
const DEFAULT_VOICES = {
  en: 'en-US-MichelleNeural',
  es: 'es-ES-ElviraNeural',
  fr: 'fr-FR-DeniseNeural',
  de: 'de-DE-KatjaNeural',
  it: 'it-IT-ElsaNeural',
  ja: 'ja-JP-NanamiNeural',
  zh: 'zh-CN-XiaoxiaoNeural',
  ar: 'ar-SA-ZariyahNeural',
};

/**
 * Validate prosody value (pitch, rate, volume)
 * @param {string} value - Value to validate
 * @returns {boolean} True if valid
 */
function validateProsodyValue(value) {
  if (value === 'default') return true;
  if (typeof value === 'string' && value.endsWith('%')) {
    const num = parseInt(value);
    return !isNaN(num) && num >= -100 && num <= 100;
  }
  return false;
}

/**
 * Ensure temp directory exists
 * @returns {Promise<void>}
 */
async function ensureTempDir() {
  try {
    await fs.access(TEMP_DIR);
  } catch (error) {
    await fs.mkdir(TEMP_DIR, { recursive: true });
  }
}

/**
 * Generate unique temporary file path
 * @param {string} extension - File extension (e.g., '.mp3')
 * @returns {string} Temporary file path
 */
function generateTempPath(extension = '.mp3') {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  const filename = `tts_${timestamp}_${random}${extension}`;
  return path.join(TEMP_DIR, filename);
}

/**
 * Convert text to speech
 * @param {string} text - Text to convert
 * @param {object} options - TTS options
 * @returns {Promise<string>} Path to generated audio file
 */
async function textToSpeech(text, options = {}) {
  const {
    voice,
    lang = 'en-US',
    outputFormat = 'audio-24khz-48kbitrate-mono-mp3',
    pitch = 'default',
    rate = 'default',
    volume = 'default',
    saveSubtitles = false,
    outputPath = null, // If null, use temp file
    proxy,
    timeout = DEFAULT_TIMEOUT_MS,
  } = options;

  // Validate input text
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    throw new Error('Text cannot be empty');
  }
  
  // Warn about very long text
  if (text.length > MAX_TEXT_LENGTH) {
    console.warn(`⚠  Warning: Text is very long (${text.length} characters), may cause issues`);
  }
  
  // Validate prosody values
  if (!validateProsodyValue(pitch)) {
    throw new Error(`Invalid pitch value: "${pitch}". Must be "default" or a percentage (e.g., "+10%", "-20%")`);
  }
  if (!validateProsodyValue(rate)) {
    throw new Error(`Invalid rate value: "${rate}". Must be "default" or a percentage (e.g., "+10%", "-20%")`);
  }
  if (!validateProsodyValue(volume)) {
    throw new Error(`Invalid volume value: "${volume}". Must be "default" or a percentage (e.g., "+10%", "-20%")`);
  }
  
  // Validate timeout
  if (timeout && timeout <= 0) {
    throw new Error(`Invalid timeout: ${timeout}. Must be a positive number`);
  }

  const finalVoice = voice || DEFAULT_VOICES[lang.split('-')[0]] || DEFAULT_VOICES.en;

  // Ensure temp directory exists and use temp file if no output path specified
  await ensureTempDir();
  const finalOutputPath = outputPath || generateTempPath('.mp3');

  // Filter out TTS-related words from text to avoid converting them to audio
  const ttsKeywords = ['tts', 'text-to-speech', 'text to speech'];
  const filteredText = text.split(/\s+/).filter(word => {
    const lowerWord = word.toLowerCase().replace(/[^\w\s-]/g, '');
    return !ttsKeywords.includes(lowerWord);
  }).join(' ');

  if (filteredText !== text.trim()) {
    console.log(`ℹ  Filtered TTS keywords from text: "${text}" -> "${filteredText}"`);
  }

  console.log(`Converting text to speech...`);
  console.log(`  Text: ${filteredText.substring(0, 50)}${filteredText.length > 50 ? '...' : ''}`);
  console.log(`  Voice: ${finalVoice}`);
  console.log(`  Language: ${lang}`);
  console.log(`  Rate: ${rate}`);
  console.log(`  Pitch: ${pitch}`);
  console.log(`  Volume: ${volume}`);

  try {
    // Create TTS instance with configuration
    const tts = new EdgeTTS({
      voice: finalVoice,
      lang,
      outputFormat,
      saveSubtitles,
      proxy,
      timeout,
      pitch,
      rate,
      volume,
    });

    // Synthesize speech
    await tts.ttsPromise(filteredText, finalOutputPath);

    // Check if file was created
    const stats = await fs.stat(finalOutputPath);
    console.log(`\n✓ Audio saved to: ${finalOutputPath}`);
    console.log(`✓ File size: ${stats.size} bytes`);

    if (saveSubtitles) {
      const subtitlePath = finalOutputPath.replace(/\.[^/.]+$/, '.json');
      try {
        const subStats = await fs.stat(subtitlePath);
        console.log(`✓ Subtitles saved to: ${subtitlePath}`);
        console.log(`✓ Subtitle size: ${subStats.size} bytes`);
      } catch (e) {
        console.log(`ℹ  No subtitles generated`);
      }
    }

    return finalOutputPath;
  } catch (error) {
    console.error('\n✗ Conversion failed:', error.message);
    throw error;
  }
}

/**
 * List available voices (shows common ones - full list available from Microsoft Edge service)
 */
function listVoices() {
  console.log('Common voices by language:\n');

  const voicesByLang = {
    'en': ['en-US-MichelleNeural', 'en-US-AriaNeural', 'en-US-GuyNeural', 'en-GB-SoniaNeural', 'en-GB-RyanNeural'],
    'es': ['es-ES-ElviraNeural', 'es-MX-DaliaNeural'],
    'fr': ['fr-FR-DeniseNeural', 'fr-FR-HenriNeural'],
    'de': ['de-DE-KatjaNeural', 'de-DE-ConradNeural'],
    'it': ['it-IT-ElsaNeural'],
    'ja': ['ja-JP-NanamiNeural'],
    'zh': ['zh-CN-XiaoxiaoNeural', 'zh-CN-YunyangNeural'],
    'ar': ['ar-SA-ZariyahNeural', 'ar-SA-HamedNeural'],
  };

  for (const [lang, voices] of Object.entries(voicesByLang)) {
    console.log(`${lang}:`);
    voices.forEach(v => console.log(`  ${v}`));
  }

  console.log('\nVoice name format: {lang}-{region}-{Name}{VoiceType}');
  console.log('Example: en-US-AriaNeural = English (US), Aria, Neural voice');
}

// CLI setup
program
  .argument('<text>', 'Text to convert to speech')
  .option('-v, --voice <voice>', 'Voice name (e.g., en-US-MichelleNeural)')
  .option('-l, --lang <language>', 'Language code (e.g., en-US, es-ES)', 'en-US')
  .option('-o, --format <format>', 'Output format (e.g., audio-24khz-48kbitrate-mono-mp3)', 'audio-24khz-48kbitrate-mono-mp3')
  .option('--pitch <pitch>', 'Pitch adjustment (e.g., +10%, -20%, default)', 'default')
  .option('-r, --rate <rate>', 'Rate adjustment (e.g., +10%, -20%, default)', 'default')
  .option('--volume <volume>', 'Volume adjustment (e.g., +0%, -50%, default)', 'default')
  .option('-s, --save-subtitles', 'Save subtitles as JSON file', false)
  .option('-f, --output <path>', 'Output file path (default: temp file in system temp dir)')
  .option('-p, --proxy <proxy>', 'Proxy URL (e.g., http://localhost:7890)')
  .option('--timeout <ms>', 'Request timeout in milliseconds', '10000')
  .option('-L, --list-voices', 'List available voices')
  .description('Convert text to speech using node-edge-tts')
  .version('2.0.0');

program.parse(process.argv);
const options = program.opts();
const text = program.args[0];

if (options.listVoices) {
  listVoices();
  process.exit(0);
}

if (!text) {
  console.error('Error: No text provided');
  console.log('Usage: node tts-converter.js "Your text" [options]');
  console.log('Run: node tts-converter.js --list-voices to see available voices');
  process.exit(1);
}

textToSpeech(text, {
  voice: options.voice,
  lang: options.lang,
  outputFormat: options.format,
  pitch: options.pitch,
  rate: options.rate,
  volume: options.volume,
  saveSubtitles: options.saveSubtitles,
  outputPath: options.output,
  proxy: options.proxy,
  timeout: parseInt(options.timeout),
}).catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});

module.exports = { textToSpeech, listVoices };