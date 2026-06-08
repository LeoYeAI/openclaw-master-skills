# Getting Started — Step by Step

This guide assumes you have never installed anything like this before. Follow each step in order.

---

## What You're Installing

Mission Control is a dashboard that runs on your computer alongside OpenClaw. It gives you a browser-based window to see what your AI agents are working on, review their output, approve decisions, track costs, and keep a library of everything they produce.

**What it is NOT**: Mission Control does not replace OpenClaw. OpenClaw still runs your agents and does all the AI work. Mission Control is just the control panel you look through.

---

## Before You Start

You need three things already working:

1. **A computer** running macOS, Linux, or Windows
2. **OpenClaw installed and running** — if not, go to [docs.openclaw.ai/start/getting-started](https://docs.openclaw.ai/start/getting-started) first
3. **Node.js version 22 or newer** — OpenClaw already requires it, so you likely have it

**How to check Node.js**: Open a terminal and type `node --version`. You should see `v22` or higher. If not, visit [nodejs.org](https://nodejs.org) to install it.

---

## Step 1: Open Your Terminal

The terminal is a text-based way to give your computer commands.

- **Mac**: Press `Cmd + Space`, type "Terminal", press Enter
- **Windows**: Press the Windows key, type "PowerShell", press Enter
- **Linux**: Press `Ctrl + Alt + T`

You should see a window with a blinking cursor.

---

## Step 2: Go to Your OpenClaw Folder

Type this command and press Enter:

```bash
cd ~/.openclaw
```

> **What this does**: `cd` means "change directory" — it moves you into the folder where OpenClaw keeps its files. `~` means your home folder.

> **If you see "No such file or directory"**: OpenClaw isn't installed. Go to docs.openclaw.ai first.

---

## Step 3: Extract the Skill

If you downloaded the `mission-control-skill.tar.gz` file, copy it to your OpenClaw folder and extract it:

```bash
tar -xzf mission-control-skill.tar.gz
```

This creates a `mission-control-skill` folder with everything inside.

---

## Step 4: Run the Setup Script

The setup script does everything automatically — installs the dashboard, configures the connection, and sets up the hook:

```bash
cd mission-control-skill
./setup.sh
```

The script will ask you a few questions. Press Enter to accept the default answer (shown in brackets):

- **Backend port**: Which port number the dashboard runs on. Default `8000` is fine.
- **Hook secret**: A password that agents use to talk to the dashboard. A random one is generated for you.
- **Gateway WebSocket URL**: Where your OpenClaw gateway is running. Default `ws://127.0.0.1:18789` is correct for local setups.
- **Gateway token**: If your gateway requires a token. Leave empty if unsure.
- **Install directory**: Where to put the dashboard files. Default `~/.openclaw/mission-control`.

> **Want to skip all questions?** Use: `./setup.sh --auto`

The script will install all software packages. This takes 1-3 minutes. Wait for the "Setup complete!" message.

---

## Step 5: Start Mission Control

Navigate to the dashboard folder and start it:

```bash
cd ~/.openclaw/mission-control
npm run dev
```

You should see:

```
Backend running on http://localhost:8000
Frontend running on http://localhost:4173
```

> **Keep this terminal open!** Mission Control runs as long as this window stays open. Press `Ctrl + C` to stop it.

---

## Step 6: Open the Dashboard

Open your web browser and go to:

**http://localhost:4173**

You should see the Mission Control dashboard with a dark theme and a sidebar on the left. If you see it — the installation is complete!

> The dashboard will be empty at first. That's normal — you haven't created any projects yet.

---

## Step 7: Restart OpenClaw Gateway

For the hook to start working, restart your OpenClaw gateway:

```bash
openclaw gateway restart
```

Wait about 10 seconds, then verify:

```bash
openclaw gateway status
```

You should see "running" in the output.

---

## Step 8: Verify the Hook

Check that the Mission Control hook is installed and enabled:

```bash
openclaw hooks list
```

You should see `mission-control` listed as **enabled**. If not:

```bash
openclaw hooks enable mission-control
```

---

## Step 9: Create Your First Project

Back in your browser at http://localhost:4173:

1. Click **"Projects"** in the sidebar
2. Click **"+ New Project"** in the top right
3. Enter a name like "Test Project"
4. Click **"Create Project"**

You should see your project appear with a progress bar at 0%.

Or submit a request through the Inbox:

1. Click **"Inbox"** in the sidebar
2. Click **"+ New Request"**
3. Describe what you need
4. Click **Submit** — it appears as a pending item
5. Click the green **✓** to approve it

---

## What Happens Next

Your agents will now automatically report their work to Mission Control. When an agent starts a task, it appears as "In Progress" on the Pipeline. When it finishes, it moves to "Review" and shows up in your Inbox for you to check.

Read the other docs for more detail:

- **HOOK-EVENTS.md** — Every event agents can send
- **API-REFERENCE.md** — All API endpoints
- **LIBRARY-GUIDE.md** — How the document Library works
- **TROUBLESHOOTING.md** — If something isn't working

---

## Notifications

Mission Control notifies you when agents need attention — even if you're in a different browser tab.

**Desktop notifications**: When the dashboard tab is not focused, you'll get a native system notification for reviews submitted, approvals needed, task failures, and stalled tasks. Your browser will ask for permission the first time — click "Allow".

**In-app toasts**: Even when the tab is focused, small notification pills slide in from the top-right corner, color-coded by type: purple for reviews, amber for approvals, blue for requests, red for errors. They auto-dismiss after 5 seconds.

---

## Running on Your LAN

By default, Mission Control only listens on `localhost` — you can only access it from the same machine. To access the dashboard from other devices on your network (your phone, a tablet, another computer), you need to bind it to your LAN address.

### Quick: Bind the frontend to all interfaces

Edit the `dev` script in `app/frontend/package.json` or run:

```bash
cd ~/.openclaw/mission-control/frontend
npx vite --port 4173 --host 0.0.0.0
```

Then open `http://YOUR_MACHINE_IP:4173` from any device on your network. Find your IP with `hostname -I` (Linux) or `ipconfig getifaddr en0` (Mac).

The backend already listens on all interfaces when you set `PORT=8000`, but make sure your `CORS_ORIGIN` in `backend/.env` matches the address you'll use:

```
CORS_ORIGIN=http://192.168.1.100:4173
```

### Running as systemd User Services (Linux)

If you want Mission Control to start automatically and survive terminal close:

**Create the backend service:**

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/mc-backend.service << EOF
[Unit]
Description=Mission Control Backend
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/.openclaw/mission-control
ExecStart=/usr/bin/node backend/src/server.js
Restart=on-failure
RestartSec=5
Environment=NODE_ENV=production
EnvironmentFile=%h/.openclaw/mission-control/backend/.env

[Install]
WantedBy=default.target
EOF
```

**Create the frontend service:**

```bash
cat > ~/.config/systemd/user/mc-frontend.service << EOF
[Unit]
Description=Mission Control Frontend
After=mc-backend.service

[Service]
Type=simple
WorkingDirectory=%h/.openclaw/mission-control/frontend
ExecStart=/usr/bin/npx vite --port 4173 --host 0.0.0.0
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
```

**Enable and start:**

```bash
systemctl --user daemon-reload
systemctl --user enable mc-backend mc-frontend
systemctl --user start mc-backend mc-frontend
```

**Check status:**

```bash
systemctl --user status mc-backend
systemctl --user status mc-frontend
journalctl --user -u mc-backend -f   # live backend logs
```

**Enable lingering** so services run even when you're not logged in:

```bash
sudo loginctl enable-linger $USER
```

---

## Daily Routine

Once everything is set up, your daily flow is:

```bash
cd ~/.openclaw/mission-control && npm run dev
```

Open http://localhost:4173 and:

1. **Dashboard** — Check alerts, pipeline state, agent health
2. **Inbox** — Review work, approve requests, handle approvals
3. **Pipeline** — See if anything is stuck
4. **Library** — Read new research or reports
5. **Costs** — Check spending

Press `Ctrl + C` to stop when done. Your data persists — it's all in the SQLite database.
