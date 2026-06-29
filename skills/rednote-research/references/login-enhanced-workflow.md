# Login-Enhanced Workflow

Use this file when the user explicitly chooses deeper RedNote/Xiaohongshu access and is willing to log in.

## Goal

Turn login-enhanced mode into a controlled, user-choice workflow.
Do not treat login as implicit.
Do not request passwords in chat when a site-native login flow is available.

## When to escalate to login-enhanced mode

Offer this mode when one or more of these are true:
- the user wants a full account summary or recent-post scan
- the user wants comment-area analysis
- public-web mode returned thin or blocked results
- the user wants higher confidence on an account, post, or trend

Suggested wording:
- "Public-web mode is too thin for this account. If you want, you can switch to login-enhanced mode and log in inside the controlled browser session for fuller coverage."

## Recommended browser flow

1. Explain why public-web mode is incomplete.
2. Ask whether the user wants to stay no-login or switch to login-enhanced mode.
3. If the user chooses login-enhanced mode:
   - open RedNote/Xiaohongshu in browser automation
   - navigate to the relevant profile/search/post page if known
   - tell the user to complete QR/code/password login in the browser session themselves
   - wait for confirmation that login succeeded
4. After login, continue only with the minimum navigation needed for the task.
5. At the end, summarize findings and say the result used login-enhanced access.

## What to collect after login

Collect the smallest evidence set that answers the user's request.

For an account summary, prefer:
- profile headline and self-description
- visible recent note list
- visible timestamps / posting cadence
- recurring themes
- visible media formats: image post, video, repost, guide, etc.
- visible engagement clues when available
- visible comments only if the user asked for them

## Account summary checklist

For "summarize this account's recent 1-3 months":
- identify the visible date range actually inspected
- count or estimate how many recent notes were directly inspected
- group notes into 3-6 recurring themes
- note whether posts are mostly food, local guide, lifestyle, ads, reposts, or mixed
- note whether style is diary-like, recommendation-heavy, deal-focused, aesthetic, meme-like, or informational
- note whether there are obvious campaigns, merchant collaborations, or repeated venue types
- note what remains missing even after login

## Comment review checklist

When comments are requested:
- inspect only enough comments to identify major clusters
- cluster into 3-5 themes
- separate support / criticism / joking / questions / purchase intent
- do not imply exhaustive full-thread coverage unless the full thread was actually reviewed

## Failure and fallback

If login cannot be completed or the platform still blocks access:
- say exactly what failed
- fall back to public-web mode
- ask for seed links, screenshots, or copied titles if needed

Example fallback wording:
- "Login-enhanced review didn’t complete successfully, so I’m falling back to public-web evidence plus any links/screenshots you provide."

## Privacy and restraint

- Do not browse unrelated private areas.
- Do not message, like, follow, or post unless the user explicitly asks.
- Do not scrape more history than needed.
- Treat authenticated sessions as sensitive.

## Output note

Add one short line in the final answer:
- "Access mode: login-enhanced browser review"
or
- "Access mode: public-web only"