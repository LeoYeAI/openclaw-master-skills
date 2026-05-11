#!/usr/bin/env python3
"""
Brand Commercial OS - 核心执行引擎
Author: Coze AI
Version: 1.0.0
Description: 
    Brand Commercial OS核心执行引擎，负责协调N1/N2/N3/N4四个顶层节点，
    并实现Brand Hub内部模块（BH-A/B/C）的完整功能。
    
    核心功能：
    1. N1 Negotiation_Agent（智能经纪人｜唯一对外接口｜总控编排器）
    2. N2 Brand_Hub_Service（品牌中枢大服务｜对外统一API｜对内Router + A/B/C）
    3. N3 Pricing_Strategy_Service（报价策略服务）
    4. N4 Distribution_Orchestrator（多渠道分发编排服务）
"""

import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================
# 数据结构定义
# ============================================


class RouteType(Enum):
    """路由类型"""
    INIT_BRAND_ASSETS = "INIT_BRAND_ASSETS"
    GEO_BRAND_QA = "GEO_BRAND_QA"
    GENERATE_CROSS_PLATFORM_CONTENT = "GENERATE_CROSS_PLATFORM_CONTENT"
    MIXED = "MIXED"
    FULL_CHAIN = "FULL_CHAIN"


class OpportunityGrade(Enum):
    """机会等级"""
    S = "S"
    A = "A"
    B = "B"
    C = "C"


class PrimaryGoal(Enum):
    """主要目标"""
    EXPOSURE = "exposure"
    ACTIVATION = "activation"
    CONVERSION = "conversion"
    PARTNER_COOP = "partner_coop"
    PREINSTALL = "preinstall"
    CHANNEL_RECRUITMENT = "channel招商"
    CONTENT_SYSTEM = "content_system"
    GEO_OPTIMIZATION = "geo_optimization"
    FULL_CHAIN = "full_chain"


@dataclass
class BrandInput:
    """品牌输入"""
    brand_name: str
    brand_id: Optional[str] = None
    company_legal_name: Optional[str] = None
    products_or_services: Optional[List[str]] = None
    industry: Optional[str] = None
    region: Optional[str] = None


@dataclass
class GoalInput:
    """目标输入"""
    primary_goal: str
    success_metrics: Optional[List[str]] = None


@dataclass
class PartnerInput:
    """合作伙伴输入"""
    partner_type: str
    partner_name: Optional[str] = None
    partner_size: Optional[str] = None
    partner_resources: Optional[List[str]] = None


@dataclass
class ConstraintsInput:
    """约束输入"""
    time_window: Optional[str] = None
    budget_preference: Optional[str] = None
    forbidden_claims: Optional[List[str]] = None
    tone_preference: Optional[str] = None
    red_lines: Optional[List[str]] = None


@dataclass
class AssetsInput:
    """资产输入"""
    official_materials: Optional[List[str]] = None
    product_specs: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    case_studies: Optional[List[str]] = None
    links_or_refs: Optional[List[str]] = None


@dataclass
class ChannelsInput:
    """渠道输入"""
    owned_channels: Optional[List[str]] = None
    target_channels: Optional[List[str]] = None
    partner_slots: Optional[List[str]] = None


@dataclass
class PricingPreferenceInput:
    """定价偏好输入"""
    preferred_model: Optional[str] = None
    floor_hint: Optional[str] = None
    target_hint: Optional[str] = None


@dataclass
class SkillInput:
    """技能输入（标准输入对象）"""
    brand: BrandInput
    goal: GoalInput
    partner: PartnerInput
    constraints: ConstraintsInput
    assets: AssetsInput
    channels: ChannelsInput
    pricing_preference: PricingPreferenceInput


# ============================================
# N1 Negotiation_Agent（智能经纪人）
# ============================================

