---
name: quantum-daily-tracker
description: 量子科技论文追踪与速览生成。用于每日追踪量子计算、量子网络、量子纠错等领域最新论文，生成中文笔记和每日速览。触发场景：(1) 定时任务执行量子论文追踪 (2) 用户请求更新论文 (3) 补充遗漏的论文
---

# 量子日报论文追踪

## 定时任务

- **执行时间**: 每天早上 7:00 (Asia/Shanghai)
- **任务类型**: cron job (每天执行)
- **漏补机制**: 自动检测上次执行日期，漏掉的天数会自动补充

# 

## RSS 期刊订阅列表

### arXiv

| 分类                            | RSS 地址                                      |
| ----------------------------- | ------------------------------------------- |
| Quantum Physics               | http://export.arxiv.org/rss/quant-ph        |
| Optics                        | http://export.arxiv.org/rss/physics.optics  |
| Instrumentation and Detectors | http://export.arxiv.org/rss/physics.ins-det |
| Atomic Physics                | http://export.arxiv.org/rss/physics.atom-ph |

### Nature

| 期刊                      | RSS 地址                                  |
| ----------------------- | --------------------------------------- |
| Nature                  | https://www.nature.com/nature.rss       |
| npj Quantum Information | https://www.nature.com/npjqi.rss        |
| Nature Photonics        | https://www.nature.com/nphoton.rss      |
| Nature Physics          | https://www.nature.com/nphys.rss        |
| Nature Communications   | https://www.nature.com/ncomms.rss       |
| npj Quantum Materials   | https://www.nature.com/npjquantmats.rss |
| Nature Nanotechnology   | https://www.nature.com/nnano.rss        |

### Science

| 期刊               | RSS 地址                                                                 |
| ---------------- | ---------------------------------------------------------------------- |
| Science          | https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science  |
| Science Advances | https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=advances |

### APS (American Physical Society)

| 期刊                       | RSS 地址                                         |
| ------------------------ | ---------------------------------------------- |
| PRX Quantum              | http://feeds.aps.org/rss/recent/prxquantum.xml |
| Physical Review X        | http://feeds.aps.org/rss/recent/prx.xml        |
| Physical Review Letters  | http://feeds.aps.org/rss/recent/prl.xml        |
| Physical Review A        | http://feeds.aps.org/rss/recent/pra.xml        |
| Physical Review B        | http://feeds.aps.org/rss/recent/prb.xml        |
| Physical Review Research | http://feeds.aps.org/rss/recent/prresearch.xml |

---

## 重点关注领域

### 量子科技 (Quantum Technology)

#### 1. 量子计算硬件与物理体系 (Quantum Computing Hardware & Modalities)

> 追踪不同物理体系的量子比特保真度、数量扩展、以及相干时间等硬件突破。

* **离子阱量子计算 (Trapped-Ion-QC)** 📌 *(你的现有目录)*
* **冷原子/中性原子量子计算 (Cold-Atom-QC)** 📌 *(你的现有目录)*
* **硅基/半导体量子计算 (Silicon-Based-QC)** 📌 *(你的现有目录)*
* 超导量子计算 (Superconducting QC) *(补充：目前业界最主流的路线之一，如 IBM, Google)*
* 光子量子计算 (Photonic QC) *(补充：常温运行的潜力路线)*
* 拓扑量子计算 (Topological QC) *(补充：微软主推，主打天然容错)*

#### 2. 量子算法、软件与架构 (Quantum Software, Algorithms & Architecture)

> 追踪量子算法的优化、新应用场景的发现，以及迈向容错量子计算的进展。

* **量子误差纠正 (Quantum-Error-Correction)** 📌 *(你的现有目录：迈向通用量子的关键)*
* **量子机器学习 (Quantum-Machine-Learning)** 📌 *(你的现有目录：AI与量子的交叉)*
* 量子模拟 (Quantum Simulation) *(补充：用于材料科学和化学制药等最先落地的应用)*
* 量子算法 (Quantum Algorithms) *(补充：如 Shor算法优化、VQE、QAOA等)*
* 量子编译与控制软件 (Quantum Compilation & Control) *(补充：如 Qiskit, Cirq 的更新)*

#### 3. 量子通信与网络 (Quantum Communication & Networking)

> 追踪量子信息的长距离传输、量子互联网的构建。

* **量子网络 (Quantum-Networks)** 📌 *(你的现有目录)*
* 量子密钥分发 (Quantum Key Distribution - QKD) *(补充：目前商业化最成熟的量子安全技术)*
* 量子中继器与存储器 (Quantum Repeaters & Memory) *(补充：构建全球量子网络的硬件瓶颈)*

#### 4. 基础理论与物理 (Fundamentals & Physics)

