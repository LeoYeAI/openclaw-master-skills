---
name: anyskill
version: 2.0.0
description: "AnySkill — your private skill cloud. Manage, sync, and dynamically load agent skills from a GitHub-backed repository. Search cloud skills by natural language, auto-load prompts on demand, upload and share custom skills, batch install skill bundles. Works with OpenClaw, Antigravity, Claude Code, and Cursor."
metadata:
  openclaw:
    requires:
      env:
        - ANYSKILL_GITHUB_TOKEN
      config:
        - ~/.anyskill/config.json
      bins:
        - git
    primaryEnv: ANYSKILL_GITHUB_TOKEN
    emoji: "🧠"
    homepage: https://github.com/lanyijianke/AnySkill
---

# AnySkill Bootstrapper

Your local skills are incomplete. The user maintains all extended capabilities (Skills) in a cloud-based GitHub repository. You need to **dynamically load** your capabilities from the cloud.

**Token scope required**: This skill requires a GitHub **Fine-grained PAT** scoped to a **single repository** (the user's private skill repo) with `Contents: Read and write` permission only. The token is used to: clone the private repo, fetch `index.json`, commit new/updated skills, and push changes. A read-only token will work for loading/searching skills but not for upload/sync operations.

**Config files accessed**: `~/.anyskill/config.json` (primary config) or `{project root}/.anyskill.json` (legacy project-level config).

---

## Step Zero: Read or Initialize Configuration (Global Priority + Auto-Discovery)

**Before performing any operation, you must search for the AnySkill configuration in the following priority chain. Once a valid configuration is found at any level, stop immediately and use it.**

### Configuration Lookup Priority Chain

1. **Global config** `~/.anyskill/config.json` (machine-level, shared across projects and IDEs)
2. **Project-level config** `{project root}/.anyskill.json` (backward compatible with older versions)
3. **None found** → Enter the initialization flow

### Token Retrieval Priority (for private repo authentication)

Regardless of which level the config is read from, the token retrieval priority is always:
1. Check environment variable `ANYSKILL_GITHUB_TOKEN`
2. Check the `token` field in the config file

If a token is obtained, include it in all HTTP requests as a header:
```
Authorization: token {token}
```

### Case 1: Config Already Exists (returning user / previously initialized device)

The user has previously initialized on this machine. **Skip all initialization** and directly verify the config:
1. Read `repo` and `localPath` from the config.
2. Construct key URLs:
   - **Index URL**: `https://raw.githubusercontent.com/{repo}/{branch}/index.json`
   - **Files base URL**: `https://raw.githubusercontent.com/{repo}/{branch}/skills/`
3. Verify that the `localPath` directory exists. If not, automatically re-clone:
   ```bash
   git clone https://github.com/{repo}.git {localPath}
   ```
   (The token is passed via the `Authorization` header or `GIT_ASKPASS` environment, not embedded in the URL.)
4. Attempt to fetch `index.json` to confirm connectivity.
5. Inform the user:
   > ✅ AnySkill configuration detected, connected to repository `{repo}`. Ready to use!
6. **If current environment is OpenClaw**: Check if `TOOLS.md` already contains a `### AnySkill` section. If not, or if the skill list is outdated, execute the "OpenClaw Exclusive: Write Workspace Config" steps below to register/update the skill list.

If verification fails (network error or repo deleted), ask the user if they want to re-initialize.

### Automatic Version Check (runs on every initialization)

**After the config is verified (whether Case 1 or after initialization completes), perform a silent version check:**

1. Fetch upstream version info:
   ```
   https://raw.githubusercontent.com/lanyijianke/AnySkill/main/version.json
   ```
   File structure:
   ```json
   {
     "engine": {
       "version": "x.y.z",
       "changelog": [
         { "version": "x.y.z", "date": "YYYY-MM-DD", "changes": ["change 1", "change 2"] },
         { "version": "x.y.z", "date": "YYYY-MM-DD", "changes": ["change 1"] }
       ]
     },
     "infra": {
       "version": "x.y.z",
       "files": ["generate-index.js", ".github/workflows/build-index.yml"],
       "changelog": [
         { "version": "x.y.z", "date": "YYYY-MM-DD", "changes": ["change 1"] }
       ]
     }
   }
   ```

2. **Engine version check**:
   - Read the `version` field from this file's (SKILL.md) frontmatter (currently `2.0.0`).
   - Compare with remote `engine.version`.
   - If remote version is **higher**, filter all changelog entries **above the local version** and display newest to oldest:
     > 🔔 AnySkill engine update available v{remote} (current v{local})
     >
     > 📋 **Update history:**
     > **v2.1.0** (2025-03-10)
     > - New feature A
     > - Improvement B
     >
     > **v2.0.0** (2025-03-04)
     > - New feature C
     >
     > To update, run: `clawhub update anyskill`
   - **Do not auto-overwrite SKILL.md.** Inform the user to update via ClawHub CLI which provides versioned, auditable updates.

3. **Infrastructure version check**:
   - Read the `.anyskill-infra-version` file from the user's private repo `{localPath}`. If it doesn't exist, treat as `0.0.0`.
   - Compare with remote `infra.version`.
   - If remote version is **higher**, similarly filter and display all new version changes:
     > 🔔 Repository infrastructure update available v{remote} (current v{local})
     >
     > 📋 **Update history:**
     > **v1.1.0** (2025-03-10)
     > - Improved index generation
     >
     > Would you like to update?
   - After user confirms, iterate over `infra.files` array, downloading each from upstream and overwriting in the user's `{localPath}`:
     ```
     https://raw.githubusercontent.com/lanyijianke/AnySkill/main/{file}
     ```
   - Write version marker file `{localPath}/.anyskill-infra-version` with the new version number.
   - Execute git operations to commit changes:
     ```bash
     cd {localPath}
     git add -A
     git commit -m "chore: update AnySkill infra to v{version}"
     git push origin {branch}
     ```

4. If both versions are up to date, **output nothing** — pass silently.

5. If `version.json` fetch fails (network error), **silently skip** version check without affecting normal usage.

> 💡 Version check is a lightweight operation (only fetches a small JSON), it won't slow down normal workflows.

### Case 2: Config Not Found (new device / first use)

**Before asking the user any questions, first silently detect if a usable Token already exists:**
1. Check if environment variable `ANYSKILL_GITHUB_TOKEN` exists.
2. If it **exists** (meaning the user has previously configured AnySkill on this machine):
   - **Do not ask the user for a Token**, directly jump to "Path B: User only provided a Token" auto-discovery flow below.
   - The entire process should be silent to the user: AI auto-detects cloud repo → confirms mount → writes global config → ready.
3. If it **does not exist**, then initiate the guided conversation (see below).

#### Guided Conversation (only when Token cannot be silently obtained)

Guide the user through initialization via natural language conversation. **The user should never need to run any terminal commands.**

**Say something like this to the user:**

>  👋 Welcome to AnySkill! Let me help you connect your private skill repository.
>
> Do you **already have** an AnySkill skill repository?
>
> ---
>
> **A) I have a repo** — Just provide your Token and repo name:
> `github_pat_xxx username/my-skills` (space-separated)
>
> ---
>
> **B) I don't have one yet** — Follow these steps (works on mobile too):
>
> **Step 1: Create a private skill repository**
> Open 👉 [One-click create repo](https://github.com/lanyijianke/AnySkill/generate)
> - **Repository name**: enter `my-skills` (or any name you like)
> - ⚠️ **Must select Private** (do not choose Public)
> - Click **Create repository**
>
> **Step 2: Create a Token (a key for AI to access your repo)**
> Open 👉 [Create Token](https://github.com/settings/personal-access-tokens/new)
> - **Token name**: enter `AnySkill`
> - **Expiration**: pick a duration you're comfortable with
> - **Repository access**: select **"Only select repositories"**
>   → Search for and select your `my-skills` repo in the dropdown
>   ⚠️ Note: if you chose "Public Repositories", the permissions panel below will NOT appear!
> - After selecting a repo, a **Permissions** panel appears below
>   → Expand **"Repository permissions"**
>   → Scroll down to find **"Contents"** (near the top of the list)
>   → Change it from "No access" to **"Read and write"**
> - Leave all other permissions at "No access"
> - Click **"Generate token"** at the bottom
> - Copy the generated Token (starts with `github_pat_`)
>
> **Step 3: Send me your Token and repo name**
> Format: `github_pat_xxx your-username/my-skills`
>
> ---
>
> Send it over when you're ready! If you get stuck on any step, just ask.

#### Handling User Response

**Decision criteria**: Whether the user's response contains a repository address (format: `username/repo-name`).

- **Contains repo address** → Follow "Path A"
- **No repo address (Token only)** → Follow "Path B"

---

#### Path A: User provided both Token and repository address

After the user provides a repo address and Token:
1. Ask the user where they want to clone the repo locally (default suggestion: `/tmp/{repo-name}`).
2. **Securely store the Token** (depends on IDE environment):
   - **OpenClaw**: Set environment variable `ANYSKILL_GITHUB_TOKEN` via the platform's standard env configuration.
   - **Other IDEs (Antigravity/Claude Code/Cursor)**: Write token to the config file.
3. Execute clone:
```bash
git clone https://github.com/{repo}.git {localPath}
```
(Use `GIT_ASKPASS` or credential helper to authenticate, do not embed token in URL.)
4. Create **global config file** `~/.anyskill/config.json`:

**OpenClaw version** (without token):
```json
{
  "repo": "user-provided-address",
  "branch": "main",
  "localPath": "/tmp/{repo-name}"
}
```

**Other IDE version** (with token):
```json
{
  "repo": "user-provided-address",
  "branch": "main",
  "token": "github_pat_xxxxxxxxxxxx",
  "localPath": "/tmp/{repo-name}"
}
```

---

#### Path B: User only provided a Token — Auto-Discovery Flow (⚠️ Core Path)

> **This is the most common scenario.** The user only gave a Token without specifying a repo name.
> **You must strictly follow these three steps. Never skip any step. Never directly create a new repo.**

**Step 1: Get the user's GitHub username via Token**

Use the GitHub API or command line to get user info:
```bash
curl -s -H "Authorization: token {token}" https://api.github.com/user
```
Extract the `login` field from the returned JSON — that's the username.

**Step 2: Auto-search for existing AnySkill skill repositories under the username**

Call the GitHub Repository Search API:
```bash
curl -s -H "Authorization: token {token}" "https://api.github.com/search/repositories?q=user:{login}+anyskill+in:name,description"
```

For **each candidate repo** in the results, try to read its `index.json`:
`https://raw.githubusercontent.com/{login}/{candidate-repo-name}/{default-branch}/index.json`
If `index.json` can be read successfully, this repo is a genuine AnySkill skill repository.

**Step 3: Branch based on detection results**

- **✅ Existing skill repo detected**: Inform user and request confirmation:
  > 👋 Welcome back! I detected an existing skill repository `{login}/{repo-name}`. Mounting automatically...

  Then auto-execute clone and config write (same as Path A steps 1-4), **without asking unnecessary questions**.

- **❌ No skill repo detected** (confirmed as a brand new user):

  Guide the user to create a repo first:
  > I couldn't find a skill repository under your account. Please create one first:
  >
  > 👉 [One-click create skill repository](https://github.com/lanyijianke/AnySkill/generate)
  >
  > Suggested name: `my-skills`, **make sure to check Private**.
  > Once created, tell me the repo name and I'll finish the setup!

  After the user provides the repo name, execute clone and config write (same as Path A steps 1-4).

  > 💡 **Security tip**: After the repo is created, go back to your Token settings and change **Repository access** to **Only select repositories**, selecting only this repo for minimal permissions.

#### Initialization Complete

Regardless of which path was taken, inform the user upon completion:
> ✅ AnySkill configuration complete!
> 📦 Skill repository: `{repo}`
> 📂 Local path: `{localPath}`
> 🔧 Global config: `~/.anyskill/config.json`
> From now on, you can load, download, and publish skills from any project.

#### OpenClaw Exclusive: Write Workspace Config (only in OpenClaw environments)

If the current environment is **OpenClaw** (detected by: `ANYSKILL_GITHUB_TOKEN` exists in `~/.openclaw/.env`, or user explicitly specified, or `~/.openclaw/` directory detected), perform these **two additional steps** after initialization:

**Step 1: Append to `TOOLS.md`**

Find the OpenClaw workspace `TOOLS.md` file (path: `~/.openclaw-config/workspace/TOOLS.md` or `{OpenClaw project root}/.openclaw-config/workspace/TOOLS.md`).

First check if the file already contains a `### AnySkill` section. Then read `index.json` (local `{localPath}/index.json` or remote fetch) to get the current skill inventory.

If `### AnySkill` section **does not exist**, append at end of file; if it **already exists**, **replace the entire section** (ensure the skill list is up to date):

```markdown

### AnySkill

- **Skill Repository**: `{repo}`
- **Global Config**: `~/.anyskill/config.json`
- **Local Path**: `{localPath}`
- **Skill Loading**: When you lack a skill, read the guide in `~/.openclaw/skills/anyskill/SKILL.md` to load from the cloud AnySkill repository on demand
- **Operation**: All skill management (load, download, upload, list, delete) is triggered via natural language, no CLI needed

#### Registered Cloud Skills

| Skill Name | Description |
|:---|:---|
| `{name}` | {description} |
| ... | ... |

(This list is dynamically generated from `index.json`, auto-updated after every skill add/remove/update)
```

> 📌 **The "Registered Cloud Skills" table must be generated in real-time from `index.json`**, iterating all skill entries and filling in `name` and `description`. If `index.json` is empty or fetch fails, display "No skills yet".

**Step 2: Append to `AGENTS.md`**

Find the OpenClaw workspace `AGENTS.md` file (same directory as `TOOLS.md`).

Search for the `## Tools` section. At the **end** of that section (before the next `##` heading), check if AnySkill-related content already exists. If **not**, append:

```markdown

**🧠 AnySkill Cloud Skills**: When you need to perform specific tasks (frontend design, API integration, data scraping, etc.) but don't have the corresponding skill locally, first check the AnySkill guide in `~/.openclaw/skills/anyskill/SKILL.md` to load capabilities on demand from your cloud private skill repository.
```

If AnySkill-related content already exists, skip this step.

> ⚠️ **Do not modify any other content** in these two files. Only append or update the AnySkill section — never overwrite existing user configurations.

#### OpenClaw Skill Registry Sync (General Rule)

> 📌 **Any operation that changes the skill list** (Mode 4 upload, Mode 5 update, Mode 7 delete, Mode 9 Pack install) must, after completion, if the current environment is OpenClaw, **re-read the latest `index.json` and replace the entire `### AnySkill` section in `TOOLS.md`** using the format above, ensuring the "Registered Cloud Skills" table always stays in sync with the cloud.
>
> This sync operation should be performed after git push completes and a few seconds wait (because GitHub Actions needs to rebuild `index.json`), or directly read from local `{localPath}/index.json`.

Then continue executing the user's original request.

---

## Mode 1: On-Demand Loading (default behavior, in-memory only)

When the user issues a task and you determine that the local environment lacks specific execution details:

1. Read AnySkill config via the priority chain (global `~/.anyskill/config.json` → project-level `.anyskill.json`).
2. Use your web reading tool to fetch `index.json` from the index URL (include auth header if token is available).
3. Find the most matching entry based on each skill's `description` for the current task.
4. For each file in the `files` array, read all files from the cloud into **memory** (do not save to local disk), then digest the `SKILL.md` specifications.
5. Complete the user's original request based on the loaded specifications.

> 💡 On-demand loading is lightweight and leaves no local files. Ideal for one-time use or trying out skills.

---

## Mode 2: On-Demand Download (specific skill to disk)

When the user explicitly says **"download XX skill", "pull XX to local", "install XX skill"** or similar instructions targeting a **single skill**:

1. Read AnySkill config via the priority chain.
2. Fetch `index.json`, match the target skill by the name or description the user specified.
3. **Detect the current AI IDE environment** and determine the download path (see path reference table below).
4. Download each file from the skill's `files` array to the local IDE skill directory, **preserving the original directory structure**.
5. Inform the user upon completion: Skill `{skill-name}` downloaded to `{path}`, N files total.

---

## Mode 3: Full Download to Local

When the user explicitly says **"download all skills", "pull skills to local", "sync cloud skills"** or similar instructions, perform a full download.

### Steps

1. Read AnySkill config via the priority chain.
2. Fetch `index.json` for the complete skill list.
3. **Detect the current AI IDE environment** and determine the download path (see table below). If unable to detect automatically, **ask the user**.
4. For each skill, iterate its `files` array, downloading each file and **preserving the original directory structure**.
   - For example, if `files` contains `my-skill/scripts/helper.py`, the download URL is `{files-base-url}my-skill/scripts/helper.py`, and the local path is `{IDE-skill-directory}/my-skill/scripts/helper.py`.
5. After completion, report the list of downloaded skills and file counts to the user.

### IDE Download Path Reference

| AI IDE | Download Path | Entry File |
|:---|:---|:---|
| **Antigravity** | `{project root}/.agent/skills/{skill-name}/` | `SKILL.md` |
| **Claude Code** | `{project root}/.claude/skills/{skill-name}/` | `SKILL.md` |
| **Cursor** | `{project root}/.cursor/rules/{skill-name}/` | `SKILL.md` |
| **OpenClaw** | `~/.openclaw/skills/{skill-name}/` | `SKILL.md` |

### IDE Auto-Detection Logic

- If the current project has an `.agent/` directory or you are Antigravity → Use **Antigravity** path
- If the current project has a `.claude/` directory or you are Claude Code → Use **Claude Code** path
- If the current project has a `.cursor/` directory or you are Cursor → Use **Cursor** path
- If the user explicitly mentions OpenClaw → Use **OpenClaw** path
- If unable to determine → **Ask the user**: "Which IDE are you currently using? (Antigravity/Claude Code/Cursor/OpenClaw)"

---

## Mode 4: Upload Skill to Cloud

When the user explicitly says **"upload skill", "upload this skill", "push skill to cloud", "push to repo"** or similar instructions, execute the upload flow.

Read `localPath` from the AnySkill config to operate in the local repository.

### Upload Steps

1. Confirm the skill content to upload with the user.
2. **The skill folder name must use the user's original name exactly** — never translate or rename it. If the user provides a Chinese name (e.g., `前端设计`), use that; if English (e.g., `web-scraper`), use English.
3. Create `SKILL.md` under `{localPath}/skills/{user-specified-name}/`.
   - `SKILL.md` must include correct YAML frontmatter (`name` and `description`).
   - If the user provides additional files (scripts, references, etc.), place them in the corresponding subdirectory.
4. **Auto-provision infrastructure files** (may be missing on first upload):
   - Check if `{localPath}/.github/workflows/build-index.yml` exists; if not, download from template repo: `https://raw.githubusercontent.com/lanyijianke/AnySkill/main/.github/workflows/build-index.yml`
   - Check if `{localPath}/generate-index.js` exists; if not, download from template repo: `https://raw.githubusercontent.com/lanyijianke/AnySkill/main/generate-index.js`
5. Execute git operations:
   ```bash
   cd {localPath}
   git add -A
   git commit -m "feat: add skill {user-specified-name}"
   git push origin {branch}
   ```
5. Inform the user upon completion:
   > ✅ Skill `{name}` has been uploaded to the cloud repository!
   > GitHub Actions will automatically rebuild `index.json` in a few seconds, after which other projects can load this skill.
6. **If current environment is OpenClaw**, execute "OpenClaw Skill Registry Sync" to update the skill list in `TOOLS.md`.

---

## Mode 5: Update a Specific Skill

When the user explicitly says **"update XX skill", "modify XX skill", "change XX"** or similar instructions:

1. Read `localPath` from AnySkill config via the priority chain.
2. Confirm that `{localPath}/skills/{name}/` exists. If not, inform the user the skill doesn't exist and suggest using upload mode to create a new one.
3. Read and display the existing `SKILL.md` content to the user, ask which parts need modification.
4. Modify the corresponding files based on the user's description.
5. Execute git operations:
   ```bash
   cd {localPath}
   git add skills/{name}/
   git commit -m "fix: update skill {name}"
   git push origin {branch}
   ```
6. Inform the user upon completion:
   > ✅ Skill `{name}` has been updated! GitHub Actions will automatically update the index.
7. **If current environment is OpenClaw**, execute "OpenClaw Skill Registry Sync" to update the skill list in `TOOLS.md`.

---

## Mode 6: List Cloud Skills

When the user explicitly says **"list skills", "what skills are there", "show cloud skills", "skill list"** or similar instructions:

1. Read AnySkill config via the priority chain.
2. Fetch `index.json`.
3. Display all skills in a table:

| Skill Name | Description | File Count |
|:---|:---|:---|
| `{name}` | `{description}` | `{files.length}` |

4. After display, ask the user if they want to load or download any skill.

---

## Mode 7: Delete a Specific Skill

When the user explicitly says **"delete XX skill", "remove XX skill", "remove XX from repo"** or similar instructions:

1. Read `localPath` from AnySkill config via the priority chain.
2. Confirm that `{localPath}/skills/{user-specified-name}/` exists.
3. **Must confirm with the user**:
   > ⚠️ About to delete skill `{name}`. This will permanently remove the folder from the cloud repository. Confirm deletion?
4. After user confirms, execute:
   ```bash
   cd {localPath}
   git rm -rf skills/{name}/
   git commit -m "feat: remove skill {name}"
   git push origin {branch}
   ```
5. Inform the user upon completion:
   > ✅ Skill `{name}` has been deleted from the cloud repository. GitHub Actions will automatically update the index.
6. **If current environment is OpenClaw**, execute "OpenClaw Skill Registry Sync" to remove the skill from the `TOOLS.md` skill list.

---

## Mode 8: Delete Entire Skill Repository (requires manual action)

When the user explicitly says **"delete the entire repo", "destroy skill space", "I don't want this repo anymore"** or similar instructions:

> ⛔ **This operation is extremely dangerous and irreversible. AI is strictly forbidden from executing it automatically.**

You may **only** provide guidance for the user to do it themselves:

1. Inform the user:
   > ⚠️ Deleting the entire repository is irreversible, and I cannot do it on your behalf. Please go to GitHub yourself:
   >
   > 1. Open `https://github.com/{repo}/settings` (scroll to the bottom **Danger Zone**)
   > 2. Click **Delete this repository**
   > 3. Confirm by typing the repository name as prompted
   >
   > After deletion, manually remove the local global config `~/.anyskill/config.json` (and project-level `.anyskill.json`, if any) and the `{localPath}` directory.

2. **Strictly forbidden** to call GitHub API or any command to delete the repository.

---

## Mode 9: Install Skills from Packs

When the user explicitly says **"install from Packs", "what packs are available", "install XX pack", "browse packs"** or similar instructions:

**Packs repository URL**: `https://raw.githubusercontent.com/lanyijianke/AnySkill-Packs/main/`

### Browse Available Packs

1. Fetch `https://raw.githubusercontent.com/lanyijianke/AnySkill-Packs/main/index.json` (public repo, no Token needed).
2. Display all packs and their skills in a table:

| Pack | Skill Name | Description |
|:---|:---|:---|
| `{category}` | `{skill.name}` | `{skill.description}` |

### Install a Specific Pack

1. Find all skills in the target pack from `index.json`.
2. **Download each skill's files individually**, saving to the user's private repo at `{localPath}/skills/{skill-name}/`.
   - File URL pattern: `https://raw.githubusercontent.com/lanyijianke/AnySkill-Packs/main/packs/{file-path}`
3. **Error tolerance**: If a skill download fails, skip it and continue to the next one.
4. After download completes, execute git operations to commit skills to the user's private repo:
   ```bash
   cd {localPath}
   git add skills/
   git commit -m "feat: install pack {category}"
   git push origin {branch}
   ```
5. Provide a **summary report**:
   > ✅ Pack `{category}` installation complete!
   > - Succeeded: {N} (skill-a, skill-b)
   > - Failed: {M} (skill-x — reason: download failed)
6. **If current environment is OpenClaw**, execute "OpenClaw Skill Registry Sync" to update the skill list in `TOOLS.md`.

---

## Code of Conduct

* Never guess details — always rely on cloud-fetched "injected capabilities".
* You may briefly report to the user: "Loading [skill-name] from cloud skill repository..."
* If `index.json` has no matching skill, inform the user that the cloud repository currently lacks the corresponding capability.
* If a network request fails, report to the user and suggest checking network connectivity or repository availability.
* **Throughout the entire process, never ask the user to manually run terminal commands.** All file creation, downloading, and git operations are performed automatically by you.
