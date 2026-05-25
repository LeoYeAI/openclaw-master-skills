# v2.1 Launch Posts - WORKING DRAFT

## Post 1 (Hook)

V2.1 of @slashlast30days launches today. Three headline features:

1. @openclaw + watchlists  - automated research on your competitors, people, and topics
2. YouTube transcripts as a 4th source
3. Works in OpenAI Codex

## Post 2 (Watchlist + Open Claw  - THE KILLER FEATURE)

@openclaw + WATCHLISTS.

Pair /last30days with @openclaw and it re-researches topics on a schedule across Reddit, X, YouTube, and the web.

"last30 watch my biggest competitor every week"
"last30 watch Peter Steinberger every 30 days"
"last30 watch AI video tools monthly"

Research that runs while you sleep. Designed for @openclaw and always-on bots.

## Post 3 (YouTube)

YOUTUBE IS NOW A 4TH SOURCE.

The skill searches YouTube, grabs view counts, and reads the actual transcripts. A 20-minute review has 10x the signal of one X post  - now the skill reads it.

## Post 4 (Codex)

WORKS IN OPENAI CODEX.

Same skill, same engine, same four sources. Install to ~/.agents/skills/last30days and invoke with $last30days. Claude Code and Codex users get the same research.

## Post 5 (Example: Seedance 2.0 access)

Asked it how to access Seedance 2.0.

3 Reddit threads. 31 X posts. 20 YouTube videos (685K views, 4 transcripts read). 10 web pages. All four sources hit.

It found the real answer buried in Chinese YouTube tutorials: Little Skylark (Xiao Yun Que)  - zero cost, no queue, no VPN. Just select Seedance 2.0 from the model dropdown. Also surfaced: Disney sent ByteDance a cease-and-desist over uncensored IP generation.

## Post 6 (Example: AI Generated Ads)

Asked it about AI generated ads.

12 Reddit threads. 29 X posts. 3 YouTube videos (83K views, 3 transcripts read). 30 web pages.

The finding that stuck: Svedka ran the first "primarily AI-generated" Super Bowl spot. Brand match: 7%. Industry norm: 63%. Meanwhile 86% of ad buyers are planning to use AI for video ads anyway. Cost is winning over quality.

## Post 7 (Example: Peter Steinberger)

Asked it about @steipete.

30 X posts. 5 YouTube videos (112K views). Found the Lex Fridman interview from 3 days ago.

Key reveal: OpenAI and Meta both made acquisition offers for OpenClaw. He said no. He's losing $10-20K/month maintaining it. "A fun project became a world project."

## Post 8 (Install)

Tell your @openclaw bot:

"Install the last30days skill from github.com/mvanhorn/last30days-skill"

That's it. One message.

## Post 9 (Close)

Thank you to @hutchins for pushing me to add YouTube and to @steipete whose summarize tool showed me how yt-dlp could power transcript extraction.

Try it: last30 [any topic]

github.com/mvanhorn/last30days-skill

PS: @steipete ClawHub login is broken right now so we can't publish the official skill there yet. Hoping for a fix soon.

---

## Standalone Posts

### Greg Isenberg best tips

Prompt: `last30 greg isenberg best tips`

1 Reddit thread. 6 X posts. 4 YouTube videos (all transcribed). 8 web pages.

His core playbook is ACP: Audience, Community, Product. Not the other way around.

Big thesis: "2026 is the GREATEST time to build a startup in 30 years." Boring industries, AI agents, rapid dev tools collapsing build time.

Most-watched: "Clawdbot Clearly Explained" (273K views), "Claude Code Built My $450K Marketing Campaign" (40K views), daily workflows with Kitze (83K views).

@gregisenberg @slashlast30days

### Lenny Rachitsky best learnings

Prompt: `last30 lenny rachitsky top learnings`

5 Reddit threads. 29 X posts. 20 YouTube videos (1.1M+ views, 5 transcribed). 30 web pages.

"Execution is no longer the bottleneck. Clarity is." That's the thesis running through everything @lennysan has been publishing lately.

He open-sourced 320 episode transcripts and the community went wild. 87 skills got built from them. Someone on Reddit distilled 86 discrete product skills from 100+ episodes.

