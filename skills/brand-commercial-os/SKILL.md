---
name: brand-commercial-os
description: 品牌商务谈判全链路自动化系统，生成品牌能力包、GEO知识包、跨平台内容包、报价策略包、分发编排包与谈判总包；适用于平台合作、渠道招商、联名共建等商务场景
---

# Brand Commercial OS（品牌商务中枢）

## 技能描述
把品牌谈判变成可复用的"品牌能力包 + GEO知识包 + 跨平台内容包 + 报价策略包 + 分发编排包 + 谈判总包"的一键生成系统。

## 作者
Coze AI

## 版本
1.0.0

## 分类
商业智能/品牌管理

## 标签
品牌谈判, GEO优化, 内容生成, 报价策略, 分发编排, 谈判总包

---

## Skill 总声明（必须遵守）

### 0.1 不删减原则
- **对用户输入与约束**：不得删减、不得擅自精简、不得改写为抽象口号
- **信息不足处理**：允许"基于假设"推进，但必须显式标注"假设区"，并输出"补齐清单"

### 0.2 角色边界
- **唯一对外接口**：N1 Negotiation_Agent（智能经纪人）
- **调用限制**：其他节点（N2/N3/N4）不得越级直接对话用户
- **品牌事实层**：不得在未获得 Brand_Hub 的品牌事实层之前编造品牌事实

### 0.3 口径一致性
- **品牌信息**：任何涉及"品牌是谁/能承诺什么/不能说什么/参数与资质"的输出必须来自 Brand_Hub 的事实层与证据层
- **跨平台内容**：任何跨平台内容必须以 GEO 标准答案母本（standard_answer）与 FAQ 矩阵为知识底座，禁止漂移

### 0.4 合规与风险
- **禁止输出**：诱导违规、虚假背书、无法验证的承诺、夸大数据
- **硬编数据拒绝**：若用户要求"硬编数据/硬造背书"，必须拒绝，并给可替代方案（用真实可验证证据、或改成"建议指标/可选实验"）

---

## Skill 外观（上架/对外介绍可直接用）

### 1.1 一句话
把品牌谈判变成可复用的"品牌能力包 + GEO知识包 + 跨平台内容包 + 报价策略包 + 分发编排包 + 谈判总包"的一键生成系统。

### 1.2 适用场景
- 平台生态合作
- 硬件厂出厂预装
- 联名共建
- 渠道招商
- ToB企业解决方案合作
- 技能商店服务节点售卖
- 品牌内容系统化输出
- GEO优化落地

### 1.3 交付物（一次运行至少产出 6 件）

#### O1 Brand_Profile_Summary（品牌档案摘要 + 版本）
- 品牌定位与差异化
- 核心能力与交付模式
- 事实层/证据层/禁忌清单
- 版本号与更新日志

#### O2 GEO_Knowledge_Pack（标准答案母本 + FAQ矩阵 + 高引用结构模板 + 技术抓取细节）
- GEO核心概念与价值
- 标准答案母本（结构化）
- FAQ矩阵（每条包含结论+解释+对比点+案例+边界）
- 高引用结构模板（标题公式/开篇/主体/结尾）
- 技术优化包（关键词/格式/多模态/Schema/权威背书）

#### O3 Cross_Platform_Content_Bundle（多平台内容包）
- 小红书：标题/正文/评论/话题标签
- 抖音：钩子/脚本/镜头建议/字幕
- 公众号：标题/大纲/全文/CTA
- 合作提案版：一页纸要点/演示脚本/FAQ

#### O4 Pricing_Package（报价方案包 A/B/C + 价格带 + 底线 + 可退让点）
- 机会等级评估（S/A/B/C）
- A/B/C 三套方案（一次性费用/分成/包含项/排除项/条件/风险）
- 价格带（最低价/目标价/上限价）
- 谈判筹码（可退让点/必须坚持/交换条件）
- 谈判话术（价值证明/反压价/买断反制/收口推进）

