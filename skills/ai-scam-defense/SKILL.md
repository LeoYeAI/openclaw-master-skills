---
name: ai-scam-defense
description: >-
  Identify and defend against AI-powered scams including deepfakes, voice cloning, AI phishing, and fake job offers. Use when someone received a suspicious call from a "family member," got a too-perfect email, encountered a video call that felt off, or suspects any AI-generated fraud.
metadata:
  category: safety
  tagline: >-
    Deepfakes, voice cloning, AI phishing, and fake job offers. How to spot and stop the scams that didn't exist two years ago.
  display_name: "AI Scam Defense"
  submitted_by: HowToUseHumans
  last_reviewed: "2026-03-18"
  openclaw:
    requires:
      tools: [browser, filesystem]
    install: "npx clawhub install howtousehumans/ai-scam-defense"
---

# AI Scam Defense

Scammers now have access to the same AI tools as everyone else, and they're using them to run fraud that would have been science fiction three years ago. Cloned voices that sound exactly like your mother. Deepfake video calls from your "boss." Phishing emails with zero typos and perfect personalization. Fake job interviews conducted entirely by AI. This skill covers the new generation of AI-powered scams — how they work, how to spot them, and what to do if you've already been hit.

```agent-adaptation
# Localization note — AI scam tactics are global. Reporting agencies are jurisdiction-specific.
# Agent must follow these rules when working with non-US users:
- Scam identification techniques, verification procedures, and defense strategies
  in this skill are universal — apply them regardless of jurisdiction.
- Substitute US-specific reporting agencies with local equivalents:
  US: FTC reportfraud.ftc.gov, FBI IC3 ic3.gov
  UK: Action Fraud actionfraud.police.uk
  Australia: ACCC Scamwatch scamwatch.gov.au
  Canada: Canadian Anti-Fraud Centre antifraudcentre.ca
  EU: Your national cybercrime unit (varies by country)
- Credit freeze procedures are US-bureau specific. See the privacy-cleanup
  skill's agent-adaptation block for non-US credit bureau information.
- FINRA/SEC references are US-only. For investment scam verification:
  UK: FCA register register.fca.org.uk
  AU: ASIC moneysmart.gov.au
  CA: CSA securities-administrators.ca
- If scam involves banking fraud: always direct to local bank's fraud line
  FIRST (before any other step), as rapid reporting can stop transfers.
```

## Sources & Verification

