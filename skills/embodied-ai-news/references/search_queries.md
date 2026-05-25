# 🔍 Embodied AI — Search Query Templates

Pre-defined search query templates for discovering Embodied AI news across hardware, algorithms, deployments, funding, and academic research.

---

## Date Variables

Use dynamic date insertion based on current date:
- **Today**: `[today]` (e.g., 2026-02-23)
- **Yesterday**: `[today - 1d]` (e.g., 2026-02-22)
- **This week**: `[today - 7d]` (e.g., 2026-02-16)
- **This month**: `[today - 30d]` (e.g., 2026-01-24)

---

## 1. General Embodied AI News

### 1.1 Daily Overview
```
("embodied AI" OR "embodied intelligence" OR "humanoid robot") AND ("news" OR "announcement" OR "launch") after:[today - 1d]
```

### 1.2 Weekly Roundup
```
("embodied AI" OR "robot learning" OR "humanoid robot") AND ("breakthrough" OR "milestone" OR "update") after:[today - 7d]
```

### 1.3 Broad Robotics + AI Intersection
```
("robot foundation model" OR "robotics AI" OR "physical AI" OR "physical intelligence") after:[today - 1d]
```

### 1.4 Noise Exclusion Filter
> Append to any query above to reduce irrelevant results:
```
NOT "Roomba" NOT "chatbot" NOT "crypto" NOT "blockchain" NOT "RPA" NOT "software robot"
```

---

## 2. Foundation Models & Algorithms

### 2.1 Vision-Language-Action (VLA) Models
```
("vision language action" OR "VLA model" OR "VLA policy") AND ("robot" OR "embodied") after:[today - 7d]
```

### 2.2 Diffusion Policy & Flow Matching
```
("diffusion policy" OR "action diffusion" OR "flow matching policy") AND ("robot" OR "manipulation") after:[today - 7d]
```

### 2.3 World Models for Robotics
```
("world model" OR "video prediction model") AND ("robot" OR "embodied" OR "physical") after:[today - 7d]
```

### 2.4 Imitation Learning & Teleoperation Data
```
("imitation learning" OR "learning from demonstration" OR "teleoperation" OR "human demonstration") AND ("robot") after:[today - 7d]
```

### 2.5 Reinforcement Learning for Robotics
```
("reinforcement learning" OR "RL policy" OR "reward shaping") AND ("robot" OR "locomotion" OR "manipulation") after:[today - 7d]
```

### 2.6 Sim-to-Real Transfer
```
("sim-to-real" OR "sim2real" OR "domain randomization" OR "simulation transfer") AND ("robot") after:[today - 7d]
```

### 2.7 End-to-End Robot Control
```
("end-to-end" OR "visuomotor policy" OR "sensorimotor") AND ("robot control" OR "robot learning") after:[today - 7d]
```

### 2.8 Large Behavior Models / Generalist Policies
```
("generalist robot" OR "generalist policy" OR "large behavior model" OR "cross-embodiment") after:[today - 7d]
```

### 2.9 3D / Spatial Understanding
```
("3D scene understanding" OR "spatial reasoning" OR "NeRF" OR "3D Gaussian" OR "point cloud") AND ("robot" OR "embodied") after:[today - 7d]
```

### 2.10 Language-Conditioned Robotics
```
("language conditioned" OR "instruction following" OR "LLM planning") AND ("robot" OR "manipulation" OR "navigation") after:[today - 7d]
```

---

## 3. Hardware & Platforms

### 3.1 Humanoid Robots (General)
```
("humanoid robot" OR "bipedal robot" OR "full-body humanoid") AND ("new" OR "launch" OR "update" OR "demo") after:[today - 7d]
```

### 3.2 Dexterous Hands & Grippers
```
("dexterous hand" OR "robot hand" OR "robotic gripper" OR "tactile manipulation") AND ("new" OR "breakthrough" OR "launch") after:[today - 7d]
```

### 3.3 Actuators & Motors
```
("robot actuator" OR "quasi-direct-drive" OR "harmonic drive" OR "electric actuator" OR "torque motor") AND ("new" OR "breakthrough") after:[today - 7d]
```