Recent guest highlights: Sherwin Wu (OpenAI) says 95% of their engineers use Codex daily. Marc Andreessen: "This is as normal as it's going to be. It's going to be much weirder very soon." Dalton Caldwell (YC): "just don't die" and avoid tar pit ideas.

@lennysan @slashlast30days

---

## NOTES

- Thread leads with Open Claw + watchlist as the killer feature  - pair with an always-on bot for automated research
- YouTube is the #2 hero  - the stats ("685K views, 4 transcripts read") prove it works
- Codex compatibility is #3  - brief but shows cross-platform reach
- Example posts prove quality with verified results from real runs
- Consider screenshots of the actual output for each example post
- @steipete credit in close  - he inspired YouTube (yt-dlp toolchain) and X search (Bird MIT code)
- @slashlast30days vs /last30days  - which handle? Used /last30days above since it's the actual command

---

## RAW RESULTS (for reference / pulling quotes)

### Nano Banana Pro prompting (PROMPTING)  - VERIFIED 2/15

Stats: 0 Reddit (timed out) | 32 X posts | 164 likes | 22 reposts | 5 YouTube videos | 98,539 views | 5 with transcripts | 10 web pages
Top voices: @KusoPhoto (106 likes), @TzqQaiser (35 likes) | Jake Dawson (15K views), AI Master (37K views)

Key findings:
- Structured JSON prompts are the meta  - nested fields for character, scene, lighting beat plain prose. @TzqQaiser's viral post shows the format.
- Design brief > keyword stuffing  - "The second I started writing prompts like a real design brief, everything changed"  - Jake Dawson on YouTube
- 6-factor formula: Subject, Composition, Action, Setting, Style, then refine with camera/lighting  - per Google's official blog
- ICS framework for infographics: Image type + Content + Style  - leverages Nano Banana Pro's unique legible text rendering
- Scale logic for cinematic compositions  - define size relationships and camera distance explicitly, per @Strength04_X
- Nano Banana Pro → video pipeline trending (generate image, animate with Kling 3.0 or Veo 3.1)  - per @KusoPhoto

### Peter Steinberger / OpenClaw creator (GENERAL)  - VERIFIED 2/15

Stats: 31 X posts | 0 Reddit (quiet) | YouTube timed out on 2 | 4 web pages
Top voices: @steipete | Lex Fridman podcast

Key findings:
- Lex Fridman podcast (Feb 12) went viral  - "One of the most honest discussions I've seen"
- OpenAI and Meta made acquisition offers (conditional on keeping project open)  - he declined
- Losing $10-20K/month maintaining OpenClaw, rejected crypto tokenization for funding
- 180K+ GitHub stars, 6,600 commits in 1 month  - "A fun project became a world project"
- Also built: gogcli (Google Workspace CLI), summarize (URL/YouTube summarizer), bird (X/Twitter CLI)
- Pragmatic Engineer: "I ship code I don't read"
- Prediction: AI agents could dominate >60% of software economy by 2030

### Seedance 2.0 Prompting (PROMPTING)  - VERIFIED 2/15

Stats: 21 Reddit threads | 33 X posts | 20 YouTube videos | 5 web pages
Top voices: @charliebcurran (61K+ likes) | r/AI_Agents, r/ChatGPT, r/PromptEngineering | AI Search (127K views), Theoretically Media (157K views), Dan Dingle (126K views)

Key findings:
- "Slow and continuous" is the #1 prompting secret  - rough state transitions = worse outcomes, per r/AI_Agents
- Include timings in prompts (e.g., "0-3s: character walks, 3-6s: turns head")  - per r/ChatGPT
- Image-to-video for consistency  - start with a reference image, not text-only
- English works just as well as Chinese  - per r/AI_India
- CapCut integration coming = "every 12 year old in America will have this superpower"
- Cost: ~$0.55/10s clips (~$3.30/min), Seedance 3.0 rumored at 1/8th price
- Prompt resources: GitHub repo of curated prompts, Prompt Director Pro (440 settings system)
- Top YouTube tutorials: "Seedance 2.0 crushes everything" (127K), "Claims the AI Video Throne" (157K), "ABUSING China's Crazy New Video AI" (126K)

