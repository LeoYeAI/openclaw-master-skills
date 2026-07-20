// ============================================================
// Afterself — Persona Manager (CLI)
// Analyzes message history to build a persona profile
// for Ghost Mode. Also provides RAG retrieval for the agent.
// ============================================================
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { appendAudit } from "./state.js";
const STATE_DIR = join(process.env.HOME || "~", ".afterself");
const PERSONA_FILE = join(STATE_DIR, "persona.json");
// -----------------------------------------------------------
// Persona Persistence
// -----------------------------------------------------------
export function loadPersona() {
    if (!existsSync(PERSONA_FILE)) {
        return {
            name: "",
            writingStyle: {
                formality: "mixed",
                averageMessageLength: "medium",
                usesEmoji: false,
                commonEmojis: [],
                commonPhrases: [],
                humor: "warm",
                punctuationStyle: "standard",
            },
            knownTopics: [],
            blockedTopics: [],
            sampleMessages: [],
            lastUpdated: new Date().toISOString(),
            messagesAnalyzed: 0,
        };
    }
    try {
        return JSON.parse(readFileSync(PERSONA_FILE, "utf-8"));
    }
    catch {
        return loadPersona(); // Return default
    }
}
export function savePersona(persona) {
    if (!existsSync(STATE_DIR)) {
        mkdirSync(STATE_DIR, { recursive: true, mode: 0o700 });
    }
    writeFileSync(PERSONA_FILE, JSON.stringify(persona, null, 2), { mode: 0o600 });
}
function analyzeMessages(existing, messages) {
    const allContent = messages.map((m) => m.content);
    return {
        ...existing,
        writingStyle: analyzeWritingStyle(allContent, existing.writingStyle),
        knownTopics: extractTopics(allContent, existing.knownTopics),
        sampleMessages: selectSampleMessages(messages, existing.sampleMessages),
        messagesAnalyzed: existing.messagesAnalyzed + messages.length,
        lastUpdated: new Date().toISOString(),
    };
}
function analyzeWritingStyle(messages, existing) {
    const avgLen = messages.reduce((sum, m) => sum + m.length, 0) / messages.length;
    const averageMessageLength = avgLen < 50 ? "short" : avgLen < 200 ? "medium" : "long";
    // Emoji usage
    const emojiRegex = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2702}-\u{27B0}]/gu;
    const emojiMessages = messages.filter((m) => emojiRegex.test(m));
    const usesEmoji = emojiMessages.length / messages.length > 0.15;
    // Common emojis
    const emojiCounts = {};
    for (const msg of messages) {
        const emojis = msg.match(emojiRegex) || [];
        for (const emoji of emojis) {
            emojiCounts[emoji] = (emojiCounts[emoji] || 0) + 1;
        }
    }
    const commonEmojis = Object.entries(emojiCounts)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([emoji]) => emoji);
    // Formality
    const casualIndicators = ["lol", "lmao", "haha", "omg", "nah", "yeah", "gonna", "wanna", "tbh"];
    const casualCount = messages.filter((m) => casualIndicators.some((ind) => m.toLowerCase().includes(ind))).length;
    const casualRatio = casualCount / messages.length;
    const formality = casualRatio > 0.3 ? "casual" : casualRatio > 0.1 ? "mixed" : "formal";
    // Common phrases (bigrams)
    const phraseCounts = {};
    for (const msg of messages) {
        const words = msg.toLowerCase().split(/\s+/);
        for (let i = 0; i < words.length - 1; i++) {
            const phrase = `${words[i]} ${words[i + 1]}`;
            if (phrase.length > 5) {
                phraseCounts[phrase] = (phraseCounts[phrase] || 0) + 1;
            }
        }
    }
    const commonPhrases = Object.entries(phraseCounts)
        .filter(([, count]) => count >= 3)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 20)
        .map(([phrase]) => phrase);
    // Punctuation style
    const exclamationRate = messages.filter((m) => m.includes("!")).length / messages.length;
    const questionRate = messages.filter((m) => m.includes("?")).length / messages.length;
    const ellipsisRate = messages.filter((m) => m.includes("...")).length / messages.length;
    let punctuationStyle = "standard";
    if (exclamationRate > 0.4)
        punctuationStyle = "enthusiastic (lots of !)";
    else if (ellipsisRate > 0.2)
        punctuationStyle = "trailing (uses ... often)";
    else if (questionRate > 0.3)
        punctuationStyle = "inquisitive (lots of ?)";
    return {
        formality,
        averageMessageLength,
        usesEmoji,
        commonEmojis,
        commonPhrases,
        humor: existing.humor,
        punctuationStyle,
    };
}
function extractTopics(messages, existing) {
    const stopWords = new Set([
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "both",
        "each", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "don", "should", "now", "i", "me", "my", "we", "you", "your", "he",
        "she", "it", "they", "them", "what", "which", "who", "this", "that",
        "these", "those", "am", "but", "if", "or", "because", "until", "while",
        "about", "get", "got", "like", "know", "think", "going", "want", "really",
        "yeah", "okay", "right", "good", "one", "also", "much", "even", "well",
    ]);
    const wordCounts = {};
    for (const msg of messages) {
        const words = msg.toLowerCase().replace(/[^\w\s]/g, "").split(/\s+/);
        for (const word of words) {
            if (word.length > 3 && !stopWords.has(word)) {
                wordCounts[word] = (wordCounts[word] || 0) + 1;
            }
        }
    }
    const newTopics = Object.entries(wordCounts)
        .filter(([, count]) => count >= 5)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 30)
        .map(([word]) => word);
    const merged = [...new Set([...existing, ...newTopics])];
    return merged.slice(0, 50);
}
function selectSampleMessages(messages, existing) {
    const personalityIndicators = [
        "!", "?", "haha", "lol", "love", "hate", "think", "feel",
        "honestly", "actually", "personally", "imo", "tbh",
    ];
    const scored = messages.map((m) => ({
        message: m,
        score: personalityIndicators.reduce((score, indicator) => score + (m.content.toLowerCase().includes(indicator) ? 1 : 0), 0) + (m.content.length > 30 && m.content.length < 300 ? 2 : 0),
    }));
    const topMessages = scored
        .sort((a, b) => b.score - a.score)
        .slice(0, 50)
        .map((s) => ({
        message: s.message.content,
        context: s.message.context,
        channel: s.message.channel,
        timestamp: s.message.timestamp,
    }));
    const merged = [...existing, ...topMessages];
    const seen = new Set();
    const deduped = merged.filter((m) => {
        if (seen.has(m.message))
            return false;
        seen.add(m.message);
        return true;
    });
    return deduped.slice(0, 100);
}
// -----------------------------------------------------------
// RAG: Retrieve Relevant Messages
// -----------------------------------------------------------
/**
 * Simple keyword-based retrieval for finding persona samples
 * relevant to an incoming message.
 */