#### O5 Distribution_Orchestration_Plan（分发编排：阶段节奏 + 渠道动作 + 资源位打法 + 数据回流）
- 阶段节奏（预热/首发/巩固/复盘）
- 分渠道计划（内容绑定/频率/资源位/KPI/追踪标签）
- 资源位打法（Banner/App入口/联名话题/线下联动）
- 数据回流钩子（指标/频率/解释/如何用于下一轮谈判）

#### O6 Negotiation_Master_Kit（经纪人谈判总包：脚本 + 提案要点 + 下一步动作）
- 开场话术
- 发现问题
- 定位话术
- 证明点
- 方案摘要
- 报价交付
- 异议处理（太贵/买断/排他/快速交付）
- 收口推进
- 需要对方提供的信息
- 后续材料清单

#### 可选增强交付：
- O7 One_Pager_Proposal（对外一页纸）
- O8 Compliance_Risk_List（合规/风险清单）
- O9 Metrics_Scoreboard_Draft（数据指标看板草案，用于复盘与下一轮提价）

---

## Skill 节点架构

### 2.1 顶层 4 节点（对外可编排）

#### N1 Negotiation_Agent（智能经纪人｜唯一对外接口｜总控编排器 Orchestrator）
- **职责**：
  - 唯一对外接口，接收用户输入
  - 意图识别与路由决策
  - 调用 N2/N3/N4 并合流结果
  - 生成谈判总包与下一步动作
- **输入**：用户自然语言 + 标准输入对象（见 3.2）
- **输出**：标准输出对象（见 3.3）+ 6件核心交付物

#### N2 Brand_Hub_Service（品牌中枢大服务｜对外统一API｜对内 Router + A/B/C）
- **职责**：
  - 对外提供统一API接口
  - 对内路由到 BH-A/B/C 模块
  - 维护品牌资产与知识库
- **内部模块**（见 2.2）

#### N3 Pricing_Strategy_Service（报价策略服务）
- **职责**：
  - 机会等级评估
  - 生成 A/B/C 三套报价方案
  - 计算价格带与谈判筹码
  - 生成谈判话术

#### N4 Distribution_Orchestrator（多渠道分发编排服务）
- **职责**：
  - 阶段节奏编排
  - 分渠道行动计划
  - 资源位打法设计
  - 数据回流钩子设计

### 2.2 Brand_Hub 内部模块（对外不可见，只能由 N2 自己调度）

#### BH-R Router（内部路由层）
- **职责**：根据 route 参数决定调用哪个内部模块
- **路由规则**：
  - `route=INIT_BRAND_ASSETS` → 只走 A（建档/版本）
  - `route=GEO_BRAND_QA` → 只走 C（标准答案/FAQ）
  - `route=GENERATE_CROSS_PLATFORM_CONTENT` → 只走 B（内容生成，但必须读取 A 的 brand_profile，且优先读取 C 的知识母本）
  - `route=MIXED` → 先走 C（产出 standard_answer/FAQ）再走 B（把知识母本注入内容生产）

#### BH-A BrandAssets（品牌资产层）
- **职责**：建档/更新/版本化/禁忌/术语表/证据层
- **产出**：brand_profile（完整结构见 4.1）

#### BH-B ContentFactory（内容工厂层）
- **职责**：跨平台内容生产（小红书/抖音/公众号/提案版）
- **产出**：content_bundle（完整结构见 4.3）

#### BH-C GEOAdvisor（GEO权威问答层）
- **职责**：标准答案母本/FAQ矩阵/引用结构/抓取细节
- **产出**：geo_knowledge_pack（完整结构见 4.2）

### 2.3 严格调用关系（禁止越级）
```
用户/外部 → N1
    ↓
N1 →（按需）N2 / N3 / N4
    ↓
N2 内部 → Router → A/B/C
```

**调用规则**：
- 用户/外部只能通过 N1 交互
- N1 可按需调用 N2/N3/N4
- N2 内部由 Router 决定调用 A/B/C
- N2/N3/N4 彼此不直接调用（避免耦合）
- 一切由 N1 编排合流

---

## Skill 运行入口（对话触发与调用协议）