### 3.4 Tactile & Force Sensors
```
("tactile sensor" OR "force torque sensor" OR "GelSight" OR "tactile sensing") AND ("robot") after:[today - 7d]
```

### 3.5 Quadruped / Legged Robots
```
("quadruped robot" OR "legged robot" OR "robot dog") AND ("new" OR "update" OR "demo") after:[today - 7d]
```

### 3.6 Mobile Manipulators
```
("mobile manipulator" OR "mobile manipulation" OR "wheeled robot arm") after:[today - 7d]
```

### 3.7 Robot Compute & Edge AI Hardware
```
("robot compute" OR "edge AI chip" OR "onboard inference") AND ("robot" OR "NVIDIA Jetson" OR "Orin") after:[today - 7d]
```

### 3.8 Robot Supply Chain & Manufacturing
```
("robot manufacturing" OR "robot supply chain" OR "robot production line" OR "robot component") after:[today - 7d]
```

---

## 4. Simulation & Infrastructure

### 4.1 Simulation Platforms
```
("Isaac Sim" OR "Isaac Lab" OR "MuJoCo" OR "SAPIEN" OR "Genesis simulator") AND ("robot" OR "update" OR "release") after:[today - 7d]
```

### 4.2 Digital Twins for Robotics
```
("digital twin" OR "synthetic data") AND ("robot" OR "factory" OR "warehouse") after:[today - 7d]
```

### 4.3 Benchmarks & Evaluation
```
("robot benchmark" OR "manipulation benchmark" OR "SIMPLER" OR "RoboCasa" OR "ManiSkill") after:[today - 7d]
```

### 4.4 Robot Datasets
```
("robot dataset" OR "Open X-Embodiment" OR "DROID dataset" OR "robot demonstration data") after:[today - 30d]
```

### 4.5 Robot Operating System & Middleware
```
("ROS 2" OR "robot middleware" OR "robot software framework") AND ("update" OR "release") after:[today - 30d]
```

---

## 5. Deployments & Commercial

### 5.1 Factory & Warehouse Deployments
```
("robot deployment" OR "robot factory" OR "warehouse robot" OR "logistics robot") AND ("humanoid" OR "embodied AI") after:[today - 7d]
```

### 5.2 Task Success & Performance Metrics
```
("task success rate" OR "robot performance" OR "robot uptime" OR "pick rate") AND ("deployment" OR "production") after:[today - 7d]
```

### 5.3 Household & Service Robots
```
("household robot" OR "home robot" OR "service robot" OR "domestic robot") AND ("AI" OR "embodied") after:[today - 7d]
```

### 5.4 Healthcare & Medical Robotics
```
("surgical robot" OR "medical robot" OR "rehabilitation robot") AND ("AI" OR "learning") after:[today - 7d]
```

### 5.5 Agriculture & Field Robotics
```
("agriculture robot" OR "farming robot" OR "field robot" OR "harvesting robot") AND ("AI") after:[today - 7d]
```

### 5.6 Construction & Inspection Robots
```
("construction robot" OR "inspection robot" OR "infrastructure robot") AND ("AI" OR "autonomous") after:[today - 7d]
```

---

## 6. Funding, M&A & Business

### 6.1 Robotics Funding Rounds
```
("robotics funding" OR "robot startup funding" OR "humanoid robot investment") after:[today - 7d]
```

### 6.2 Embodied AI Startup News
```
("embodied AI startup" OR "robotics startup" OR "humanoid startup") AND ("funding" OR "launch" OR "raise") after:[today - 7d]
```

### 6.3 M&A and Partnerships
```
("robotics acquisition" OR "robot company acquired" OR "robotics partnership") after:[today - 7d]
```

### 6.4 IPO & Public Markets
```
("robotics IPO" OR "robot company public" OR "robotics SPAC" OR "robotics stock") after:[today - 30d]
```

### 6.5 Market Sizing & Forecasts
```
("humanoid robot market" OR "robotics market size" OR "embodied AI TAM") AND ("forecast" OR "billion" OR "trillion") after:[today - 30d]
```