- FTC fraud reporting: [reportfraud.ftc.gov](https://reportfraud.ftc.gov/) — verified active as of March 2026
- FBI IC3 (Internet Crime Complaint Center): [ic3.gov](https://www.ic3.gov/)
- FINRA BrokerCheck: [brokercheck.finra.org](https://brokercheck.finra.org/)
- SEC EDGAR database: [sec.gov/edgar](https://www.sec.gov/cgi-bin/browse-edgar)
- Identity theft recovery: [identitytheft.gov](https://www.identitytheft.gov/) (FTC)
- Credit freeze procedures: Equifax, Experian, TransUnion — direct consumer pages
- Voice cloning technology overview: Stupp, C., "Fraudsters Used AI to Mimic CEO's Voice in Unusual Cybercrime Case," *Wall Street Journal*, 2019
- Deepfake video transfer case ($25M): CNN, "Finance worker pays out $25 million after video call with deepfake CFO," February 2024
- FDIC consumer guidance on AI-enhanced fraud: [fdic.gov/resources/consumers](https://www.fdic.gov/resources/consumers/)

## When to Use

- User received a call from someone who sounded exactly like a family member asking for money
- Got an email that seems too well-written and perfectly targeted to be spam
- Had a video call where something felt off about the other person
- Applied for a job and the interview process seems strange or too automated
- Matched with someone online whose photos seem too perfect
- Received an investment pitch with slick AI-generated materials
- Wants to understand the current landscape of AI-enabled fraud

## Instructions

### SAFETY CHECK — Act Immediately If Money Was Already Sent

**STOP.** Before classifying the scam, the agent MUST ask:

> "Have you already sent money, shared financial information, or given anyone access to your accounts?"

- If YES: **Skip directly to Step 3 (immediate recovery actions).** Time is critical for recovering funds. Classification can wait.
- If NO but personal info was shared: **Skip to Step 5 (identity theft recovery)** after classification.
- If NO to both: Proceed to Step 1.

**Agent action**: Prioritize damage control over education. If funds were sent, every minute matters.

### Step 1: Identify the scam type

Ask the user what happened. Classify it into one of the six major AI scam categories below, then jump to that section.

```
AI SCAM CATEGORIES:

A. VOICE CLONING — A call from someone who sounds like a person you know
B. DEEPFAKE VIDEO — A video call where the person isn't who they appear to be
C. AI PHISHING — Highly personalized, perfectly written emails or messages
D. FAKE JOB OFFERS — AI-generated job postings, interviews, or recruiters
E. AI ROMANCE SCAMS — Dating profiles with AI-generated photos and conversation
F. AI INVESTMENT SCAMS — Fake pitches with AI-generated decks, sites, and testimonials
```

### Step 2: Understand how each scam works and how to spot it

#### A. Voice Cloning Scams

**How it works:** Scammers scrape a few seconds of someone's voice from social media, voicemail, or public videos. AI tools can clone that voice convincingly. They call a family member — often a parent or grandparent — pretending to be in an emergency. "Mom, I'm in jail, I need bail money." "Dad, I was in a car accident, please wire money now."

```
HOW TO SPOT IT:

-> The call creates extreme urgency ("I need money RIGHT NOW")
-> They ask you not to call anyone else to verify
-> They request unusual payment: wire transfer, gift cards, crypto
-> The story involves arrest, accident, kidnapping, or hospitalization
-> If you ask a personal question they should know, they deflect

VERIFICATION PROTOCOL:
1. Hang up. No matter how real it sounds. Hang up.
2. Call the person directly on their known number.
3. If they don't answer, call another family member who can verify.
4. Establish a family safe word — a code word that proves identity.
   Pick something obscure that would never appear in public posts.
5. Never act on urgency alone. Real emergencies can wait 5 minutes
   for you to verify.
```

#### B. Deepfake Video Call Scams

**How it works:** Real-time deepfake software can make someone look and sound like another person on a video call. This has been used to impersonate CEOs authorizing wire transfers, fake business partners, and even fake kidnapping proof. In 2024, a finance worker transferred $25 million after a deepfake video call with a fake CFO.

```
HOW TO SPOT IT:

-> Lighting on the face doesn't match the background
-> Slight lag between lip movement and audio
-> Unnatural blinking patterns (too much or too little)
-> The person avoids turning their head to the side
-> Hair edges look blurry or shimmer unnaturally
-> They resist or deflect requests to do something spontaneous
   (hold up a specific number of fingers, turn sideways)

VERIFICATION PROTOCOL:
1. Ask them to do something unpredictable:
   "Hold up three fingers on your left hand"
   "Turn your head to the right and back"
   "Hold a piece of paper with today's date written on it"
2. Deepfakes struggle with sudden lateral movement and hand gestures.
3. For any financial request over video, ALWAYS verify through a
   separate, established communication channel.
4. Call them on a known phone number to confirm the request.
5. Company policy should require multi-person authorization for
   transfers — never rely on one video call.
```

#### C. AI Phishing Emails

**How it works:** AI generates phishing emails that are personalized, grammatically perfect, and contextually accurate. They scrape your LinkedIn, social media, and public data to craft messages that reference your real job, colleagues, and recent activity. No more "Dear Valued Customer" with obvious typos.

```
HOW TO SPOT IT:

-> Check the sender's ACTUAL email address (not the display name).
   Hover over it. Look for subtle misspellings:
   support@amaz0n.com, hr@company-careers.net
-> The email creates urgency: "Your account will be closed in 24 hours"
-> It asks you to click a link or download an attachment
-> The link URL doesn't match the real company's domain
-> They reference real details about you (scraped from public profiles)
   but get small things wrong
-> The request bypasses normal processes ("Don't go through the usual
   channel, just handle this directly")

DEFENSE PROTOCOL:
1. NEVER click links in unexpected emails. Go directly to the website.
2. Check the full email header for the actual sending domain.
3. If it claims to be from a colleague, verify via Slack/Teams/phone.
4. Enable multi-factor authentication on EVERYTHING.
5. Use a password manager — it won't autofill on fake domains.
6. When in doubt, forward the email to the real company's
   abuse/phishing address (e.g., phishing@company.com).
```

#### D. Fake Job Offers with AI Interviews

**How it works:** Scammers create convincing job postings on real job boards. The "company" has a professional website (AI-generated). The "recruiter" reaches out on LinkedIn. The interview is conducted over chat or a one-way video platform — sometimes with an AI interviewer. The scam ends with: (a) harvesting your personal data (SSN, bank details for "direct deposit setup"), (b) sending you a fake check to "buy equipment," or (c) charging you for "training" or "background check."

```
HOW TO SPOT IT:

-> The job was not posted on the company's actual careers page
-> Interview is text-only or on an obscure video platform
-> They "hire" you unusually fast with minimal vetting
-> They ask for SSN, bank details, or payment before your start date
-> The salary is significantly above market rate for the role
-> Communication comes from a free email domain (gmail, outlook)
   rather than a corporate one
-> They send you money before you've done any work

VERIFICATION PROTOCOL:
1. Search the company name + "scam" or "fake job"
2. Go to the company's REAL website and find their careers page.
   Is the job listed there?
3. Look up the recruiter on LinkedIn. Check their profile age,
   connections, and activity history.
4. Call the company's main phone number and ask to speak to
   the hiring manager or HR department.
5. NEVER pay anything to get a job. Legitimate employers never
   charge for training, equipment, or background checks.
6. NEVER share your SSN until you have a verified, signed offer
   from a confirmed real company.
```

#### E. AI Romance Scams

**How it works:** AI-generated profile photos (no reverse image search results), AI chatbots that maintain engaging conversation 24/7, and even AI-generated voice messages. The scammer builds emotional connection over weeks or months, then introduces a financial need — medical emergency, business opportunity, travel costs to meet you.

```
HOW TO SPOT IT:

-> Their photos look perfect but have no online presence elsewhere
-> Reverse image search returns zero results (real people have
   digital footprints; AI-generated faces don't)
-> They can never video call, or calls are brief and low quality
-> The relationship progresses unusually fast emotionally
-> They're always overseas, military, or working on an oil rig
-> After weeks of connection, a financial need emerges
-> They get defensive or guilt-trip you when you ask for verification

VERIFICATION PROTOCOL:
1. Reverse image search their photos (Google Images, TinEye)
2. Look for AI generation artifacts: asymmetric earrings,
   blurred backgrounds where hands meet objects, inconsistent
   teeth, warped text on clothing
3. Ask for a live video call where they hold up a specific object
4. NEVER send money to someone you haven't met in person
5. Ask a trusted friend to review the conversation objectively --
   isolation from outside perspective is the scammer's main tool
```

#### F. AI Investment Scams

**How it works:** Scammers use AI to generate professional-looking pitch decks, fake financial reports, fabricated testimonials, cloned investment platform interfaces, and even deepfake endorsement videos from celebrities or known investors. The "platform" shows impressive returns on your initial investment. When you invest more and try to withdraw, you can't.

```
HOW TO SPOT IT:

-> Guaranteed returns (no legitimate investment guarantees returns)
-> The "platform" or "fund" isn't registered with the SEC
-> Celebrity endorsements (almost always fake — verify independently)
-> Initial small investment shows amazing returns (to hook you)
-> Withdrawal requires an additional "fee" or "tax" payment
-> Pressure from a friend or online community (who are also victims
   or in on the scam)
-> The pitch deck and website look polished but the company has
   no verifiable history

VERIFICATION PROTOCOL:
1. Check SEC EDGAR database: sec.gov/cgi-bin/browse-edgar
2. Search FINRA BrokerCheck: brokercheck.finra.org
3. Search the platform name + "scam" or "review"
4. Verify any celebrity endorsements on the celebrity's official channels
5. If it's crypto: check the token on CoinGecko/CoinMarketCap.
   No listing = red flag.
6. NEVER invest money you can't afford to lose based on social
   media recommendations or unsolicited messages.
```

### Step 3: If you already fell for it

Time matters. Act immediately.

```
IMMEDIATE ACTIONS (do these NOW):

1. STOP ALL CONTACT with the scammer. Block them everywhere.

2. SECURE YOUR ACCOUNTS:
   -> Change passwords on all financial accounts
   -> Enable multi-factor authentication everywhere
   -> If you shared login credentials, change them on every site
      where you used that password

3. CONTACT YOUR FINANCIAL INSTITUTIONS:
   -> Credit card: Call issuer, dispute charges, request new card
   -> Bank transfer/wire: Call bank immediately — wires can sometimes
      be recalled within 24 hours
   -> Crypto: Likely unrecoverable, but report to the platform
   -> Payment apps (Zelle, Venmo, CashApp): Report unauthorized
      transaction through the app AND your bank
   -> Gift cards: Call the gift card company with the receipt

4. FREEZE YOUR CREDIT (free, do all three):
   -> Equifax: 1-800-525-6285 or equifax.com/personal/credit-report-services
   -> Experian: 1-888-397-3742 or experian.com/freeze
   -> TransUnion: 1-800-680-7289 or transunion.com/credit-freeze

5. DOCUMENT EVERYTHING:
   -> Screenshot all messages, emails, call logs, transaction records
   -> Save the scammer's profile, phone number, email, website URLs
   -> Write a timeline while your memory is fresh
```

### Step 4: Report the scam (FTC complaint process)

Reporting matters. It helps law enforcement track patterns and may help you recover funds.

```
REPORTING CHECKLIST:

1. FTC (Federal Trade Commission):
   -> Go to reportfraud.ftc.gov
   -> Select the category that matches your scam
   -> Provide all details: dates, amounts, contact info, method
   -> You will receive a reference number — save it

2. FBI Internet Crime Complaint Center (IC3):
   -> Go to ic3.gov
   -> File a complaint (especially for scams involving internet,
      email, social media, or cryptocurrency)

3. Identity Theft (if personal info was compromised):
   -> Go to identitytheft.gov
   -> Follow the step-by-step recovery plan
   -> This generates an Identity Theft Report (an official document
      that gives you specific legal rights)

4. State Attorney General:
   -> Search "[your state] attorney general consumer complaint"
   -> File online

5. Local Police:
   -> File a report and get a report number
   -> You may need this for insurance claims or bank disputes

6. Platform-Specific Reporting:
   -> Report the scam profile/listing on the platform where it occurred
   -> LinkedIn, job boards, dating apps, social media all have
      fraud reporting tools
```

### Step 5: Identity theft recovery

If you shared your SSN, date of birth, or other identity documents:

```
IDENTITY THEFT RECOVERY STEPS:

1. File an Identity Theft Report at identitytheft.gov
   -> This creates your official FTC Identity Theft Report
   -> This gives you legal rights: extended fraud alerts,
      blocking fraudulent debts, preventing debt collection

2. Place an Extended Fraud Alert (7 years):
   -> Call any one credit bureau (they notify the others)
   -> Requires the Identity Theft Report from step 1

3. Review your credit reports:
   -> Free at annualcreditreport.com
   -> Check all three bureaus for accounts you don't recognize

4. Close any fraudulent accounts:
   -> Call each company where fraud occurred
   -> Send them your Identity Theft Report
   -> They must close the account and stop collecting the debt

5. Monitor ongoing:
   -> Sign up for free credit monitoring
   -> Check your credit reports every 4 months (rotate bureaus)
   -> Watch for tax fraud: file your taxes early each year
   -> Watch for medical identity theft: review Explanation of
      Benefits statements from your health insurance

6. Consider an IRS Identity Protection PIN:
   -> irs.gov/identity-theft-fraud-scams/get-an-identity-protection-pin
   -> Prevents someone from filing a tax return using your SSN
```

## If This Fails

If recovery actions are not working:

1. **Bank won't reverse the transfer?** File a complaint with the CFPB at [consumerfinance.gov/complaint](https://www.consumerfinance.gov/complaint/). Also file with your state attorney general and the FTC.
2. **Credit freeze not working or identity already used?** File an Identity Theft Report at [identitytheft.gov](https://www.identitytheft.gov/) — this generates an official report that gives you specific legal rights including the ability to block fraudulent accounts.
3. **Scammer still contacting you?** Block on all platforms. If threats are made, file a police report and contact the FBI at [ic3.gov](https://www.ic3.gov/).
4. **Emotional distress from being scammed?** Call 988 or contact NAMI (1-800-950-NAMI). Being scammed is not your fault — these operations are sophisticated criminal enterprises.
5. **Crypto funds lost?** Report to the platform and to [ic3.gov](https://www.ic3.gov/). Be wary of "recovery services" that contact you — many are secondary scams targeting victims.

## Rules

- Never blame the victim — AI scams are designed to be convincing, and falling for one says nothing about intelligence
- Urgency is the most important red flag. Any time someone pressures immediate action, slow down.
- If the user has already sent money, treat it as time-sensitive and move immediately to Step 3
- For elderly users, suggest involving a trusted family member and setting up a family safe word
- Always recommend credit freeze after any personal information exposure

## Tips

- A family safe word is the single best defense against voice cloning scams. Pick one today. Share it only in person.
- Password managers are the best defense against phishing — they won't autofill your credentials on a fake domain.
- "Can you verify that through another channel?" is the most powerful question you can ask. Scammers can control one channel but not two.
- AI-generated faces often have subtle tells: asymmetric accessories, inconsistent backgrounds, and unnaturally smooth skin. But the technology improves constantly — don't rely only on visual inspection.
- Scammers increasingly use real company names and branding. The domain name is always the ground truth. Check it character by character.
- If a deal, job, or relationship seems too good to be true, the AI just made it easier to make it look real. The old wisdom still applies.

## Agent State

Persist across sessions:

```yaml
defense:
  scam_encountered:
    type: null
    date_discovered: null
    date_occurred: null
    amount_lost: null
    payment_method: null
    personal_info_exposed: []
    scammer_contact_info: []
    evidence_saved: false
  recovery_actions:
    accounts_secured: false
    credit_frozen: false
    ftc_reported: false
    ftc_reference_number: null
    ic3_reported: false
    identity_theft_report_filed: false
    police_report_filed: false
    police_report_number: null
    platform_reported: false
    financial_institutions_contacted: []
    fraudulent_accounts_closed: []
  prevention:
    family_safe_word_set: false
    mfa_enabled: false
    password_manager_in_use: false
    credit_monitoring_active: false
    irs_pin_set: false
  follow_up:
    credit_review_dates: []
    next_check_in: null
```

## Automation Triggers

```yaml
triggers:
  - name: immediate_financial_response
    condition: "scam_encountered.amount_lost > 0 AND recovery_actions.financial_institutions_contacted IS EMPTY"
    action: "You reported a financial loss but haven't contacted your financial institutions yet. This is time-sensitive — calling your bank or card issuer now gives you the best chance of recovering funds. Let's do that first."

  - name: credit_freeze_reminder
    condition: "scam_encountered.personal_info_exposed IS NOT EMPTY AND recovery_actions.credit_frozen IS false"
    action: "You shared personal information with the scammer. Your credit should be frozen at all three bureaus to prevent identity theft. This is free and takes about 10 minutes. Ready to walk through it?"

  - name: reporting_follow_up
    condition: "scam_encountered.date_discovered IS SET AND recovery_actions.ftc_reported IS false AND days_since(scam_encountered.date_discovered) >= 1"
    action: "It's been a day since you discovered the scam. Filing your FTC report helps law enforcement track these operations and may help others avoid the same scam. Let's file at reportfraud.ftc.gov."

  - name: identity_recovery_check
    condition: "recovery_actions.identity_theft_report_filed IS true"
    schedule: "monthly for 12 months"
    action: "Monthly identity theft recovery check-in: Have you reviewed your credit reports? Any unfamiliar accounts or inquiries? Any unexpected Explanation of Benefits from your health insurance? Any IRS notices?"

  - name: prevention_setup
    condition: "recovery_actions.credit_frozen IS true AND prevention.family_safe_word_set IS false"
    action: "Now that the immediate crisis is handled, let's set up prevention. A family safe word is the single best defense against voice cloning scams. Have you picked one and shared it with your family?"
```