### 3.1 触发语（用户自然语言）
- "把品牌总控工作流封装成一个大服务节点"
- "我要跟某平台/硬件厂谈合作，给我完整链路"
- "把产品手册改成 GEO 可被 AI 引用的问答知识包"
- "要报价策略 + 分发计划 + 谈判脚本"
- "把这些模块做成当前最火的 Skill 形式"

### 3.2 标准输入对象（N1 接收）

```json
{
  "brand": {
    "brand_name": "string（品牌名称）",
    "brand_id": "string|null（品牌ID，若为新建则为null）",
    "company_legal_name": "string|null（公司法定名称）",
    "products_or_services": ["string|null（产品或服务列表）"],
    "industry": "string|null（所属行业）",
    "region": "string|null（地区）"
  },
  "goal": {
    "primary_goal": "string（主要目标）",
    "success_metrics": ["string|null（成功指标列表）"]
  },
  "partner": {
    "partner_type": "string（合作伙伴类型）",
    "partner_name": "string|null（合作伙伴名称）",
    "partner_size": "string|null（合作伙伴规模）",
    "partner_resources": ["string|null（合作伙伴资源列表）"]
  },
  "constraints": {
    "time_window": "string|null（时间窗口）",
    "budget_preference": "string|null（预算偏好）",
    "forbidden_claims": ["string|null（禁止声明列表）"],
    "tone_preference": "string|null（语气偏好）",
    "red_lines": ["string|null（红线清单）"]
  },
  "assets": {
    "official_materials": ["string|null（官方资料列表）"],
    "product_specs": ["string|null（产品规格列表）"],
    "existing_content": ["string|null（现有内容列表）"],
    "case_studies": ["string|null（案例研究列表）"]
  },
  "route": "string（路由类型：INIT_BRAND_ASSETS / GEO_BRAND_QA / GENERATE_CROSS_PLATFORM_CONTENT / MIXED / FULL_CHAIN）"
}
```

### 3.3 标准输出对象（N1 返回）