---

## 7. Policy, Safety & Ethics

### 7.1 Robot Safety Standards
```
("robot safety" OR "robot safety standard" OR "ISO 10218" OR "ISO 13482" OR "collaborative robot safety") after:[today - 30d]
```

### 7.2 AI & Robotics Regulation
```
("robot regulation" OR "AI regulation" OR "EU AI Act") AND ("robot" OR "embodied" OR "physical AI") after:[today - 30d]
```

### 7.3 Export Controls & Geopolitics
```
("robot export control" OR "chip export" OR "robotics sanctions") AND ("China" OR "US") after:[today - 30d]
```

### 7.4 Robot Ethics & Labor Impact
```
("robot ethics" OR "robot labor" OR "automation job displacement" OR "robot workforce") after:[today - 30d]
```

---

## 8. Company-Specific Queries

### 🇺🇸 US Companies

#### Tesla Optimus
```
("Tesla Optimus" OR "Tesla robot" OR "Tesla humanoid" OR "Tesla Bot") after:[today - 7d]
```

#### Figure AI
```
("Figure AI" OR "Figure 02" OR "Figure humanoid" OR "Figure robot") after:[today - 7d]
```

#### Boston Dynamics
```
("Boston Dynamics" OR "Atlas robot" OR "Spot robot" OR "Stretch robot") after:[today - 7d]
```

#### Agility Robotics
```
("Agility Robotics" OR "Digit robot" OR "RoboFab") after:[today - 7d]
```

#### 1X Technologies
```
("1X Technologies" OR "NEO robot" OR "1X humanoid") after:[today - 7d]
```

#### Physical Intelligence (π)
```
("Physical Intelligence" OR "pi zero" OR "π0" OR "physical intelligence company") AND ("robot") after:[today - 7d]
```

#### Skild AI
```
("Skild AI" OR "Skild robot" OR "Skild foundation model") after:[today - 7d]
```

#### Apptronik
```
("Apptronik" OR "Apollo robot" OR "Apptronik humanoid") after:[today - 7d]
```

#### Sanctuary AI
```
("Sanctuary AI" OR "Phoenix robot" OR "Carbon AI system") after:[today - 7d]
```

#### Toyota Research Institute
```
("Toyota Research Institute" OR "TRI robot" OR "TRI manipulation" OR "TRI diffusion policy") after:[today - 7d]
```

---

### 🇨🇳 Chinese Companies & Labs

#### Unitree (宇树)
```
("Unitree" OR "Unitree G1" OR "Unitree H1" OR "Unitree humanoid" OR "宇树") after:[today - 7d]
```

#### AGIBOT / Zhiyuan (智元)
```
("AGIBOT" OR "Zhiyuan robot" OR "智元机器人" OR "AGIBOT humanoid") after:[today - 7d]
```

#### UBTECH (优必选)
```
("UBTECH" OR "Walker robot" OR "优必选" OR "UBTECH humanoid") after:[today - 7d]
```

#### Galbot (银河通用)
```
("Galbot" OR "银河通用" OR "Galbot robot") after:[today - 7d]
```

#### Fourier Intelligence (傅利叶)
```
("Fourier Intelligence" OR "Fourier GR" OR "傅利叶" OR "Fourier humanoid") after:[today - 7d]
```

#### Xiaomi CyberOne / Robotics
```
("Xiaomi robot" OR "CyberOne" OR "Xiaomi humanoid" OR "小米机器人") after:[today - 7d]
```

#### Huawei / Peng Cheng Lab
```
("Huawei robot" OR "Peng Cheng Lab" OR "鹏城实验室") AND ("embodied" OR "robot") after:[today - 7d]
```

#### Chinese Embodied AI Policy
```
("China humanoid robot" OR "China robot policy" OR "中国人形机器人" OR "具身智能政策") after:[today - 30d]
```

---

### 🌐 Platform & Infra Companies

#### NVIDIA Robotics
```
("NVIDIA Isaac" OR "NVIDIA GR00T" OR "NVIDIA robot" OR "NVIDIA Isaac Lab" OR "NVIDIA Cosmos") after:[today - 7d]
```