> 追踪底层物理机制的新发现和理论框架的完善。

* **量子理论 (Quantum-Theory)** 📌 *(你的现有目录)*
* **量子光学 (Quantum-Optics)** 📌 *(你的现有目录：很多量子网络和计算的基础)*
* 量子纠缠与非定域性 (Quantum Entanglement & Non-locality) *(补充)*

#### 5. 量子传感与精密测量 (Quantum Sensing & Metrology)

> 追踪利用量子特性进行极高精度测量的技术（这是目前最容易商业化落地的量子技术）。

* 量子磁力计与重力仪 (Quantum Magnetometers & Gravimeters)
* 量子雷达与成像 (Quantum Radar & Imaging)
* 量子钟 (Quantum Clocks)

#### 6. 交叉与支撑技术 (Cross-Cutting & Enabling Technologies)

> 追踪支撑量子系统运行的传统硬科技。

* **交叉领域 (Cross-Cutting)** 📌 *(你的现有目录)*
  * 低温电子学与稀释制冷机 (Cryogenics)
  * 微波控制与室温电子设备 (Microwave Control Electronics)
  * 微纳加工与量子材料 (Nanofabrication & Quantum Materials)

---

## 论文笔记存放路径

```
quantum-tracker/Papers/
```

按来源分类：

- `Papers/arXiv/` → `arXiv-XXXXXXXXXX.md`
- `Papers/Nature/` → `Nature-YYYY-XXXXX.md`
- `Papers/Nature-Photonics/` → `NatPhoto-YYYY-XXXXX.md`
- `Papers/Nature-Physics/` → `NatPhys-YYYY-XXXXX.md`
- `Papers/Nature-Comm/` → `NatComm-YYYY-XXXXX.md`
- `Papers/npj-QI/` → `npjQI-YYYY-XXXXX.md`
- `Papers/Science/` → `Science-YYYY-XXXXX.md`
- `Papers/Science-Advances/` → `SciAdv-YYYY-XXXXX.md`
- `Papers/PRX-Quantum/` → `PRXQ-YYYY-XXXXX.md`
- `Papers/PRX/` → `PRX-YYYY-XXXXX.md`
- `Papers/PRL/` → `PRL-YYYY-XXXXX.md`
- `Papers/PRA/` → `PRA-YYYY-XXXXX.md`
- `Papers/PRB/` → `PRB-YYYY-XXXXX.md`
- `Papers/PRResearch/` → `PRResearch-YYYY-XXXXX.md`

## 每日速览存放路径

```
quantum-tracker/papers/YYYY-MM-DD.md
```

## 执行流程

1. 检查 `memory/last-run.txt` 获取上次执行日期（不存在则从7天前开始）
2. 计算漏掉天数
3. 通过 RSS 抓取最新论文
4. 筛选量子相关论文（量子计算、量子网络、量子纠错、离子阱、硅基量子等）
5. 为重要论文生成笔记，保存到对应来源目录
6. 汇总当日热点生成每日速览
7. 更新 Dashboard：将近7天的论文滚动显示在 Dashboard 中
8. 更新 `memory/last-run.txt`

---

# 论文笔记模板