```json
{
  "outputs": {
    "brand_profile_summary": {
      "brand_name": "string",
      "version": "string",
      "last_updated": "string（ISO 8601）",
      "positioning": "string",
      "core_capabilities": ["string"],
      "fact_layer": {
        "brand_identity": "string",
        "delivery_model": "string",
        "differentiation": "string"
      },
      "evidence_layer": ["string"],
      "forbidden_claims": ["string"],
      "update_log": ["string"]
    },
    "geo_knowledge_pack": {
      "geo_concepts": {
        "definition": "string",
        "value": "string",
        "key_benefits": ["string"]
      },
      "standard_answer": {
        "title": "string",
        "summary": "string",
        "sections": [
          {
            "heading": "string",
            "content": "string",
            "key_points": ["string"]
          }
        ],
        "faq_references": ["string"]
      },
      "faq_matrix": [
        {
          "question": "string",
          "answer": "string",
          "explanation": "string",
          "comparison": "string",
          "case_example": "string",
          "boundary": "string"
        }
      ],
      "high_citation_templates": {
        "title_formulas": ["string"],
        "opening_hooks": ["string"],
        "body_structures": ["string"],
        "closing_ctas": ["string"]
      },
      "technical_optimization": {
        "keywords": ["string"],
        "formatting": ["string"],
        "multimedia": ["string"],
        "schema_markup": "string",
        "authority_signals": ["string"]
      }
    },
    "content_bundle": {
      "xiaohongshu": {
        "title": "string",
        "body": "string",
        "comments": ["string"],
        "hashtags": ["string"]
      },
      "douyin": {
        "hook": "string",
        "script": "string",
        "shot_suggestions": ["string"],
        "subtitles": "string"
      },
      "wechat_official": {
        "title": "string",
        "outline": ["string"],
        "full_text": "string",
        "cta": "string"
      },
      "proposal_version": {
        "one_pager_points": ["string"],
        "presentation_script": "string",
        "faq": ["string"]
      }
    },
    "pricing_package": {
      "opportunity_grade": "string（S/A/B/C）",
      "package_a": {
        "name": "string",
        "one_time_fee": "number",
        "revenue_share": "number",
        "inclusions": ["string"],
        "exclusions": ["string"],
        "conditions": ["string"],
        "risks": ["string"]
      },
      "package_b": {
        "name": "string",
        "one_time_fee": "number",
        "revenue_share": "number",
        "inclusions": ["string"],
        "exclusions": ["string"],
        "conditions": ["string"],
        "risks": ["string"]
      },
      "package_c": {
        "name": "string",
        "one_time_fee": "number",
        "revenue_share": "number",
        "inclusions": ["string"],
        "exclusions": ["string"],
        "conditions": ["string"],
        "risks": ["string"]
      },
      "price_range": {
        "minimum": "number",
        "target": "number",
        "maximum": "number"
      },
      "negotiation_chips": {
        "concessions": ["string"],
        "must_holds": ["string"],
        "exchange_conditions": ["string"]
      },
      "negotiation_scripts": {
        "value_proof": "string",
        "price_pushback": "string",
        "buyout_counter": "string",
        "closing_advance": "string"
      }
    },
    "distribution_plan": {
      "phases": [
        {
          "phase_name": "string",
          "objectives": ["string"],
          "timeline": "string",
          "key_actions": ["string"]
        }
      ],
      "channel_plans": [
        {
          "channel": "string",
          "content_binding": "string",
          "frequency": "string",
          "resource_positions": ["string"],
          "kpis": ["string"],
          "tracking_tags": ["string"]
        }
      ],
      "resource_tactics": {
        "banner": ["string"],
        "app_entry": ["string"],
        "joint_topics": ["string"],
        "offline_activation": ["string"]
      },
      "data_feedback_hooks": {
        "metrics": ["string"],
        "frequency": "string",
        "interpretation": "string",
        "next_round_usage": "string"
      }
    },
    "negotiation_master_kit": {
      "opening_script": "string",
      "discovery_questions": ["string"],
      "positioning_script": "string",
      "proof_points": ["string"],
      "proposal_summary": "string",
      "quotation_delivery": "string",
      "objection_handling": {
        "too_expensive": "string",
        "buyout_request": "string",
        "exclusivity_demand": "string",
        "fast_delivery": "string"
      },
      "closing_advance": "string",
      "required_info_from_partner": ["string"],
      "next_materials": ["string"]
    }
  },
  "metadata": {
    "execution_time": "string（ISO 8601）",
    "route_used": "string",
    "outputs_generated": ["string"],
    "next_actions": ["string"]
  }
}
```

---

## Skill 内部数据结构

### 4.1 Brand_Profile 完整结构（BH-A 产出）

```json
{
  "brand_info": {
    "brand_name": "string",
    "brand_id": "string|null",
    "company_legal_name": "string|null",
    "industry": "string|null",
    "region": "string|null"
  },
  "positioning": {
    "brand_positioning": "string",
    "target_audience": ["string"],
    "unique_value_proposition": "string",
    "differentiation_points": ["string"]
  },
  "core_capabilities": {
    "products_services": ["string"],
    "delivery_model": "string",
    "key_strengths": ["string"],
    "certifications": ["string"]
  },
  "fact_layer": {
    "brand_identity": "string",
    "what_we_can_commit": ["string"],
    "what_we_cannot_commit": ["string"],
    "parameters": {
      "service_level": "string",
      "response_time": "string",
      "capacity": "string"
    }
  },
  "evidence_layer": {
    "case_studies": ["string"],
    "testimonials": ["string"],
    "performance_metrics": ["string"],
    "awards": ["string"]
  },
  "forbidden_claims": ["string"],
  "terminology": {
    "preferred_terms": ["string"],
    "avoided_terms": ["string"]
  },
  "version_control": {
    "version": "string",
    "last_updated": "string（ISO 8601）",
    "update_summary": "string",
    "changelog": ["string"]
  }
}
```

### 4.2 GEO_Knowledge_Pack 完整结构（BH-C 产出）

