# -*- coding: utf-8 -*-
"""
公文智能提示系统
根据公文类型和上下文提供智能提示
"""

from typing import Dict, List, Optional
from enum import Enum


class DocumentType(Enum):
    """公文类型枚举"""
    NOTICE = "通知"
    REPORT = "报告"
    REQUEST = "请示"
    LETTER = "函"
    CIRCULAR = "通报"
    MINUTES = "纪要"
    DECISION = "决定"
    OPINION = "意见"
    REPLY = "批复"
    ORDER = "命令(令)"


class SmartPromptSystem:
    """智能提示系统"""
    
    def __init__(self):
        self.opening_prompts = self._init_opening_prompts()
        self.ending_prompts = self._init_ending_prompts()
        self.structure_hints = self._init_structure_hints()
        self.language_templates = self._init_language_templates()
    
    def _init_opening_prompts(self) -> Dict[str, List[str]]:
        """初始化开头语提示"""
        return {
            "通知": [
                "为{subject}，现{action}如下：",
                "根据{basis}，决定{action}。",
                "为了{purpose}，现将{content}通知如下：",
                "经{authority}研究决定，现就{subject}通知如下："
            ],
            "报告": [
                "现将{subject}报告如下：",
                "关于{subject}情况报告如下：",
                "根据{requirement}，现将{content}报告如下：",
                "按照{instruction}，现就{subject}报告如下："
            ],
            "请示": [
                "关于{subject}的请示",
                "现就{subject}请示如下：",
                "为{purpose}，拟{action}，现请示如下："
            ],
            "函": [
                "关于{subject}的函",
                "现就{subject}函告如下：",
                "为{purpose}，商请{action}，现函告如下："
            ],
            "通报": [
                "现将{subject}通报如下：",
                "关于{subject}情况的通报",
                "为{purpose}，现将{content}通报如下："
            ],
            "纪要": [
                "{meeting_name}纪要",
                "{date}，{organizer}召开{meeting_name}，现将会议主要情况纪要如下："
            ],
            "决定": [
                "为{purpose}，决定{action}。",
                "经{authority}研究，决定{action}。"
            ],
            "意见": [
                "为{purpose}，现提出如下意见：",
                "关于{subject}的意见",
                "根据{basis}，现就{subject}提出如下意见："
            ],
            "批复": [
                "你{unit}《关于{subject}的请示》收悉。现批复如下：",
                "关于{subject}的批复"
            ],
            "命令(令)": [
                "为{purpose}，现发布命令如下：",
                "根据{authority}，现发布{order_type}："
            ]
        }
    
    def _init_ending_prompts(self) -> Dict[str, List[str]]:
        """初始化结尾语提示"""
        return {
            "通知": [
                "特此通知。",
                "请认真贯彻执行。",
                "请遵照执行。",
                "以上通知，请认真贯彻落实。"
            ],
            "报告": [
                "特此报告。",
                "以上报告，请审阅。",
                "以上报告如有不妥，请指正。",
                "专此报告。"
            ],
            "请示": [
                "妥否，请批示。",
                "以上请示，请予批复。",
                "当否，请批示。",
                "以上请示如无不妥，请批复。"
            ],
            "函": [
                "请予研究函复。",
                "特此函告。",
                "盼复。",
                "请予支持为盼。",
                "特此函达。"
            ],
            "通报": [
                "特此通报。",
                "望各单位引以为戒。",
                "希各单位认真学习借鉴。"
            ],
            "纪要": [
                "（纪要一般不写结尾语）"
            ],
            "决定": [
                "（决定一般不写结尾语）",
                "本决定自发布之日起施行。"
            ],
            "意见": [
                "以上意见，请结合实际贯彻执行。",
                "以上意见如无不妥，请批转各地执行。"
            ],
            "批复": [
                "此复。",
                "特此批复。"
            ],
            "命令(令)": [
                "（命令一般不写结尾语）",
                "此令。"
            ]
        }
    
    def _init_structure_hints(self) -> Dict[str, List[str]]:
        """初始化结构提示"""
        return {
            "通知": [
                "一、{背景和目的}",
                "二、{主要内容}",
                "三、{具体要求}",
                "四、{执行时间}"
            ],
            "报告": [
                "一、{工作背景}",
                "二、{主要做法}",
                "三、{取得成效}",
                "四、{存在问题}",
                "五、{下一步打算}"
            ],
            "请示": [
                "一、{请示事由}",
                "二、{请示事项}",
                "三、{请示理由}",
                "四、{建议方案}"
            ],
            "函": [
                "一、{发函事由}",
                "二、{主要内容}",
                "三、{请求事项}"
            ],
            "通报": [
                "一、{通报事由}",
                "二、{基本情况}",
                "三、{经验教训}",
                "四、{工作要求}"
            ],
            "纪要": [
                "会议时间：{time}",
                "会议地点：{location}",
                "参会人员：{participants}",
                "会议议题：{agenda}",
                "会议内容：{content}",
                "会议决定：{decisions}"
            ],
            "决定": [
                "一、{决定事由}",
                "二、{决定事项}",
                "三、{执行要求}"
            ],
            "意见": [
                "一、{指导思想}",
                "二、{基本原则}",
                "三、{主要目标}",
                "四、{重点任务}",
                "五、{保障措施}"
            ],
            "批复": [
                "一、{批复依据}",
                "二、{批复意见}",
                "三、{执行要求}"
            ],
            "命令(令)": [
                "一、{命令事由}",
                "二、{命令事项}",
                "三、{执行要求}"
            ]
        }
    
    def _init_language_templates(self) -> Dict[str, Dict[str, str]]:
        """初始化语言模板"""
        return {
            "通知": {
                "subject": "事由",
                "action": "行动",
                "basis": "依据",
                "purpose": "目的",
                "content": "内容",
                "authority": "权威机关"
            },
            "报告": {
                "subject": "报告事项",
                "requirement": "要求",
                "instruction": "指示",
                "content": "内容"
            },
            "请示": {
                "subject": "请示事项",
                "purpose": "目的",
                "action": "行动"
            },
            "函": {
                "subject": "函告事项",
                "purpose": "目的",
                "action": "行动"
            }
        }
    
    def get_opening_prompt(self, doc_type: str, context: Optional[Dict] = None) -> List[str]:
        """获取开头语提示"""
        prompts = self.opening_prompts.get(doc_type, [])
        
        if context:
            filled_prompts = []
            for prompt in prompts:
                try:
                    filled_prompt = prompt.format(**context)
                    filled_prompts.append(filled_prompt)
                except KeyError:
                    filled_prompts.append(prompt)
            return filled_prompts
        
        return prompts
    
    def get_ending_prompt(self, doc_type: str) -> List[str]:
        """获取结尾语提示"""
        return self.ending_prompts.get(doc_type, [])
    
    def get_structure_hint(self, doc_type: str) -> List[str]:
        """获取结构提示"""
        return self.structure_hints.get(doc_type, [])
    
    def get_language_template(self, doc_type: str) -> Dict[str, str]:
        """获取语言模板"""
        return self.language_templates.get(doc_type, {})
    
    def suggest_title(self, doc_type: str, issuer: str, subject: str) -> str:
        """建议标题"""
        return f"{issuer}关于{subject}的{doc_type}"
    
    def suggest_doc_number(self, issuer_abbr: str, year: int, seq: int) -> str:
        """建议发文字号"""
        return f"{issuer_abbr}〔{year}〕{seq}号"
    
    def get_contextual_hint(self, doc_type: str, field: str) -> str:
        """获取上下文提示"""
        hints = {
            "issuer": "发文机关是公文的制发机关，应使用全称或规范化简称",
            "recipient": "主送机关是公文的主要受理机关，应当使用全称、规范化简称或同类型机关统称",
            "title": "标题由发文机关名称、事由和文种组成，应当准确简要地概括公文的主要内容",
            "doc_number": "发文字号由发文机关代字、年份和发文顺序号组成，年份用六角括号〔〕括入",
            "date": "成文日期署会议通过或者发文机关负责人签发的日期，用阿拉伯数字将年、月、日标全",
            "body": "正文是公文的主体，用来表述公文的内容，应当条理清楚、文字简练、用词准确"
        }
        
        return hints.get(field, "")
    
    def generate_sample_content(self, doc_type: str) -> str:
        """生成示例内容"""
        samples = {
            "通知": """
为加强安全管理，防范安全事故发生，现就开展2026年度安全检查工作通知如下：

一、检查时间
2026年3月15日至2026年4月15日。

二、检查范围
公司各部门、各下属单位。

三、检查内容
（一）安全生产责任制落实情况；
（二）安全管理制度执行情况；
（三）安全隐患排查整改情况；
（四）安全教育培训开展情况。

四、工作要求
（一）高度重视，精心组织；
（二）认真检查，不留死角；
（三）发现问题，及时整改；
（四）总结经验，完善制度。

请各部门、各单位按照本通知要求，认真组织开展安全检查工作，确保安全生产。

特此通知。
""",
            "报告": """
现将2025年度工作情况报告如下：

一、主要工作完成情况
（一）业务发展稳步推进；
（二）重点项目顺利实施；
（三）管理水平持续提升；
（四）队伍建设不断加强。

二、存在的问题和不足
（一）业务创新能力有待提高；
（二）人才队伍建设需要加强；
（三）内部管理机制有待完善。

三、2026年度工作计划
（一）加快业务发展；
（二）推进重点项目；
（三）加强队伍建设；
（四）完善管理机制。

以上报告，请审阅。
""",
            "请示": """
关于购置办公设备的请示

因公司业务发展需要，现有办公设备已不能满足工作需求，拟购置一批办公设备。现请示如下：

一、购置原因
公司现有办公设备使用年限较长，性能下降，影响工作效率。

二、购置清单
（一）台式电脑10台；
（二）笔记本电脑5台；
（三）打印机3台；
（四）复印机1台。

三、预算金额
预计总费用约15万元。

四、资金来源
拟从公司年度预算中列支。

妥否，请批示。
"""
        }
        
        return samples.get(doc_type, "暂无示例内容")


def create_smart_prompt_system():
    """创建智能提示系统实例"""
    return SmartPromptSystem()
