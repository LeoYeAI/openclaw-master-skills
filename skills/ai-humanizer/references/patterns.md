# AI writing patterns — full catalog

Comprehensive reference for all 24 AI writing patterns detected by humanizer. Each entry includes the pattern description, detection signals, and before/after examples.

## Content patterns (1-6)

### 1. Significance inflation

LLMs puff up the importance of mundane things with claims about legacy, evolution, and broader trends.

**Signals:** "pivotal moment", "testament to", "vital/crucial/significant role", "evolving landscape", "setting the stage for", "indelible mark", "deeply rooted", "shaping the future"

**Before:**
> The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics in Spain.

**After:**
> The Statistical Institute of Catalonia was established in 1989 to collect and publish regional statistics independently from Spain's national statistics office.

---

### 2. Notability name-dropping

LLMs list media outlets and sources to claim notability without providing specific claims or context.

**Signals:** Comma-separated lists of publications, "active social media presence", "written by a leading expert"

**Before:**
> Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu. She maintains an active social media presence with over 500,000 followers.

**After:**
> In a 2024 New York Times interview, she argued that AI regulation should focus on outcomes rather than methods.

---

### 3. Superficial -ing analyses

AI tacks present participle phrases onto sentences to fake analytical depth.

**Signals:** Trailing clauses starting with: highlighting, underscoring, emphasizing, ensuring, reflecting, symbolizing, contributing to, cultivating, fostering, encompassing, showcasing

**Before:**
> The temple's color palette resonates with the region's natural beauty, symbolizing Texas bluebonnets, reflecting the community's deep connection to the land.

**After:**
> The temple uses blue, green, and gold. The architect said these reference local bluebonnets and the Gulf coast.

---

### 4. Promotional language

Tourism-brochure language that sounds like ad copy rather than neutral description.

**Signals:** "nestled", "breathtaking", "stunning", "renowned", "groundbreaking", "must-visit", "in the heart of", "rich cultural heritage", "world-class", "unparalleled"

**Before:**
> Nestled within the breathtaking region of Gonder, this vibrant town boasts a rich cultural heritage and stunning natural beauty.

**After:**
> Alamata Raya Kobo is a town in the Gonder region of Ethiopia, known for its weekly market and 18th-century church.

---

### 5. Vague attributions

Attributing claims to unnamed experts, studies, or reports instead of specific sources.

**Signals:** "Experts believe", "Industry reports suggest", "Studies show", "Observers have noted", "widely regarded"

**Before:**
> Experts believe it plays a crucial role in the regional ecosystem.

**After:**
> The river supports several endemic fish species, according to a 2019 survey by the Chinese Academy of Sciences.

---

### 6. Formulaic challenges

Boilerplate "despite challenges" sections that follow a predictable template.

**Signals:** "Despite its challenges", "continues to thrive", "future outlook remains", "challenges typical of"

**Before:**
> Despite its industrial prosperity, the area faces challenges typical of urban areas. Despite these challenges, it continues to thrive.

**After:**
> Traffic congestion increased after 2015 when three new IT parks opened. A stormwater drainage project began in 2022 to address recurring floods.

---

## Language patterns (7-12)

### 7. AI vocabulary

Words that appear far more frequently in AI-generated text than human writing.

**High-frequency words:** additionally, delve, tapestry, testament, underscore, pivotal, landscape (abstract), intricate/intricacies, showcasing, fostering, garner, interplay, enduring, vibrant, crucial, enhance

**Medium-frequency words:** furthermore, moreover, notably, comprehensive, multifaceted, nuanced, paradigm, transformative, leveraging, synergy, holistic, robust, streamline, utilize, facilitate, elucidate, encompassing, cornerstone, reimagine, empower, harness, navigate, realm, poised, myriad

**Before:**
> Additionally, a testament to Italian colonial influence is the widespread adoption of pasta in the local culinary landscape, showcasing integration into the traditional diet.

**After:**
> Pasta dishes, introduced during Italian colonization, remain common, especially in the south.

---

### 8. Copula avoidance

Using elaborate constructions where simple "is" or "has" works better.

**Signals:** "serves as", "stands as", "functions as", "boasts", "features" (as replacement for "has")

**Before:**
> Gallery 825 serves as LAAA's exhibition space. The gallery features four spaces and boasts over 3,000 square feet.

**After:**
> Gallery 825 is LAAA's exhibition space. The gallery has four rooms totaling 3,000 square feet.

---

### 9. Negative parallelisms

"Not just X, it's Y" and "Not only X but also Y" — overused rhetorical frame.

