# Gmail Setup via Himalaya (OPTIONAL)

Connect Gmail to a Dockerized OpenClaw instance using **Himalaya** — a full-featured email CLI that supports reading, sending, and **downloading attachments**.

---

## Why Himalaya, Not gog?

Both Himalaya and gog can access Gmail. The choice matters for one critical reason:

**gog does not support attachment download.** It can list emails and read plain text, but if you need to open, save, or process attached files (PDFs, spreadsheets, images), gog fails silently or returns incomplete data. In real workflows — reading invoices, reviewing reports, processing documents — attachments are not optional.

**Himalaya handles attachments reliably.** It uses IMAP/SMTP directly and can:
- Download any attachment to a local path
- List attachments by name and size before downloading
- Save attachments from inside the Docker container to mounted volumes

**Rule: use Himalaya for all email operations. Use gog only for Google Drive, Docs, Sheets, and Calendar (see `google-drive-setup.md`).**

| Task | Use |
|------|-----|
| Read emails | Himalaya |
| Send emails | Himalaya |
| Download attachments | Himalaya |
| List/search Drive files | gog |
| Read/write Google Docs | gog |
| Calendar events | gog |
| Google Sheets | gog |

---

## Prerequisites

- Running `openclaw-isolated` container (see SKILL.md)
- A Gmail account to use as the bot account (dedicated account recommended)
- Gmail IMAP must be enabled on the account

---

## Step 1: Create a Dedicated Gmail Account

Create a new Google account at https://accounts.google.com/signup specifically for the bot. Do not use your personal Gmail — it keeps the bot's inbox separate and reduces security risk.

Example: `<YOUR_BOT_EMAIL>`

---

## Step 2: Enable Gmail IMAP

1. Sign in to the bot Gmail account
2. Go to **Settings > See all settings > Forwarding and POP/IMAP**
3. Under IMAP Access, select **Enable IMAP**
4. Click **Save Changes**

---

## Step 3: Create a Google App Password

Gmail requires App Passwords for IMAP access when 2-Step Verification is enabled.

1. Go to https://myaccount.google.com/security
2. Under "How you sign in to Google", click **2-Step Verification** and enable it if not already
3. Go back to Security page, scroll to **App passwords**
4. Select **Mail** as the app
5. Click **Generate**
6. Copy the 16-character password (e.g. `abcd efgh ijkl mnop`)

**Keep this password — you will not see it again. Store it securely (e.g. in your password manager).**

---

## Step 4: Install Himalaya Inside the Container

### Apple Silicon (M1/M2/M3/M4):

```bash
docker exec openclaw-isolated sh -c \
  'mkdir -p /home/node/.local/bin && \
  curl -L https://github.com/pimalaya/himalaya/releases/latest/download/himalaya-aarch64-unknown-linux-musl.tar.gz \
  | tar -xz -C /home/node/.local/bin/'
```

### Intel Mac:

```bash
docker exec openclaw-isolated sh -c \
  'mkdir -p /home/node/.local/bin && \
  curl -L https://github.com/pimalaya/himalaya/releases/latest/download/himalaya-x86_64-unknown-linux-musl.tar.gz \
  | tar -xz -C /home/node/.local/bin/'
```

Verify:

```bash
docker exec openclaw-isolated /home/node/.local/bin/himalaya --version
```

---

## Step 5: Create Himalaya Config Inside the Container

Pipe the config directly — do NOT use `docker cp` (causes permission errors with `--cap-drop=ALL`):

```bash
docker exec openclaw-isolated sh -c 'mkdir -p /home/node/.config/himalaya'

cat << 'CONFIG' | docker exec -i openclaw-isolated sh -c \
  'cat > /home/node/.config/himalaya/config.toml'
[accounts.gmail]
default = true
email = "<YOUR_BOT_EMAIL>"
display-name = "OpenClaw Bot"

[accounts.gmail.incoming]
type = "imap"
host = "imap.gmail.com"
port = 993
login = "<YOUR_BOT_EMAIL>"
auth.type = "password"
auth.raw = "APP_PASSWORD_HERE"

[accounts.gmail.outgoing]
type = "smtp"
host = "smtp.gmail.com"
port = 587
login = "<YOUR_BOT_EMAIL>"
auth.type = "password"
auth.raw = "APP_PASSWORD_HERE"
CONFIG
```