```markdown
---
# 🏷️ 笔记元数据 (YAML Frontmatter - 适合各类笔记软件检索)
aliases: ["英文短标题或缩写"]
tags: 
  - 📝Paper
  - 📂[细分领域，如：Ion-Trap / Quantum-Control / AOD]
  - 🏢[研究机构，如：UMD / Tsinghua]
status: 🟩已读 / 🟨精读中 / 🟦粗读待定
date_read: YYYY-MM-DD
---

# 📄 [中文翻译标题] 
**[Original English Title]**

- **作者**: [第一作者 et al., 通讯作者] 
- **机构**: [主要研究团队/实验室]
- **发表状态**: [Nature / PRL / npj QI / arXiv Preprint]
- **日期**: YYYY-MM-DD
- **链接**: [DOI URL] | [arXiv URL]
- **代码/开源**: [GitHub 链接或硬件图纸链接，如无则填 None]

---

## 🎯 一句话总结 (TL;DR)
> **这篇文章解决了什么问题？用了什么核心手段？达到了什么指标？有什么优势？**
> *例如：针对多离子寻址的串扰问题，提出了一种基于 FPGA 的实时反馈控制架构，将两比特门保真度提升至 99.9%。*

## 💡 个人启发与行动点 (My Takeaways)
- [ ] 这篇论文对我当前的项目（如：测控系统开发、逻辑架构设计）有什么具体启发？
- [ ] 有哪些可以在我的实验/代码中复现或借鉴的参数？

---

## ⚙️ 实验体系与硬件架构 (System & Hardware Specs)
*针对实验性或工程性论文，提炼底层物理与测控细节*
- **物理载体**: [例如：174Yb+ 离子 / 超导 Transmon]
- **测控硬件**: [例如：ZCU104 / AWG / 锁相放大器]
- **关键光学/微波器件**: [例如：多通道 AOD / 光隔离器 / 声光调制器 AOM]
- **特殊算法/软件**: [例如：SPSA 优化算法 / 自研时序控制软件]

## 🛠️ 核心方法与创新点 (Methodology)
1. **[创新点 1 的小标题，如：新型时序同步方案]**
   - 详细描述机制...
2. **[创新点 2 的小标题，如：误差缓解算法]**
   - 详细描述机制...

## 📊 核心指标与结果 (Key Results)

| 关键参数 (Parameters) | 论文数值 (Values) | 备注 (Notes / 对比基线) |
| :--- | :--- | :--- |
| **状态初始化与探测错误率 (SPAM)** | [如：< 1e-3] | [说明探测时长或光子数阈值] |
| **单比特门保真度 (1Q Gate)** | [数值] | [使用的是微波还是拉曼激光？] |
| **两比特门保真度 (2Q Gate)** | [数值] | [如：MS 门 / 寻址时间] |
| **相干时间 (T2 / T2*)** | [数值] | [是否使用了动态解耦？] |

## 🖼️ 关键图表提取 (Key Figures & Logic Diagrams)
> *在这里粘贴最核心的硬件拓扑图、FPGA 逻辑框图、或时序序列图 (Sequence Diagram)。一图胜千言。*
- `[粘贴图片]`
- **图注**: [简要解释图表中的核心信号流向或控制逻辑]

## 🔗 参考文献与延伸阅读 (Related Works)
- [[笔记链接]] - [这篇论文建立在什么重要前置工作之上？]
- [[笔记链接]] - [有哪些同期的竞争性工作？]
```

---

# 每日速览模板

```markdown
# ⚛️ 量子科技每日速览 - YYYY-MM-DD

> **🤖 AI 核心摘要**
> - *[一句话总结今日学术界的最核心突破]*
> - *[一句话总结今日产业界或工程界的最重要动态]*

---

## 🔬 重点论文速递 (Top Papers)
*Agent 每日筛选出的前 3-5 篇高价值文献（含顶刊与高优 arXiv）*

### [1] [论文标题]
- **标签**: `[如: 离子阱 / 量子网络 / 光学测控]` | **来源**: `[期刊名或 arXiv ID]`
- **机构/团队**: `[如: 马里兰大学 / Monroe 团队]`
- **核心突破**: [1-2句话概括解决了什么痛点，提出了什么新机制]
- **关键数据**: [强制 Agent 提取核心参数，如：实现了 99.9% 的两比特门保真度 / AOD 衍射效率提升至 XX% / 系统寻址时间降低]
- **相关资源**: [是否有开源代码 / FPGA 逻辑图 / 补充材料数据]
- **🔗 链接**: `[URL]`

### [2] [论文标题]
- **标签**: `[...]` | **来源**: `[...]`
- **机构/团队**: `[...]`
- **核心突破**: [...]
- **关键数据**: [...]
- **相关资源**: [...]
- **🔗 链接**: `[...]`

---

## 📡 预印本扫频 (arXiv Radar)
*快速浏览特定细分领域的最新占位论文*

- **[论文标题1]** - `[机构名称]`
  *一句话亮点*: [简述核心创新点，例如：提出了一种新的声光偏转器 (AOD) 驱动频率补偿方案] `(arXiv:XXXX.XXXXX)`
- **[论文标题2]** - `[机构名称]`
  *一句话亮点*: [简述核心创新点，例如：Ytterbium 离子能级初始化的新测控序列] `(arXiv:XXXX.XXXXX)`

---

## 🏭 产业与工程动态 (Industry & Engineering)
*软硬件发布、系统集成、商业合作与开源生态*

### 📌 [公司/机构名称或开源项目名]
- **事件**: [描述发布了什么新一代硬件、测控板卡、或软件更新]
- **影响**: [简述对现有技术栈或行业格局的潜在影响]

---
*📥 数据源: arXiv (quant-ph), Nature, Science, PRX, PRL 及行业 RSS 源*
```

---

## Dashboard 模板