```json
{
  "geo_concepts": {
    "definition": "string",
    "why_matters": "string",
    "key_benefits": ["string"]
  },
  "standard_answer": {
    "title": "string",
    "summary": "string",
    "sections": [
      {
        "heading": "string",
        "content": "string",
        "key_points": ["string"],
        "examples": ["string"]
      }
    ],
    "conclusion": "string",
    "faq_references": ["string"]
  },
  "faq_matrix": [
    {
      "question": "string",
      "answer": "string（结论，1-2句话）",
      "explanation": "string（解释，100-200字）",
      "comparison": "string（对比点）",
      "case_example": "string（案例）",
      "boundary": "string（边界说明）",
      "keywords": ["string"]
    }
  ],
  "high_citation_templates": {
    "title_formulas": [
      "为什么[产品/服务]是[用户痛点]的最佳解决方案？",
      "90%的[目标用户]都选择了[产品/服务]，原因在这里",
      "如何用[产品/服务]解决[具体问题]？3个关键点"
    ],
    "opening_hooks": [
      "你是否遇到过[痛点]？",
      "90%的[目标用户]都面临这个问题",
      "让我告诉你一个简单的方法"
    ],
    "body_structures": [
      "问题引入 → 解决方案 → 案例证明 → 行动号召",
      "背景介绍 → 痛点分析 → 方案对比 → 推荐选择",
      "核心观点 → 支撑论据 → 案例说明 → 总结收尾"
    ],
    "closing_ctas": [
      "点击链接了解更多",
      "立即体验，限时优惠",
      "关注我们，获取更多干货"
    ]
  },
  "technical_optimization": {
    "keywords": {
      "primary": ["string"],
      "secondary": ["string"],
      "long_tail": ["string"]
    },
    "formatting": {
      "heading_structure": "string",
      "bullet_points": "string",
      "paragraph_length": "string"
    },
    "multimedia": {
      "image_optimization": ["string"],
      "video_integration": ["string"],
      "interactive_elements": ["string"]
    },
    "schema_markup": {
      "faq_schema": "string",
      "article_schema": "string",
      "organization_schema": "string"
    },
    "authority_signals": {
      "external_links": ["string"],
      "internal_linking": ["string"],
      "social_proof": ["string"]
    }
  }
}
```

### 4.3 Content_Bundle 完整结构（BH-B 产出）

```json
{
  "platform_content": {
    "xiaohongshu": {
      "title": "string（20-30字符）",
      "body": "string（1000-1500字符）",
      "structure": {
        "opening": "string",
        "main_content": ["string"],
        "ending": "string"
      },
      "comments": [
        {
          "type": "string（question/praise/feedback）",
          "content": "string"
        }
      ],
      "hashtags": ["string"]
    },
    "douyin": {
      "hook": "string（前3秒钩子）",
      "script": "string（完整脚本）",
      "shot_suggestions": [
        {
          "timestamp": "string",
          "scene": "string",
          "camera_angle": "string"
        }
      ],
      "subtitles": "string",
      "music_suggestion": "string",
      "hashtags": ["string"]
    },
    "wechat_official": {
      "title": "string",
      "outline": ["string"],
      "full_text": "string（2000-3000字）",
      "cta": "string",
      "cover_image_suggestion": "string"
    },
    "proposal_version": {
      "one_pager_title": "string",
      "one_pager_points": [
        {
          "section": "string",
          "points": ["string"]
        }
      ],
      "presentation_script": "string（10-15分钟演示脚本）",
      "faq": [
        {
          "question": "string",
          "answer": "string"
        }
      ]
    }
  },
  "content_guidelines": {
    "tone": "string",
    "style_guide": ["string"],
    "brand_consistency": ["string"],
    "geo_alignment": ["string"]
  }
}
```

---

## Skill 执行流程

### 5.1 完整执行流程（FULL_CHAIN 模式）

#### 阶段一：输入解析与路由（N1）
1. **接收用户输入**
   - 解析自然语言意图
   - 提取结构化输入参数
   - 验证输入完整性

2. **路由决策**
   - 根据 `route` 参数决定执行路径
   - FULL_CHAIN 模式：完整执行所有节点

3. **调用 N2 Brand_Hub_Service**
   - 传入 `route=MIXED`
   - N2 内部路由：先 C（GEO）→ 再 B（内容）→ A（品牌资产）