**Before:**
> It's not just about the beat; it's part of the aggression. It's not merely a song, it's a statement.

**After:**
> The heavy beat adds to the aggressive tone.

---

### 10. Rule of three

Forcing ideas into groups of three to sound comprehensive.

**Before:**
> Attendees can expect innovation, inspiration, and industry insights.

**After:**
> The event includes talks, panels, and informal networking.

---

### 11. Synonym cycling

Referring to the same thing by different names in consecutive sentences.

**Before:**
> The protagonist faces many challenges. The main character must overcome obstacles. The central figure eventually triumphs. The hero returns home.

**After:**
> The protagonist faces many challenges but eventually triumphs and returns home.

---

### 12. False ranges

"From X to Y" where X and Y aren't on a meaningful scale.

**Before:**
> Our journey has taken us from the singularity of the Big Bang to the grand cosmic web, from the birth of stars to the dance of dark matter.

**After:**
> The book covers the Big Bang, star formation, and current theories about dark matter.

---

## Style patterns (13-18)

### 13. Em dash overuse

LLMs use em dashes more than humans, mimicking punchy sales writing.

**Before:**
> The term is promoted by Dutch institutions — not by the people themselves. You don't say "Netherlands, Europe" — yet this continues — even in official documents.

**After:**
> The term is promoted by Dutch institutions, not by the people. This mislabeling continues in official documents.

---

### 14. Boldface overuse

Mechanical emphasis of phrases in bold throughout the text.

**Before:**
> It blends **OKRs**, **KPIs**, and tools like the **Business Model Canvas** and **Balanced Scorecard**.

**After:**
> It blends OKRs, KPIs, and tools like the Business Model Canvas and Balanced Scorecard.

---

### 15. Inline-header lists

List items starting with bolded headers and colons, often repeating the header word.

**Before:**
> - **User Experience:** The user experience has been improved.
> - **Performance:** Performance has been enhanced.
> - **Security:** Security has been strengthened.

**After:**
> The update improves the interface, speeds up load times, and adds end-to-end encryption.

---

### 16. Title Case headings

Capitalizing every main word in headings.

**Before:**
> ## Strategic Negotiations And Global Partnerships

**After:**
> ## Strategic negotiations and global partnerships

---

### 17. Emoji overuse

Decorating headings or bullet points with emojis in professional text.

**Before:**
> 🚀 **Launch Phase:** The product launches in Q3
> 💡 **Key Insight:** Users prefer simplicity

**After:**
> The product launches in Q3. User research showed a preference for simplicity.

---

### 18. Curly quotes

ChatGPT uses Unicode curly quotes instead of straight quotes.

**Before:**
> He said \u201Cthe project is on track\u201D

**After:**
> He said "the project is on track"

---

## Communication patterns (19-21)

### 19. Chatbot artifacts

Leftover phrases from chatbot conversations pasted into content.

**Signals:** "I hope this helps!", "Let me know if...", "Here is an overview", "Of course!", "Certainly!", "I'd be happy to"

**Before:**
> Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand.

**After:**
> The French Revolution began in 1789 when financial crisis and food shortages led to widespread unrest.

---

### 20. Cutoff disclaimers

AI knowledge-cutoff disclaimers left in text.

**Signals:** "As of my last training", "While specific details are limited", "Based on available information"

**Before:**
> While specific details are not extensively documented, it appears to have been established in the 1990s.

**After:**
> The company was founded in 1994, according to its registration documents.

---

### 21. Sycophantic tone

Overly positive, people-pleasing language.

**Before:**
> Great question! You're absolutely right! That's an excellent point!

**After:**
> The economic factors you mentioned are relevant here.

---

## Filler and hedging (22-24)

### 22. Filler phrases

Wordy phrases that can be shortened.

| Filler | Replacement |
|--------|-------------|
| In order to | to |
| Due to the fact that | because |
| At this point in time | now |
| In the event that | if |
| Has the ability to | can |
| It is important to note that | (remove) |
| When it comes to | for |
| For the purpose of | to |
| First and foremost | first |

---

### 23. Excessive hedging

Stacking qualifiers instead of committing to a claim.

**Before:**
> It could potentially possibly be argued that the policy might have some effect.

**After:**
> The policy may affect outcomes.

---

### 24. Generic conclusions

Vague upbeat endings that say nothing.

**Signals:** "The future looks bright", "Exciting times lie ahead", "journey toward excellence", "poised for growth", "the possibilities are endless"

**Before:**
> The future looks bright. Exciting times lie ahead as they continue their journey toward excellence.

**After:**
> The company plans to open two more locations next year.
