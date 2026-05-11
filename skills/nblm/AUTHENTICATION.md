# Authentication Notes

This skill uses the `agent-browser` daemon to automate NotebookLM. Authentication is handled by a visible browser session and kept in memory by the daemon while it runs. NotebookLM API credentials (token + cookie header) are persisted to `data/auth/google.json` on demand, or supplied via environment variables.

## How Authentication Works

- `auth_manager.py setup` launches a headed browser via the daemon.
- You log in to Google manually.
- The daemon keeps cookies/storage in memory for subsequent commands.
- Cookies and local storage are cached to `data/agent_browser/storage_state.json` for reuse after daemon restarts.
- NotebookLM API credentials are stored in `data/auth/google.json`:
  - `notebooklm_auth_token`
  - `notebooklm_cookies`
- If cached NotebookLM credentials are older than 10 days, the skill attempts an HTTP refresh using stored Google cookies before falling back to the daemon.
- You can also provide credentials via environment variables:
  - `NOTEBOOKLM_AUTH_TOKEN`
  - `NOTEBOOKLM_COOKIES`
- The daemon stops after 10 minutes of inactivity; any agent-browser command resets the timer.
- Set `AGENT_BROWSER_OWNER_PID` to stop the daemon when your agent process exits.
- `scripts/run.py` sets `AGENT_BROWSER_OWNER_PID` to its parent PID by default; override it if your agent runs differently.
- Stopping the daemon ends the active session and requires re-authentication.
- The skill stores minimal metadata in `data/auth_info.json` and `data/agent_browser/session_id`.

## Troubleshooting Authentication

1. **Not authenticated**
   ```bash
   python scripts/run.py auth_manager.py setup
   ```

2. **Reset and re-authenticate**
   ```bash
   python scripts/run.py auth_manager.py clear
   python scripts/run.py auth_manager.py setup
   ```

3. **Refresh NotebookLM API credentials**
   ```bash
   python scripts/run.py auth_manager.py setup
   ```

4. **Use API credentials without the browser daemon**
   ```bash
   export NOTEBOOKLM_AUTH_TOKEN="..."
   export NOTEBOOKLM_COOKIES="SID=...; HSID=..."
   ```

3. **Missing browsers**
   ```bash
   npm install
   npm run install-browsers
   ```

4. **Stop the daemon**
   ```bash
   python scripts/run.py auth_manager.py stop-daemon
   ```

5. **Check watchdog status**
   ```bash
   python scripts/run.py auth_manager.py watchdog-status
   ```

## Security Notes

- All browser activity runs locally.
- The `data/` directory contains sensitive auth metadata. Never commit it.
- Use a dedicated Google account for automation if you prefer extra isolation.