function retrieveRelevant(query, samples, limit) {
    const queryWords = new Set(query.toLowerCase().replace(/[^\w\s]/g, "").split(/\s+/).filter((w) => w.length > 3));
    if (queryWords.size === 0) {
        return samples.slice(0, limit);
    }
    const scored = samples.map((sample) => {
        const sampleWords = sample.message.toLowerCase().split(/\s+/);
        const overlap = sampleWords.filter((w) => queryWords.has(w)).length;
        const contextOverlap = sample.context
            ? sample.context.toLowerCase().split(/\s+/).filter((w) => queryWords.has(w)).length
            : 0;
        return { sample, score: overlap * 2 + contextOverlap };
    });
    return scored
        .sort((a, b) => b.score - a.score)
        .slice(0, limit)
        .map((s) => s.sample);
}
// -----------------------------------------------------------
// CLI
// -----------------------------------------------------------
function output(data) {
    console.log(JSON.stringify({ ok: true, data }, null, 2));
}
function fail(message) {
    console.log(JSON.stringify({ ok: false, error: message }, null, 2));
    process.exit(1);
}
function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    switch (command) {
        case "load": {
            output(loadPersona());
            break;
        }
        case "status": {
            const persona = loadPersona();
            output({
                name: persona.name,
                messagesAnalyzed: persona.messagesAnalyzed,
                sampleCount: persona.sampleMessages.length,
                topicsCount: persona.knownTopics.length,
                lastUpdated: persona.lastUpdated,
                writingStyle: persona.writingStyle,
            });
            break;
        }
        case "analyze": {
            // Analyze messages from a JSON file
            // Expected format: array of { content, channel, timestamp, isFromUser, context? }
            const inputFlag = args.indexOf("--input");
            const inputFile = inputFlag !== -1 ? args[inputFlag + 1] : args[1];
            if (!inputFile) {
                fail("Usage: persona.ts analyze --input <file.json>");
                return;
            }
            const raw = readFileSync(inputFile, "utf-8");
            const messages = JSON.parse(raw);
            const userMessages = messages.filter((m) => m.isFromUser);
            if (userMessages.length === 0) {
                fail("No user messages found in input file");
                return;
            }
            const persona = loadPersona();
            const updated = analyzeMessages(persona, userMessages);
            savePersona(updated);
            appendAudit("ghost", "messages_collected", {
                newMessages: userMessages.length,
                totalAnalyzed: updated.messagesAnalyzed,
            });
            output({
                newMessages: userMessages.length,
                totalAnalyzed: updated.messagesAnalyzed,
                topics: updated.knownTopics.slice(0, 10),
                style: updated.writingStyle,
            });
            break;
        }
        case "retrieve": {
            // Retrieve relevant sample messages for a query
            const queryFlag = args.indexOf("--query");
            const query = queryFlag !== -1 ? args[queryFlag + 1] : args[1];
            if (!query) {
                fail("Usage: persona.ts retrieve --query \"text\"");
                return;
            }
            const limitFlag = args.indexOf("--limit");
            const limit = limitFlag !== -1 ? parseInt(args[limitFlag + 1], 10) : 10;
            const persona = loadPersona();
            const results = retrieveRelevant(query, persona.sampleMessages, limit);
            output(results);
            break;
        }
        case "set-name": {
            const name = args[1];
            if (!name) {
                fail("Usage: persona.ts set-name <name>");
                return;
            }
            const persona = loadPersona();
            persona.name = name;
            savePersona(persona);
            output({ name: persona.name });
            break;
        }
        case "set-humor": {
            const humor = args[1];
            const valid = ["dry", "playful", "sarcastic", "warm", "none"];
            if (!humor || !valid.includes(humor)) {
                fail(`Usage: persona.ts set-humor <${valid.join("|")}>`);
                return;
            }
            const persona = loadPersona();
            persona.writingStyle.humor = humor;
            savePersona(persona);
            output({ humor });
            break;
        }
        case "add-blocked-topic": {
            const topic = args[1];
            if (!topic) {
                fail("Usage: persona.ts add-blocked-topic <topic>");
                return;
            }
            const persona = loadPersona();
            if (!persona.blockedTopics.includes(topic)) {
                persona.blockedTopics.push(topic);
                savePersona(persona);
            }
            output({ blockedTopics: persona.blockedTopics });
            break;
        }
        case "remove-blocked-topic": {
            const topic = args[1];
            if (!topic) {
                fail("Usage: persona.ts remove-blocked-topic <topic>");
                return;
            }
            const persona = loadPersona();
            persona.blockedTopics = persona.blockedTopics.filter((t) => t !== topic);
            savePersona(persona);
            output({ blockedTopics: persona.blockedTopics });
            break;
        }
        default: {
            fail(`Unknown command: ${command}\n` +
                `Available commands: load, status, analyze, retrieve, set-name, set-humor, ` +
                `add-blocked-topic, remove-blocked-topic`);
        }
    }
}
// Only run CLI when this is the entry point
import { fileURLToPath } from "url";
if (process.argv[1] === fileURLToPath(import.meta.url)) {
    main();
}