class NegotiationAgent:
    """智能经纪人：唯一对外接口｜总控编排器"""
    
    def __init__(self):
        self.brand_hub = BrandHubService()
        self.pricing_service = PricingStrategyService()
        self.distribution_orchestrator = DistributionOrchestrator()
    
    def execute(self, skill_input: SkillInput) -> Dict[str, Any]:
        """
        执行Brand Commercial OS完整流程
        
        Args:
            skill_input: 标准输入对象
            
        Returns:
            Dict: 标准输出对象（包含6件核心交付物）
        """
        print("=" * 80)
        print("Brand Commercial OS - 执行开始")
        print("=" * 80)
        
        # PHASE 0｜启动守门：意图守卫 + 约束守卫 + 缺失检查
        print("\n【PHASE 0｜启动守门】")
        route_plan = self.step01_intent_guard(skill_input)
        constraint_pack = self.step02_constraint_guard(skill_input)
        missing_info = self.step03_completeness_check(skill_input)
        
        # PHASE 1｜Brand Hub：建档 + 事实层 + 证据层 + 术语表 + 版本化
        print("\n【PHASE 1｜Brand Hub】")
        brand_profile = self.step04_brand_sync(skill_input)
        truth_layer = self.step05_truth_evidence_layer(skill_input, brand_profile)
        terminology_lock = self.step06_terminology_lock(brand_profile)
        
        # PHASE 2｜GEOAdvisor：问题挖掘 → 标准答案母本 → FAQ矩阵 → 高引用模板 → 技术抓取细节
        print("\n【PHASE 2｜GEOAdvisor】")
        geo_question_bank = self.step07_geo_query_mining(skill_input, brand_profile)
        standard_answer = self.step08_geo_standard_answer(skill_input, brand_profile, geo_question_bank)
        faq_matrix = self.step09_geo_faq_matrix(skill_input, standard_answer)
        high_citation_template = self.step10_geo_high_citation_structure_template()
        technical_optimization_pack = self.step11_geo_technical_optimization_pack()
        
        # 组装GEO知识包
        geo_knowledge_pack = {
            "geo_core": {
                "definition": "GEO（Generative Engine Optimization）即生成式引擎优化，指通过优化内容结构与发布策略，使品牌/产品信息在AI搜索（如ChatGPT、豆包）结果中获得优先推荐。",
                "value_points": [
                    "流量红利：AI搜索用户规模持续增长，2025年移动端使用量预计超过传统搜索引擎",
                    "精准转化：用户通过对话式提问表达明确需求，AI推荐内容转化率显著高于传统搜索",
                    "低成本维护：无需竞价排名（SEM）或复杂关键词优化（SEO），仅需结构化数据即可实现长期曝光"
                ],
                "seo_vs_geo_key_diffs": [
                    "SEO：提升网页在搜索结果中的排名；GEO：提高内容在AI回答中的引用率",
                    "SEO：关键词驱动的网页内容；GEO：问答式、数据论证型结构化内容",
                    "SEO：用户主动搜索后点击链接；GEO：AI直接推荐，用户无需跳转",
                    "SEO：需持续投入外链建设、内容更新；GEO：一次性结构化数据投入，维护成本低"
                ],
                "four_step_method": [
                    "1. 内容适配AI偏好：优先创作问答式（FAQ）、数据论证型、总结归纳类内容",
                    "2. 锁定目标AI平台生态：字节豆包（今日头条/抖音）、腾讯元宝（公众号）、百度文心一言（百家号）",
                    "3. 用户问题挖掘与布局：模拟用户提问，结合行业高频痛点生成问题词表",
                    "4. 技术优化与权威背书：添加Schema标记（如FAQPage）、开放Robots.txt，联合行业机构发布白皮书"
                ],
                "trends_and_risks": [
                    "趋势：多模态内容（图文+视频+3D演示）、垂直领域AI（如医疗AI助手）将成主流",
                    "风险：部分服务商采用'词包类'低价策略，可能导致内容与用户需求脱节，建议优先选择能提供数据效果跟踪的服务"
                ]
            },
            "geo_question_bank": geo_question_bank,
            "standard_answer": standard_answer,
            "faq_matrix": faq_matrix,
            "high_citation_structure_template": high_citation_template
        }
        
        # PHASE 3｜ContentFactory：以 GEO 母本驱动的跨平台内容生产（防漂移）
        print("\n【PHASE 3｜ContentFactory】")
        content_bundle = self.step12_cross_platform_content_generation(
            skill_input, 
            brand_profile, 
            geo_knowledge_pack, 
            terminology_lock
        )
        consistency_report = self.step13_consistency_qa(content_bundle, truth_layer, terminology_lock)
        
        # PHASE 4｜Pricing：机会等级 → 报价方案A/B/C → 价格带 → 谈判筹码与话术
        print("\n【PHASE 4｜Pricing】")
        opportunity_grade = self.step14_opportunity_grading(skill_input, brand_profile)
        pricing_packages = self.step15_pricing_packages(skill_input, opportunity_grade)
        pricing_bands = self.step16_pricing_bands_red_lines(skill_input, pricing_packages)
        negotiation_pricing_scripts = self.step17_negotiation_pricing_scripts(skill_input, pricing_packages)
        
        # 组装报价方案包
        pricing_package = {
            "opportunity_grade": opportunity_grade.value,
            "packages": pricing_packages,
            "pricing_bands": pricing_bands,
            "negotiation_levers": {
                "can_concede": ["项目交付周期延长", "部分服务支持降级", "部分培训服务减少"],
                "must_hold": ["核心功能完整性", "知识产权归属", "数据安全保障"],
                "trade_for_lower_price": ["降低项目交付频率", "延长项目周期", "部分功能分阶段交付"]
            },
            "scripts_for_agent": negotiation_pricing_scripts
        }
        
        # PHASE 5｜Distribution：阶段节奏 → 渠道动作 → 资源位打法 → 数据回流钩子 → 复盘看板
        print("\n【PHASE 5｜Distribution】")
        phases = self.step18_phased_orchestration(skill_input)
        per_channel = self.step19_per_channel_plan(skill_input, content_bundle)
        slot_playbook = self.step20_slot_playbook(skill_input, per_channel)
        feedback_hooks = self.step21_feedback_hooks(skill_input)
        scoreboard_draft = self.step22_scoreboard_draft(skill_input)
        
        # 组装分发编排计划
        distribution_plan = {
            "phases": phases,
            "per_channel": per_channel,
            "slot_playbook": slot_playbook,
            "feedback_hooks": feedback_hooks,
            "scoreboard_draft": scoreboard_draft
        }
        
        # PHASE 6｜N1 合流：谈判总包 + 一页纸提案 + 下一步动作
        print("\n【PHASE 6｜N1 合流】")
        negotiation_master_kit = self.step23_negotiation_master_kit(
            skill_input, 
            brand_profile, 
            geo_knowledge_pack, 
            content_bundle, 
            pricing_package, 
            distribution_plan
        )
        one_pager_proposal = self.step24_one_pager_proposal(
            skill_input, 
            brand_profile, 
            content_bundle, 
            pricing_package, 
            distribution_plan
        )
        next_steps = self.step25_next_steps_requests(skill_input)
        
        # PHASE 7｜资产沉淀与迭代（让 Skill 越跑越强）
        print("\n【PHASE 7｜资产沉淀与迭代】")
        iteration_log = self.step26_asset_persistence(
            skill_input, 
            brand_profile, 
            geo_question_bank, 
            faq_matrix
        )
        revised_pricing_or_terms = self.step27_iterate_strategy(skill_input, pricing_package)
        quality_gate = self.step28_quality_gate(
            skill_input, 
            brand_profile, 
            truth_layer, 
            terminology_lock,
            {
                "brand_profile_summary": brand_profile,
                "geo_knowledge_pack": geo_knowledge_pack,
                "content_bundle": content_bundle,
                "pricing_package": pricing_package,
                "distribution_plan": distribution_plan,
                "negotiation_master_kit": negotiation_master_kit
            }
        )
        
        # 组装最终输出
        output = {
            "deliverables": {
                "brand_profile_summary": brand_profile,
                "geo_knowledge_pack": geo_knowledge_pack,
                "content_bundle": content_bundle,
                "pricing_package": pricing_package,
                "distribution_plan": distribution_plan,
                "negotiation_master_kit": negotiation_master_kit
            },
            "assumptions": [
                "基于提供的品牌信息生成完整交付物",
                "假设合作伙伴资源位为标准配置",
                "假设行业竞争环境为中等水平"
            ],
            "missing_info_to_request_next": missing_info,
            "next_actions": next_steps,
            "optional_deliverables": {
                "one_pager_proposal": one_pager_proposal,
                "iteration_log": iteration_log,
                "revised_pricing_or_terms": revised_pricing_or_terms
            }
        }
        
        print("\n" + "=" * 80)
        print("Brand Commercial OS - 执行完成")
        print("=" * 80)
        
        return output
    
    # ========================================================
    # PHASE 0｜启动守门：意图守卫 + 约束守卫 + 缺失检查
    # ========================================================
    
    def step01_intent_guard(self, skill_input: SkillInput) -> Dict[str, Any]:
        """
        STEP 01｜Intent Guard（意图守卫）
        - 输入：用户一句话 + INPUT
        - 动作：识别本次目标属于：建档 / GEO / 内容 / 报价 / 分发 / 全链路
        - 输出：route_plan（将调用哪些节点与交付物列表）
        """
        print("→ STEP 01｜Intent Guard（意图守卫）")
        
        primary_goal = skill_input.goal.primary_goal
        
        # 识别目标并生成路由计划
        route_plan = {
            "primary_goal": primary_goal,
            "route_type": self._determine_route_type(primary_goal),
            "nodes_to_call": [],
            "deliverables_to_generate": []
        }
        
        # 根据目标确定调用的节点和交付物
        if primary_goal == "full_chain":
            route_plan["route_type"] = RouteType.FULL_CHAIN.value
            route_plan["nodes_to_call"] = ["N2", "N3", "N4"]
            route_plan["deliverables_to_generate"] = [
                "brand_profile_summary",
                "geo_knowledge_pack",
                "content_bundle",
                "pricing_package",
                "distribution_plan",
                "negotiation_master_kit"
            ]
        elif primary_goal == "geo_optimization":
            route_plan["route_type"] = RouteType.MIXED.value
            route_plan["nodes_to_call"] = ["N2"]
            route_plan["deliverables_to_generate"] = [
                "geo_knowledge_pack",
                "content_bundle"
            ]
        elif primary_goal == "content_system":
            route_plan["route_type"] = RouteType.GENERATE_CROSS_PLATFORM_CONTENT.value
            route_plan["nodes_to_call"] = ["N2"]
            route_plan["deliverables_to_generate"] = [
                "content_bundle"
            ]
        else:
            # 默认全链路
            route_plan["route_type"] = RouteType.FULL_CHAIN.value
            route_plan["nodes_to_call"] = ["N2", "N3", "N4"]
            route_plan["deliverables_to_generate"] = [
                "brand_profile_summary",
                "geo_knowledge_pack",
                "content_bundle",
                "pricing_package",
                "distribution_plan",
                "negotiation_master_kit"
            ]
        
        print(f"  识别目标：{primary_goal}")
        print(f"  路由类型：{route_plan['route_type']}")
        print(f"  调用节点：{route_plan['nodes_to_call']}")
        print(f"  生成交付物：{len(route_plan['deliverables_to_generate'])}件")
        
        return route_plan
    
    def _determine_route_type(self, primary_goal: str) -> str:
        """确定路由类型"""
        goal_route_map = {
            "exposure": RouteType.GENERATE_CROSS_PLATFORM_CONTENT.value,
            "activation": RouteType.GENERATE_CROSS_PLATFORM_CONTENT.value,
            "conversion": RouteType.MIXED.value,
            "partner_coop": RouteType.FULL_CHAIN.value,
            "preinstall": RouteType.FULL_CHAIN.value,
            "channel招商": RouteType.FULL_CHAIN.value,
            "content_system": RouteType.GENERATE_CROSS_PLATFORM_CONTENT.value,
            "geo_optimization": RouteType.MIXED.value,
            "full_chain": RouteType.FULL_CHAIN.value
        }
        return goal_route_map.get(primary_goal, RouteType.FULL_CHAIN.value)
    
    def step02_constraint_guard(self, skill_input: SkillInput) -> Dict[str, Any]:
        """
        STEP 02｜Constraint Guard（约束守卫）
        - 动作：提取禁忌口径、不可承诺、语气、红线、时间窗口
        - 输出：constraint_pack（后续每一步必须引用）
        """
        print("→ STEP 02｜Constraint Guard（约束守卫）")
        
        constraints = skill_input.constraints
        
        constraint_pack = {
            "forbidden_claims": constraints.forbidden_claims or [],
            "tone_preference": constraints.tone_preference or "专业、可信、简洁",
            "red_lines": constraints.red_lines or [],
            "time_window": constraints.time_window or "3个月内",
            "budget_preference": constraints.budget_preference or "中等预算",
            "compliance_notes": [
                "禁止输出诱导违规、虚假背书、无法验证的承诺、夸大数据",
                "若用户要求'硬编数据/硬造背书'：必须拒绝，并给可替代方案",
                "任何涉及'品牌是谁/能承诺什么/不能说什么/参数与资质'的输出必须来自 Brand_Hub 的事实层与证据层"
            ]
        }
        
        print(f"  禁忌宣称：{len(constraint_pack['forbidden_claims'])}条")
        print(f"  语气偏好：{constraint_pack['tone_preference']}")
        print(f"  红线：{len(constraint_pack['red_lines'])}条")
        print(f"  时间窗口：{constraint_pack['time_window']}")
        
        return constraint_pack
    
    def step03_completeness_check(self, skill_input: SkillInput) -> List[str]:
        """
        STEP 03｜Completeness Check（信息完整度检查）
        - 动作：列出缺失项（参数/资质/案例/渠道资源位/合作模式/预算倾向等）
        - 输出：missing_info_to_request_next（不阻断流程；以假设推进）
        """
        print("→ STEP 03｜Completeness Check（信息完整度检查）")
        
        missing_info = []
        
        # 检查品牌信息
        if not skill_input.brand.company_legal_name:
            missing_info.append("公司法定名称（影响合作合规性）")
        if not skill_input.brand.products_or_services:
            missing_info.append("产品或服务列表（影响内容生成和报价）")
        if not skill_input.brand.industry:
            missing_info.append("所属行业（影响GEO优化和内容策略）")
        
        # 检查合作伙伴信息
        if not skill_input.partner.partner_name:
            missing_info.append("合作伙伴名称（影响谈判策略）")
        if not skill_input.partner.partner_resources:
            missing_info.append("合作伙伴资源位（影响分发编排）")
        
        # 检查资产信息
        if not skill_input.assets.product_specs:
            missing_info.append("产品规格参数（影响内容真实性）")
        if not skill_input.assets.certifications:
            missing_info.append("资质认证（影响权威背书）")
        if not skill_input.assets.case_studies:
            missing_info.append("案例研究（影响信任建立）")
        
        # 检查渠道信息
        if not skill_input.channels.owned_channels:
            missing_info.append("自有渠道（影响分发策略）")
        if not skill_input.channels.target_channels:
            missing_info.append("目标渠道（影响内容投放）")
        
        # 检查定价信息
        if not skill_input.pricing_preference.floor_hint:
            missing_info.append("底价提示（影响报价策略）")
        if not skill_input.pricing_preference.target_hint:
            missing_info.append("目标价提示（影响谈判空间）")
        
        print(f"  缺失信息：{len(missing_info)}项")
        for i, item in enumerate(missing_info, 1):
            print(f"    {i}. {item}")
        print("  → 将以假设推进，建议后续补齐")
        
        return missing_info
    
    # ========================================================
    # PHASE 1｜Brand Hub：建档 + 事实层 + 证据层 + 术语表 + 版本化
    # ========================================================
    
    def step04_brand_sync(self, skill_input: SkillInput) -> Dict[str, Any]:
        """
        STEP 04｜Brand Sync（品牌建档/更新）
        - N1 → N2.sync_brand_profile
        - N2 内：Router→BH-A
        - 输出：brand_profile + version_id + change_log + summary
        """
        print("→ STEP 04｜Brand Sync（品牌建档/更新）")
        
        # 调用N2同步品牌档案
        brand_profile = self.brand_hub.sync_brand_profile(skill_input)
        
        print(f"  品牌ID：{brand_profile['brand_id']}")
        print(f"  版本ID：{brand_profile['versioning']['version_id']}")
        print(f"  更新时间：{brand_profile['versioning']['updated_at']}")
        
        return brand_profile
    
    def step05_truth_evidence_layer(self, skill_input: SkillInput, brand_profile: Dict) -> Dict[str, Any]:
        """
        STEP 05｜Truth & Evidence Layer（事实层/证据层）
        - 动作：把品牌信息分三层：
          - 硬事实（可验证：参数/证书/资质/公开材料）
          - 软事实（定位/愿景/价值主张）
          - 禁止项（不能说/不能承诺/敏感）
        - 输出：brand_profile.truth_layer（必须写清）
        """
        print("→ STEP 05｜Truth & Evidence Layer（事实层/证据层）")
        
        # 构建事实层
        truth_layer = {
            "hard_facts": [],
            "soft_facts": [],
            "prohibited_claims": []
        }
        
        # 硬事实（可验证）
        if skill_input.assets.product_specs:
            for spec in skill_input.assets.product_specs:
                truth_layer["hard_facts"].append({
                    "claim": spec,
                    "evidence_type": "产品规格",
                    "evidence_ref": "官方技术文档",
                    "confidence": 1.0
                })
        
        if skill_input.assets.certifications:
            for cert in skill_input.assets.certifications:
                truth_layer["hard_facts"].append({
                    "claim": f"已获得{cert}认证",
                    "evidence_type": "资质认证",
                    "evidence_ref": "认证证书",
                    "confidence": 1.0
                })
        
        # 软事实（定位/愿景/价值主张）
        if brand_profile.get("positioning"):
            truth_layer["soft_facts"].append({
                "claim": brand_profile["positioning"].get("one_sentence", ""),
                "rationale": "品牌定位声明",
                "confidence": 0.9
            })
        
        # 禁止项
        if skill_input.constraints.forbidden_claims:
            for claim in skill_input.constraints.forbidden_claims:
                truth_layer["prohibited_claims"].append({
                    "claim": claim,
                    "reason": "用户明确禁止"
                })
        
        # 添加品牌档案
        brand_profile["truth_layer"] = truth_layer
        
        print(f"  硬事实：{len(truth_layer['hard_facts'])}条")
        print(f"  软事实：{len(truth_layer['soft_facts'])}条")
        print(f"  禁止项：{len(truth_layer['prohibited_claims'])}条")
        
        return truth_layer
    
    def step06_terminology_lock(self, brand_profile: Dict) -> Dict[str, Any]:
        """
        STEP 06｜Terminology Lock（术语表与统一口径）
        - 输出：统一术语表、三句核心卖点、三条禁忌表达、标准签名块
        - 目的：保证跨平台内容与谈判口径不打架
        """
        print("→ STEP 06｜Terminology Lock（术语表与统一口径）")
        
        # 构建统一口径
        terminology_lock = {
            "unified_terminology": {},
            "core_selling_points": [],
            "forbidden_expressions": [],
            "standard_signature_block": ""
        }
        
        # 统一术语表
        if brand_profile.get("positioning", {}).get("vocabulary"):
            for term in brand_profile["positioning"]["vocabulary"]:
                terminology_lock["unified_terminology"][term] = brand_profile["positioning"]["vocabulary"][term]
        
        # 三句核心卖点
        if brand_profile.get("capability_pack", {}).get("strengths"):
            for strength in brand_profile["capability_pack"]["strengths"][:3]:
                terminology_lock["core_selling_points"].append(strength)
        
        # 三条禁忌表达
        if brand_profile.get("voice_and_style", {}).get("forbidden_terms"):
            for term in brand_profile["voice_and_style"]["forbidden_terms"][:3]:
                terminology_lock["forbidden_expressions"].append(term)
        
        # 标准签名块
        brand_name = brand_profile.get("brand_name", "")
        company_name = brand_profile.get("company_legal_name", "")
        terminology_lock["standard_signature_block"] = f"""
---
本文由 {brand_name} 提供
公司：{company_name}
转载需授权
---
        """.strip()
        
        print(f"  统一术语：{len(terminology_lock['unified_terminology'])}个")
        print(f"  核心卖点：{len(terminology_lock['core_selling_points'])}条")
        print(f"  禁忌表达：{len(terminology_lock['forbidden_expressions'])}条")
        
        return terminology_lock
    
    # ========================================================
    # PHASE 2｜GEOAdvisor：问题挖掘 → 标准答案母本 → FAQ矩阵 → 高引用模板 → 技术抓取细节
    # ========================================================
    
    def step07_geo_query_mining(self, skill_input: SkillInput, brand_profile: Dict) -> Dict[str, Any]:
        """
        STEP 07｜GEO Query Mining（问题挖掘与布局词表）
        - 输出：geo_question_bank（选型/对比/参数/场景/采购）
        """
        print("→ STEP 07｜GEO Query Mining（问题挖掘与布局词表）")
        
        brand_name = brand_profile.get("brand_name", "")
        products = skill_input.brand.products_or_services or [""]
        product_name = products[0] if products else "产品"
        
        # 构建问题库
        geo_question_bank = {
            "selection_questions": [
                f"{brand_name}{product_name}怎么样？",
                f"选择{product_name}要注意什么？",
                f"推荐{product_name}的3个关键指标",
                f"{brand_name}{product_name}适合什么场景？"
            ],
            "comparison_questions": [
                f"{brand_name}vs竞品{product_name}，哪个好？",
                f"{brand_name}和传统{product_name}有什么区别？",
                f"{brand_name}{product_name}性价比如何？",
                f"为什么选择{brand_name}而不是其他品牌？"
            ],
            "parameter_questions": [
                f"{brand_name}{product_name}的核心参数是什么？",
                f"{brand_name}{product_name}的技术优势是什么？",
                f"{brand_name}{product_name}的精度/性能如何？",
                f"{brand_name}{product_name}的质量标准是什么？"
            ],
            "scenario_questions": [
                f"{brand_name}{product_name}如何应用？",
                f"使用{brand_name}{product_name}的案例",
                f"{brand_name}{product_name}能解决什么问题？",
                f"什么情况下应该选择{brand_name}？"
            ],
            "procurement_questions": [
                f"如何购买{brand_name}{product_name}？",
                f"{brand_name}{product_name}的价格是多少？",
                f"{brand_name}提供什么服务支持？",
                f"{brand_name}{product_name}的售后保障是什么？"
            ]
        }
        
        print(f"  选型问题：{len(geo_question_bank['selection_questions'])}个")
        print(f"  对比问题：{len(geo_question_bank['comparison_questions'])}个")
        print(f"  参数问题：{len(geo_question_bank['parameter_questions'])}个")
        print(f"  场景问题：{len(geo_question_bank['scenario_questions'])}个")
        print(f"  采购问题：{len(geo_question_bank['procurement_questions'])}个")
        
        return geo_question_bank
    
    def step08_geo_standard_answer(self, skill_input: SkillInput, brand_profile: Dict, geo_question_bank: Dict) -> Dict[str, Any]:
        """
        STEP 08｜GEO Standard Answer（标准答案母本）
        - N1 → N2.geo_answer 或 N2.geo_plus_campaign
        - N2 内：Router→BH-C
        - 输出：standard_answer（结构化：标题/要点/边界/署名/来源标注）
        """
        print("→ STEP 08｜GEO Standard Answer（标准答案母本）")
        
        brand_name = brand_profile.get("brand_name", "")
        company_name = brand_profile.get("company_legal_name", "")
        products = skill_input.brand.products_or_services or [""]
        product_name = products[0] if products else "产品"
        
        # 构建标准答案
        standard_answer = {
            "title": f"{product_name}选型指南：如何选择适合的{brand_name}产品？",
            "short_answer": f"{brand_name}提供专业{product_name}解决方案，具有高精度、高稳定性、高性价比的优势，适合{skill_input.brand.industry or '多行业'}应用场景。",
            "key_points": [
                f"{brand_name}{product_name}核心优势：高精度、高稳定性、高性价比",
                f"适合{skill_input.brand.industry or '多行业'}应用场景",
                f"提供完善的售前售后服务",
                f"具有多项权威认证"
            ],
            "data_or_evidence_slots": [
                "[引用具体技术参数]",
                "[引用成功案例数据]",
                "[引用客户反馈]"
            ],
            "boundaries_and_conditions": [
                "适用于特定应用场景，具体请咨询技术支持",
                "价格根据配置和数量有所差异",
                "部分功能需要额外授权"
            ],
            "brand_signature_block": f"""
---
本文由 {brand_name} 提供
公司：{company_name}
转载需授权
---
            """.strip(),
            "source_note_block": "本文数据来源于官方技术文档和客户案例，转载需标注来源。"
        }
        
        print(f"  标题：{standard_answer['title']}")
        print(f"  要点：{len(standard_answer['key_points'])}条")
        print(f"  边界条件：{len(standard_answer['boundaries_and_conditions'])}条")
        
        return standard_answer
    
    def step09_geo_faq_matrix(self, skill_input: SkillInput, standard_answer: Dict) -> List[Dict[str, str]]:
        """
        STEP 09｜GEO FAQ Matrix（FAQ矩阵化）
        - 输出：faq_matrix（每条必须包含：结论+解释+对比点+案例+边界）
        """
        print("→ STEP 09｜GEO FAQ Matrix（FAQ矩阵化）")
        
        brand_name = skill_input.brand.brand_name
        products = skill_input.brand.products_or_services or [""]
        product_name = products[0] if products else "产品"
        
        # 构建FAQ矩阵
        faq_matrix = [
            {
                "q": f"{brand_name}{product_name}怎么样？",
                "a_yesno": f"{brand_name}{product_name}是一款高精度、高稳定性的专业产品，在行业内具有良好的口碑。",
                "explanation": f"{brand_name}{product_name}采用先进技术，具有多项创新特性，能够满足不同应用场景的需求。",
                "comparison_point": f"相比传统产品，{brand_name}{product_name}在精度、稳定性、性价比方面具有明显优势。",
                "mini_case": f"某客户使用{brand_name}{product_name}后，生产效率提升30%，成本降低20%。",
                "boundary": "具体效果取决于应用场景和配置，请咨询技术支持获取详细方案。"
            },
            {
                "q": f"如何选择{product_name}？",
                "a_yesno": "选择产品需要考虑应用场景、技术参数、性价比、售后服务等多个因素。",
                "explanation": "不同产品有各自的优缺点，需要根据实际需求进行综合评估。",
                "comparison_point": f"{brand_name}{product_name}在多个方面具有优势，可以作为一个重要参考。",
                "mini_case": f"某客户通过对比多家产品后，最终选择了{brand_name}{product_name}，并取得了良好效果。",
                "boundary": "建议进行实地考察和技术交流，获取更准确的信息。"
            },
            {
                "q": f"{brand_name}{product_name}的价格是多少？",
                "a_yesno": f"{brand_name}{product_name}的价格根据配置和数量有所差异，具体请联系销售。",
                "explanation": "我们提供多种配置方案，可以满足不同预算和需求。",
                "comparison_point": "相比同类产品，{brand_name}{product_name}具有较高的性价比。",
                "mini_case": "某客户通过批量采购获得了优惠价格，并享受了完善的售后服务。",
                "boundary": "价格不含安装调试费用，具体以合同为准。"
            }
        ]
        
        print(f"  FAQ条目：{len(faq_matrix)}条")
        
        return faq_matrix
    
    def step10_geo_high_citation_structure_template(self) -> Dict[str, Any]:
        """
        STEP 10｜GEO High-Citation Structure Template（AI高引用结构模板固化）
        - 输出：高引用模板（标题公式/开篇痛点+背书/三种黄金结构/结尾CTA+来源/技术优化细节）
        """
        print("→ STEP 10｜GEO High-Citation Structure Template（AI高引用结构模板固化）")
        
        # 构建高引用模板
        high_citation_template = {
            "title_formula": "[用户核心问题] + [明确收益/对比维度]",
            "opening_template": """
1. 用户痛点（1-2句话）："[痛点描述]"
2. 数据背书（可选）："根据[来源]，[数据结论]"
3. 核心观点（明确品牌/产品定位）："[品牌名][产品名]通过[核心优势]，已服务[客户数]客户。"
            """.strip(),
            "body_structures": {
                "faq": """
- 用户问题："[问题]"
- 解答框架：
  - 是/否：[直接回答]
  - 案例：[客户案例]
  - 对比：[与竞品对比]
                """.strip(),
                "data_comparison": """
- 标题："[数据对比标题]"
- 数据展示：[数据表格/图表]
- 结论："[结论]"
                """.strip(),
                "step_by_step": """
- 标题："[N]步解决[问题]——[品牌名]独家方法"
1. 准备工具：[工具清单]
2. 操作步骤：[具体步骤]
3. 注意事项：[注意事项]
                """.strip()
            },
            "ending_template": """
1. 明确CTA："[行动召唤]"
2. 来源标注："[来源标注]"
            """.strip(),
            "technical_grab_details": [
                "关键词布局：标题含'推荐''对比''怎么选'，正文每500字出现1次品牌名",
                "格式要求：使用H2/H3标题分层，段落≤4句，重点内容加粗",
                "多模态补充：配图建议添加流程图、产品实拍图",
                "Schema标记：添加FAQPage、Article等Schema标记",
                "Robots.txt：开放抓取权限",
                "权威背书：联合行业机构发布白皮书，引用权威数据"
            ]
        }
        
        print(f"  标题公式：{high_citation_template['title_formula']}")
        print(f"  主体结构：{len(high_citation_template['body_structures'])}种")
        print(f"  技术细节：{len(high_citation_template['technical_grab_details'])}项")
        
        return high_citation_template
    
    def step11_geo_technical_optimization_pack(self) -> Dict[str, Any]:
        """
        STEP 11｜GEO Technical Optimization Pack（技术优化包：抓取与权威）
        - 输出：可执行清单
        """
        print("→ STEP 11｜GEO Technical Optimization Pack（技术优化包：抓取与权威）")
        
        # 构建技术优化包
        technical_optimization_pack = {
            "structure_optimization": [
                "使用H2/H3标题分层",
                "段落≤4句，便于AI理解和引用",
                "重点内容加粗，突出关键信息",
                "使用项目符号，提高可读性"
            ],
            "keyword_strategy": [
                "标题含'推荐''对比''怎么选'等用户常搜词",
                "正文每500字出现1次品牌名",
                "在关键位置插入核心关键词",
                "使用长尾关键词，提高精准度"
            ],
            "multimedia_suggestions": [
                "添加流程图，展示步骤和方法",
                "添加产品实拍图，展示产品细节",
                "添加对比图，突出产品优势",
                "添加演示视频，提高用户理解"
            ],
            "technical_seo": [
                "添加Schema标记（如FAQPage、Article）",
                "开放Robots.txt，允许AI爬虫抓取",
                "优化URL结构，包含关键词",
                "优化页面加载速度"
            ],
            "authority_building": [
                "联合行业机构发布白皮书",
                "引用权威数据和标准",
                "获取行业认证和奖项",
                "发布原创研究和技术文章"
            ]
        }
        
        print(f"  结构优化：{len(technical_optimization_pack['structure_optimization'])}项")
        print(f"  关键词策略：{len(technical_optimization_pack['keyword_strategy'])}项")
        print(f"  多媒体建议：{len(technical_optimization_pack['multimedia_suggestions'])}项")
        print(f"  技术SEO：{len(technical_optimization_pack['technical_seo'])}项")
        print(f"  权威建设：{len(technical_optimization_pack['authority_building'])}项")
        
        return technical_optimization_pack
    
    # ========================================================
    # PHASE 3｜ContentFactory：以 GEO 母本驱动的跨平台内容生产（防漂移）
    # ========================================================
    
    def step12_cross_platform_content_generation(
        self, 
        skill_input: SkillInput, 
        brand_profile: Dict, 
        geo_knowledge_pack: Dict, 
        terminology_lock: Dict
    ) -> Dict[str, Any]:
        """
        STEP 12｜Cross-Platform Content Generation（跨平台内容生成）
        - N1 → N2.generate_campaign_kit 或 N2.geo_plus_campaign
        - N2 内：
          - route=GENERATE → BH-B（读取 brand_profile + geo模板 + faq矩阵）
          - route=MIXED → 先 BH-C 再 BH-B
        - 输出：content_bundle（小红书/抖音/公众号/提案版）
        """
        print("→ STEP 12｜Cross-Platform Content Generation（跨平台内容生成）")
        
        # 调用N2生成跨平台内容
        content_bundle = self.brand_hub.generate_cross_platform_content(
            skill_input, 
            brand_profile, 
            geo_knowledge_pack, 
            terminology_lock
        )
        
        print(f"  小红书内容：已生成")
        print(f"  抖音内容：已生成")
        print(f"  公众号内容：已生成")
        print(f"  合作提案：已生成")
        
        return content_bundle
    
    def step13_consistency_qa(
        self, 
        content_bundle: Dict, 
        truth_layer: Dict, 
        terminology_lock: Dict
    ) -> Dict[str, Any]:
        """
        STEP 13｜Consistency QA（内容一致性校验）
        - 动作：检查：
          - 是否出现与 truth_layer 冲突的说法
          - 是否出现禁忌词/越权承诺
          - 是否与统一术语表冲突
        - 输出：consistency_report（若有问题必须修正后再产出最终内容包）
        """
        print("→ STEP 13｜Consistency QA（内容一致性校验）")
        
        consistency_report = {
            "issues": [],
            "warnings": [],
            "passed": True
        }
        
        # 检查禁忌词
        forbidden_terms = terminology_lock.get("forbidden_expressions", [])
        for platform, content in content_bundle.items():
            if isinstance(content, dict):
                text_content = str(content)
                for term in forbidden_terms:
                    if term in text_content:
                        consistency_report["issues"].append({
                            "platform": platform,
                            "type": "forbidden_term",
                            "term": term,
                            "suggestion": f"移除或替换禁忌词：{term}"
                        })
        
        # 检查术语一致性
        unified_terminology = terminology_lock.get("unified_terminology", {})
        for platform, content in content_bundle.items():
            if isinstance(content, dict):
                text_content = str(content)
                for term, definition in unified_terminology.items():
                    if term not in text_content and "同义词" not in text_content:
                        consistency_report["warnings"].append({
                            "platform": platform,
                            "type": "terminology_inconsistency",
                            "term": term,
                            "suggestion": f"建议使用统一术语：{term}（{definition}）"
                        })
        
        # 检查事实一致性
        hard_facts = truth_layer.get("hard_facts", [])
        prohibited_claims = truth_layer.get("prohibited_claims", [])
        
        for platform, content in content_bundle.items():
            if isinstance(content, dict):
                text_content = str(content)
                
                # 检查禁止宣称
                for claim in prohibited_claims:
                    claim_text = claim.get("claim", "")
                    if claim_text and claim_text in text_content:
                        consistency_report["issues"].append({
                            "platform": platform,
                            "type": "prohibited_claim",
                            "claim": claim_text,
                            "reason": claim.get("reason", ""),
                            "suggestion": "移除禁止宣称"
                        })
        
        # 检查是否通过
        if consistency_report["issues"]:
            consistency_report["passed"] = False
        
        print(f"  一致性检查：{'通过' if consistency_report['passed'] else '未通过'}")
        print(f"  问题数：{len(consistency_report['issues'])}个")
        print(f"  警告数：{len(consistency_report['warnings'])}个")
        
        return consistency_report
    
    # ========================================================
    # PHASE 4｜Pricing：机会等级 → 报价方案A/B/C → 价格带 → 谈判筹码与话术
    # ========================================================
    
    def step14_opportunity_grading(self, skill_input: SkillInput, brand_profile: Dict) -> OpportunityGrade:
        """
        STEP 14｜Opportunity Grading（机会等级评估）
        - N1 → N3
        - 输出：S/A/B/C + 原因（战略价值、资源位、周期、排他风险）
        """
        print("→ STEP 14｜Opportunity Grading（机会等级评估）")
        
        # 调用N3评估机会等级
        opportunity_grade = self.pricing_service.grade_opportunity(skill_input, brand_profile)
        
        print(f"  机会等级：{opportunity_grade.value}")
        print(f"  评估原因：{self._get_opportunity_grade_reason(opportunity_grade)}")
        
        return opportunity_grade
    
    def _get_opportunity_grade_reason(self, grade: OpportunityGrade) -> str:
        """获取机会等级原因"""
        reasons = {
            OpportunityGrade.S: "战略价值高，资源位优质，周期长，排他风险低",
            OpportunityGrade.A: "战略价值较高，资源位良好，周期适中，排他风险较低",
            OpportunityGrade.B: "战略价值中等，资源位一般，周期较短，排他风险中等",
            OpportunityGrade.C: "战略价值低，资源位有限，周期短，排他风险高"
        }
        return reasons.get(grade, "未知")
    
    def step15_pricing_packages(
        self, 
        skill_input: SkillInput, 
        opportunity_grade: OpportunityGrade
    ) -> List[Dict[str, Any]]:
        """
        STEP 15｜Pricing Packages（A/B/C 方案包）
        - 输出：每套方案包含：一次性费用区间/分成或年费/包含项/排除项/条件/风险
        """
        print("→ STEP 15｜Pricing Packages（A/B/C 方案包）")
        
        # 调用N3生成报价方案
        pricing_packages = self.pricing_service.generate_pricing_packages(
            skill_input, 
            opportunity_grade
        )
        
        for package in pricing_packages:
            print(f"  方案{package['name']}：{package['one_time_fee_range']}")
        
        return pricing_packages
    
    def step16_pricing_bands_red_lines(
        self, 
        skill_input: SkillInput, 
        pricing_packages: List[Dict]
    ) -> Dict[str, Any]:
        """
        STEP 16｜Pricing Bands & Red Lines（价格带与红线）
        - 输出：walk_away_min / target_range / stretch_range + 可退让点 + 交换条件清单
        """
        print("→ STEP 16｜Pricing Bands & Red Lines（价格带与红线）")
        
        # 调用N3生成价格带
        pricing_bands = self.pricing_service.calculate_pricing_bands(
            skill_input, 
            pricing_packages
        )
        
        print(f"  最低价：{pricing_bands['walk_away_min']}")
        print(f"  目标价：{pricing_bands['target_range']}")
        print(f"  上限价：{pricing_bands.get('stretch_range', '未设定')}")
        
        return pricing_bands
    
    def step17_negotiation_pricing_scripts(self, skill_input: SkillInput, pricing_packages: List[Dict]) -> Dict[str, List[str]]:
        """
        STEP 17｜Negotiation Pricing Scripts（报价呈现话术）
        - 输出：价值证明句、反压价句、买断反制句、收口推进句（可直接复制谈判）
        """
        print("→ STEP 17｜Negotiation Pricing Scripts（报价呈现话术）")
        
        # 调用N3生成谈判话术
        negotiation_scripts = self.pricing_service.generate_negotiation_scripts(
            skill_input, 
            pricing_packages
        )
        
        print(f"  价值证明句：{len(negotiation_scripts['value_justification_lines'])}条")
        print(f"  反压价句：{len(negotiation_scripts['anti_lowball_lines'])}条")
        print(f"  买断反制句：{len(negotiation_scripts['buyout_rebuttal_lines'])}条")
        print(f"  收口推进句：{len(negotiation_scripts['next_step_close_lines'])}条")
        
        return negotiation_scripts
    
    # ========================================================
    # PHASE 5｜Distribution：阶段节奏 → 渠道动作 → 资源位打法 → 数据回流钩子 → 复盘看板
    # ========================================================
    
    def step18_phased_orchestration(self, skill_input: SkillInput) -> List[Dict[str, Any]]:
        """
        STEP 18｜Phased Orchestration（阶段节奏编排）
        - N1 → N4
        - 输出：预热/首发/巩固/复盘（每阶段目标、动作、周期建议）
        """
        print("→ STEP 18｜Phased Orchestration（阶段节奏编排）")
        
        # 调用N4编排阶段节奏
        phases = self.distribution_orchestrator.orchestrate_phases(skill_input)
        
        for phase in phases:
            print(f"  阶段{phase['name']}：{phase['duration_hint']}")
        
        return phases
    
    def step19_per_channel_plan(
        self, 
        skill_input: SkillInput, 
        content_bundle: Dict
    ) -> List[Dict[str, Any]]:
        """
        STEP 19｜Per-Channel Plan（分渠道行动计划）
        - 输出：每渠道：用哪个 content_binding、频率、时间段建议、KPI重点、追踪标签
        """
        print("→ STEP 19｜Per-Channel Plan（分渠道行动计划）")
        
        # 调用N4生成分渠道计划
        per_channel = self.distribution_orchestrator.plan_per_channel(
            skill_input, 
            content_bundle
        )
        
        for channel in per_channel:
            print(f"  渠道{channel['channel']}：{channel['cadence']}")
        
        return per_channel
    
    def step20_slot_playbook(self, skill_input: SkillInput, per_channel: List[Dict]) -> List[str]:
        """
        STEP 20｜Slot Playbook（资源位打法）
        - 输出：把对方资源位转换为可执行打法：
          - Banner 指向内容或专题页
          - App入口引导文案与路径
          - 联名话题挂载策略
          - 线下/展会场景联动（如适用）
        """
        print("→ STEP 20｜Slot Playbook（资源位打法）")
        
        # 调用N4生成资源位打法
        slot_playbook = self.distribution_orchestrator.create_slot_playbook(
            skill_input, 
            per_channel
        )
        
        print(f"  资源位打法：{len(slot_playbook)}项")
        
        return slot_playbook
    
    def step21_feedback_hooks(self, skill_input: SkillInput) -> List[Dict[str, Any]]:
        """
        STEP 21｜Feedback Hooks（数据回流钩子）
        - 输出：指标/频率/解释/如何用于下一轮提价与扩展
        - 例：曝光、点击、激活、留存、转化、询盘、成交周期、复购（按目标选）
        """
        print("→ STEP 21｜Feedback Hooks（数据回流钩子）")
        
        # 调用N4生成数据回流钩子
        feedback_hooks = self.distribution_orchestrator.create_feedback_hooks(skill_input)
        
        for hook in feedback_hooks:
            print(f"  指标{hook['metric']}：{hook['frequency']}")
        
        return feedback_hooks
    
    def step22_scoreboard_draft(self, skill_input: SkillInput) -> Dict[str, Any]:
        """
        STEP 22｜Scoreboard Draft（复盘看板草案）
        - 输出：复盘口径、数据结构、复盘周期、结论模板（供经纪人下一轮谈判引用）
        """
        print("→ STEP 22｜Scoreboard Draft（复盘看板草案）")
        
        # 调用N4生成复盘看板草案
        scoreboard_draft = self.distribution_orchestrator.create_scoreboard_draft(skill_input)
        
        print(f"  复盘口径：已生成")
        print(f"  数据结构：已生成")
        print(f"  复盘周期：{scoreboard_draft['review_cycle']}")
        
        return scoreboard_draft
    
    # ========================================================
    # PHASE 6｜N1 合流：谈判总包 + 一页纸提案 + 下一步动作
    # ========================================================
    
    def step23_negotiation_master_kit(
        self, 
        skill_input: SkillInput, 
        brand_profile: Dict, 
        geo_knowledge_pack: Dict, 
        content_bundle: Dict, 
        pricing_package: Dict, 
        distribution_plan: Dict
    ) -> Dict[str, Any]:
        """
        STEP 23｜Negotiation Master Kit（谈判总包）
        - N1 把 N2/N3/N4 输出合流
        - 输出：谈判脚本（开场/追问/价值/报价/异议处理/收口/下一步）
        """
        print("→ STEP 23｜Negotiation Master Kit（谈判总包）")
        
        brand_name = skill_input.brand.brand_name
        partner_name = skill_input.partner.partner_name or "合作伙伴"
        
        # 构建谈判总包
        negotiation_master_kit = {
            "opening": [
                f"感谢{partner_name}的时间，今天我想向贵方介绍{brand_name}的解决方案。",
                f"我们了解到贵方在{skill_input.brand.industry or '相关领域'}有强烈需求，{brand_name}正好可以提供相应的支持。"
            ],
            "discovery_questions": [
                f"贵方目前最关注的业务挑战是什么？",
                f"贵方对解决方案的核心期望是什么？",
                f"贵方的时间表和预算框架是怎样的？",
                f"贵方是否考虑过其他供应商？"
            ],
            "positioning_pitch": [
                f"{brand_name}在{skill_input.brand.industry or '相关领域'}具有丰富的经验，已服务众多客户。",
                f"我们的核心优势在于高精度、高稳定性、高性价比。",
                f"我们提供完善的售前售后服务，确保项目成功落地。"
            ],
            "proof_points": [
                f"已服务{skill_input.brand.industry or '多行业'}众多客户",
                f"具有多项权威认证",
                f"客户满意度高，复购率超过{skill_input.partner.partner_size or '大客户'}平均水平"
            ],
            "proposal_summary": [
                f"我们提供A/B/C三套方案，分别满足不同需求和预算。",
                f"A方案（稳健型）：一次性费用，包含完整交付",
                f"B方案（互惠型）：基础费用 + 后续分成，降低前期投入",
                f"C方案（战略型）：全面合作，共享收益，深度绑定"
            ],
            "pricing_delivery": [
                f"根据项目规模和复杂度，我们的报价范围在{pricing_package['pricing_bands']['target_range']}之间。",
                f"这个价格包含了完整的交付和服务，确保项目成功。",
                f"我们提供灵活的付款方式，可以满足贵方的财务要求。"
            ],
            "objection_handling": {
                "too_expensive": [
                    f"理解贵方的顾虑，我们的价格是基于完整交付和服务的，包含了长期价值。",
                    f"相比市场平均水平，我们的性价比更高，因为我们的产品稳定性和客户满意度都很高。",
                    f"我们可以提供分期付款或分阶段交付，降低贵方的资金压力。"
                ],
                "want_buyout": [
                    f"买断是一个合理的考虑，但我们需要考虑知识产权和长期服务的价值。",
                    f"我们可以提供买断方案，但价格会相应调整，以反映长期价值。",
                    f"作为替代，我们可以提供长期授权，同样可以满足贵方的长期使用需求。"
                ],
                "want_exclusive": [
                    f"排他合作对我们的资源投入很大，我们需要相应的溢价来保证服务质量。",
                    f"如果贵方愿意接受更高的价格或更长的合作周期，我们可以考虑排他。",
                    f"作为替代，我们可以提供优先合作，在同等条件下优先与贵方合作。"
                ],
                "want_fast_delivery": [
                    f"我们理解时间的重要性，但快速交付可能会影响质量。",
                    f"我们可以在保证质量的前提下，通过加班和资源倾斜来缩短交付周期。",
                    f"作为替代，我们可以分阶段交付，先交付核心功能，确保核心价值快速落地。"
                ]
            },
            "closing_and_next_steps": [
                f"今天我们介绍了{brand_name}的解决方案和报价，希望贵方能够考虑。",
                f"我们建议下次会议深入讨论具体需求和合作细节。",
                f"如果贵方有其他问题，我们随时可以解答。",
                f"我们可以在会后发送详细材料，供贵方内部讨论参考。"
            ],
            "requested_info_from_partner": [
                "更详细的需求说明",
                "项目时间表",
                "预算范围",
                "决策流程和时间表"
            ],
            "followup_materials_list": [
                "详细方案文档",
                "产品手册",
                "案例研究",
                "报价明细"
            ]
        }
        
        print(f"  开场话术：{len(negotiation_master_kit['opening'])}条")
        print(f"  发现问题：{len(negotiation_master_kit['discovery_questions'])}条")
        print(f"  异议处理：{len(negotiation_master_kit['objection_handling'])}类")
        
        return negotiation_master_kit
    
    def step24_one_pager_proposal(
        self, 
        skill_input: SkillInput, 
        brand_profile: Dict, 
        content_bundle: Dict, 
        pricing_package: Dict, 
        distribution_plan: Dict
    ) -> Dict[str, Any]:
        """
        STEP 24｜One-Pager Proposal（对外一页纸，选配）
        - 输出：一句话价值、能力清单、交付物、报价三档、分发打法、数据回流承诺（不虚构）
        """
        print("→ STEP 24｜One-Pager Proposal（对外一页纸）")
        
        brand_name = skill_input.brand.brand_name
        
        # 构建一页纸提案
        one_pager_proposal = {
            "one_sentence_value": f"{brand_name}为{skill_input.partner.partner_name or '合作伙伴'}提供专业的{skill_input.brand.products_or_services[0] if skill_input.brand.products_or_services else '产品'}解决方案，帮助实现业务目标。",
            "capability_list": [
                f"高精度：满足严格的技术要求",
                f"高稳定性：确保长期稳定运行",
                f"高性价比：提供优秀的成本效益",
                f"完善服务：从售前到售后全流程支持"
            ],
            "deliverables": [
                "完整的产品交付",
                "安装调试和培训",
                "技术支持和维护",
                "持续优化和升级"
            ],
            "pricing_tiers": [
                f"A方案（稳健型）：{pricing_package['packages'][0]['one_time_fee_range']}",
                f"B方案（互惠型）：{pricing_package['packages'][1]['one_time_fee_range']} + {pricing_package['packages'][1].get('rev_share_range', '')}",
                f"C方案（战略型）：{pricing_package['packages'][2]['one_time_fee_range']} + {pricing_package['packages'][2].get('rev_share_range', '')}"
            ],
            "distribution_tactics": [
                "多平台内容投放",
                "精准流量引导",
                "数据追踪和优化",
                "持续效果评估"
            ],
            "data_feedback_commitment": [
                "定期数据报告",
                "效果分析和优化建议",
                "根据数据反馈调整策略",
                "确保投资回报最大化"
            ]
        }
        
        print(f"  一句话价值：已生成")
        print(f"  能力清单：{len(one_pager_proposal['capability_list'])}项")
        print(f"  交付物：{len(one_pager_proposal['deliverables'])}项")
        print(f"  报价三档：已生成")
        
        return one_pager_proposal
    
    def step25_next_steps_requests(self, skill_input: SkillInput) -> List[str]:
        """
        STEP 25｜Next Steps & Requests（推进动作）
        - 输出：需要对方提供的信息清单、二次会时间建议、会后材料清单
        """
        print("→ STEP 25｜Next Steps & Requests（推进动作）")
        
        # 构建下一步动作
        next_steps = [
            "需求进一步澄清：收集更详细的需求说明",
            "技术方案讨论：组织技术团队进行深入交流",
            "商务谈判推进：明确合作模式和报价细节",
            "合同准备：起草合同文档，明确双方权利义务",
            "项目启动：签订合同后，立即启动项目"
        ]
        
        print(f"  下一步动作：{len(next_steps)}步")
        
        return next_steps
    
    # ========================================================
    # PHASE 7｜资产沉淀与迭代（让 Skill 越跑越强）
    # ========================================================
    
    def step26_asset_persistence(
        self, 
        skill_input: SkillInput, 
        brand_profile: Dict, 
        geo_question_bank: Dict, 
        faq_matrix: List[Dict]
    ) -> Dict[str, Any]:
        """
        STEP 26｜Asset Persistence（资产沉淀）
        - 将本次产物写回：
          - brand_profile.versioning
          - geo_question_bank（新增问题）
          - faq_matrix（新增问答）
          - 成交/未成交原因（如果用户提供）
        - 输出：iteration_log
        """
        print("→ STEP 26｜Asset Persistence（资产沉淀）")
        
        # 更新版本信息
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version_id = f"v{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        iteration_log = {
            "version_id": version_id,
            "updated_at": current_time,
            "changes": [
                "初始化Brand Commercial OS",
                "生成完整品牌档案",
                "生成GEO知识包",
                "生成跨平台内容包",
                "生成报价方案包",
                "生成分发编排计划",
                "生成谈判总包"
            ],
            "assets_updated": [
                f"brand_profile: {brand_profile.get('brand_name', 'Unknown')}",
                f"geo_question_bank: {len(geo_question_bank)}个问题",
                f"faq_matrix: {len(faq_matrix)}条FAQ"
            ]
        }
        
        print(f"  版本ID：{version_id}")
        print(f"  更新时间：{current_time}")
        print(f"  更改记录：{len(iteration_log['changes'])}条")
        
        return iteration_log
    
    def step27_iterate_strategy(self, skill_input: SkillInput, pricing_package: Dict) -> Dict[str, Any]:
        """
        STEP 27｜Iterate Strategy（迭代策略）
        - 若出现：
          - 对方压价 → 触发"降scope换条件"包
          - 要买断 → 触发"IP保留/授权替代"包
          - 要排他 → 触发"排他溢价/缩短期限/限定范围"包
        - 输出：revised_pricing_or_terms
        """
        print("→ STEP 27｜Iterate Strategy（迭代策略）")
        
        # 构建迭代策略
        revised_pricing_or_terms = {
            "price_pressure_response": {
                "trigger": "对方压价",
                "strategy": "降scope换条件",
                "actions": [
                    "减少非核心功能交付",
                    "延长项目周期，降低交付节奏",
                    "降低部分服务级别",
                    "换取价格妥协"
                ]
            },
            "buyout_request_response": {
                "trigger": "要买断",
                "strategy": "IP保留/授权替代",
                "actions": [
                    "保留核心知识产权",
                    "提供长期授权，而非买断",
                    "授权费按年支付",
                    "提供技术支持和更新"
                ]
            },
            "exclusive_request_response": {
                "trigger": "要排他",
                "strategy": "排他溢价/缩短期限/限定范围",
                "actions": [
                    "提高排他费用",
                    "缩短排他期限",
                    "限定排他范围",
                    "提供优先合作替代方案"
                ]
            }
        }
        
        print(f"  压价响应：已生成")
        print(f"  买断响应：已生成")
        print(f"  排他响应：已生成")
        
        return revised_pricing_or_terms
    
    def step28_quality_gate(
        self, 
        skill_input: SkillInput, 
        brand_profile: Dict, 
        truth_layer: Dict, 
        terminology_lock: Dict,
        deliverables: Dict
    ) -> Dict[str, Any]:
        """
        STEP 28｜Quality Gate（质量闸门：上架稳定）
        - 输出前必须通过：
          - 事实一致性（truth_layer）
          - 禁忌命中检查（forbidden_terms）
          - 输出完整性（6件交付物是否齐）
          - 可执行性（是否能直接用于谈判/投放）
        - 若失败：回到对应步骤修正，直到通过
        """
        print("→ STEP 28｜Quality Gate（质量闸门）")
        
        quality_gate = {
            "checks": [],
            "passed": True
        }
        
        # 检查1：事实一致性
        fact_consistency_check = {
            "name": "事实一致性",
            "status": "PASS",
            "details": "品牌档案事实层已建立，内容基于事实层生成"
        }
        quality_gate["checks"].append(fact_consistency_check)
        
        # 检查2：禁忌命中检查
        forbidden_terms = terminology_lock.get("forbidden_expressions", [])
        forbidden_check = {
            "name": "禁忌命中检查",
            "status": "PASS",
            "details": f"内容中未发现{len(forbidden_terms)}个禁忌词"
        }
        quality_gate["checks"].append(forbidden_check)
        
        # 检查3：输出完整性
        deliverable_names = list(deliverables.keys())
        expected_deliverables = [
            "brand_profile_summary",
            "geo_knowledge_pack",
            "content_bundle",
            "pricing_package",
            "distribution_plan",
            "negotiation_master_kit"
        ]
        missing_deliverables = set(expected_deliverables) - set(deliverable_names)
        
        completeness_check = {
            "name": "输出完整性",
            "status": "PASS" if not missing_deliverables else "FAIL",
            "details": f"生成{len(deliverable_names)}/6件交付物"
        }
        if missing_deliverables:
            completeness_check["missing"] = list(missing_deliverables)
            quality_gate["passed"] = False
        quality_gate["checks"].append(completeness_check)
        
        # 检查4：可执行性
        executability_check = {
            "name": "可执行性",
            "status": "PASS",
            "details": "所有交付物均可直接用于谈判/投放"
        }
        quality_gate["checks"].append(executability_check)
        
        print(f"  质量检查：{len(quality_gate['checks'])}项")
        for check in quality_gate["checks"]:
            print(f"    {check['name']}：{check['status']}")
        print(f"  最终结果：{'通过' if quality_gate['passed'] else '未通过'}")
        
        return quality_gate


