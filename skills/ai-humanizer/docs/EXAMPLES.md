# Real-world before/after examples

## Example 1: Tech product description

**Before (score: 72):**
> Great question! Here is a comprehensive overview of our groundbreaking platform.
>
> Our platform serves as a testament to the transformative power of AI, marking a pivotal moment in the evolution of enterprise software. In today's rapidly evolving landscape, businesses need cutting-edge solutions that streamline operations, enhance productivity, and foster collaboration.
>
> The platform boasts a robust suite of tools, showcasing our commitment to innovation. Additionally, the seamless integration capabilities highlight the intricate interplay between modern workflows and AI-driven automation, ensuring organizations can harness the full potential of their data.
>
> Industry experts believe our platform plays a crucial role in digital transformation. The future looks bright as exciting times lie ahead. I hope this helps! Let me know if you'd like more details.

**After (score: 2):**
> The platform connects to Salesforce, Slack, and Jira through pre-built integrations. Setup takes about 20 minutes.
>
> We added AI-powered search in March. It finds relevant documents across connected apps. In our beta with 50 companies, users said they spent 30% less time looking for files. That number came from self-reported surveys, so take it with some salt.
>
> The pricing starts at $15/user/month. There's a free tier for teams under 5.

**Patterns removed:** Chatbot artifacts (19), significance inflation (1), promotional language (4), AI vocabulary (7), copula avoidance (8), -ing analyses (3), vague attributions (5), filler phrases (22), generic conclusions (24)

---

## Example 2: City description

**Before (score: 65):**
> Nestled within the breathtaking Pacific Northwest, Portland stands as a vibrant city with a rich cultural heritage and stunning natural beauty. The city boasts a thriving arts scene, showcasing local talent and fostering community engagement.
>
> Portland's culinary landscape is equally impressive, featuring a diverse array of restaurants. Experts believe the city plays a crucial role in the regional economy, with industry reports suggesting continued growth. Despite its challenges, Portland continues to thrive.

**After (score: 6):**
> Portland has about 650,000 people and sits on the Willamette River, 60 miles from the Pacific coast. It rains a lot — around 155 days a year — which partly explains why there are so many coffee shops and bookstores.
>
> The food cart scene is the main draw for visitors. There are over 500 licensed food carts, more per capita than any other US city. The tech sector grew after Intel and Nike established headquarters nearby in the 1990s.

**Patterns removed:** Promotional language (4), copula avoidance (8), -ing analyses (3), AI vocabulary (7), vague attributions (5), formulaic challenges (6)

---

## Example 3: Email draft

**Before (score: 58):**
> Dear Team,
>
> I hope this email finds you well! I wanted to take a moment to delve into our Q3 results, which serve as a testament to our team's enduring commitment to excellence.
>
> It's not just about the numbers; it's about the journey. Our performance showcases the intricate interplay between strategy and execution, highlighting our ability to navigate challenges while fostering innovation, collaboration, and growth.
>
> In order to continue this momentum, it is important to note that we need to align our efforts with the evolving landscape. The future looks bright!
>
> Let me know if you have any questions. I hope this helps!

**After (score: 3):**
> Hi team,
>
> Q3 results are in. Revenue hit $2.4M, up 12% from Q2. The Harris account drove most of that — they expanded their contract in August.
>
> Two things to watch for Q4: the enterprise pipeline is thinner than I'd like, and we still haven't backfilled the two sales roles. I'd like to have candidates by mid-October.
>
> Full deck is attached. Let's discuss at Thursday's standup.

**Patterns removed:** Chatbot artifacts (19), AI vocabulary (7), significance inflation (1), copula avoidance (8), -ing analyses (3), negative parallelisms (9), filler phrases (22), generic conclusions (24)

---

## Example 4: Blog post intro

**Before (score: 45):**
> In today's rapidly evolving world of artificial intelligence, the landscape of machine learning continues to transform at an unprecedented pace. This groundbreaking technology has garnered significant attention from industry leaders and researchers alike, showcasing its potential to revolutionize various sectors.
>
> Furthermore, the multifaceted nature of deep learning encompasses a myriad of applications, from natural language processing to computer vision, highlighting the comprehensive scope of this transformative paradigm.

**After (score: 0):**
> Machine learning models got noticeably better in 2024. GPT-4o handles images and audio. Claude writes code that usually works on the first try. Stable Diffusion 3 makes hands that look right.
>
> The practical question isn't whether the technology works — it's whether it works well enough for your specific use case, and at what cost. A fine-tuned model for classifying support tickets costs a few hundred dollars and saves real time. A custom LLM to replace your writing staff probably doesn't.

**Patterns removed:** Filler (22), AI vocabulary (7), promotional language (4), -ing analyses (3), false ranges (12)