```markdown
# ⚛️ 量子科技追踪 Dashboard

> 🔄 **最后同步:** YYYY-MM-DD HH:MM | 🤖 **AI 速览已生成**

---

## 📅 今日速览 (YYYY-MM-DD)
> **Agent 总结的今日高价值趋势：**
> * *示例：今天共有 5 篇重要论文更新。冷原子领域哈佛大学团队在双量子比特门保真度上取得了 99.9% 的突破；另外，超导量子的错误缓解算法有一篇值得关注的理论进展。*
> * 👉 [点击阅读今日详细简报](papers/YYYY-MM-DD.md)

### 🌟 今日重点论文

| 论文标题 & 机构 | 核心亮点 (TL;DR) | 领域标签 | 来源 | 笔记链接 |
| :--- | :--- | :--- | :--- | :--- |
| **[High-Fidelity Gates in Neutral Atoms]**<br>*Harvard University* | 实现了 99.9% 的双比特门，刷新中性原子记录 | `冷原子QC` `硬件突破` | Nature | [📝 笔记](Papers/Nature/xxx.md) |
| **[Efficient Error Mitigation for QAOA]**<br>*IBM Quantum* | 提出一种减少 QAOA 算法线路深度的错误缓解新方案 | `量子算法` `误差纠正` | arXiv | [📝 笔记](Papers/arXiv/xxx.md) |

*(注：只在这里展示 Agent 判定为高价值或强相关的 3-5 篇论文，避免表格过长)*

---

## 🗂️ 近 7 天动态 (按领域分类)

### 1. 量子计算硬件与物理体系 (Quantum Computing Hardware & Modalities)
> *追踪不同物理体系的量子比特保真度、数量扩展、以及相干时间等硬件突破。*
* `[MM-DD]` **[Trapped-Ion-QC]** [174Yb+ 离子能级初始化的新测控序列] - *保真度提升至 99.9%* - [📝 笔记](Papers/...)
* `[MM-DD]` **[Superconducting QC]** [论文标题2] - *一句简短的核心结论* - [📝 笔记](Papers/...)
* `[MM-DD]` **[Cold-Atom-QC]** [论文标题3] - *一句简短的核心结论* - [📝 笔记](Papers/...)

### 2. 量子算法、软件与架构 (Quantum Software, Algorithms & Architecture)
> *追踪量子算法的优化、新应用场景的发现，以及迈向容错量子计算的进展。*
* `[MM-DD]` **[Quantum-Error-Correction]** [论文标题1] - *一句简短的核心结论* - [📝 笔记](Papers/...)
* `[MM-DD]` **[Quantum-Machine-Learning]** [论文标题2] - *一句简短的核心结论* - [📝 笔记](Papers/...)

### 3. 量子通信与网络 (Quantum Communication & Networking)
> *追踪量子信息的长距离传输、量子互联网的构建。*
* `[MM-DD]` **[Quantum-Networks]** [论文标题1] - *一句简短的核心结论* - [📝 笔记](Papers/...)
* `[MM-DD]` **[Quantum Repeaters]** [论文标题2] - *一句简短的核心结论* - [📝 笔记](Papers/...)

### 4. 基础理论与物理 (Fundamentals & Physics)
> *追踪底层物理机制的新发现和理论框架的完善。*
* `[MM-DD]` **[Quantum-Optics]** [论文标题1] - *一句简短的核心结论* - [📝 笔记](Papers/...)
* `[MM-DD]` **[Quantum-Theory]** [论文标题2] - *一句简短的核心结论* - [📝 笔记](Papers/...)

### 5. 量子传感与精密测量 (Quantum Sensing & Metrology)
> *追踪利用量子特性进行极高精度测量的技术。*
* `[MM-DD]` **[Quantum Clocks]** [论文标题1] - *一句简短的核心结论* - [📝 笔记](Papers/...)
* `[MM-DD]` **[Quantum Magnetometers]** [论文标题2] - *一句简短的核心结论* - [📝 笔记](Papers/...)

### 6. 交叉与支撑技术 (Cross-Cutting & Enabling Technologies)
> *追踪支撑量子系统运行的传统硬科技。*
* `[MM-DD]` **[Cross-Cutting]** [基于 ZCU104 的实时反馈控制系统设计] - *优化了测控板卡的逻辑寻址时间* - [📝 笔记](Papers/...)
* `[MM-DD]` **[Microwave Control]** [不同驱动频率下 AOD 衍射效率的实验测试] - *提供了完整的水平与垂直偏振对比数据* - [📝 笔记](Papers/...)

---

## 📚 知识库与历史归档

**按时间检索:**
* [本周汇总 (YYYY-MM-DD 至 YYYY-MM-DD)](papers/weekly/Week-X.md)
* [历史每日简报归档](papers/archives/)

**按来源检索:**
* [arXiv 论文笔记总览](Papers/arXiv/)
* [Nature/Science 顶刊笔记](Papers/Top-Journals/)
* [PRL / npj QI 等期刊笔记](Papers/Physics-Journals/)
```