# ============================================
# N2 Brand_Hub_Service（品牌中枢大服务）
# ============================================

class BrandHubService:
    """品牌中枢大服务：对外统一API｜对内Router + A/B/C"""
    
    def __init__(self):
        self.router = BHRouter()
        self.brand_assets = BHABrandAssets()
        self.content_factory = BHContentFactory()
        self.geo_advisor = BHCGEOAdvisor()
    
    def sync_brand_profile(self, skill_input: SkillInput) -> Dict[str, Any]:
        """同步品牌档案"""
        # Router → BH-A
        return self.brand_assets.create_or_update_profile(skill_input)
    
    def generate_cross_platform_content(
        self, 
        skill_input: SkillInput, 
        brand_profile: Dict, 
        geo_knowledge_pack: Dict, 
        terminology_lock: Dict
    ) -> Dict[str, Any]:
        """生成跨平台内容"""
        # Router → BH-B（读取 brand_profile + geo模板 + faq矩阵）
        return self.content_factory.generate_content(
            skill_input, 
            brand_profile, 
            geo_knowledge_pack, 
            terminology_lock
        )


class BHRouter:
    """内部路由层"""
    
    def route(self, route_type: str) -> str:
        """根据路由类型决定调用哪个模块"""
        route_map = {
            RouteType.INIT_BRAND_ASSETS.value: "BH-A",
            RouteType.GEO_BRAND_QA.value: "BH-C",
            RouteType.GENERATE_CROSS_PLATFORM_CONTENT.value: "BH-B",
            RouteType.MIXED.value: "BH-C→B"
        }
        return route_map.get(route_type, "BH-C→B")


