# RedNote Access Modes

Use this file when deciding how deep to go on a RedNote/Xiaohongshu task.

## Principle

The user should choose the access level.
Do not assume login by default.
Start in public-web mode unless the user explicitly wants deeper coverage and is willing to log in.

## Mode 1: Public-web mode (default)

Use when:
- the user wants a fast reputation check, trend scan, local recommendation scan, gossip synthesis, or weak-clue recovery
- the user does not want to log in
- the task can tolerate incomplete coverage

Capabilities:
- search-engine discovery
- public page fetching
- snippet/title/OCR/subtitle recovery
- cross-source verification
- structured claim extraction and concise reporting

Limits:
- weak coverage for cold accounts or newly posted content
- comment areas are often unavailable or incomplete
- user profile feeds may be inaccessible or thin
- public-web indexing can lag behind the app
- platform anti-bot controls may block direct browsing

Recommended phrasing:
- "I can do a public-web pass without login; coverage may be partial."
- "If you want fuller account-level or comment-level coverage, you can choose the login-enhanced mode."

## Mode 2: Login-enhanced mode (optional)

Use only when the user explicitly agrees to log in.

Use when:
- the user wants a fuller account summary
- the user wants recent posts from a specific account
- the user wants comment-area inspection
- public-web mode is too thin due to anti-bot, missing indexing, or cold-account visibility

What login changes:
- profile pages and recent posts are more likely to load fully
- note lists, media, and metadata may become inspectable
- comment and reaction patterns may become much easier to analyze
- browser automation can operate on a real authenticated session instead of a blocked public view

### Login path to offer the user

Present login as a choice, not a requirement.

Suggested explanation:
- "This skill supports two paths: public-web mode (no login, partial coverage) and login-enhanced mode (more complete coverage). If you want, you can log in inside the controlled browser session and I’ll use that session only for this research task."

Suggested workflow:
1. Explain the tradeoff between public-web mode and login-enhanced mode.
2. Ask whether the user wants to stay no-login or switch to login-enhanced mode.
3. If the user chooses login:
   - open the RedNote/Xiaohongshu site in the browser automation environment
   - let the user complete QR/code/password login themselves
   - wait for confirmation that login succeeded
   - continue research inside that authenticated browser session
4. If the user does not choose login, stay in public-web mode and proceed with explicit caveats.

## Safety and privacy notes

- Never force login.
- Never ask for the user’s password in chat when a normal site login flow is available.
- Prefer user-completed QR or site-native login flows inside the browser session.
- Treat the authenticated session as task-scoped and privacy-sensitive.
- Do not over-collect data just because login is available.
- State clearly when a finding depends on authenticated access versus public-web access.

## Decision rule

Choose the smallest sufficient access mode.

- If the user asks a broad question and public-web mode is enough, stay no-login.
- If the user asks for account-level completeness, recent-post coverage, or comments, offer login-enhanced mode.
- If public-web mode fails because of anti-bot or thin indexing, explicitly say login-enhanced mode is the next escalation path.

## Output note

When login-enhanced mode was used, say so briefly in the answer.
Example:
- "This summary is based on an authenticated in-app/browser review, so coverage is fuller than public-web search alone."

When public-web mode was used, say that too.
Example:
- "This summary is based on public-web evidence only; recent or low-visibility posts may be missing."