#### Google DeepMind Robotics
```
("DeepMind robot" OR "RT-2" OR "AutoRT" OR "Google robot" OR "DeepMind embodied") after:[today - 7d]
```

#### Meta Robotics
```
("Meta robot" OR "Meta embodied" OR "Habitat simulator" OR "Meta AI robot") after:[today - 7d]
```

#### Hugging Face Robotics
```
("LeRobot" OR "Hugging Face robot" OR "Hugging Face robotics") after:[today - 7d]
```

---

## 9. Academic & Research Queries

### 9.1 arXiv Robotics
```
site:arxiv.org ("cs.RO" OR "robotics") AND ("embodied" OR "manipulation" OR "humanoid" OR "VLA") after:[today - 7d]
```

### 9.2 arXiv — Vision-Language-Action
```
site:arxiv.org ("vision language action" OR "VLA" OR "visuomotor") AND ("robot") after:[today - 7d]
```

### 9.3 arXiv — World Models for Robotics
```
site:arxiv.org ("world model" OR "video prediction") AND ("robot" OR "embodied" OR "manipulation") after:[today - 7d]
```

### 9.4 Conference Papers
```
("CoRL 2026" OR "ICRA 2026" OR "RSS 2026" OR "IROS 2026") AND ("robot learning" OR "embodied") after:[today - 30d]
```

### 9.5 Top Lab Publications
```
("Stanford" OR "CMU" OR "MIT" OR "Berkeley" OR "Tsinghua" OR "PKU") AND ("robot" OR "embodied AI") AND ("paper" OR "research") after:[today - 7d]
```

### 9.6 Open-Source Robot Models & Code
```
("open source" OR "GitHub") AND ("robot model" OR "robot policy" OR "robot learning" OR "embodied AI") after:[today - 7d]
```

---

## 10. Source-Specific Queries

### 10.1 Core Robotics Media
```
site:therobotreport.com ("humanoid" OR "embodied AI" OR "robot deployment") after:[today - 1d]
```
```
site:spectrum.ieee.org ("robot" OR "humanoid" OR "manipulation") after:[today - 7d]
```

### 10.2 Tech Business Media
```
site:techcrunch.com ("robotics" OR "humanoid robot" OR "embodied AI") after:[today - 7d]
```
```
site:reuters.com ("humanoid robot" OR "robotics" OR "robot factory") after:[today - 7d]
```

### 10.3 Company Blogs
```
site:developer.nvidia.com/blog ("robotics" OR "Isaac" OR "GR00T") after:[today - 30d]
```
```
site:deepmind.google ("robot" OR "embodied" OR "manipulation") after:[today - 30d]
```
```
site:bostondynamics.com/blog after:[today - 30d]
```

### 10.4 Chinese Media (English Coverage)
```
site:syncedreview.com ("robot" OR "embodied" OR "humanoid") after:[today - 7d]
```
```
("China robot" OR "Chinese humanoid") AND ("news" OR "launch" OR "funding") after:[today - 7d]
```

---

## 11. Query Combination Recipes

### 📰 Recipe A: Daily Briefing (5 queries, ~15 min)
```
Q1: ("embodied AI" OR "humanoid robot") AND ("news" OR "announcement") after:[today - 1d]
Q2: ("robot foundation model" OR "VLA" OR "diffusion policy") AND ("new" OR "paper") after:[today - 1d]
Q3: ("Tesla Optimus" OR "Figure AI" OR "Boston Dynamics" OR "Unitree") after:[today - 1d]
Q4: ("robotics funding" OR "robot startup") AND ("raise" OR "funding") after:[today - 7d]
Q5: site:therobotreport.com OR site:spectrum.ieee.org ("robot") after:[today - 1d]
```

