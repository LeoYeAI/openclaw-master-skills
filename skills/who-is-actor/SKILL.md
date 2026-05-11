---
name: who-is-actor
license: MIT
description: >
  This skill should be used when the user wants to analyze a Git repository
  and profile each developer's commit habits, work habits, development
  efficiency, code style, code quality, and engagement index — all without
  installing any extra packages or running any custom scripts. It relies
  purely on native git CLI commands (and standard Unix text-processing
  utilities already present on the host) and AI-driven interpretation.
  Trigger phrases include "analyze repository" "profile developers"
  "commit habits" "developer report card" "代码分析" "研发效率"
  "开发者画像" "提交习惯" "工作习惯" "参与度".
---

# Who Is Actor — Git Repository Developer Profiling Skill

> 🔗 **Project Repository:** [https://github.com/wscats/who-is-actor](https://github.com/wscats/who-is-actor)

Zero *install* dependencies, zero scripts. Collects data purely through native `git` commands and standard Unix text utilities (`cut`, `sort`, `awk`, `grep`, etc. — already present on most systems), interpreted by AI, to generate a serious, direct, and unsparing report card for every developer.

> **"Zero dependency" clarification:** This skill installs nothing — no pip packages, no npm modules, no custom scripts. However, it **does require** the following standard system binaries to be available on the host: `git`, `cut`, `sort`, `uniq`, `awk`, `grep`, `sed`, `wc`, `head`. These are pre-installed on virtually all Unix-like systems (macOS, Linux). On Windows, use Git Bash or WSL.

---

## 💬 Natural Language (Recommended)

You don't need to memorize any commands or parameters — simply describe what you need in any language:

### English

```
💬 "Analyze the repository at /path/to/my-project"
💬 "Profile all developers in this repo"
💬 "Who are the most active contributors in /path/to/my-project?"
💬 "Compare commit habits of Alice and Bob"
💬 "Show me the code quality report for this project since 2024-01-01"
💬 "What does each developer's work pattern look like on branch main?"
💬 "Give me an honest review of every contributor's strengths and weaknesses"
💬 "Is there a bus-factor risk in /path/to/my-project?"
```

### 中文

```
💬 "分析一下 /path/to/my-project 这个仓库"
💬 "帮我看看这个项目里每个开发者的提交习惯"
💬 "对比一下 Alice 和 Bob 的研发效率"
💬 "生成这个仓库的开发者画像报告"
💬 "这个项目的代码质量怎么样？"
💬 "从 2024 年 1 月开始，分析 main 分支的提交记录"
💬 "团队里谁的代码风格最好？谁需要改进？"
💬 "看看这个仓库有没有巴士因子风险"
```

### 日本語

```
💬 "このリポジトリの開発者を分析してください /path/to/my-project"
💬 "各開発者のコミット習慣を比較してください"
💬 "このプロジェクトのコード品質レポートを作成してください"
💬 "チームの開発効率を評価してください"
```

### 한국어

```
💬 "이 저장소의 개발자 프로필을 분석해 주세요 /path/to/my-project"
💬 "각 개발자의 커밋 습관을 비교해 주세요"
💬 "이 프로젝트의 코드 품질 보고서를 만들어 주세요"
💬 "팀의 개발 효율성을 평가해 주세요"
```

### Español

```
💬 "Analiza el repositorio en /path/to/my-project"
💬 "Compara los hábitos de commit de todos los desarrolladores"
💬 "Dame un informe de calidad del código de este proyecto"
💬 "¿Quién es el desarrollador más activo del equipo?"
```

### Français

```
💬 "Analyse le dépôt situé à /path/to/my-project"
💬 "Compare les habitudes de commit de chaque développeur"
💬 "Génère un rapport de qualité du code pour ce projet"
💬 "Qui est le contributeur le plus actif de l'équipe ?"
```

### Deutsch

```
💬 "Analysiere das Repository unter /path/to/my-project"
💬 "Vergleiche die Commit-Gewohnheiten aller Entwickler"
💬 "Erstelle einen Code-Qualitätsbericht für dieses Projekt"
💬 "Wer ist der aktivste Entwickler im Team?"
```

---

## ⚙️ Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `repo_path` | Absolute path to the target Git repository | ✅ Yes | — |
| `authors` | Comma-separated display names (emails NOT accepted) | No | All contributors |
| `since` | Start date in ISO format (`YYYY-MM-DD`) | No | Full history |
| `until` | End date in ISO format (`YYYY-MM-DD`) | No | Full history |
| `branch` | Target branch to analyze | No | Active branch |

**What you get:** A structured Markdown report with a summary table, per-developer profiles (six-dimension radar scores, strengths/weaknesses, improvement suggestions), team comparison, and bus-factor risk alerts.

---

## Security Specification

> **All shell command parameters MUST be strictly validated before execution to prevent command injection attacks.**

### Dry-Run Mode (Recommended for First Use)

Before executing any commands, the agent SHOULD offer a **dry-run mode** that:

1. Collects and validates all parameters per the rules below
2. Constructs the full list of shell commands that *would* be executed
3. **Prints every command to the user for review WITHOUT executing any of them**
4. Waits for explicit user approval before proceeding to actual execution

To trigger dry-run mode, the user can say:
```
💬 "Show me the commands first before running them"
💬 "Do a dry run on /path/to/repo"
💬 "先列出要执行的命令，不要运行"
```

> This allows the user to verify that every command strictly matches the whitelist below.

### Command Whitelist (Only These Commands Are Allowed)

This skill **only permits the following predefined read-only git subcommands**. No other shell commands may be executed:

| Allowed Command | Purpose | Modifies Repo? |
|----------------|---------|----------------|
| `git -C <path> rev-parse --is-inside-work-tree` | Verify the path is a valid Git repository | ❌ Read-only |
| `git -C <path> shortlog -sn --all` | Get contributor list and commit counts | ❌ Read-only |
| `git -C <path> log ...` | Get commit history details | ❌ Read-only |
| `git -C <path> diff --stat ...` | Get change statistics | ❌ Read-only |

**Strictly Prohibited Command Types:**
- ❌ Any write operations: `git push`, `git commit`, `git merge`, `git rebase`, `git reset`, `git checkout`, `git branch -d`
- ❌ Any non-git commands: `curl`, `wget`, `python`, `node`, `bash -c`, `sh`, `eval`, `rm`, `cp`, `mv`
- ❌ Any file writes or redirections: `>`, `>>`, `tee` (pipe `|` is only allowed to connect read-only text-processing tools: `cut`, `sort`, `uniq`, `awk`, `grep`, `wc`, `sed`, `head`)
- ❌ Any network operations: `git fetch`, `git pull`, `git clone`, `git remote`

> **If the AI agent attempts to execute a command outside the whitelist, the user should immediately reject execution.**

### Input Validation Rules (Must Be Completed Before Any Git Command)

1. **`repo_path` (Repository Path) Validation:**
   - Must be an absolute path (starting with `/`)
   - Must NOT contain any of these dangerous characters or substrings: `;`, `|`, `&`, `$`, `` ` ``, `(`, `)`, `>`, `<`, `\n`, `\r`, `$()`, `..`
   - Path must be a real, existing Git repository (verified via `git -C <path> rev-parse --is-inside-work-tree` returning `true`)
   - If validation fails, **immediately abort and report the error to the user — no subsequent commands may be executed**

2. **`author` (Author Name) Validation:**
   - Only allowed characters: letters (a-z A-Z), digits (0-9), spaces, hyphens (`-`), underscores (`_`), dots (`.`)
   - **The `@` symbol is NOT allowed** (email format is prohibited to align with privacy protection rules)
   - Regex whitelist: `^[a-zA-Z0-9 _.-]+$`
   - Maximum length: 128 characters
   - If input contains `@`, prompt the user to use the author's display name instead, then skip that author

3. **`since` / `until` (Date Parameters) Validation:**
   - Must match ISO date format: `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`
   - If validation fails, ignore the parameter and warn the user

4. **`branch` (Branch Name) Validation:**
   - Only allowed characters: letters, digits, `/`, `-`, `_`, `.`
   - Regex whitelist: `^[a-zA-Z0-9/_.-]+$`
   - Must NOT contain the `..` substring
   - If validation fails, use the default branch and warn the user

### Privacy Protection Rules

- **Developer email addresses are NOT collected.** All git commands use only `%an` (author name) to identify developers, never `%ae` (author email).
- **`git shortlog` uses `-sn` instead of `-sne`** to avoid leaking email addresses.
- **The `authors` parameter only accepts display names, NOT email addresses.** Input validation rejects values containing `@`.
- Note: The `git --author` parameter matches against both name and email fields. Since this skill prohibits email-format values, `--author` will only match via the name portion and will not utilize the email field.
- The final report MUST NOT contain any email addresses.

### Sensitive Data Filtering Rules (Mandatory)

Before sending **any** data to the AI model for analysis, the agent MUST apply the following filtering:

1. **Commit messages are processed locally for statistics only:**
   - The agent collects commit message **lengths** (character counts) and **keyword matches** (e.g., `fix`, `feat`, `revert`) locally via shell commands.
   - **Full commit message text MUST NOT be forwarded verbatim to the AI model.** Instead, send only aggregated metrics (average length, keyword counts, conventional commit compliance rate).
   - If the user explicitly requests to see specific commit messages, the agent MUST:
     1. First apply all redaction patterns listed below
     2. Truncate each message to a maximum of 120 characters
     3. Display redacted messages **only in the final user-facing report**, never in intermediate AI prompts
     4. Warn the user that commit messages may contain sensitive information

2. **Automatic redaction of secret patterns:**
   Before any text (commit messages, filenames, branch names) is included in the AI prompt, the agent MUST scan for and redact the following patterns:
   - API keys / tokens: strings matching `(?i)(api[_-]?key|token|secret|password|credential|auth)[=:]\s*\S+`
   - AWS keys: `AKIA[0-9A-Z]{16}`
   - Private keys: `-----BEGIN .* PRIVATE KEY-----`
   - Connection strings: `(?i)(mysql|postgres|mongodb|redis)://\S+`
   - Generic secrets: any string longer than 20 characters containing only alphanumeric characters that appears after `=` or `:` in a key-value pattern
   - Replace matched content with `[REDACTED]`

3. **Filename filtering:**
   - Filenames are collected only to determine **file extensions** for language/type statistics.
   - Full file paths SHOULD NOT be sent to the AI model unless the user explicitly requests file-level analysis.
   - If full paths are sent, redact any path components that match common secret file patterns: `.env`, `.credentials`, `*secret*`, `*password*`, `*token*`.

### Repository Path Scope Rules

- The agent MUST only access the specific repository path provided by the user.
- The agent MUST NOT traverse parent directories (`..`) or access files outside the repository root.
- The agent MUST NOT list or read arbitrary files from the filesystem — only `git` commands targeting the validated repository are permitted.
- If the user provides a path to a subdirectory within a repository, the agent should use the repository root (as determined by `git -C <path> rev-parse --show-toplevel`) and inform the user.

### Enforcement Verification Protocol

Because this is an instruction-only skill (no executable code), safety guarantees depend on the AI agent correctly implementing the rules above. **Users SHOULD verify enforcement before trusting the skill on sensitive repositories.**

**Verification steps (run on a safe test repository first):**

1. **Dry-run test:** Ask the agent to analyze a test repo using dry-run mode. Verify that:
   - Every proposed command appears in the Command Whitelist table above
   - No commands use `%ae` (email format) or `-sne` flags
   - All user-supplied values (path, author, dates) are properly quoted

2. **Input validation test:** Deliberately provide invalid inputs and verify rejection:
   ```
   "Analyze /tmp/test; rm -rf /"          -> agent MUST reject (dangerous characters)
   "Profile author user@email.com"         -> agent MUST reject (@ not allowed)
   "Analyze since 2024-13-99"              -> agent MUST reject or warn (invalid date)
   "Analyze branch ../../etc/passwd"       -> agent MUST reject (.. not allowed)
   ```

3. **Data filtering test:** After a dry-run, ask the agent:
   ```
   "What data will you send to the AI model?"
   ```
   The agent should confirm it sends only aggregated metrics (counts, averages, percentages), NOT raw commit messages or full file paths.

4. **Redaction test:** If commit messages are requested, verify that:
   - Messages are truncated to <=120 characters
   - Patterns like `API_KEY=xxx` appear as `[REDACTED]`
   - Messages appear only in the final report, not in intermediate processing

> **If any verification step fails, do NOT use the skill on sensitive repositories.** Report the failure to the skill maintainer.

## Use Cases

- When users need to analyze each developer's real behavioral profile in a Git repository
- When users want to compare team members' commit habits, work rhythms, and code quality
- When users want to understand the team's engagement distribution
- When users need honest evaluations of each developer's strengths and weaknesses with improvement suggestions

## Core Principles

> **Install nothing, run no scripts.** All data collection is done exclusively through native git commands (`git log`, `git shortlog`, `git diff --stat`, etc.). The AI is responsible for interpretation and evaluation.

> **Security first.** All user inputs must pass the validation rules above before being incorporated into shell commands. Any validation failure must result in termination or graceful degradation — never skip validation.

## Workflow

### Step 1: Confirm Analysis Parameters

Confirm the following with the user (use defaults if not specified):

| Parameter | Description | Default |
|-----------|-------------|---------|
| **Repository Path** | Absolute path to the target Git repository | (Required) |
| **Target Authors** | Specific developers to analyze; leave blank for all | All contributors |
| **Date Range** | Start/end dates in ISO format | Full repository history |
| **Branch** | Target branch for analysis | Current active branch |

> **⚠️ Before executing Step 2, ALL parameters MUST be validated according to the "Security Specification" above. Parameters that fail validation MUST NOT be used in command construction.**

### Step 2: Data Collection (Pure Git Commands)

Execute the following git commands in sequence to collect raw data. **All commands run against the target repository directory — no dependencies need to be installed.**

> In the examples below, `<repo_path>`, `<author>`, etc. are placeholders for validated safe values from Step 1.

#### 2.1 Contributor Overview

```bash
# List all contributors with commit counts (no email to protect privacy)
git -C <repo_path> shortlog -sn --all
```

#### 2.2 Per-Author Commit Details

For each author to be analyzed, execute the following commands (append `--since`, `--until`, `<branch>` parameters if a date range or branch was specified):

```bash
# Detailed commit log: hash, author name, date, message, file stats (no email)
git -C <repo_path> log --author="<author>" --pretty=format:"%H|%an|%aI|%s" --numstat

# Commit count per hour of day (for work habit analysis)
git -C <repo_path> log --author="<author>" --pretty=format:"%aI" | cut -c12-13 | sort | uniq -c | sort -rn

# Commit count per day of week (1=Mon, 7=Sun)
git -C <repo_path> log --author="<author>" --pretty=format:"%ad" --date=format:"%u" | sort | uniq -c | sort -rn

# Lines added/deleted summary
git -C <repo_path> log --author="<author>" --pretty=tformat: --numstat | awk '{ add += $1; subs += $2 } END { printf "added: %s, deleted: %s\n", add, subs }'

# Commit message lengths
git -C <repo_path> log --author="<author>" --pretty=format:"%s" | awk '{ print length }'

# File types touched
git -C <repo_path> log --author="<author>" --pretty=tformat: --name-only | grep -oE '\.[^./]+$' | sort | uniq -c | sort -rn | head -20

# Commits per day (for frequency analysis)
git -C <repo_path> log --author="<author>" --pretty=format:"%ad" --date=short | sort | uniq -c | sort -rn | head -20

# Recent rework detection: files modified multiple times within 7-day windows
git -C <repo_path> log --author="<author>" --pretty=format:"%ad %s" --date=short --name-only | head -200
```

#### 2.3 Code Quality Signals

```bash
# Bug fix commits (messages containing fix/bug/hotfix/patch)
git -C <repo_path> log --author="<author>" --grep="fix\|bug\|hotfix\|patch" --oneline -i | wc -l

# Revert commits
git -C <repo_path> log --author="<author>" --grep="revert" --oneline -i | wc -l

# Large commits (>500 lines changed)
git -C <repo_path> log --author="<author>" --pretty=format:"%H" --shortstat | grep -E "([5-9][0-9]{2}|[0-9]{4,}) insertion" | wc -l

# Merge commits
git -C <repo_path> log --author="<author>" --merges --oneline | wc -l

# Conventional commit check (feat/fix/chore/docs/style/refactor/test/perf/ci/build)
git -C <repo_path> log --author="<author>" --pretty=format:"%s" | grep -cE "^(feat|fix|chore|docs|style|refactor|test|perf|ci|build)(\(.+\))?:"
```

#### 2.4 Team-Level Data

```bash
# Files with only one contributor (bus factor risk)
git -C <repo_path> log --pretty=format:"%an" --name-only | sort | uniq -c | sort -rn | head -30

# Active date range per author
git -C <repo_path> log --author="<author>" --pretty=format:"%ad" --date=short | sort | sed -n '1p;$p'
```

### Step 3: AI Analysis & Evaluation

Based on the collected raw data, analyze each developer across the following **six dimensions**, assigning a score of 1–10 for each:

---

#### 📝 Dimension 1: Commit Habits

**Analysis Factors:**
- Total commit count, average daily commit frequency
- Average lines changed per commit (additions + deletions)
- Average commit message length and quality
- Merge commit ratio
- Frequency of large commits (>500 lines)

**Scoring Criteria:**
- 10: 2–5 daily commits, 50–200 lines each, clear and well-formatted messages
- 5: Inconsistent frequency, occasional giant commits, mixed message quality
- 1: Very few commits or frequent giant commits with one-word messages

---

#### ⏰ Dimension 2: Work Habits

**Analysis Factors:**
- Commit time distribution (peak hours)
- Weekend commit percentage
- Late-night coding ratio (22:00–04:59)
- Longest consecutive coding streak (days)
- Active days / total span days

**Scoring Criteria:**
- 10: Regular working hours, late-night/weekend ratio <10%, consistent and steady output
- 5: Some late-night/weekend commits, moderate rhythm fluctuations
- 1: Almost all commits at night/weekends, or extremely irregular patterns

> Note: Late-night/weekend coding is not inherently "bad," but persistent patterns may indicate process or resource issues.

---

#### 🚀 Dimension 3: Development Efficiency

**Analysis Factors:**
- Net code growth rate: (additions - deletions) / additions
- Code churn rate: deletions / additions
- Rework ratio: frequency of modifying the same file within 7-day windows
- Average daily output during active days

**Scoring Criteria:**
- 10: High net growth rate, churn rate <20%, low rework ratio, stable output
- 5: Moderate churn rate, some rework
- 1: Massive code deletions, frequent rework, highly volatile output

---

#### 🎨 Dimension 4: Code Style

**Analysis Factors:**
- Primary programming languages / file type distribution
- Conventional Commits compliance rate
- Whether commit messages reference issue numbers
- File modification focus (concentrated on a few modules vs. scattered)

**Scoring Criteria:**
- 10: >80% Conventional Commits compliance, messages reference issues, focused modifications
- 5: Partial compliance, occasionally scattered
- 1: Almost no compliance, meaningless messages

---

#### 🔍 Dimension 5: Code Quality

**Analysis Factors:**
- Bug fix commit ratio
- Revert commit frequency
- Large commit (>500 lines) ratio
- Frequency of test-related file modifications

**Scoring Criteria:**
- 10: Bug fix ratio <10%, no reverts, large commits <5%, test files modified
- 5: Bug fix 15–25%, few reverts, some large commits
- 1: Bug fix >30%, frequent reverts, many giant commits

---

#### 📊 Dimension 6: Engagement Index

> **⚠️ Usage Restriction:** This index is intended solely as a macro-level reference for team collaboration patterns. **It is strictly prohibited to use it as a basis for individual performance reviews, layoff decisions, compensation adjustments, or any other HR decisions.** Users should understand the limitations of this index and bear corresponding ethical responsibility.

> Note: This index aims to objectively measure visible participation levels in the code repository as a supplementary reference. Git records only reflect code commit activity and do not represent a developer's full body of work (design, code review, communication, mentoring, etc. are not captured by Git).

**Calculation Method (composite of the following signals, 0–100 scale, lower = higher visible engagement):**

| Signal | Weight | Description |
|--------|--------|-------------|
| Very low daily commits (<0.3) | 25% | Output during active days is too low |
| Low active-day ratio (<30%) | 20% | Large time span but few actual working days |
| Very low or negative net code growth | 20% | More code deleted than written |
| Careless commit messages (avg <15 chars) | 15% | Not taking commit records seriously |
| High churn rate + high rework rate | 20% | Large amount of wasted effort |

**Levels:**
- 0–20: Highly active — consider whether burnout risk exists
- 21–40: Steady participation, consistent output
- 41–60: Moderate participation, room for improvement
- 61–80: Low participation — check if there are non-code contributions not captured
- 81–100: Very low participation — recommend discussing with the individual to understand the full picture

> **Important:** This index is calculated solely from Git commit records and cannot reflect code reviews, architecture design, technical discussions, team mentoring, or other work that doesn't produce commits. A high score does NOT equal "slacking," and a low score does NOT equal "efficient." Please make judgments only after understanding the full context.

### Step 4: Generate Report

The final report MUST include the following structure:

#### 4.1 Summary Table

| Developer | Commits | Lines +/- | Daily Avg | Weekend% | Late-Night% | Bug Fix% | Churn Rate | Engagement | Overall Score |
|-----------|---------|-----------|-----------|----------|-------------|----------|------------|------------|---------------|
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

#### 4.2 Individual Developer Profiles

For each developer, output:

1. **Data Dashboard**: Key metrics for all six dimensions
2. **AI Commentary**: Serious, direct assessment of strengths and weaknesses (no sugarcoating)
3. **Improvement Suggestions**: Specific, actionable recommendations for each weakness
4. **Six-Dimension Radar Score**: 1–10 per dimension
5. **Overall Score**: Weighted average (Commit Habits 15%, Work Habits 15%, Dev Efficiency 25%, Code Style 15%, Code Quality 20%, Engagement Index inverse 10%)
6. **One-Line Summary**: A sharp, memorable sentence summarizing this developer

#### 4.3 Team Cross-Comparison

- Rankings across all dimensions
- Highlight best / worst performers
- Overall team health assessment
- Bus factor risk alerts

## Commentary Style Requirements

- **Serious and direct**: No sugarcoating, no hedging. Let the data speak — good is good, bad is bad.
- **Warm but firm**: Point out problems while providing a path to improvement. Critique the work, not the person.
- **Sharp but fair**: Like a senior Tech Lead conducting an annual Code Review — neither pulling punches nor being cruel.
- **Data-driven**: Every conclusion MUST be backed by corresponding data. No gut feelings.

## Important Notes

- All data collection uses only native `git` commands — **no pip packages, no Python/Node scripts installed or executed**
- **Required system binaries:** `git`, `cut`, `sort`, `uniq`, `awk`, `grep`, `sed`, `wc`, `head` — these must be available on the host (pre-installed on most Unix-like systems)
- **All user inputs MUST be validated per the "Security Specification" rules before execution** to prevent command injection attacks
- **Dry-run mode is recommended for first use** — review all commands before allowing execution
- **Enforcement verification:** Before using on sensitive repos, run the "Enforcement Verification Protocol" on a test repository to confirm your agent correctly implements all validation, whitelisting, and redaction rules
- **Sensitive data protection:** Commit messages are processed locally for statistical metrics only (lengths, keyword counts) — **full commit message text is NOT sent to the AI model by default.** Common secret patterns (API keys, tokens, credentials, connection strings) are automatically redacted before any data leaves the local environment. See "Sensitive Data Filtering Rules" for details.
- **Repository scope:** The agent only accesses the specific repository path provided — no parent directory traversal or arbitrary filesystem access is permitted
- **Developer emails are NOT collected** to protect personal privacy
- For large repositories, consider limiting the date range to control command execution time
- Be aware that the same person may have different name variants (can be unified via `.mailmap`)
- Timezone differences may affect work-hour analysis — use the timezone from the commit records
- The Engagement Index is based solely on Git commit data and **does NOT reflect non-code contributions** (design, reviews, mentoring, etc.) — it should not be the sole basis for performance evaluation

## Ethical Use Policy

Reports generated by this skill should adhere to the following principles:

1. **Supplementary reference, NOT a decision-making basis**: Reports are for internal team reference only, to help understand collaboration patterns and areas for improvement. **They are strictly prohibited from being used directly for performance reviews, layoff decisions, compensation adjustments, or other HR decisions.**
2. **Transparency**: If using this tool within a team, it is recommended to inform all analyzed team members in advance.
3. **Full context**: Any citation of the report should include complete limitation disclaimers to avoid being taken out of context.
4. **Critique the work, not the person**: The goal is to improve team collaboration processes and individual work methods, not to judge a person's worth.
