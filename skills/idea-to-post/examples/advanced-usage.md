# Advanced Usage Examples

This document demonstrates advanced usage scenarios of the `idea-to-post` skill, including information search integration, framework combination usage, multi-round dialogue optimization, etc.

---

## Example 1: Technical Topic Deep Expansion (with Information Search)

### User Input

```
Help me write a post about WebAssembly development prospects, make it professional
```

### Skill Execution Flow

**Step 1: Analyze and Recommend Framework**

```
Your input involves technical trend analysis, contains the keyword "prospects".
I recommend using 5W1H framework, combined with latest technical materials for deep analysis.
```

**Step 2: Smart Information Search**

```
Your topic involves professional technology, let me search related materials first...

🔍 Searching...
1. WebAssembly official documentation and technical specifications
2. 2024 WebAssembly development trend report
3. WebAssembly application cases and practices
4. Mainstream browser support for WebAssembly

✅ Search complete, organized following information:
- WebAssembly 2.0 specification has been released
- 2024 browser support rate reached 95%
- Performance close to native applications
- Main application scenarios: high-performance computing in browser, cloud functions, game engines
```

**Step 3: Interactive Questioning**

```
【Post Goal】
What's the main goal of this post?
A. Technical popularization, let more people know WebAssembly
B. Industry analysis, discuss technical trends
C. Practice sharing, share usage experience
D. Technical selection advice
```

(User selects: B. Industry analysis, discuss technical trends)

```
【Target Platform】
Which platform do you plan to publish on?
A. WeChat Official Account
B. Juejin/Zhihu
C. Twitter/Weibo
D. LinkedIn
```

(User selects: B. Juejin/Zhihu)

```

【Focus Area】
Based on search results, which aspect do you want to focus on?
A. Technical principles and characteristics
B. Application scenarios and cases
C. Performance advantage analysis
D. Future development trends
```

(User selects: D. Future development trends)

```

【Professional Depth】
How to handle technical depth?
A. Introductory popularization, accessible
B. Advanced discussion,面向 developers
C. Deep analysis, facing architects
```

(User selects: B. Advanced discussion, facing developers)

**Step 4: Generate Post**

```
Based on search information and your selections, here's the professional version post:
```

---

### Generated Result

#### Juejin/Zhihu Version (Professional Advanced)

```markdown
# WebAssembly 2024: Technology Evolution from Edge to Mainstream

## Preface

WebAssembly (Wasm) is no longer experimental technology, but is becoming the cornerstone of the Web platform. According to the latest data, in 2024 browser support for WebAssembly reached 95%, and mainstream frameworks and tools have integrated Wasm capabilities.

This article will analyze WebAssembly's development trends and future prospects.

## What: What is WebAssembly?

WebAssembly is a new code format that can run in modern web browsers. It has the following characteristics:

- **High performance**: Execution speed close to native applications
- **Security**: Runs in sandbox environment
- **Portability**: Cross-platform compatible
- **Language agnostic**: Supports C/C++/Rust/Go and other languages to compile

## Why: Why is WebAssembly increasingly important?

### 1. Performance Demand Growth

As web application complexity increases, JavaScript's performance bottleneck gradually appears. WebAssembly fills this gap, enabling high-performance computing tasks in the browser.

### 2. Ecosystem Maturity

- WebAssembly 2.0 specification has been released
- Toolchain increasingly complete (Emscripten, wasm-pack, etc.)
- Mainstream framework integration (React, Vue support Wasm components)

### 3. Application Scenario Expansion

According to MDN statistics, main application scenarios include:
- High-performance computing in browser (video/audio processing)
- Cloud functions and edge computing
- Game engine porting
- Cryptography operations

## Where: WebAssembly's Application Status

### Success Cases

**Figma**: Uses WebAssembly to achieve high-performance graphics editing in the browser

**AutoCAD Web**: Migrated desktop applications to the web platform

**Google Earth**: Achieves 3D Earth rendering in the browser

## How: How Can Developers Embrace WebAssembly?

### Learning Path

1. **Understand basic concepts**: Linear memory, modules, imports/exports
2. **Choose language**: Rust (recommended), C/C++, AssemblyScript
3. **Master toolchain**: Emscripten, wasm-bindgen
4. **Practice projects**: Start with simple computing-intensive tasks

### Practice Advice

```rust
// Simple Rust WebAssembly example
#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}
```

## Future: Future Development Trends

### 1. WASI (WebAssembly System Interface)

WASI enables WebAssembly to run outside the browser, entering server-side, edge computing and other fields.

### 2. Component Model

The component model being developed will make WebAssembly modules easier to compose and reuse.

### 3. Better Debugging Tools

Source mapping, browser DevTools integration are improving.

### 4. Multi-threading Support

Standardization of SharedArrayBuffer and atomic operations will bring better parallel computing capabilities.

## Conclusion

WebAssembly has grown from experimental technology to a core capability of the Web platform. For front-end developers, understanding and mastering WebAssembly will become an increasingly important skill.

**Recommended Reading:**
- [WebAssembly Official Documentation](https://webassembly.org/)
- [MDN WebAssembly Guide](https://developer.mozilla.org/zh-CN/docs/WebAssembly)
- [Rust and WebAssembly book](https://rustwasm.github.io/docs/book/)

---

**Reference Materials:**
1. WebAssembly 2.0 Specification, W3C, 2024
2. "The State of WebAssembly 2024", Mozilla Hacks
3. MDN Web Docs - WebAssembly
```