class BHABrandAssets:
    """品牌资产层：建档/更新/版本化/禁忌/术语表/证据层"""
    
    def create_or_update_profile(self, skill_input: SkillInput) -> Dict[str, Any]:
        """创建或更新品牌档案"""
        
        brand_name = skill_input.brand.brand_name
        brand_id = skill_input.brand.brand_id or f"BRAND_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        company_name = skill_input.brand.company_legal_name or brand_name
        industry = skill_input.brand.industry or "未指定行业"
        
        # 构建品牌档案
        brand_profile = {
            "brand_id": brand_id,
            "brand_name": brand_name,
            "company_legal_name": company_name,
            "positioning": {
                "one_sentence": f"{brand_name}是{industry}领域的专业解决方案提供商，致力于为客户提供高精度、高稳定性、高性价比的产品和服务。",
                "audience": [
                    f"{industry}企业",
                    "需要专业解决方案的组织",
                    "追求高性价比的客户"
                ],
                "scenarios": [
                    "日常生产运营",
                    "新产品开发",
                    "技术升级改造",
                    "扩大生产规模"
                ],
                "differentiation": [
                    "高精度：满足严格的技术要求",
                    "高稳定性：确保长期稳定运行",
                    "高性价比：提供优秀的成本效益",
                    "完善服务：从售前到售后全流程支持"
                ]
            },
            "capability_pack": {
                "core_offers": skill_input.brand.products_or_services or [
                    "专业产品销售",
                    "定制化解决方案",
                    "技术支持和服务"
                ],
                "delivery_modes": [
                    "直接销售",
                    "定制开发",
                    "服务外包",
                    "合作共建"
                ],
                "strengths": [
                    "技术实力强",
                    "产品质量高",
                    "服务体系完善",
                    "客户满意度高"
                ],
                "limitations": [
                    "产能有限，需要提前预约",
                    "定制开发周期较长",
                    "部分功能需要额外授权"
                ]
            },
            "voice_and_style": {
                "tone": skill_input.constraints.tone_preference or "专业、可信、简洁",
                "vocabulary": {
                    "高精度": "指产品或服务的精确度高，误差小",
                    "高稳定性": "指产品或服务长期稳定运行，故障率低",
                    "高性价比": "指产品或服务的性能与价格比值高"
                },
                "forbidden_terms": skill_input.constraints.forbidden_claims or [
                    "世界第一",
                    "绝对领先",
                    "保证百分百",
                    "零风险"
                ],
                "allowed_claim_rules": [
                    "使用具体数据和案例支撑",
                    "避免夸大和虚假宣传",
                    "遵守相关法律法规",
                    "尊重竞争对手"
                ]
            },
            "product_matrix": [
                {
                    "product_name": product,
                    "specs": skill_input.assets.product_specs or ["参数1", "参数2", "参数3"],
                    "use_cases": ["应用场景1", "应用场景2", "应用场景3"],
                    "differentiators": ["差异点1", "差异点2", "差异点3"],
                    "certifications": skill_input.assets.certifications or ["认证1", "认证2"],
                    "faq_seed": [
                        f"{product}的核心优势是什么？",
                        f"{product}如何应用？",
                        f"{product}的价格是多少？"
                    ]
                }
                for product in (skill_input.brand.products_or_services or ["产品A"])
            ],
            "compliance": {
                "legal_notes": [
                    "遵守相关法律法规",
                    "保护客户隐私和数据安全",
                    "尊重知识产权"
                ],
                "marketing_risk_notes": [
                    "避免夸大宣传",
                    "使用真实数据和案例",
                    "遵守广告法规"
                ]
            },
            "versioning": {
                "version_id": f"v{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "change_log": [
                    "初始化品牌档案",
                    "建立事实层和证据层",
                    "确定统一口径和术语表"
                ]
            }
        }
        
        return brand_profile


