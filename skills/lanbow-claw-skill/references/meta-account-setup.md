# Meta Ad Account Setup Guide

Two paths to get started — pick the one that fits:

| Path | Token Type | Validity | Best For |
|------|-----------|----------|----------|
| **Quick Start (recommended for new users)** | User Access Token via OAuth | ~1-2 hours (short-lived) or ~60 days (long-lived) | Get ads running fast, minimal setup |
| **Production Setup** | System User Token | Never expires | Long-running automation, team/agency use |

**Start with Quick Start.** You can upgrade to a System User Token later without recreating campaigns.

## Agent Behavior

**You (the agent) are almost certainly NOT on the user's local machine.** You have the CLI; the user has the browser. This means:

- `lanbow-ads auth login` opens a browser + local HTTP callback on **your** machine, not the user's — **it will not work**.
- Sending the OAuth authorization URL to the user is also useless — the callback redirects to `localhost` on your machine, so the user completing auth in their browser still cannot reach your local server.

**Never attempt `lanbow-ads auth login` by default.** Only try it if the user explicitly confirms they are on the same machine and have a browser available.

### How to authenticate — try in this order:

**1. Environment variables or platform secret fields (best — zero interaction):**

If `META_ACCESS_TOKEN`, `META_APP_ID`, and `META_AD_ACCOUNT_ID` are already set as environment variables (or via the platform's secret/credential fields), configure the CLI automatically without asking the user:
```bash
lanbow-ads config set --app-id "$META_APP_ID"
lanbow-ads auth set-token "$META_ACCESS_TOKEN"
lanbow-ads config set --account "$META_AD_ACCOUNT_ID"
# Only if META_APP_SECRET is set (optional — needed only for token exchange):
[ -n "$META_APP_SECRET" ] && lanbow-ads config set --app-secret "$META_APP_SECRET"
```

**2. Ask the user to provide credentials directly (most common):**

If env vars are not set, ask the user for their Access Token, App ID, and Ad Account ID. **Only request the minimum credentials needed for the current task.** Tell the user exactly how to get each value — don't just ask, give them step-by-step instructions they can follow in their browser.

**Recommend the user use environment variables or their platform's secret fields rather than pasting credentials into chat.** If direct input is the only option, proceed with the instructions below.

**To get an Access Token, tell the user:**

> You can get an Access Token yourself:
> 1. Open https://developers.facebook.com/tools/explorer/
> 2. In the top-right **App** dropdown, select your App (use the App ID from Step 2)
> 3. Click **"Generate Access Token"** → select permissions: `ads_management`, `ads_read`, `business_management`
> 4. Click **"Submit"**
> 5. Copy the generated Access Token and send it to me

**To get App ID, tell the user:**

> 1. Go to https://developers.facebook.com/apps/ and select your App
> 2. Go to **App Settings → Basic**
> 3. Your **App ID** is at the top of the page

**To get App Secret (only if needed for token exchange), tell the user:**

> 1. On the same App Settings → Basic page
> 2. Click **Show** next to **App Secret** (requires password), then copy it
>
> Note: App Secret is only needed if you want to exchange a short-lived token for a long-lived one (~60 days). You can skip this if you don't need it.

**To get Ad Account ID, tell the user:**

> 1. Go to https://adsmanager.facebook.com/
> 2. Your Ad Account ID is in the URL or account dropdown (format: `act_XXXXXXXXX`)

Once the user provides these values, run the CLI commands on their behalf:

```bash
# User provides App ID → you run:
lanbow-ads config set --app-id <APP_ID>

# User provides Access Token → you run:
lanbow-ads auth set-token <ACCESS_TOKEN>

# User provides Ad Account ID → you run:
lanbow-ads config set --account <AD_ACCOUNT_ID>

# Only if user provides App Secret (optional) → you run:
lanbow-ads config set --app-secret <APP_SECRET>
```

**3. `lanbow-ads auth login` (last resort — same machine only):**

Only if the user explicitly says they are on the same machine and can open a browser. If `auth login` fails or the user says they can't open the link, **immediately fall back to method 2** — ask for their credentials directly instead of retrying or sending more URLs.

### Credential handling rules:
- Do NOT log, echo, or print credentials in plain text
- Do NOT store credentials in any file other than via `lanbow-ads` CLI commands
- Do NOT repeatedly attempt `auth login` or send OAuth URLs when the user cannot open them — ask for credentials directly instead

---

# Quick Start (User Access Token)

This gets you from zero to running ads in minutes. You only need an App and a personal login.

## Step 1: Register a Meta Developer Account

1. Go to [developers.facebook.com](https://developers.facebook.com/)
2. Click **Get Started** in the top right corner
3. Log in with your Facebook account
4. Agree to the developer platform terms
5. Verify your account (phone number verification may be required)

Once complete, you will be taken to the developer Dashboard.

## Step 2: Create an App

> **Note:** Meta's developer UI changes frequently. Button labels and flows may differ from what's described below. The goal is the same regardless of UI changes: **get a valid App ID + App Secret with Marketing API enabled.**

1. In the developer Dashboard, click **Create App**
2. You may see different flows depending on your account:
   - If you see **use case selection**: choose **"Create & manage ads with Marketing API"** or similar
   - If you see **app type selection**: choose **Other** → **Business**
3. Fill in the app details:
   - **App Name**: Choose any name, e.g. `My Ads Tool`
   - **App Contact Email**: Your email address
   - **Business Portfolio**: Select your Business Manager if you have one, otherwise skip
4. Click **Create App**

### Get App ID and App Secret

1. Your **App ID** is displayed at the top of the app Dashboard (a numeric string like `1234567890123456`)
2. Go to **App Settings** → **Basic** in the left menu
3. Find **App Secret**, click **Show** (requires Facebook password), and copy it

> **The App Secret is sensitive. Do not share it or commit it to a code repository.**

### Enable Marketing API

1. In the left menu, click **Add Product** (or scroll down on the app Dashboard)
2. Find **Marketing API** and click **Set Up**

## Step 3: Get an Access Token

The user needs to generate a token in their browser and paste it to you. There are two ways:

### Option A: Graph API Explorer (fastest)

Guide the user to:

1. Open [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. In the top-right **App** dropdown, select the app created in Step 2
3. Click **Generate Access Token**
4. In the permissions dialog, check at least:
   - `ads_management`
   - `ads_read`
   - `pages_show_list`
   - `pages_read_engagement`
5. Click **Continue** and authorize
6. Copy the generated token from the Access Token field

This produces a short-lived token (~1-2 hours). Good enough to get started immediately.

### Option B: Marketing API Tools (alternative)

Guide the user to:

1. Go to the app's Dashboard on [developers.facebook.com](https://developers.facebook.com/)
2. In the left menu, click **Marketing API** → **Tools**
3. Check the required permissions (`ads_management`, `ads_read`)
4. Click **Get Token**
5. Copy the token

## Step 4: Configure the CLI

Once the user provides their App ID, App Secret, and Access Token, run:

```bash
lanbow-ads config set --app-id <APP_ID> --app-secret <APP_SECRET>
lanbow-ads auth set-token <ACCESS_TOKEN>
```

### Extend Token Validity (Recommended)

The token from Step 3 is short-lived (~1-2 hours). If the user has provided the App Secret, you can exchange it for a long-lived token (~60 days):

```bash
lanbow-ads auth exchange --token <SHORT_LIVED_TOKEN>
```

Verify the result:

```bash
lanbow-ads auth status
```

## Step 5: Set Default Ad Account

List available ad accounts and set the default:

```bash
lanbow-ads accounts list
lanbow-ads config set --account <AD_ACCOUNT_ID>
```

## Step 6: Verify

Run these commands. All should succeed without errors:

```bash
lanbow-ads auth status
lanbow-ads accounts list
lanbow-ads campaigns list       # may be empty, but should not error
lanbow-ads pages list
```

**Quick Start is done.** The user can now create and manage campaigns. When the token expires, ask the user to generate a new one from Graph API Explorer and provide it to you.

---

# Production Setup (System User Token)

Use this when you need a token that never expires, or when operating on behalf of a team/agency. This requires a Meta Business Manager.

## Why System User Token?

| | User Token | System User Token |
|--|-----------|-------------------|
| Expires | Yes (~60 days max) | No |
| Tied to a person | Yes | No (survives employee offboarding) |
| Setup complexity | Low | Higher |
| Best for | Getting started, personal use | Production, automation, agencies |

## Prerequisites

- A [Meta Business Manager](https://business.facebook.com/) account
- An Ad Account owned by or shared with that Business Manager

## Step 1: Create a System User

1. Go to [Business Settings](https://business.facebook.com/settings/) → **Users** → **System Users**
2. Click **Add** to create a new System User
3. Set the role to **Admin** (required for full ads management)
4. Give it a descriptive name, e.g. `lanbow-ads-bot`

## Step 2: Assign Assets to the System User

**This is the most critical step.** A token without asset assignments will fail with permission errors even if all scopes are correct.

Meta permissions are three layers stacked:

```
Layer 1: Token scopes (ads_management, ads_read, etc.)
Layer 2: System User role (Admin)
Layer 3: Asset assignments (Ad Account, Page, Pixel assigned to this System User)
         ↑ This is the layer most people miss
```

All three layers must be in place. Missing any one layer causes API permission errors.

### Assign the Ad Account

1. In the System User details page, click **Assign Assets**
2. Select **Ad Accounts**
3. Find your ad account and select it
4. Set permission level to **Manage campaigns** or **Full control**
5. Click **Save Changes**

### Assign Pages (if needed for ad delivery)

1. Same **Assign Assets** flow → select **Pages**
2. Assign the Facebook Page that will be used in ads
3. Set permission to **Manage Page**

### Verify Asset Assignment

Before generating the token, confirm:

- [ ] Ad Account is listed under the System User's assigned assets
- [ ] Permission level is **Manage campaigns** or **Full control**
- [ ] Facebook Page is assigned (if you plan to create ads with a Page identity)

## Step 3: Generate the System User Token

1. On the System User details page, click **Generate New Token**
2. Select your App (created in Quick Start Step 2)
3. Check these scopes:
   - `ads_management`
   - `ads_read`
   - `business_management`
   - `pages_show_list`
   - `pages_read_engagement` (if using Pages)
4. Click **Generate Token**
5. **Copy the token immediately** — it will not be shown again

## Step 4: Configure the CLI

Ask the user for the System User Token and Ad Account ID, then run:

```bash
lanbow-ads auth set-token <SYSTEM_USER_TOKEN>
lanbow-ads config set --account <AD_ACCOUNT_ID>
```

Verify:

```bash
lanbow-ads auth status
lanbow-ads campaigns list
```

---

# Troubleshooting

## Permission Checklist

When you get permission errors, check this chain in order (most common failures first):

1. **Asset assignment** — Is the Ad Account assigned to the System User / your user?
   - Go to Business Settings → System Users → [your user] → Assigned Assets
   - The Ad Account must be listed with **Manage campaigns** or **Full control**
2. **Token scopes** — Does the token include `ads_management` and `ads_read`?
   - Regenerate the token with correct scopes if missing
3. **System User role** — Is the System User an **Admin**?
   - **Employee** role has limited permissions
4. **Ad Account ownership** — Is the Ad Account owned by or shared with the Business Manager?
   - Go to Business Settings → Accounts → Ad Accounts to verify

## Common Errors

### "App Not Set Up" or "Invalid App ID"

```bash
lanbow-ads config list           # Check stored app-id
lanbow-ads config set --app-id CORRECT_APP_ID
```

### CLI Did Not Receive the Callback After Browser Authorization

1. Check if port 8080 is in use: `lsof -i :8080`
2. If occupied, terminate the process and retry `lanbow-ads auth login`

### "Error validating access token: Session has expired"

Token has expired. For User Tokens, re-run `lanbow-ads auth login`. For System User Tokens, generate a new one in Business Settings.

### Cannot Find Ad Accounts

- Confirm the Ad Account is in the Business Manager: Business Settings → Accounts → Ad Accounts
- Confirm it is assigned to your System User (or your personal user has access)

### Insufficient Permissions ("Permissions error")

Check the permission chain above. The most common cause is **missing asset assignment** — the Ad Account exists in the Business Manager but is not assigned to the System User.

For User Tokens, log out and re-login with all permissions checked:

```bash
lanbow-ads auth logout
lanbow-ads auth login
```

On the browser authorization page, expand the permissions list and ensure `ads_management`, `ads_read`, `pages_show_list` are all checked.

### Meta UI looks different from this guide

Meta's developer platform UI changes frequently. The exact button labels, menu positions, and flow steps may differ from what's documented here. Focus on the goal of each step rather than the exact UI path:

- **Goal of app creation**: Get a valid App ID + App Secret
- **Goal of Marketing API**: Enable ads API access on the app
- **Goal of System User**: Get a non-expiring token with asset assignments

---

# Credential Cleanup

**Always clean up stored credentials after your session ends**, especially if you used long-lived tokens or App Secret.

## Remove Stored Credentials

```bash
lanbow-ads auth logout                    # Remove stored access token
lanbow-ads config unset --app-secret      # Remove stored app secret
lanbow-ads config list                    # Verify no secrets remain
```

## Revoke Tokens (Meta Side)

- **User Tokens**: expire automatically (1-2 hours for short-lived, ~60 days for long-lived). To revoke immediately, go to [Facebook Settings → Security → Active Sessions](https://www.facebook.com/settings?tab=security) and remove the app authorization
- **System User Tokens**: go to [Business Settings → System Users](https://business.facebook.com/settings/system-users) → select the System User → click **Revoke Token**

## Verify Cleanup

```bash
lanbow-ads auth status    # Should show "not authenticated"
lanbow-ads config list    # Should not contain app-secret or sensitive values
```