Replace `<YOUR_BOT_EMAIL>` with the bot Gmail address and `APP_PASSWORD_HERE` with the 16-character App Password from Step 3.

Verify the file was written correctly:

```bash
docker exec openclaw-isolated cat /home/node/.config/himalaya/config.toml
```

---

## Step 6: Test Himalaya Inside the Container

List inbox:

```bash
docker exec openclaw-isolated \
  /home/node/.local/bin/himalaya -c /home/node/.config/himalaya/config.toml \
  envelope list --max-width 100
```

**Success:** A table of recent email subjects, senders, and dates.

Read an email (use ID from the list):

```bash
docker exec openclaw-isolated \
  /home/node/.local/bin/himalaya -c /home/node/.config/himalaya/config.toml \
  message read 1
```

List attachments on an email:

```bash
docker exec openclaw-isolated \
  /home/node/.local/bin/himalaya -c /home/node/.config/himalaya/config.toml \
  attachment list 1
```

Download an attachment:

```bash
docker exec openclaw-isolated \
  /home/node/.local/bin/himalaya -c /home/node/.config/himalaya/config.toml \
  attachment download 1 --output-dir /home/node/attachments/
```

---

## Step 7: Update TOOLS.md Inside the Container

The agent reads `TOOLS.md` to know what tools are available. Without this update, the agent will say no email integration exists even when everything is working.

```bash
docker exec openclaw-isolated sh -c 'cat >> /home/node/.openclaw/workspace/TOOLS.md << '"'"'EOF'"'"'

### Gmail (Himalaya)

- Account: <YOUR_BOT_EMAIL>
- Binary: /home/node/.local/bin/himalaya
- Config: /home/node/.config/himalaya/config.toml
- Capabilities: read emails, send emails, list and DOWNLOAD attachments (use for all email tasks)
- Examples:
  - List inbox: `himalaya -c ~/.config/himalaya/config.toml envelope list`
  - Read email: `himalaya -c ~/.config/himalaya/config.toml message read <ID>`
  - Send email: `himalaya -c ~/.config/himalaya/config.toml message send --to user@example.com --subject "Hi" <<< "body"`
  - List attachments: `himalaya -c ~/.config/himalaya/config.toml attachment list <ID>`
  - Download attachment: `himalaya -c ~/.config/himalaya/config.toml attachment download <ID> --output-dir ~/attachments/`
- NOTE: Use Himalaya for ALL email. Use gog only for Drive/Docs/Sheets/Calendar (see google-drive-setup.md)
EOF'
```

Replace `<YOUR_BOT_EMAIL>` with the actual bot address.

Restart the container:

```bash
docker restart openclaw-isolated
```

---

## Step 8: Verify via OpenClaw Agent

Send to your Discord bot: "List my recent emails"

The agent should use Himalaya to list inbox contents and return a summary.

---

## Maintenance

### App Password expired or revoked

If Himalaya returns authentication errors, generate a new App Password (Step 3) and update the config:

```bash
# Edit config inside container
docker exec -it openclaw-isolated sh -c \
  'sed -i "s/auth.raw = .*/auth.raw = \"NEW_APP_PASSWORD\"/" \
  /home/node/.config/himalaya/config.toml'
```

### Update Himalaya binary

```bash
# Apple Silicon
docker exec openclaw-isolated sh -c \
  'curl -L https://github.com/pimalaya/himalaya/releases/latest/download/himalaya-aarch64-unknown-linux-musl.tar.gz \
  | tar -xz -C /home/node/.local/bin/'
```

---

## What NOT to Do

### Do NOT use gog for email with attachments

gog can list Gmail messages but does not support downloading attachment files. Any workflow that needs to process attached documents, PDFs, or files must use Himalaya.

### Do NOT use `docker cp` for config files

`docker cp` creates files owned by host UID 501. The container runs as `node` (UID 1000). With `--cap-drop=ALL`, `chown` is unavailable. Always pipe content using `docker exec -i ... sh -c 'cat > /path'`.
