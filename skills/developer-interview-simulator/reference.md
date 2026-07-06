# Developer Interview Simulator — Reference

Use this file for question banks, topic lists, and company-style prep. The agent should read it when running coding rounds, system design, tech Q&A, or company prep.

---

## Full Coding Problem Statements (use verbatim when presenting)

**Two Sum (Easy)**  
Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`. You may assume exactly one solution exists, and you may not use the same element twice.  
Constraints: `2 <= nums.length <= 10^4`; one valid answer exists.  
Example: `nums = [2, 7, 11, 15]`, `target = 9` → `[0, 1]`.  
Follow-up: Optimize for time; then discuss space.

**Valid Parentheses (Easy)**  
Given a string `s` containing only `(`, `)`, `{`, `}`, `[`, `]`, determine if the input string is valid. Valid means: open brackets closed by same type, in correct order.  
Example: `"()[]{}"` → true; `"(]"` → false.  
Follow-up: Time and space complexity; edge cases (empty string, single char).

**Longest Substring Without Repeating Characters (Medium)**  
Given a string `s`, find the length of the longest substring without repeating characters.  
Example: `"abcabcbb"` → 3 (`"abc"`); `"bbbbb"` → 1.  
Follow-up: Sliding window approach; time O(n), space O(min(n, alphabet)).

**LRU Cache (Medium)**  
Design a data structure that supports `get(key)` and `put(key, value)` in O(1) average time. Capacity is fixed; when full, evict the least recently used item.  
Follow-up: Hash map + doubly linked list; why not array or single linked list.

**Number of Islands (Medium)**  
Given a 2D grid of `'1'` (land) and `'0'` (water), return the number of islands. An island is surrounded by water and formed by connecting adjacent lands horizontally or vertically.  
Example: grid `[["1","1","0"],["1","1","0"],["0","0","1"]]` → 2.  
Follow-up: DFS vs BFS; time/space; how to modify for very large grid.

---

## Coding Problems (by difficulty)

**Easy**  
- Two Sum (array, hash map)  
- Valid Palindrome (two pointers)  
- Merge Two Sorted Lists (linked list)  
- Maximum Subarray (Kadane / DP)  
- Valid Parentheses (stack)  
- Reverse Linked List  
- Contains Duplicate (set/hash)  
- Binary Search (basic)

**Medium**  
- Add Two Numbers (linked list)  
- Longest Substring Without Repeating Characters (sliding window)  
- 3Sum (two pointers + sort)  
- Container With Most Water (two pointers)  
- LRU Cache (hash + doubly linked list)  
- Validate BST (tree, recursion)  
- Number of Islands (DFS/BFS)  
- Clone Graph (BFS/DFS + hash)  
- Top K Frequent Elements (heap or bucket sort)  
- Product of Array Except Self (prefix/suffix)

**Hard (use sparingly for senior)**  
- Merge K Sorted Lists (heap)  
- Serialize/Deserialize Binary Tree  
- Trapping Rain Water (two pointers / stack)  
- Longest Consecutive Sequence (set)

---

## System Design Topics

- URL Shortener (hash, redirect, scale)  
- Rate Limiter (token bucket, sliding window, distributed)  
- Chat / Messaging (WebSocket, persistence, scale)  
- News Feed (fan-out, ranking, caching)  
- Search Autocomplete (trie, top-k, latency)  
- Distributed Cache (e.g. Redis-style, consistency)  
- Design Pastebin / Paste Service  
- Design YouTube / Video Streaming (upload, encode, CDN)  
- Design Notifications (push, batch, channels)  
- Design a Key-Value Store (consistent hashing, replication)

For each: requirements (functional + scale), high-level components, APIs, data model, scaling, bottlenecks, trade-offs (consistency vs availability, etc.).

---

## System Design Step-by-Step (guide the candidate)

**URL Shortener**  
1. **Requirements:** Functional (shorten, redirect, optional analytics); scale (e.g. 100M URLs/month, 10:1 read:write).  
2. **High-level:** Client → API → app servers → DB (shortURL → longURL); optional cache.  
3. **API:** `POST /shorten { longUrl }` → `{ shortUrl }`; `GET /:shortCode` → 302 redirect.  
4. **Data model:** `short_code` (PK), `long_url`, `created_at`, `user_id` (optional).  
5. **Scaling:** Base62/Base64 for short codes; DB sharding by short_code; cache hot URLs; CDN for redirect.  
6. **Trade-offs:** Consistency (same long URL shortened twice: idempotency?); cache invalidation.  
Probe: "What if the same long URL is shortened twice?" "How do you generate unique short codes at scale?"

**Rate Limiter**  
1. **Requirements:** Limit requests per user/IP per window (e.g. 100 req/min); distributed (multiple app servers).  
2. **High-level:** Request → rate limiter middleware → app; store counters in Redis (or similar).  
3. **API:** N/A (middleware); or expose `GET /quota` for client.  
4. **Data model:** Key = user_id or IP; value = count + window start (or sliding window log).  
5. **Algorithms:** Fixed window, sliding window log, or token bucket; choose one and discuss pros/cons.  
6. **Scaling:** Redis with TTL; partition by user_id; clock skew considerations.  
Probe: "How do you handle a burst at the window boundary?" "What if Redis is down?"

---

## Behavioral Question Bank by Category

**Leadership / ownership**  
- Tell me about a time you took ownership of a problem that wasn't yours.  
- Describe a project you led from idea to delivery.

**Conflict / disagreement**  
- Describe a disagreement about technical approach and how you resolved it.  
- Tell me about a time you had to push back on a product or engineering decision.

**Failure / learning**  
- Tell me about a technical failure and what you learned.  
- Describe a time you missed a deadline or shipped a bug. How did you handle it?

**Trade-offs / prioritization**  
- Describe a time you had to make a trade-off between speed and quality.  
- Tell me about a time you had to deprioritize a feature. How did you decide?

**Influence / communication**  
- Tell me about a time you had to explain a technical decision to a non-technical stakeholder.  
- Describe how you've influenced the technical direction of your team.

---

## Tech / Concept Topics

**JavaScript**  
- Event loop, call stack, microtasks vs macrotasks  
- Closure, `this`, arrow functions  
- `let` / `const` / `var`, temporal dead zone  
- Prototype, inheritance, `class`  
- Promises, async/await, error handling  
- Event delegation, bubbling/capturing  

**Python**  
- GIL, threading vs multiprocessing  
- List vs tuple vs set, mutability  
- Decorators, context managers  
- `*args`, `**kwargs`, duck typing  
- Generators, iterators  

**React**  
- Virtual DOM, reconciliation  
- Hooks: useState, useEffect, rules  
- Props vs state, lifting state  
- Keys, list rendering, performance  
- Context, when to use  

**SQL**  
- JOINs (INNER, LEFT, RIGHT), subqueries  
- Indexes, when they help, trade-offs  
- Aggregations, GROUP BY, HAVING  
- Transactions, ACID, isolation levels  

**Data Structures**  
- Array, linked list, when to use  
- Hash map, set, collision handling  
- Stack, queue, deque  
- BST, balanced trees (AVL, red-black high-level)  
- Graph: adjacency list vs matrix, BFS/DFS  

**Algorithms**  
- Sort: quicksort, mergesort, time/space  
- Search: binary search, variants  
- DP: 1D/2D, classic (coin change, LCS)  
- Sliding window, two pointers  
- BFS/DFS, topological sort  

**System design concepts**  
- Load balancing, horizontal scaling  
- Caching (strategy, invalidation)  
- CAP, eventual consistency  
- Message queues, async processing  
- CDN, database replication/sharding  

---

## Concept Q&A with Ideal Answers (for scoring)

**JavaScript — "What's the difference between let, const, and var?"**  
Ideal answer bullets: `var` is function-scoped and hoisted (undefined until assigned); `let` and `const` are block-scoped and not hoisted; `let` can be reassigned, `const` cannot (object/array contents can still change); `let`/`const` are in the temporal dead zone until declaration; prefer `const` by default, `let` when reassignment needed, avoid `var`.

**JavaScript — "Explain the event loop."**  
Ideal answer bullets: Single-threaded; call stack runs synchronous code; Web APIs (setTimeout, fetch) run outside the stack; callbacks go to task queue (macrotasks) or microtask queue (Promises, queueMicrotask); after stack is empty, all microtasks run, then one macrotask; repeat.

**SQL — "What's the difference between INNER JOIN, LEFT JOIN, RIGHT JOIN?"**  
Ideal answer bullets: INNER returns only matching rows from both tables; LEFT returns all from left plus matches from right (NULLs for no match); RIGHT returns all from right plus matches from left; FULL OUTER (if supported) returns all from both with NULLs where no match; use LEFT when you want to keep "all from one side."

**SQL — "When do indexes help, and what are the trade-offs?"**  
Ideal answer bullets: Help for WHERE, JOIN, ORDER BY, GROUP BY on indexed columns; B-tree (default) for range queries and sort; trade-offs: faster reads, slower writes (maintain index); extra storage; wrong index or too many indexes can hurt; mention covering index when all needed columns are in the index.

---

## Company-Style Prep (general knowledge only)

**Google**  
- Strong algorithms and data structures; code quality and clarity.  
- System design for scale; distributed systems.  
- Behavioral often tied to leadership/collaboration and past projects.  
- Example question types: Past project with impact; Handling ambiguity; Conflict with teammate; Design a system that scales (storage, search, or similar).  
- Values/theme: Ownership, collaboration, technical depth.

**Meta (Facebook)**  
- Coding: arrays, strings, trees, graphs; sometimes product-minded follow-ups.  
- System design: large-scale, real-time or social features.  
- Behavioral: impact, move fast, ownership.  
- Example question types: Design a feature (e.g. feed, stories); Scaling to millions; Metric-driven decisions; Technical trade-off under deadline.  
- Values/theme: Impact, move fast, ownership, authenticity.

**Amazon**  
- Leadership Principles (LP) drive behavioral: Customer Obsession, Ownership, Invent and Simplify, Bias for Action, Learn and Be Curious, Hire and Develop the Best, Insist on Highest Standards, Think Big, etc.  
- Coding: medium difficulty, clean code.  
- System design: scalability, availability, operational excellence.  
- Example question types: STAR with metrics; Customer-focused decision; Ownership of a problem; Design for scale and failure; Disagree and commit.  
- Values/theme: LP-based; STAR with quantifiable results.

**Microsoft**  
- Coding and problem-solving; sometimes practical/design.  
- Behavioral: collaboration, growth mindset.  
- Example question types: Past technical challenge; Collaboration with difficult stakeholder; Design a simple service or API; Learning from failure.  
- Values/theme: Growth mindset, collaboration, clarity.

**Netflix**  
- Culture fit and ownership; senior bar high.  
- System design and scalability; reliability.  
- Example question types: Freedom and responsibility; Trade-offs under uncertainty; Designing for reliability; Ownership of an incident or outcome.  
- Values/theme: Freedom and responsibility, context over control, high performance.

Use only for **style** and **topic focus**. Do not invent specific leaked questions or claim insider information.