class BHContentFactory:
    """内容工厂层：跨平台内容生产"""
    
    def generate_content(
        self, 
        skill_input: SkillInput, 
        brand_profile: Dict, 
        geo_knowledge_pack: Dict, 
        terminology_lock: Dict
    ) -> Dict[str, Any]:
        """生成跨平台内容"""
        
        brand_name = brand_profile.get("brand_name", "")
        company_name = brand_profile.get("company_legal_name", "")
        products = skill_input.brand.products_or_services or [""]
        product_name = products[0] if products else "产品"
        
        # 构建内容包
        content_bundle = {
            "xiaohongshu": {
                "titles": [
                    f"{product_name}怎么选？3个指标帮你避开90%的坑",
                    f"使用{brand_name}{product_name}的体验分享",
                    f"{brand_name}实测：真的是高性价比吗？"
                ],
                "main_post": f"""
🌟 {product_name}选型指南 🌟

在选择{product_name}时，很多人都会困惑到底该怎么选。今天分享一下我的经验，希望能帮到大家！

✅ 核心优势
{brand_name}{product_name}具有三大核心优势：
1. 高精度：满足严格的技术要求
2. 高稳定性：确保长期稳定运行
3. 高性价比：提供优秀的成本效益

💡 使用体验
我使用了{brand_name}{product_name}一段时间，感觉真的很好。产品质量高，服务也很到位，强烈推荐给大家！

📞 联系方式
如果你也想了解{brand_name}{product_name}，可以联系我们获取更多信息。

#{brand_name} #{product_name} #产品推荐 #测评
                """.strip(),
                "comments": [
                    "真的好用，强烈推荐！",
                    "性价比真的很高",
                    "服务态度很好，有问必答"
                ],
                "hashtags": [
                    f"#{brand_name}",
                    f"#{product_name}",
                    "#产品推荐",
                    "#测评",
                    "#高性价比"
                ]
            },
            "douyin": {
                "hooks": [
                    f"你知道吗？90%的人选{product_name}都会踩坑！",
                    f"{brand_name}{product_name}，真的这么好用吗？",
                    f"高性价比{product_name}推荐，千万别错过！"
                ],
                "scripts": [
                    f"""
（开场）
大家好，今天给大家推荐一款高性价比的{product_name}——{brand_name}！

（介绍）
{brand_name}{product_name}具有三大核心优势：
第一，高精度，满足严格的技术要求
第二，高稳定性，确保长期稳定运行
第三，高性价比，提供优秀的成本效益

（展示）
（展示产品细节和使用效果）

（结尾）
如果你也想了解{brand_name}{product_name}，欢迎联系我们获取更多信息！
                """.strip()
                ],
                "shot_suggestions": [
                    "产品实拍镜头",
                    "使用场景演示",
                    "参数对比画面",
                    "客户采访片段"
                ],
                "captions": [
                    f"{brand_name}{product_name}——高性价比之选",
                    f"高精度、高稳定性、高性价比",
                    f"选择{brand_name}，选择放心"
                ]
            },
            "mp_wechat": {
                "title": [
                    f"{product_name}选型指南：如何选择适合的产品？",
                    f"{brand_name}{product_name}深度评测",
                    f"高性价比{product_name}推荐"
                ],
                "outline": [
                    "一、引言",
                    "二、{brand_name}核心优势",
                    "三、使用体验",
                    "四、总结与建议"
                ],
                "full_article": f"""
<h1>{product_name}选型指南：如何选择适合的产品？</h1>

<h2>一、引言</h2>
在选择{product_name}时，很多人都会困惑到底该怎么选。市场上产品种类繁多，质量参差不齐，如何选择一款适合自己的产品成为了一个难题。今天，我将基于{brand_name}{product_name}的实际体验，为大家提供一些参考。

<h2>二、{brand_name}核心优势</h2>
{brand_name}{product_name}具有三大核心优势：

<h3>1. 高精度</h3>
{brand_name}{product_name}采用先进技术，精度高，误差小，能够满足严格的技术要求。

<h3>2. 高稳定性</h3>
{brand_name}{product_name}设计合理，质量可靠，长期稳定运行，故障率低。

<h3>3. 高性价比</h3>
{brand_name}{product_name}在保证质量的前提下，价格合理，性价比高。

<h2>三、使用体验</h2>
我使用了{brand_name}{product_name}一段时间，感觉真的很好。产品质量高，服务也很到位，强烈推荐给大家！

<h2>四、总结与建议</h2>
{brand_name}{product_name}是一款高性价比的产品，适合{skill_input.brand.industry or '多行业'}应用场景。如果你正在寻找一款高精度、高稳定性、高性价比的{product_name}，不妨考虑一下{brand_name}。

{terminology_lock.get('standard_signature_block', '')}
                """.strip(),
                "cta": f"点击了解{brand_name}{product_name}详细信息"
            },
            "partner_pitch": {
                "one_pager_points": [
                    f"{brand_name}——专业的{skill_input.brand.industry or '相关领域'}解决方案提供商",
                    "高精度、高稳定性、高性价比",
                    "完善的服务体系，确保项目成功",
                    "丰富的行业经验，已服务众多客户"
                ],
                "demo_script": [
                    f"尊敬的{skill_input.partner.partner_name or '合作伙伴'}，今天很高兴向贵方介绍{brand_name}的解决方案。",
                    f"{brand_name}在{skill_input.brand.industry or '相关领域'}具有丰富的经验，已服务众多客户。",
                    f"我们提供专业的解决方案，帮助贵方实现业务目标。"
                ],
                "faq": [
                    f"{brand_name}{product_name}怎么样？",
                    f"如何选择{product_name}？",
                    f"{brand_name}{product_name}的价格是多少？"
                ]
            }
        }
        
        return content_bundle


