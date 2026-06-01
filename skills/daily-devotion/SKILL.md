---
name: daily_devotion
description: Creates personalized daily devotions with verse of the day, pastoral message, structured prayer, and time-aware greetings
version: 1.1.0
author: Eric Kariuki
npm: daily-devotion-skill
repository: https://github.com/enjuguna/Molthub-Daily-Devotion
requirements:
  - Internet access for ourmanna API
  - Node.js/TypeScript runtime for helper scripts
---

# Daily Devotion Skill

This skill creates a complete, personalized daily devotion experience for the user. It fetches the verse of the day, generates a warm pastoral devotion message, crafts a structured prayer, and wishes the user well based on the time of day.

## Overview

The Daily Devotion skill provides:
1. **Verse of the Day** - Fetched from the ourmanna API
2. **Devotional Message** - A warm, pastoral reflection on the verse
3. **Structured Prayer** - A 6-part prayer following traditional Christian format
4. **Time-Aware Greeting** - Personalized farewell based on time of day

---

## Installation

Install the helper scripts from npm:

```bash
npm install daily-devotion-skill
```

Or use directly with npx:

```bash
npx daily-devotion-skill
```

**Repository:** [github.com/enjuguna/Molthub-Daily-Devotion](https://github.com/enjuguna/Molthub-Daily-Devotion)

---

## Step 1: Fetch the Verse of the Day

Call the ourmanna API to get today's verse:

```
GET https://beta.ourmanna.com/api/v1/get?format=json&order=daily
```

**Response Structure:**
```json
{
  "verse": {
    "details": {
      "text": "The verse text here...",
      "reference": "Book Chapter:Verse",
      "version": "NIV",
      "verseurl": "http://www.ourmanna.com/"
    },
    "notice": "Powered by OurManna.com"
  }
}
```

Extract and present:
- **Verse Text**: `verse.details.text`
- **Reference**: `verse.details.reference`
- **Version**: `verse.details.version`

Alternatively, run the helper script:
```bash
npx ts-node scripts/fetch_verse.ts
```

---

## Step 2: Generate the Devotional Message

Create a warm, pastoral devotion based on the verse. The tone should be like a caring pastor speaking directly to a beloved congregation member.

### Devotion Structure:

1. **Opening Hook** (1-2 sentences)
   - Start with a relatable life scenario or question that connects to the verse
   - Draw the reader in immediately

2. **Verse Context** (2-3 sentences)
   - Provide brief historical or cultural context of the passage
   - Explain who wrote it, to whom, and why

3. **Core Message** (3-4 sentences)
   - Unpack the meaning of the verse
   - Explain how it applies to modern life
   - Use warm, encouraging language

4. **Cross-References** (1-2 verses)
   - Include 1-2 related scripture references that reinforce the message
   - Briefly explain the connection

5. **Personal Application** (2-3 sentences)
   - Speak directly to the reader using "you"
   - Be encouraging and uplifting
   - Acknowledge struggles while pointing to hope

6. **Today's Challenge** (Dynamic - NEVER repeat the same challenge)
   - Provide ONE practical, actionable step the user can take today
   - **Vary the duration**: Use 3-15 minutes based on context and activity type
   - **Vary the activity**: Rotate between silence, meditation, journaling, action, prayer, worship
   - **Personalize**: Tailor to the verse theme and user's known context/profile
   
   **Example Challenge Templates (pick ONE and adapt to the verse):**
   1. "Set aside [3-10] minutes to [meditate/journal/reflect] on [theme from verse]..."
   2. "Before your next [meeting/task/meal], take [2-5] minutes to [action related to verse]..."
   3. "Write down [number] ways you can [apply verse principle] today..."
   4. "During your [commute/break/walk], spend [time] [speaking/listening/reflecting] on [verse theme]..."
   5. "Send a [message/note/text] to someone expressing [gratitude/encouragement/love] as the verse teaches..."
   6. "Tonight before bed, [specific reflection activity] for [3-7] minutes..."
   7. "Pause three times today to silently thank God for [verse-related blessing]..."
   8. "Choose one person to [encourage/forgive/help/pray for] as a response to this verse..."
   9. "Take a [5-10] minute prayer walk, focusing on [verse theme]..."
   10. "Write a short prayer in your own words inspired by today's scripture..."
   11. "Find a quiet moment to read [related passage] and compare its message to today's verse..."
   12. "Speak today's verse out loud [3-5] times to let it sink into your spirit..."
   13. "Share this verse with someone who might need its encouragement today..."
   14. "Before each meal today, reflect on one aspect of [verse theme]..."
   15. "Create a simple reminder (phone wallpaper, sticky note) of today's verse..."
   16. "At the end of your workday, spend [5] minutes reviewing how you applied this verse..."
   17. "Listen to a worship song that reflects the theme of [verse theme]..."
   18. "Journal about a time when you experienced [the truth of this verse]..."
   19. "Take [10] minutes to sit in complete silence, letting God's [grace/peace/love] wash over you..."
   20. "Identify one habit you can adjust today to better align with [verse principle]..."
   21. "Practice [forgiveness/patience/gratitude/trust] in your next challenging interaction..."
   22. "Memorize today's verse by writing it out [3-5] times..."
   23. "Invite the Holy Spirit to reveal one area of your life that needs [verse theme]..."
   24. "Set an alarm for [time] to pause and re-read today's verse wherever you are..."

### Tone Guidelines:
- **Warm and pastoral** - Like a loving shepherd caring for sheep
- **Encouraging** - Focus on hope, not condemnation
- **Personal** - Use "you" and "we" to create connection
- **Accessible** - Avoid overly theological jargon
- **Uplifting** - Leave the reader feeling encouraged and empowered

---

## Step 3: Handle Prayer Context

> [!IMPORTANT]
> **Do NOT ask the user for prayer requests interactively.** Prayer requests should be included in the initial prompt when the user invokes the skill.

**If prayer requests are provided in the prompt:**
- Incorporate them naturally into Part 4 of the prayer
- Be sensitive and respectful with personal matters
- If work-related, refer to it simply as "work" or "workplace"
- If health-related, pray for healing and strength
- If relationship-related, pray for wisdom and reconciliation
- If finances are mentioned, pray for provision and wise stewardship

**If no prayer context is provided:**
- Use general prayers for daily guidance and protection
- Pray for the user's family and loved ones generically
- Focus more on the verse application

---

## Step 4: Craft the Structured Prayer

> [!IMPORTANT]
> **ALWAYS use FIRST-PERSON perspective** in the prayer. Use "I", "my", "me" when referring to the user—NEVER refer to them by name in third-person (e.g., say "my family" not "Eric's family").

Create a prayer following this 6-part structure. The prayer should flow naturally as one continuous conversation with God.

> [!CAUTION]
> **NEVER repeat the same phrases across different devotions.** Each prayer should feel fresh and unique. Rotate through the example phrases and create new variations.

### Part 1: Praising the Lord
Begin by glorifying God's attributes. **ROTATE through varied openings:**

**Example Openings (vary each time - pick ONE):**
1. "Heavenly Father, I come before You in awe of Your majesty..."
2. "Lord God, I bow in worship before Your throne of grace..."
3. "Almighty God, my heart overflows with praise for who You are..."
4. "Father of lights, I lift my voice to exalt Your holy name..."
5. "Sovereign Lord, I stand amazed at Your greatness..."
6. "Gracious God, I enter Your presence with thanksgiving and praise..."
7. "Most High God, I worship You for Your unmatched glory..."
8. "Eternal Father, my soul magnifies Your wonderful name..."
9. "Lord of all creation, I honor You with all that I am..."
10. "Holy One of Israel, I come with reverence into Your presence..."
11. "Mighty God, I celebrate Your power and endless love..."
12. "Faithful Father, I praise You for Your steadfast devotion..."
13. "King of Kings, I kneel before Your awesome throne..."
14. "God of all comfort, I bless Your name this day..."
15. "Wonderful Counselor, I lift high Your glorious name..."
16. "Prince of Peace, I worship You with a grateful heart..."
17. "Ancient of Days, I stand in wonder at Your eternal nature..."
18. "Lord of Hosts, I exalt You above all earthly things..."
19. "Rock of Ages, I praise You for being my firm foundation..."
20. "Merciful Father, my spirit rejoices in Your abundant grace..."

**Rotate these attributes** (pick 2-3 per prayer): holiness, love, power, faithfulness, mercy, sovereignty, wisdom, patience, justice, goodness, omniscience, immutability, compassion, righteousness, majesty, glory, tenderness, protective nature

### Part 2: Thanking the Lord
Express gratitude with variety. **Pick 3-4 themes per prayer (not all):**

**Gratitude Themes (rotate selection):**
1. The gift of a new day and fresh mercies
2. Life, breath, and the health in my body
3. His Word that guides and instructs my steps
4. Salvation and grace through Jesus Christ
5. Family members who love and support me
6. Provision of food, shelter, and daily needs
7. Opportunities to serve and grow in faith
8. Progress on current projects and goals
9. Friendships and community that encourage me
10. The beauty of nature and creation around me
11. Peace in the midst of difficult circumstances
12. Past answered prayers and remembered blessings
13. The gift of rest and restoration
14. Wisdom granted in challenging decisions
15. Protection from seen and unseen dangers
16. The comfort of the Holy Spirit in times of grief
17. Second chances and fresh starts
18. The ability to work and create
19. Moments of joy and laughter
20. Freedom to worship without fear
21. Teachers and mentors who have shaped my journey
22. Technology and tools that assist my calling
23. The changing seasons that remind me of renewal
24. Healing received in body, mind, or spirit
25. Doors that have opened at the right time

### Part 3: Forgiveness of Sins
Humbly seek forgiveness with varied language:

**Example Phrases (rotate - pick 2-3):**
1. "Lord, I humbly acknowledge my imperfections and shortcomings..."
2. "Father, I confess that I have fallen short of Your glory..."
3. "Merciful God, I come seeking Your cleansing and renewal..."
4. "I ask forgiveness for sins known and unknown to me..."
5. "Create in me a clean heart, O God, and renew a right spirit within me..."
6. "Wash me and I shall be whiter than snow..."
7. "Help me turn from my failures and walk in Your light..."
8. "Lord, I repent of the times I have grieved Your Spirit..."
9. "Father, forgive my wandering thoughts and misplaced priorities..."
10. "I confess the words I should not have spoken..."
11. "Cleanse me from secret faults and hidden sins..."
12. "Lord, I acknowledge the times I chose my way over Yours..."
13. "Forgive me for the good I failed to do..."
14. "I lay down my pride and ask for Your mercy..."
15. "Search my heart, O God, and reveal anything that displeases You..."
16. "I confess my doubts and ask You to strengthen my faith..."
17. "Lord, I repent of worry and choosing fear over trust..."
18. "Forgive me for the times I have been unkind or impatient..."
19. "I ask pardon for neglecting time in Your presence..."
20. "Cleanse my heart from envy, bitterness, or resentment..."
21. "Lord, I confess where I have compromised my integrity..."
22. "Forgive me for loving comfort more than Your calling..."
23. "I repent of harsh judgments I have made against others..."
24. "Purify my motives and make my heart sincere before You..."

### Part 4: Prayer for Loved Ones and Context

> [!IMPORTANT]
> **Use FIRST-PERSON**: "my family", "my friends", "my work", "my nation"—NOT "Eric's family".

**For family and loved ones (rotate - pick 2-3):**
1. "I lift up my family and friends to You, Father..."
2. "Protect those I love and meet them where they are tonight..."
3. "Guide my loved ones in their own journeys of faith..."
4. "Surround my family with Your angels and keep them safe..."
5. "Grant wisdom to my parents/children as they navigate life..."
6. "Strengthen the bonds of love within my household..."
7. "Watch over my extended family and keep them in Your care..."
8. "Bless my friends with peace and joy in their daily lives..."
9. "I pray for reconciliation where there is division in my family..."
10. "Provide for my loved ones' needs according to Your riches..."
11. "Comfort those in my circle who are grieving or hurting..."
12. "Open doors of opportunity for my family members..."
13. "Protect my loved ones' minds, hearts, and spirits..."
14. "Draw those in my family who don't know You closer to Your love..."
15. "Give my family members courage to face their challenges..."
16. "Bless my friendships with depth, loyalty, and mutual encouragement..."
17. "Grant traveling mercies to my loved ones who are away..."
18. "Heal any brokenness in my family relationships..."
19. "Prosper my loved ones in their health, work, and purpose..."
20. "Unite my family in love and shared vision for the future..."

**For user's specific context (if provided in prompt):**
- Work: "Grant me wisdom and integrity in my work... favor with colleagues... clarity in complex tasks... patience in difficulties... success in my endeavors..."
- Health: "I ask for healing and strength in my body... relief from pain... restoration of energy... peace in the waiting..."
- Relationships: "Bring reconciliation and understanding to my relationships... soften hardened hearts... restore broken trust... renew love..."
- Finances: "Provide for my needs and grant me wise stewardship... open doors of provision... remove the burden of debt... bless the work of my hands..."
- Decisions: "Give me clarity and discernment as I face this decision... confirm Your will... close wrong doors... illuminate the right path..."
- Nation/World: "I pray for wisdom for the leaders of my nation... peace in troubled regions... justice for the oppressed... revival in the land..."

### Part 5: Prayer for the Verse
Connect the day's verse to the prayer with varied language:

**Example Phrases (rotate - pick 2-3):**
1. "Lord, write today's verse upon my heart..."
2. "Help me truly understand and live out this scripture..."
3. "May this truth from [reference] guide my every decision..."
4. "Let this word dwell richly in me today..."
5. "Transform my mind through the message of this verse..."
6. "I ask for strength to apply [brief verse theme] in my life..."
7. "Burn this scripture into my memory and my actions..."
8. "Let these words be a lamp to my feet throughout this day..."
9. "Help me meditate on this passage and draw wisdom from it..."
10. "May this verse reshape how I see my circumstances..."
11. "Embed this truth so deeply that it changes how I respond to challenges..."
12. "Let this scripture be my anchor when I feel unsteady..."
13. "Open my eyes to see new dimensions of this passage..."
14. "Help me share this truth with someone who needs it..."
15. "Let [verse theme] be my focus and my strength today..."
16. "May I return to this verse whenever I need Your guidance..."
17. "Use this word to correct, encourage, and direct my steps..."
18. "Plant this scripture as a seed that bears fruit in my life..."
19. "Let the power of this verse break through any doubt or fear..."
20. "May I embody the truth of [reference] in how I treat others..."
21. "Let this scripture increase my faith and trust in You..."
22. "Help me see Your character more clearly through this word..."

### Part 6: Closing
End with reverence and varied closings:

**Example Closings (rotate - pick ONE):**
1. "I commit this day into Your hands, trusting in Your perfect plan..."
2. "I surrender my worries and rest in Your strength alone..."
3. "I place my hopes and plans at Your feet..."
4. "With faith in Your promises, I step forward into this day..."
5. "I release control and embrace Your will for my life..."
6. "I lay down my burdens and take up Your peace..."
7. "I entrust everything I am and have to Your keeping..."
8. "With a heart full of expectation, I await Your movement..."
9. "I go forward knowing You go before me and behind me..."
10. "I rest in the assurance that You are working all things together..."
11. "I leave this time of prayer changed and renewed..."
12. "I walk out of this moment carrying Your presence with me..."
13. "I submit my agenda to Your greater purposes..."
14. "I trust that what You have started, You will complete..."
15. "I lean not on my own understanding but on Your wisdom..."
16. "I cast all my cares upon You, for You care for me..."
17. "I stand on Your promises and move forward with confidence..."
18. "I receive Your peace that surpasses all understanding..."
19. "I declare Your goodness over this day and all it holds..."
20. "I rise from this prayer filled with hope and gratitude..."

**Always end with:** "In Jesus' name I pray, Amen." (or "In Jesus' mighty name we pray, Amen.")

---

## Step 5: Time-Aware Greeting and Farewell

Based on the current time, provide an appropriate greeting and closing message.

### Time Determination:
- **Morning** (5:00 AM - 11:59 AM): "Good morning"
- **Afternoon** (12:00 PM - 4:59 PM): "Good afternoon"  
- **Evening** (5:00 PM - 8:59 PM): "Good evening"
- **Night** (9:00 PM - 4:59 AM): "Good night"

### Closing Messages:

**Morning:**
> "Have a blessed day ahead! May God's favor go before you in everything you do today. Remember, you are never alone – He walks with you every step of the way. ☀️"

**Afternoon:**
> "May the rest of your day be filled with God's peace and purpose. Keep pressing forward – you're doing great! 🌤️"

**Evening:**
> "As this day winds down, may you find rest in God's presence. Reflect on His goodness today and trust Him for tomorrow. 🌅"

**Night:**
> "Sleep well, knowing you are held in the loving arms of your Heavenly Father. Cast all your worries on Him, for He cares for you. May angels watch over you tonight. 🌙"

### Context-Aware Additions:
If the user shared specific context, add a relevant encouragement:
- **Work stress**: "Remember, your work is unto the Lord. He sees your efforts and will reward your faithfulness."
- **Health concerns**: "God is your healer. Rest in His promises and trust His timing."
- **Family matters**: "Your prayers for your family are powerful. God hears every word and is working even when you can't see it."

---

## Complete Output Format

Present the complete devotion in this order:

```markdown
# 📖 Daily Devotion - [Date]

## Today's Verse
> "[Verse Text]"
> — [Reference] ([Version])

---

## Devotional Message

[Generated devotion following the structure above]

---

## 🙏 Today's Prayer

[Complete 6-part prayer flowing as one continuous prayer]

---

## [Time-appropriate greeting]

[Closing message with encouragement]
```

---

## Error Handling

If the API is unavailable:
1. Inform the user gracefully
2. Offer to use a backup verse from memory
3. Suggest popular verses like Jeremiah 29:11, Philippians 4:13, or Psalm 23:1

---

## Notes

- Always maintain a warm, loving tone throughout
- Be sensitive to the user's emotional state
- Never be preachy or condemning
- Focus on God's love, grace, and faithfulness
- Make the experience personal and meaningful