### 🔬 Recipe B: Weekly Research Deep Dive (4 queries, ~30 min)
```
Q1: site:arxiv.org ("cs.RO") AND ("embodied" OR "VLA" OR "manipulation" OR "humanoid") after:[today - 7d]
Q2: ("diffusion policy" OR "world model" OR "imitation learning") AND ("robot") after:[today - 7d]
Q3: ("sim-to-real" OR "sim2real" OR "cross-embodiment" OR "generalist policy") after:[today - 7d]
Q4: ("open source" OR "GitHub") AND ("robot model" OR "robot policy") after:[today - 7d]
```

### 🏭 Recipe C: Commercial & Deployment Tracker (4 queries, ~20 min)
```
Q1: ("robot deployment" OR "robot factory" OR "warehouse robot") AND ("humanoid" OR "embodied") after:[today - 7d]
Q2: ("robotics funding" OR "robotics acquisition" OR "robotics IPO") after:[today - 7d]
Q3: ("humanoid robot market" OR "robotics market") AND ("forecast" OR "billion") after:[today - 30d]
Q4: ("robot supply chain" OR "actuator" OR "dexterous hand") AND ("new" OR "production") after:[today - 7d]
```

### 🇨🇳 Recipe D: China Ecosystem Focus (4 queries, ~15 min)
```
Q1: ("Unitree" OR "AGIBOT" OR "UBTECH" OR "Galbot" OR "Fourier") after:[today - 7d]
Q2: ("China humanoid robot" OR "China robot policy" OR "China embodied AI") after:[today - 7d]
Q3: site:syncedreview.com ("robot" OR "embodied") after:[today - 7d]
Q4: ("中国人形机器人" OR "具身智能" OR "机器人政策") after:[today - 7d]
```

### 🦾 Recipe E: Hardware & Supply Chain (4 queries, ~20 min)
```
Q1: ("humanoid robot" OR "bipedal robot") AND ("new" OR "launch" OR "specs" OR "demo") after:[today - 7d]
Q2: ("dexterous hand" OR "robot hand" OR "tactile sensor") AND ("new" OR "breakthrough") after:[today - 7d]
Q3: ("robot actuator" OR "harmonic drive" OR "quasi-direct-drive") after:[today - 30d]
Q4: ("NVIDIA Jetson" OR "edge AI" OR "onboard compute") AND ("robot") after:[today - 7d]
```

---

## 12. Query Optimization Tips for Embodied AI

### Terminology Precision
| ❌ Too Broad | ✅ Precise |
|-------------|-----------|
| `"robot news"` | `"humanoid robot" OR "embodied AI"` |
| `"AI model"` | `"VLA model" OR "diffusion policy" OR "robot foundation model"` |
| `"robot arm"` | `"dexterous manipulation" OR "mobile manipulator"` |
| `"simulation"` | `"Isaac Sim" OR "MuJoCo" OR "sim-to-real"` |

### Noise Exclusion Patterns
```
# Exclude industrial-only / non-AI robotics
NOT "Roomba" NOT "RPA" NOT "software robot" NOT "chatbot" NOT "trading bot"

# Exclude adjacent but different fields
NOT "autonomous vehicle" NOT "self-driving" NOT "drone delivery"
(unless specifically tracking these intersections)
```

### Chinese Content Search Tips
- Use **both English and Chinese** terms for Chinese companies: `"Unitree" OR "宇树"`
- For policy: `"具身智能" OR "人形机器人" OR "embodied AI China"`
- Best Chinese search engines: **Baidu News**, **WeChat Search (搜狗微信)**
- For English coverage of China: `site:syncedreview.com` or `"China" AND "humanoid robot"`

### Date Range Guidelines
| Content Type | Recommended Range | Rationale |
|-------------|-------------------|-----------|
| Breaking news & demos | `after:[today - 1d]` | Fast-moving announcements |
| Research papers | `after:[today - 7d]` | Papers accumulate weekly |
| Funding rounds | `after:[today - 7d]` | Deal flow is weekly cadence |
| Hardware launches | `after:[today - 7d]` | Product cycles are slower |
| Policy & regulation | `after:[today - 30d]` | Policy moves slowly |
| Market reports | `after:[today - 30d]` | Published monthly/quarterly |
| Supply chain | `after:[today - 30d]` | Long-cycle industry |