### OpenClaw best use cases for business (RECOMMENDATIONS)

Stats: 35 Reddit threads | ~1,130 upvotes | ~566 comments | 23 X posts | ~24 likes | 20 YouTube videos | ~1,572,000 views | 5 with transcripts | 10 web pages
Top voices: @gio__aa (8 likes), @ericosiu, @artyomx | r/openclaw, r/clawdbot, r/LocalLLaMA

Key findings:
- Email & Inbox Automation  - 8+ mentions. One user cleared 4,000+ emails in two days. 10-15 hours/week saved.
- Business Dashboards & Real-Time Reporting  - 6+ mentions. @gio__aa: "Business dashboards are going to become one of the most popular use cases."
- Morning Briefings  - 5+ mentions. Pulls from calendars, weather, emails, RSS, GitHub, Hacker News on a schedule.
- Content & SEO Pipelines  - 5+ mentions. @ericosiu claims "$45k of pSEO work in 20 minutes."
- Full CRM & Business Operations  - 4+ mentions. @artyomx runs a daycare business, legal cases, and family comms through it with 5 AI agents.
- Client Onboarding & Support  - 4+ mentions. "70% of tickets handled autonomously."
- Competitive Monitoring & Scraping  - 4+ mentions.
- Wrapper/Hosting SaaS  - 3+ mentions. Building commercial wrappers around OpenClaw as a business.

Cautions: malware in a top-downloaded skill (236 upvotes on r/LocalLLaMA), $25-50/day token burn risk, hours of config for marginal savings.

### YouTube thumbnail tips (GENERAL)

Stats: 7 Reddit threads | 654 upvotes | 176 comments | 32 X posts | 110 likes | 53 reposts | 18 YouTube videos | 6,150,368 views | 5 with transcripts | 30 web pages
Top voices: @TeamYouTube, @thewindwolf64 | r/NewTubers, r/YouTubeThumbnailHub | Think Media (1.17M views), whirow (1.46M views)

Key findings:
- Simplicity is #1  - r/NewTubers post (654 upvotes) from someone who designed 346 thumbnails: one subject, one message, one second to understand. 3+ elements = ~23% lower CTR.
- Less text = more clicks  - Under 4 words gets ~30% higher CTR. Mobile thumbnails shrink to 168x94px  - text becomes unreadable.
- Faces still win but subtlety is trending  - Faces boost CTR 20-30%, but exaggerated shock face is giving way to authentic expressions in 2026.
- "UnThumbnails" are a counter-trend  - Nate Black (71K views): deliberately raw, less-designed thumbnails that stand out.
- AI tools changing the game  - Nick Nimmin (90K views) showed free AI tools democratizing thumbnail creation.
- A/B test everything  - YouTube's built-in thumbnail testing lets you test up to 3 versions per video.

### AI SaaS crash (NEWS)

Stats: 9 Reddit threads | 31 upvotes | 52 comments | 32 X posts | 39 likes | 2 reposts | 20 YouTube videos | 929,648 views | 5 with transcripts | 30 web pages
Top voices: @jasonlk (15 likes), @WarrenInTheBuff (11 likes), @xankriegor_ | r/SaaS, r/aiwars

Key findings:
- "SaaSpocalypse"  - $285B wiped in a single day (Feb 3, 2026) after Anthropic launched Claude Cowork. Total losses exceeded $1T. Salesforce down 27% YTD, Oracle halved.
- @jasonlk: "The real inflection point wasn't January 2026. It was June 2024  - when Claude 3.5 Sonnet shipped." Public SaaS growth rates declined every quarter since 2021 peak.
- Seat-based pricing is the casualty  - 10 AI agents replace 100 sales reps = no need for 100 Salesforce seats. $470B+ hyperscaler AI spend coming from enterprise software budgets.
- Not everyone buying the doom  - Jensen Huang called it "the most illogical thing in the world." BofA called selloff irrational.
- Indian IT hit especially hard  - biggest sell-off since 2020.

### Seedance 2.0 access (GENERAL)  - VERIFIED 2/15, ALL 4 SOURCES