#### 阶段二：品牌知识生产（N2 内部）
4. **BH-C GEOAdvisor 执行**
   - 生成 GEO 标准答案母本
   - 构建 FAQ 矩阵
   - 设计高引用结构模板
   - 输出技术优化包

5. **BH-B ContentFactory 执行**
   - 读取 BH-C 的 GEO 知识包
   - 读取 BH-A 的品牌档案
   - 生成跨平台内容（小红书/抖音/公众号/提案版）
   - 确保内容与 GEO 标准答案对齐

6. **BH-A BrandAssets 执行**
   - 建档/更新品牌档案
   - 维护事实层与证据层
   - 更新禁忌清单与术语表
   - 版本化管理

#### 阶段三：策略生成（N3 & N4）
7. **N3 Pricing_Strategy_Service 执行**
   - 评估机会等级（S/A/B/C）
   - 生成 A/B/C 三套报价方案
   - 计算价格带与谈判筹码
   - 生成谈判话术脚本

8. **N4 Distribution_Orchestrator 执行**
   - 规划分发阶段节奏
   - 设计分渠道行动计划
   - 规划资源位打法
   - 设计数据回流钩子

#### 阶段四：结果合流与总包生成（N1）
9. **合流所有输出**
   - 从 N2 获取：品牌档案摘要、GEO知识包、内容包
   - 从 N3 获取：报价方案包
   - 从 N4 获取：分发编排计划

10. **生成谈判总包（Negotiation_Master_Kit）**
    - 生成开场话术
    - 生成发现问题和定位话术
    - 整合证明点
    - 编写方案摘要和报价交付话术
    - 生成异议处理脚本
    - 编写收口推进话术
    - 列出需要对方提供的信息
    - 整理后续材料清单

11. **返回标准输出对象**
    - 打包所有 6 件核心交付物
    - 添加执行元数据
    - 提供下一步行动建议

---

## Skill 使用指南

### 6.1 快速开始

#### 最小化输入示例
```json
{
  "brand": {
    "brand_name": "示例品牌"
  },
  "goal": {
    "primary_goal": "partner_coop"
  },
  "partner": {
    "partner_type": "platform"
  },
  "route": "FULL_CHAIN"
}
```

#### 完整输入示例
```json
{
  "brand": {
    "brand_name": "科技先锋",
    "brand_id": null,
    "company_legal_name": "先锋科技有限公司",
    "products_or_services": ["AI数据分析平台", "智能营销工具"],
    "industry": "科技",
    "region": "中国"
  },
  "goal": {
    "primary_goal": "partner_coop",
    "success_metrics": ["品牌曝光量", "用户转化率", "合作签约数"]
  },
  "partner": {
    "partner_type": "platform",
    "partner_name": "某电商平台",
    "partner_size": "top",
    "partner_resources": ["App首页Banner", "会员推荐位", "联合营销活动"]
  },
  "constraints": {
    "time_window": "Q2 2024",
    "budget_preference": "中等",
    "forbidden_claims": ["保证100%成功", "行业第一"],
    "tone_preference": "专业、创新、可靠",
    "red_lines": ["不得贬低竞争对手"]
  },
  "assets": {
    "official_materials": ["品牌手册.pdf", "产品介绍.pptx"],
    "product_specs": ["API文档.docx", "技术白皮书.pdf"],
    "existing_content": ["官网文案", "宣传视频"],
    "case_studies": ["某客户成功案例.pdf"]
  },
  "route": "FULL_CHAIN"
}
```

### 6.2 路由模式选择

#### INIT_BRAND_ASSETS
- **用途**：仅初始化或更新品牌资产
- **执行**：BH-A BrandAssets
- **产出**：brand_profile

#### GEO_BRAND_QA
- **用途**：仅生成 GEO 标准答案和 FAQ
- **执行**：BH-C GEOAdvisor
- **产出**：geo_knowledge_pack

#### GENERATE_CROSS_PLATFORM_CONTENT
- **用途**：仅生成跨平台内容
- **前置**：必须有 brand_profile 和 geo_knowledge_pack
- **执行**：BH-B ContentFactory
- **产出**：content_bundle