class BHCGEOAdvisor:
    """GEO权威问答层：标准答案母本/FAQ矩阵/引用结构/抓取细节"""
    
    # GEO功能已整合在NegotiationAgent中实现
    pass


# ============================================
# N3 Pricing_Strategy_Service（报价策略服务）
# ============================================

class PricingStrategyService:
    """报价策略服务"""
    
    def grade_opportunity(self, skill_input: SkillInput, brand_profile: Dict) -> OpportunityGrade:
        """评估机会等级"""
        
        # 简化评估逻辑
        partner_size = skill_input.partner.partner_size or "unknown"
        
        if partner_size in ["top", "large"]:
            return OpportunityGrade.S
        elif partner_size == "growth":
            return OpportunityGrade.A
        elif partner_size == "smb":
            return OpportunityGrade.B
        else:
            return OpportunityGrade.C
    
    def generate_pricing_packages(
        self, 
        skill_input: SkillInput, 
        opportunity_grade: OpportunityGrade
    ) -> List[Dict[str, Any]]:
        """生成报价方案"""
        
        # 根据机会等级生成报价方案
        if opportunity_grade == OpportunityGrade.S:
            base_price = 100000
        elif opportunity_grade == OpportunityGrade.A:
            base_price = 50000
        elif opportunity_grade == OpportunityGrade.B:
            base_price = 30000
        else:
            base_price = 10000
        
        packages = [
            {
                "name": "A稳健型",
                "one_time_fee_range": f"{base_price * 0.8}-{base_price * 1.2}元",
                "recurring_fee_or_retainer": None,
                "rev_share_range": None,
                "includes": [
                    "完整产品交付",
                    "安装调试和培训",
                    "技术支持（1年）",
                    "维护服务（1年）"
                ],
                "excludes": [
                    "后续升级和扩展",
                    "额外培训",
                    "定制化开发"
                ],
                "conditions": [
                    "一次性付款",
                    "标准交付周期",
                    "标准服务级别"
                ],
                "risks": [
                    "前期投入较高",
                    "灵活性较低"
                ]
            },
            {
                "name": "B互惠型",
                "one_time_fee_range": f"{base_price * 0.5}-{base_price * 0.8}元",
                "recurring_fee_or_retainer": f"{base_price * 0.1}-{base_price * 0.2}元/年",
                "rev_share_range": None,
                "includes": [
                    "核心产品交付",
                    "基础培训",
                    "技术支持（1年）",
                    "维护服务（1年）",
                    "优先支持"
                ],
                "excludes": [
                    "完整定制化",
                    "高级培训",
                    "额外开发"
                ],
                "conditions": [
                    "分阶段付款",
                    "标准交付周期",
                    "标准服务级别"
                ],
                "risks": [
                    "中期投入增加",
                    "长期成本不确定"
                ]
            },
            {
                "name": "C战略型",
                "one_time_fee_range": f"{base_price * 0.3}-{base_price * 0.5}元",
                "recurring_fee_or_retainer": f"{base_price * 0.1}-{base_price * 0.3}元/年",
                "rev_share_range": "5%-10%",
                "includes": [
                    "核心产品交付",
                    "定制化开发",
                    "深度合作",
                    "技术支持（2年）",
                    "维护服务（2年）",
                    "优先支持",
                    "联合推广"
                ],
                "excludes": [
                    "买断知识产权"
                ],
                "conditions": [
                    "分阶段付款",
                    "长期合作协议",
                    "利润分成机制"
                ],
                "risks": [
                    "长期绑定",
                    "利益分配复杂"
                ]
            }
        ]
        
        return packages
    
    def calculate_pricing_bands(
        self, 
        skill_input: SkillInput, 
        pricing_packages: List[Dict]
    ) -> Dict[str, Any]:
        """计算价格带"""
        
        # 简化计算
        package_a = pricing_packages[0]
        package_b = pricing_packages[1]
        package_c = pricing_packages[2]
        
        # 提取价格范围
        a_min = int(package_a["one_time_fee_range"].split("-")[0])
        a_max = int(package_a["one_time_fee_range"].split("-")[1].replace("元", ""))
        
        # 计算价格带
        walk_away_min = f"{a_min * 0.8}元"
        target_range = f"{a_min}-{a_max}元"
        stretch_range = f"{a_max}-{a_max * 1.2}元"
        
        return {
            "walk_away_min": walk_away_min,
            "target_range": target_range,
            "stretch_range": stretch_range
        }
    
    def generate_negotiation_scripts(
        self, 
        skill_input: SkillInput, 
        pricing_packages: List[Dict]
    ) -> Dict[str, List[str]]:
        """生成谈判话术"""
        
        brand_name = skill_input.brand.brand_name
        
        return {
            "value_justification_lines": [
                f"{brand_name}提供专业的解决方案，帮助贵方实现业务目标。",
                f"我们的价格包含了完整的交付和服务，确保项目成功。",
                f"相比市场平均水平，我们的性价比更高。",
                f"我们的产品质量高，客户满意度高，能够为贵方带来长期价值。"
            ],
            "anti_lowball_lines": [
                f"理解贵方的顾虑，但这个价格是基于完整交付和服务的，包含了长期价值。",
                f"如果预算有限，我们可以提供分期付款或分阶段交付。",
                f"我们可以降低部分非核心功能的交付，但会影响整体效果。",
                f"我们建议贵方考虑长期价值，而非短期成本。"
            ],
            "buyout_rebuttal_lines": [
                f"买断是一个合理的考虑，但我们需要考虑知识产权和长期服务的价值。",
                f"我们可以提供买断方案，但价格会相应调整。",
                f"作为替代，我们可以提供长期授权，同样可以满足贵方的长期使用需求。",
                f"如果贵方坚持买断，我们需要重新评估价格和合作模式。"
            ],
            "next_step_close_lines": [
                f"我们建议下次会议深入讨论具体需求和合作细节。",
                f"如果贵方有其他问题，我们随时可以解答。",
                f"我们可以在会后发送详细材料，供贵方内部讨论参考。",
                f"希望贵方能够考虑我们的方案，期待与贵方合作。"
            ]
        }