---

## Example 2: Product Promotion (AIDA Framework)

### User Input

```
Help me promote my new product: an AI writing assistant
```

### Skill Execution Flow

**Step 1: Analyze and Recommend Framework**

```
This is a product promotion scenario, contains "promotion" keyword.
I recommend using AIDA marketing framework to maximize conversion effect.
```

**Step 2: Search Market Information**

```
Let me search for AI writing assistant market information...

🔍 Searching...
1. AI writing assistant market scale and trends
2. Mainstream competitive product feature comparison
3. User pain points and demand analysis

✅ Search complete:
- AI writing market annual growth rate exceeds 30%
- User main pain points: Writing block, low efficiency, unstable quality
- Mainstream competitors: ChatGPT, Notion AI, Copy.ai
```

**Step 3: Interactive Questioning**

```
【Product Core Advantage】
What's your AI writing assistant's core advantage?
A. More professional domain knowledge
B. Better Chinese understanding
C. Cheaper pricing
D. Other (custom)

(User selects: B. Better Chinese understanding and A. More professional domain knowledge)

```

【Target User】
Who's your target user?
A. Content creators/self-media
B. Students/researchers
C. Marketing professionals/copywriters
D. Everyone who needs to write

(User selects: A. Content creators/self-media)

```

【Publishing Platform】
Mainly which platform to promote?
A. Xiaohongshu
B. WeChat Official Account
C. Weibo
D. Zhihu

(User selects: A. Xiaohongshu)

```

【Promotion Strategy】
What's the attractive offer for new users?
A. Free trial
B. Limited time discount
C. Give away credits
D. No offer, let product speak

(User selects: A. Free trial 7 days)

**Step 4: Generate Post**

```
Based on AIDA framework and market information, generating the following promotion copy:
```

---

### Generated Result

#### Xiaohongshu Version (AIDA Marketing Framework)

```markdown
【Title】🔥Writing Block? This AI Assistant Saved My Life!

---

📌 Writing is too hard!

Do you also encounter:
✗ Writing like squeezing toothpaste
✗ Can't think of attractive titles
✗ Content dry with no literary grace
✗ Daily struggle with updates

I used to be like this too, until I met it...💫

---

✨ It's xxx AI Writing Assistant!

Why is it different?

🎯 **Understands Chinese context**
Not stiff translation, but truly understands Chinese expression habits

📚 **Professional domain knowledge**
Technology, finance, life... can write professionally in all fields

⚡ **Second-level generation**
Input topic, 30 seconds to draft, goodbye writing blocks

---

💪 After using:

Before: Writing an article took 3 hours ⏰
Now: 30 minutes to produce viral content 🚀

Followers grew from 1000 to 10000+
Readings increased several times!

---

🎁 **Limited Time Offer**

First 100 users free trial for 7 days!
Only 50 spots left!

👇 Click link to claim now
[link]

---

#AIWriting #WritingTool #SelfMedia #ContentCreation #ProductivityTool
```

---

## Example 3: Deep Problem Analysis (5-Why Framework)

### User Input

```
I want to analyze why our company's user retention rate keeps failing to improve
```

### Skill Execution Flow

**Step 1: Analyze and Recommend Framework**

```
Your input involves problem root cause analysis, contains "why" keyword.
I recommend using 5-Why framework for deep analysis.
```

**Step 2: Interactive Questioning (Dynamic 5-Why)**

```
【Initial Problem】
What's the specific manifestation of low user retention rate?
A. Users register but don't come back
B. Users use a few times then leave
C. Paying users have low renewal rate
D. Other (custom)

(User selects: B. Users use a few times then leave)

```

