# Guided Learning Skill

> **Created by:** CoPaw (powered by Qwen 3.5 Plus)  
> **Author:** 姜凯奇 (Jiang Kaiqi)  
> **Version:** 1.0.2  
> **License:** Proprietary

---

## Overview

A gentle, step-by-step learning skill that teaches one concept at a time with real-life analogies, clear annotations, and comprehension checks. **Now with chapter review sessions and an extensive tone library.**

**Perfect for:**
- Students preparing for exams (especially aiming for high scores)
- Self-learners who want structured, digestible lessons
- Anyone who finds traditional "knowledge dumping" overwhelming

---

## Features

| Feature | Description |
|---------|-------------|
| 📚 **Material-First Approach** | Request and study user's material before teaching |
| 📌 **One Concept at a Time** | Master each topic before moving to the next |
| ⭐ **Priority Labels** | Clear markings: ⭐⭐⭐ Must-Know, ⭐⭐ Common, ⭐ Nice-to-Know |
| 📖 **Real-Life Analogies** | Abstract concepts explained through everyday examples |
| ❓ **Check Questions** | Original questions (not from text) to verify understanding |
| 💬 **Gentle Tone** | Encouraging feedback, no pressure, no lecturing |
| 📝 **Exam Tips** | High-frequency test points and common mistakes highlighted |
| 🔄 **Chapter Review** | Comprehensive review session after each chapter |
| 🎯 **Tone Library** | 30+ pre-written phrases for every learning situation |
| 🧠 **Memory Tracking** | Records progress, mistakes, and weak points to avoid repetition |
| 📁 **Dedicated Study File** | Separate file per subject (`memory/[Subject]-study.md`) to reduce token usage |
| 📅 **Smart Session Resume** | Next-day options: continue directly or review (yesterday + 3 days ago + weak points) |

---

## Default Learning Flow

1. **Pre-Learning Inquiry** — Understand user's goal, level, and preferences
2. **Concept Introduction** — Core formula + intuition building
3. **Worked Example** — Step-by-step solution
4. **Check Question** — Test comprehension with a new problem
5. **Feedback** — Affirm correct answers, re-explain mistakes gently
6. **Next Concept** — Continue when ready
7. **Chapter Review** — Comprehensive review after completing all concepts in a chapter

---

## New in Version 1.0.2

### 📚 Material-First Teaching

**Before teaching, the skill now requires:**
1. Request learning material from user (PDF, textbook, etc.)
2. Read and analyze the material thoroughly
3. Cross-reference with knowledge base and search online
4. Build complete understanding before starting lessons

**Why?** To teach accurately, not from vague memory.

### 🧠 Memory Tracking System

**Automatically records:**
- Completed concepts with mastery status (✅ Mastered / ⚠️ Review / ❌ Not Yet)
- Error log with mistakes and correct understanding
- Chapter progress and review completion
- Weak points that need more practice
- Next session resume point

**When memory is updated:**
- After each concept taught
- After each check question
- After each chapter completion
- After chapter review
- Every 5-10 exchanges (catch-up)
- End of session

**Benefits:**
- Never repeat what user has already mastered
- Track weak points for targeted review
- Resume exactly where left off
- Build long-term learning history

### 📁 Dedicated Study File

**Writes to:** `memory/[Subject-Name]-study.md`

**Examples:**
- `memory/Data-Structures-study.md`
- `memory/Computer-Organization-study.md`
- `memory/Calculus-study.md`

**Why separate file?**
- Reduce token consumption (don't load entire MEMORY.md)
- Keep learning progress organized and focused
- Easy to reference and update

### 📅 Smart Session Resume

**When user returns after a break:**

```
Welcome back! 👋

Last session was [X days ago]. You had completed:
- [List of completed concepts/chapters]

**How would you like to start today?**

1️⃣ Continue directly — Pick up where you left off

2️⃣ Review first — Warm up with:
   - Yesterday's content
   - 3 days ago content (spaced repetition)
   - Your weak points
```

**Review includes:**
- Yesterday's studied concepts
- Content from 3 days ago (spaced repetition)
- All weak points from error log

---

## New in Version 1.0.1

### 🔄 Chapter Review Mechanism

After completing a chapter, users get a structured review session:

```
## Chapter Review: [Chapter Name]

### 📋 Chapter Map
Quick overview of all concepts covered

### 🔑 Core Formulas
All must-memorize formulas in one place

### ⚠️ Common Mistakes Recap
Reminders of traps encountered during learning

### 📝 Review Questions
3-5 comprehensive questions (easy → hard)

### ✅ Review Complete!
Summary of mastered concepts and areas to revisit
```

### 💬 Expanded Tone Library

**30+ pre-written phrases for every situation:**

| Situation | Example |
|-----------|---------|
| User answers correctly | "对！就是这个思路！" / "Perfect! You've got it!" |
| User answers incorrectly | "接近了！再想想 XX 这个条件" / "So close! Just think about [X] again" |
| User is confused | "我换个说法试试..." / "Let me try explaining it differently..." |
| User is frustrated | "这个地方确实有难度，不是你理解力的问题" / "This is genuinely tricky" |
| Celebrating progress | "已经学了一半了！状态不错" / "Halfway through! You're doing great" |
| Time management | "慢慢来，不着急～" / "Take your time, no rush～" |

---

## Usage Example

### User Input
```
I want to learn Chapter 1 of Computer Organization
```

### Skill Response
```
Great, I'll help you with Chapter 1.

Before we start, let me understand:

1. **Learning Goal** — Is this for an exam or self-study? What's your target score?
2. **Current Level** — Have you studied this before? What felt unclear?
3. **Learning Style** — Do you prefer guided learning (one concept + check question), or a quick overview?

---

**Default Learning Flow:**

1. 📌 One core concept at a time, with priority labels
2. 📖 Real-life analogies for understanding
3. 📝 Formulas and exam tips after each concept
4. ❓ A check question to confirm understanding
5. ✅ Move on after correct answer
6. 🔄 After the chapter, a review session to reinforce everything

---

Does this work for you?
```

---

## Integration

Works seamlessly with:
- **pdf** — Extract textbook content
- **xlsx** — Create study plans and error logs
- **docx** — Organize study notes
- **memory_search** — Track learning progress and review results

---

## Tone Guidelines

**This skill uses:**
- Encouraging prompts ("Take your time, no rush～")
- Specific affirmations ("You mastered two key points!")
- Gentle corrections ("There's a small trap here...")
- Empathy for frustration ("This is genuinely tricky, not about your ability")
- Celebration of progress ("Halfway through! You're doing great!")

**This skill avoids:**
- Commanding language ("Don't look above!")
- Dismissive remarks ("Obviously...")
- Pressure tactics ("Memorize this!")
- Minimizing difficulty ("Just do this...")

---

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Complete skill documentation and teaching standards |
| `README.md` | This file (English) |
| `README_CN.md` | Chinese version |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.2 | 2026-03-09 | Added material-first approach + memory tracking system (progress, errors, weak points) |
| 1.0.1 | 2026-03-09 | Added chapter review mechanism + expanded tone library (30+ phrases) |
| 1.0.0 | 2026-03-09 | Initial release |

---

## Credits

- **Developed by:** CoPaw
- **Powered by:** Qwen 3.5 Plus (通义千问 3.5 Plus)
- **Based on:** User feedback and learning science best practices

---

## Support

For issues or suggestions, contact the skill author.