Stats: 3 Reddit threads | 114 upvotes | 183 comments | 31 X posts | 191 likes | 13 reposts | 20 YouTube videos | 685,297 views | 4 with transcripts | 10 web pages
Top voices: @markgadala (116 likes), @OrctonAI, @nemovideoai | Theoretically Media (158K views) | r/AIHubSpace

Key findings:
- Little Skylark (Xiao Yun Que) = best free method  - zero cost, no queue, manually select Seedance 2.0 from model dropdown, per YouTube tutorials
- Jimeng (Dreamina)  - 1 RMB trial (~$0.14), ~260 daily free credits, but severe congestion with hours-long waits for free users
- Doubao App  - 10 free video gens/day, requires joining Feishu/Lark group and submitting UID (1-2 day wait)
- Feb 24 = global unlock  - Dreamina + CapCut + API access through BytePlus
- IP controversy exploding  - @markgadala's "fully uncensored Seedance 2" post (116 likes) went viral, Disney sent C&D to ByteDance, SAG-AFTRA slammed "blatant infringement" over AI Tom Cruise/Brad Pitt fight videos
- Third-party race  - NemoVideoAI, ChatCut, RecCloud, Morph Studio all competing to be the English-language access point
- Quality consensus: "crushes everything" (AI Search, 128K views), "claims the AI video throne" (Theoretically Media, 158K views)

### AI Generated Ads (GENERAL)  - VERIFIED 2/15, ALL 4 SOURCES

Stats: 12 Reddit threads | 5 upvotes | 15 comments | 29 X posts | 101 likes | 3 reposts | 3 YouTube videos | 82,896 views | 3 with transcripts | 30 web pages
Top voices: @CaptainMcKlide (77 likes), @ugcbykaytelynn | r/editors, r/AI_UGC_Marketing, BERNTH (39K views)

Key findings:
- Super Bowl 2026 was the watershed  - 23% of ads (15/66) featured AI, reception "sharply negative," nearly 50% of social mentions critical
- Svedka ran the first "primarily AI-generated" national Super Bowl spot  - brand match of just 7% vs 63% alcohol industry norm
- Massive perception gap  - 82% of ad execs think Gen Z feels positive about AI ads, but only 45% of consumers do (IAB). Gen Z most hostile at 39% negative.
- AI UGC booming in e-commerce  - r/AI_UGC_Marketing active hub, tools: Creatify, MakeUGC, ArcAds targeting dropshippers
- Quality still low  - r/dropshipping: "the hand flip and rubbing on the face looks fake"
- @ugcbykaytelynn warns "AI generated ads RUIN your brand's image"
- Cost winning over quality  - 86% of ad buyers using or planning gen AI for video ads, cost efficiency #1 driver (64%), per IAB
- BERNTH on YouTube bought AI-generated guitar product ads, documented absurdity  - four-fingered hands, instruments don't match listings (39K views)
- Trust erosion spreading  - people now question whether ANY media is real, even billboards, per @N0rbertas

### last30days skill (META/GENERAL)  - VERIFIED 2/15

Stats: 0 Reddit | 30 X posts | 1,371 likes | 107 reposts | 5 YouTube videos | 112,082 views | 3 with transcripts | 10 web pages
Top voices: @gregisenberg (1,290 likes), @mvanhorn (34 likes) | Alejandro AO (39K views), Greg Isenberg (28K views)

Key findings:
- @gregisenberg's post (1,290 likes, 106 RT) + YouTube video (28K views) "The Claude Code Skill My Smartest Friends Use" was the breakout moment
- v2 feedback loop active  - @trevin flagged OpenAI web_search not finding niche Reddit posts, suggested Brave API. @jonthebeef submitted PR for --days flag.
- People building on top  - @tjarkoleifer created "re-skill" meta skill, @rajachirravuri recommends it as part of a PM stack
- Coverage: Alejandro AO crash course (39K views, 1,049 likes), Jason Calacanis on This Week in Startups (24K views)
- 1.5K GitHub stars, listed on skills.sh and Smithery
- Grok itself correctly attributed the skill when asked about ithah