【Why 1】Why do users leave after a few uses?
A. Can't find core function
B. Functions don't meet needs
C. Poor usage experience
D. Competitors are better

(User selects: A. Can't find core function)

```

【Why 2】Why can't they find core function?
A. Insufficient product guidance
B. Confusing interface design
C. Function entry too deep
D. Too professional terminology

(User selects: A. Insufficient product guidance)

```

【Why 3】Why insufficient product guidance?
A. Didn't make onboarding guidance
B. Guidance too complex to understand
C. Guidance coverage incomplete
D. Guidance design unreasonable

(User selects: B. Guidance too complex to understand)

```

【Why 4】Why is guidance too complex?
A. Try to teach too many functions at once
B. Too much text, no demonstration
C. Forced guidance can't be skipped
D. Confusing guidance logic

(User selects: A. Try to teach too many functions at once)

```

【Why 5】Why try to teach too many functions at once?
A. Want users to understand all value
B. Product manager requirement
C. Competitors all do it this way
D. Never questioned this approach

(User selects: D. Never questioned this approach)

**Step 3: Generate Analysis Report**

```
Based on 5-Why analysis, found the root cause.
Following is the complete analysis report:
```

---

### Generated Result

#### LinkedIn/WeChat OA Version (Deep Analysis)

```markdown
# Root Cause Analysis of Low User Retention Rate

## Problem: Users Leave After a Few Uses

### 5-Why Analysis

**Why 1: Why do users leave after a few uses?**
→ Because users can't find the core function

**Why 2: Why can't they find the core function?**
→ Because product guidance is insufficient

**Why 3: Why insufficient product guidance?**
→ Because guidance is too complex, users don't understand

**Why 4: Why is guidance too complex?**
→ Because we try to teach too many functions at once

**Why 5: Why try to teach too many functions at once?**
→ Because we never questioned the assumption that "we should comprehensively introduce the product" (root cause)

## Root Cause

**Not the user's problem, but our product philosophy problem.**

We assume "users need to understand all functions", but actually:
- New users have limited cognitive load
- Can only remember 3 points at a time
- They just want to quickly solve one problem

## Solution

### 1. Change Guidance Philosophy

From "comprehensive introduction" to "progressive disclosure"

### 2. Redesign Guidance

- First login: Only teach the 1 most core function
- Second login: Guide the second function
- On-demand guidance: Prompt when user encounters problems

### 3. A/B Testing

Test different guidance solutions' effects

## Expected Results

- Guidance completion rate: from 30% to 60%
- Day 1 retention: from 40% to 55%
- Day 7 retention: from 20% to 35%

## Insight

Sometimes the problem isn't with users, but with our assumptions.
Question "taken for granted", to find the real solution.

---

#productAnalysis #userRetention #productDesign #rootCauseAnalysis
```

---

## Example 4: Multi-Round Dialogue Optimization

### First Round Dialogue

**User:** Help me write a post about remote work

**Skill:** Recommend using PREP framework, generate first version...

**User:** Feel it's not persuasive enough, can you add some data?

### Second Round Dialogue

**Skill:** Let me search for some remote work data...

🔍 Searching...
- Remote work efficiency research
- Remote work statistics
- Company remote work cases

**Skill:** Based on search data, regenerating version...

### Third Round Dialogue

**User:** Style too serious, can you make it more lighthearted?

**Skill:** Adjusting to lighthearted humorous style...

---

## Advanced Techniques

### 1. Framework Combination Usage

**Golden Circle + FBA**: Clearly explain philosophy, then introduce product

**5-Why + First Principles**: Find root cause, then reconstruct solution

**AIDA + PREP**: First attract attention, then express viewpoint

### 2. Information Search Techniques

- Providing more context can get more precise search results
- Can proactively specify search direction
- Search results can request presentation format (data/cases/trends)

### 3. Multi-Platform Adaptation

- Generate once, multiple versions
- Clearly specify main platform, skill will optimize that platform version
- Can request specific platform format

### 4. Iterative Optimization

- Continue adjusting based on generation results
- Propose specific modification requests
- Can request "more X" (more professional/more humorous/more concise)

---

## Usage Suggestions

1. **Provide more context** - Target audience, publishing platform, style preferences

2. **Utilize search function** - Technical/professional content can be greatly enriched

3. **Multi-round dialogue optimization** - Don't expect perfection in one go, gradually adjust

4. **Specify framework** - If you know what framework to use, can directly specify

5. **Clarify platform** - Different platforms have big differences, clarify target platform

---

## More Examples

See `basic-usage.md` for more basic examples.