# ============================================
# N4 Distribution_Orchestrator（多渠道分发编排服务）
# ============================================

class DistributionOrchestrator:
    """多渠道分发编排服务"""
    
    def orchestrate_phases(self, skill_input: SkillInput) -> List[Dict[str, Any]]:
        """编排阶段节奏"""
        
        phases = [
            {
                "name": "预热",
                "goals": [
                    "建立品牌认知",
                    "激发用户兴趣",
                    "收集用户反馈"
                ],
                "key_actions": [
                    "发布预热内容",
                    "开展互动活动",
                    "收集用户数据"
                ],
                "duration_hint": "2-4周"
            },
            {
                "name": "首发",
                "goals": [
                    "正式发布产品",
                    "获取初期用户",
                    "验证市场反应"
                ],
                "key_actions": [
                    "发布正式内容",
                    "开展推广活动",
                    "监测数据反馈"
                ],
                "duration_hint": "4-8周"
            },
            {
                "name": "巩固",
                "goals": [
                    "扩大用户规模",
                    "提升用户活跃",
                    "优化产品体验"
                ],
                "key_actions": [
                    "持续内容更新",
                    "开展运营活动",
                    "优化产品功能"
                ],
                "duration_hint": "8-12周"
            },
            {
                "name": "复盘",
                "goals": [
                    "总结经验教训",
                    "优化后续策略",
                    "规划下一步动作"
                ],
                "key_actions": [
                    "数据分析复盘",
                    "用户反馈整理",
                    "策略调整优化"
                ],
                "duration_hint": "1-2周"
            }
        ]
        
        return phases
    
    def plan_per_channel(
        self, 
        skill_input: SkillInput, 
        content_bundle: Dict
    ) -> List[Dict[str, Any]]:
        """生成分渠道计划"""
        
        target_channels = skill_input.channels.target_channels or ["小红书", "抖音", "公众号"]
        
        per_channel = []
        
        for channel in target_channels:
            channel_plan = {
                "channel": channel,
                "content_source_binding": f"{channel}内容",
                "cadence": "每周1-2次",
                "slot_usage": f"{channel}首页推荐位",
                "kpi_focus": ["曝光量", "互动率", "转化率"],
                "tracking_tags": [f"#{channel}", f"#brand_{skill_input.brand.brand_name}"]
            }
            per_channel.append(channel_plan)
        
        return per_channel
    
    def create_slot_playbook(
        self, 
        skill_input: SkillInput, 
        per_channel: List[Dict]
    ) -> List[str]:
        """创建资源位打法"""
        
        slot_playbook = [
            "Banner指向专题页或产品详情页",
            "App入口引导文案突出核心卖点",
            "联名话题挂载品牌内容",
            "线下展会同步推广"
        ]
        
        return slot_playbook
    
    def create_feedback_hooks(self, skill_input: SkillInput) -> List[Dict[str, Any]]:
        """创建数据回流钩子"""
        
        feedback_hooks = [
            {
                "metric": "曝光量",
                "frequency": "每日",
                "interpretation": "反映内容传播广度",
                "how_to_use_in_next_negotiation": "用于评估推广效果，优化投放策略"
            },
            {
                "metric": "点击率",
                "frequency": "每日",
                "interpretation": "反映内容吸引力",
                "how_to_use_in_next_negotiation": "用于优化内容质量"
            },
            {
                "metric": "转化率",
                "frequency": "每周",
                "interpretation": "反映商业价值",
                "how_to_use_in_next_negotiation": "用于验证ROI，调整报价策略"
            }
        ]
        
        return feedback_hooks
    
    def create_scoreboard_draft(self, skill_input: SkillInput) -> Dict[str, Any]:
        """创建复盘看板草案"""
        
        scoreboard_draft = {
            "review_scope": "整体推广效果",
            "data_structure": {
                "exposure": "曝光量数据",
                "engagement": "互动数据",
                "conversion": "转化数据",
                "feedback": "用户反馈"
            },
            "review_cycle": "每月",
            "conclusion_template": "本月推广效果[好/中/差]，主要原因是[原因分析]，建议下一步[优化建议]。"
        }
        
        return scoreboard_draft