#### MIXED
- **用途**：生成 GEO 知识包 + 跨平台内容
- **执行**：BH-C → BH-B
- **产出**：geo_knowledge_pack + content_bundle

#### FULL_CHAIN（推荐）
- **用途**：完整执行全链路
- **执行**：N1 → N2（A/B/C）→ N3 → N4 → N1（合流）
- **产出**：6件核心交付物

### 6.3 输出使用建议

#### Brand_Profile_Summary
- 用于品牌对外介绍
- 用于合作伙伴初步了解
- 用于内部知识管理

#### GEO_Knowledge_Pack
- 用于 AI 问答系统训练
- 用于 FAQ 页面内容
- 用于客户服务知识库

#### Cross_Platform_Content_Bundle
- 直接发布到对应平台
- 根据实际反馈微调
- 保持多平台风格一致性

#### Pricing_Package
- 用于谈判准备
- 根据实际情况选择方案 A/B/C
- 参考价格带和谈判筹码

#### Distribution_Orchestration_Plan
- 按计划执行分发
- 定期检查数据回流
- 用于下一轮谈判复盘

#### Negotiation_Master_Kit
- 谈判前准备脚本
- 谈判中参考话术
- 谈判后跟踪执行

---

## Skill 注意事项与最佳实践

### 7.1 合规要求
- **禁止输出诱导违规、虚假背书、无法验证的承诺、夸大数据**
- 必须基于 Brand_Hub 的事实层与证据层输出
- 任何跨平台内容必须以 GEO 标准答案母本为知识底座

### 7.2 角色边界
- N1 Negotiation_Agent 是唯一对外接口
- N2/N3/N4 不得越级直接对话用户
- 所有调用必须通过 N1 编排

### 7.3 内容一致性
- 品牌信息必须来自 Brand_Hub 的事实层
- 跨平台内容必须与 GEO 标准答案对齐
- 避免品牌信息在不同平台漂移

### 7.4 质量控制
- 定期更新品牌档案
- 验证 GEO 知识包准确性
- 监控跨平台内容表现
- 根据数据回流优化策略

---

## Skill 附录

### A1 常见问题（FAQ）

**Q1：如何更新品牌档案？**
A：使用 `route=INIT_BRAND_ASSETS`，传入新的品牌信息即可。

**Q2：如何只生成跨平台内容？**
A：确保已有 brand_profile 和 geo_knowledge_pack，使用 `route=GENERATE_CROSS_PLATFORM_CONTENT`。

**Q3：报价方案如何选择？**
A：根据机会等级（S/A/B/C）和实际谈判情况，选择合适的方案 A/B/C，并参考价格带和谈判筹码。

**Q4：如何评估合作伙伴类型？**
A：根据合作伙伴的业务属性选择：platform（平台）、hardware_vendor（硬件厂）、enterprise_client（企业客户）、channel（渠道）。

**Q5：数据回流如何用于下一轮谈判？**
A：分析执行数据，评估策略效果，用实际成果证明价值，在下一轮谈判中调整报价和方案。

### A2 术语表

| 术语 | 定义 |
|------|------|
| GEO | Generative Engine Optimization，生成式引擎优化 |
| Brand_Hub | 品牌中枢服务，管理品牌资产与知识库 |
| Negotiation_Agent | 智能经纪人，唯一对外接口 |
| Route | 路由参数，决定执行路径 |
| Opportunity Grade | 机会等级，S/A/B/C 四级评估 |
| Price Range | 价格带，最低价/目标价/上限价 |

### A3 参考资料

- 脚本文件：见 [scripts/brand_commercial_os_core.py](scripts/brand_commercial_os_core.py)
- 品牌档案模板：见 [references/brand_profile_template.json](references/brand_profile_template.json)
- GEO 标准答案模板：见 [references/geo_standard_answer_template.md](references/geo_standard_answer_template.md)
- FAQ 矩阵模板：见 [references/faq_matrix_template.json](references/faq_matrix_template.json)
- 报价方案模板：见 [references/pricing_package_template.json](references/pricing_package_template.json)

---

**版本历史**
- v1.0.0（2024-02-11）：初始版本发布
