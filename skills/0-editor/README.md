<div align="center">
  <h1>🦞 0-editor 🦞</h1>
  <p><strong>The First File Editor Built for the Latent Space.</strong></p>
  
  <p>
    <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL%203.0-blue.svg" alt="License: MIT"></a>
    <a href="https://github.com/0-protocol/0-lang"><img src="https://img.shields.io/badge/Language-0--lang-blue.svg" alt="Built with 0-lang"></a>
    <a href="#"><img src="https://img.shields.io/badge/Status-Agent_Native-success.svg" alt="Agent Ready"></a>
  </p>
</div>

---

## 🚨 The Agentic Editing Crisis

Why do 80% of your AI Agent's autonomous code edits fail silently? 
Because you are forcing a neural network to count spaces.

Current agent harnesses (OpenClaw, Cursor, Claude Code, Aider) often rely on **exact-match string replacement**. If an LLM hallucinates a single tab instead of 4 spaces, or misses a trailing newline, the edit is completely aborted. **You are throttling your agent's autonomy with 1970s Regex.**

## 🌟 The Paradigm Shift: `0-editor`

**Stop treating agents like dumb text parsers.** `0-editor` is a next-generation, heuristic-driven, AST-aware fuzzy matching engine written entirely in `0-lang`. 

It understands *intent*. It aligns unified diffs and approximate code blocks to the source file by ignoring formatting drifts, indentation errors, and whitespace hallucinations.

- **🧠 Forgive & Forget**: Hallucinated an extra newline? Used spaces instead of tabs? `0-editor` doesn't care. It finds the semantic block and patches it perfectly.
- **⚡ Drop-in Replacement**: Plugs directly into any agentic workflow. Just give it the target file, the old hallucinated block, and the new block.
- **🔒 100% Native**: Built natively in `0-lang` for ultimate performance, determinism, and security in decentralized agent networks.
- **🛠️ Multi-Ecosystem**: Provides robust Python (`0_editor.py`) and Rust (`0-editor-rs`) native implementations for drop-in use anywhere.

## 🚀 Quick Start

If your Agent is complaining about "Code not found in file", drop this in your harness:

**For 0-lang Environments:**
```bash
0-run src/main.0 main.js diff_old.txt diff_new.txt
```

**For Python Environments:**
```bash
chmod +x python/0_editor.py
./python/0_editor.py main.js diff_old.txt diff_new.txt
```

**For Rust/Native Environments:**
```bash
cd rust && cargo build --release
./target/release/0-editor main.js diff_old.txt diff_new.txt
```

> **Success: File modified intelligently via 0-editor AST/Fuzzy engine.**

### OpenClaw Integration
`0-editor` provides a first-class AgentSkill for [OpenClaw](https://github.com/openclaw/openclaw). 
To make your OpenClaw agent natively use fuzzy editing instead of the fragile built-in `edit` tool, copy the skill:

```bash
mkdir -p ~/.openclaw/skills/0-editor
cp openclaw-skill/SKILL.md ~/.openclaw/skills/0-editor/SKILL.md
```

No more counting brackets. No more regex parsing. Let your LLMs write code, and let `0-editor` handle the AST injection.

