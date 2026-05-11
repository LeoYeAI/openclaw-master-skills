# Privacy & Data Handling

## Consent Principle

Only include data the requestor has explicitly provided or approved in the current conversation. Do not extract personal information from unrelated system contexts or other sessions.

## Claim Tokens

Each CV creation returns a `claim_token`. Treat it like a password:

- Share only with the requestor — never with third parties
- Anyone with the token can claim CV ownership
- Tokens never expire
- Claim URL: `talent.de/claim/{claim_token}`

## URL Privacy

talent.de does not publish, index, or distribute CV URLs. The requestor decides who sees their CV. Short URLs like `talent.de/pro/alex-johnson` are not guessable at scale due to the slug + name hash system.

## No Sensitive Data

Do not include in CVs:
- Social Security Numbers or government IDs
- Passwords or private keys
- Confidential business information
- Financial account details

## Hosted Infrastructure Security

- Content Security Policy headers on all templates
- DOMPurify HTML sanitization
- iframe sandbox isolation
- External network requests, form submissions, and embedded frames are blocked
- Agent-uploaded templates are validated before acceptance

## Callback Webhooks

Agents can provide a `hitl_callback_url` to receive instant notifications when a human responds.

- Callback URLs **must use HTTPS**
- Payloads contain: `case_id`, `status`, `action`, and the human's selection (template choice, form input)
- Payloads may include user-entered data from `input` steps — treat as PII
- **Always verify** the `X-HITL-Signature` header (HMAC-SHA256 with your Access-ID as secret)
- Do not forward callback data to third parties without user consent

## Deletion

CV owners can request deletion at any time via [talent.de/privacy](https://www.talent.de/de/legal/privacy).