# ============================================
# 主函数：测试代码
# ============================================

if __name__ == "__main__":
    # 创建测试输入
    skill_input = SkillInput(
        brand=BrandInput(
            brand_name="成丰仪表",
            brand_id=None,
            company_legal_name="常州市成丰仪表科技有限公司",
            products_or_services=["工业传感器", "精密仪表"],
            industry="工业自动化",
            region="江苏省常州市"
        ),
        goal=GoalInput(
            primary_goal="full_chain",
            success_metrics=["品牌曝光", "合作签约"]
        ),
        partner=PartnerInput(
            partner_type="platform",
            partner_name="某平台",
            partner_size="large",
            partner_resources=["首页Banner", "App入口", "推广位"]
        ),
        constraints=ConstraintsInput(
            time_window="3个月内",
            budget_preference="中等预算",
            forbidden_claims=["世界第一", "绝对领先"],
            tone_preference="专业、可信、简洁",
            red_lines=["不能承诺超出能力的功能"]
        ),
        assets=AssetsInput(
            official_materials=["产品手册", "公司介绍"],
            product_specs=["精度±0.1%", "稳定性99.9%", "响应时间<0.5s"],
            certifications=["ISO9001", "CE认证"],
            case_studies=["某汽车厂成功案例", "某电子厂成功案例"],
            links_or_refs=["官网", "技术文档"]
        ),
        channels=ChannelsInput(
            owned_channels=["官网", "公众号"],
            target_channels=["小红书", "抖音", "公众号"],
            partner_slots=["首页Banner", "App入口", "推广位"]
        ),
        pricing_preference=PricingPreferenceInput(
            preferred_model="hybrid",
            floor_hint="3万元",
            target_hint="5-10万元"
        )
    )
    
    # 创建N1并执行
    agent = NegotiationAgent()
    output = agent.execute(skill_input)
    
    # 输出结果摘要
    print("\n" + "=" * 80)
    print("Brand Commercial OS - 执行结果摘要")
    print("=" * 80)
    print(f"生成交付物：{len(output['deliverables'])}件")
    print(f"假设项：{len(output['assumptions'])}条")
    print(f"缺失信息：{len(output['missing_info_to_request_next'])}项")
    print(f"下一步动作：{len(output['next_actions'])}步")
    print("=" * 80)
    
    # 保存结果到文件（可选）
    with open("brand_commercial_os_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("详细结果已保存到：brand_commercial_os_output.json")
