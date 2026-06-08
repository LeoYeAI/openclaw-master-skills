# -*- coding: utf-8 -*-
"""
公文生成对话交互系统
支持完整的公文要素对话收集
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


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


class UrgencyLevel(Enum):
    """紧急程度枚举"""
    EXTRA_URGENT = "特急"
    URGENT = "加急"
    NORMAL_URGENT = "平急"
    NONE = "不需要"


class SecretLevel(Enum):
    """密级枚举"""
    TOP_SECRET = "绝密"
    SECRET = "机密"
    CONFIDENTIAL = "秘密"
    NONE = "不需要"


class DialogStep(Enum):
    """对话步骤枚举"""
    START = "start"
    DOC_TYPE = "doc_type"
    ISSUER = "issuer"
    RECIPIENT = "recipient"
    TITLE = "title"
    DOC_NUMBER = "doc_number"
    DATE = "date"
    SECRET_LEVEL = "secret_level"
    URGENCY_LEVEL = "urgency_level"
    SIGNER = "signer"
    BODY = "body"
    ATTACHMENT = "attachment"
    COPY_TO = "copy_to"
    ISSUER_OFFICE = "issuer_office"
    ISSUE_DATE = "issue_date"
    PREVIEW = "preview"
    CONFIRM = "confirm"
    COMPLETE = "complete"


@dataclass
class DocumentContent:
    """公文内容数据结构"""
    doc_type: Optional[str] = None
    issuer: Optional[str] = None
    recipient: Optional[str] = None
    title: Optional[str] = None
    doc_number: Optional[str] = None
    date: Optional[str] = None
    secret_level: Optional[str] = None
    secret_period: Optional[str] = None
    urgency_level: Optional[str] = None
    signer: Optional[str] = None
    body: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    copy_to: List[str] = field(default_factory=list)
    issuer_office: Optional[str] = None
    issue_date: Optional[str] = None
    notes: Optional[str] = None


class DocumentDialogManager:
    """公文对话管理器"""
    
    def __init__(self):
        self.content = DocumentContent()
        self.current_step = DialogStep.START
        self.dialog_history = []
        self.required_steps = []
        self.optional_steps = []
        
    def get_next_prompt(self) -> Dict[str, Any]:
        """获取下一个对话提示"""
        
        prompts = {
            DialogStep.START: self._prompt_start(),
            DialogStep.DOC_TYPE: self._prompt_doc_type(),
            DialogStep.ISSUER: self._prompt_issuer(),
            DialogStep.RECIPIENT: self._prompt_recipient(),
            DialogStep.TITLE: self._prompt_title(),
            DialogStep.DOC_NUMBER: self._prompt_doc_number(),
            DialogStep.DATE: self._prompt_date(),
            DialogStep.SECRET_LEVEL: self._prompt_secret_level(),
            DialogStep.URGENCY_LEVEL: self._prompt_urgency_level(),
            DialogStep.SIGNER: self._prompt_signer(),
            DialogStep.BODY: self._prompt_body(),
            DialogStep.ATTACHMENT: self._prompt_attachment(),
            DialogStep.COPY_TO: self._prompt_copy_to(),
            DialogStep.ISSUER_OFFICE: self._prompt_issuer_office(),
            DialogStep.ISSUE_DATE: self._prompt_issue_date(),
            DialogStep.PREVIEW: self._prompt_preview(),
            DialogStep.CONFIRM: self._prompt_confirm(),
        }
        
        return prompts.get(self.current_step, {"type": "text", "message": "未知步骤"})
    
    def process_user_input(self, user_input: str) -> bool:
        """处理用户输入，返回是否继续对话"""
        
        self.dialog_history.append({
            "step": self.current_step.value,
            "user_input": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        processors = {
            DialogStep.START: self._process_start,
            DialogStep.DOC_TYPE: self._process_doc_type,
            DialogStep.ISSUER: self._process_issuer,
            DialogStep.RECIPIENT: self._process_recipient,
            DialogStep.TITLE: self._process_title,
            DialogStep.DOC_NUMBER: self._process_doc_number,
            DialogStep.DATE: self._process_date,
            DialogStep.SECRET_LEVEL: self._process_secret_level,
            DialogStep.URGENCY_LEVEL: self._process_urgency_level,
            DialogStep.SIGNER: self._process_signer,
            DialogStep.BODY: self._process_body,
            DialogStep.ATTACHMENT: self._process_attachment,
            DialogStep.COPY_TO: self._process_copy_to,
            DialogStep.ISSUER_OFFICE: self._process_issuer_office,
            DialogStep.ISSUE_DATE: self._process_issue_date,
            DialogStep.CONFIRM: self._process_confirm,
        }
        
        processor = processors.get(self.current_step)
        if processor:
            return processor(user_input)
        
        return False
    
    def _prompt_start(self) -> Dict[str, Any]:
        """开始提示"""
        return {
            "type": "text",
            "message": "您好！我将帮您生成一份符合GB/T 9704-2012标准的公文。\n\n让我们开始吧！"
        }
    
    def _prompt_doc_type(self) -> Dict[str, Any]:
        """公文类型提示"""
        return {
            "type": "choice",
            "message": "请问您需要生成什么类型的公文？",
            "options": [
                {"value": "notice", "label": "通知", "description": "发布、传达要求下级机关执行的事项"},
                {"value": "report", "label": "报告", "description": "向上级机关汇报工作、反映情况"},
                {"value": "request", "label": "请示", "description": "向上级机关请求指示、批准"},
                {"value": "letter", "label": "函", "description": "不相隶属机关之间商洽工作"},
                {"value": "circular", "label": "通报", "description": "表彰先进、批评错误"},
                {"value": "minutes", "label": "纪要", "description": "记载会议主要情况"},
                {"value": "decision", "label": "决定", "description": "对重要事项作出决策"},
                {"value": "opinion", "label": "意见", "description": "对重要问题提出见解"},
                {"value": "reply", "label": "批复", "description": "答复下级机关请示事项"},
                {"value": "order", "label": "命令(令)", "description": "公布行政法规和规章"}
            ]
        }
    
    def _prompt_issuer(self) -> Dict[str, Any]:
        """发文机关提示"""
        return {
            "type": "text",
            "message": "请告诉我发文机关的全称：",
            "placeholder": "例如：XXX公司",
            "example": "XXX公司"
        }
    
    def _prompt_recipient(self) -> Dict[str, Any]:
        """主送机关提示"""
        return {
            "type": "text",
            "message": "请告诉我主送机关（接收单位）：",
            "placeholder": "例如：各部门、市人民政府",
            "example": "各部门"
        }
    
    def _prompt_title(self) -> Dict[str, Any]:
        """标题提示"""
        return {
            "type": "text",
            "message": f"请简要描述公文事由，我将帮您生成规范的{self.content.doc_type}标题：",
            "placeholder": "例如：开展2026年度安全检查工作",
            "example": "开展2026年度安全检查工作",
            "hint": f"规范标题格式：发文机关 + 关于 + 事由 + {self.content.doc_type}"
        }
    
    def _prompt_doc_number(self) -> Dict[str, Any]:
        """发文字号提示"""
        return {
            "type": "text",
            "message": "请提供发文字号（格式：机关代字〔年份〕序号号）：",
            "placeholder": "例如：沈数据〔2026〕1号",
            "example": "沈数据〔2026〕1号",
            "hint": "如果不提供，可以留空稍后填写"
        }
    
    def _prompt_date(self) -> Dict[str, Any]:
        """成文日期提示"""
        today = datetime.now().strftime("%Y年%-m月%-d日")
        return {
            "type": "choice",
            "message": f"成文日期是今天（{today}）吗？",
            "options": [
                {"value": "today", "label": f"是，使用今天日期（{today}）"},
                {"value": "custom", "label": "否，我要指定其他日期"}
            ]
        }
    
    def _prompt_secret_level(self) -> Dict[str, Any]:
        """密级提示"""
        return {
            "type": "choice",
            "message": "这份公文需要标注密级吗？",
            "options": [
                {"value": "none", "label": "不需要（普通公文）"},
                {"value": "confidential", "label": "秘密"},
                {"value": "secret", "label": "机密"},
                {"value": "top_secret", "label": "绝密"}
            ]
        }
    
    def _prompt_urgency_level(self) -> Dict[str, Any]:
        """紧急程度提示"""
        return {
            "type": "choice",
            "message": "这份公文的紧急程度是？",
            "options": [
                {"value": "none", "label": "不需要（普通公文）"},
                {"value": "normal", "label": "平急"},
                {"value": "urgent", "label": "加急"},
                {"value": "extra_urgent", "label": "特急"}
            ]
        }
    
    def _prompt_signer(self) -> Dict[str, Any]:
        """签发人提示（仅上行文）"""
        if self.content.doc_type in ["报告", "请示"]:
            return {
                "type": "text",
                "message": "这是一份上行文，请提供签发人姓名：",
                "placeholder": "例如：张三",
                "example": "张三"
            }
        else:
            return self._prompt_body()
    
    def _prompt_body(self) -> Dict[str, Any]:
        """正文内容提示"""
        return {
            "type": "multiline",
            "message": "请描述公文的主要内容要点：",
            "placeholder": "请分点描述主要内容，我将帮您组织成规范的公文语言",
            "hint": "可以输入多个要点，每行一个要点"
        }
    
    def _prompt_attachment(self) -> Dict[str, Any]:
        """附件提示"""
        return {
            "type": "choice",
            "message": "这份公文有附件吗？",
            "options": [
                {"value": "no", "label": "没有附件"},
                {"value": "yes", "label": "有附件"}
            ]
        }
    
    def _prompt_copy_to(self) -> Dict[str, Any]:
        """抄送机关提示"""
        return {
            "type": "text",
            "message": "是否需要抄送给其他单位？如果有，请告诉我单位名称：",
            "placeholder": "例如：市应急管理局、市公安局",
            "hint": "多个单位用顿号分隔，如果没有可以留空"
        }
    
    def _prompt_issuer_office(self) -> Dict[str, Any]:
        """印发机关提示"""
        default_office = f"{self.content.issuer}办公室" if self.content.issuer else ""
        return {
            "type": "text",
            "message": f"印发机关是发文机关办公室吗？",
            "placeholder": f"默认：{default_office}",
            "hint": "如果不同，请填写实际印发机关"
        }
    
    def _prompt_issue_date(self) -> Dict[str, Any]:
        """印发日期提示"""
        return {
            "type": "choice",
            "message": f"印发日期与成文日期（{self.content.date}）相同吗？",
            "options": [
                {"value": "same", "label": f"是，使用相同日期"},
                {"value": "different", "label": "否，我要指定其他日期"}
            ]
        }
    
    def _prompt_preview(self) -> Dict[str, Any]:
        """预览提示"""
        preview_text = self._generate_preview()
        return {
            "type": "preview",
            "message": "公文预览：",
            "content": preview_text
        }
    
    def _prompt_confirm(self) -> Dict[str, Any]:
        """确认提示"""
        return {
            "type": "choice",
            "message": "请确认公文内容是否正确？",
            "options": [
                {"value": "confirm", "label": "确认无误，生成文档"},
                {"value": "modify", "label": "需要修改"}
            ]
        }
    
    def _process_start(self, user_input: str) -> bool:
        """处理开始"""
        self.current_step = DialogStep.DOC_TYPE
        return True
    
    def _process_doc_type(self, user_input: str) -> bool:
        """处理公文类型"""
        type_mapping = {
            "notice": "通知",
            "report": "报告",
            "request": "请示",
            "letter": "函",
            "circular": "通报",
            "minutes": "纪要",
            "decision": "决定",
            "opinion": "意见",
            "reply": "批复",
            "order": "命令(令)"
        }
        
        self.content.doc_type = type_mapping.get(user_input, user_input)
        
        self._determine_required_steps()
        
        self.current_step = DialogStep.ISSUER
        return True
    
    def _process_issuer(self, user_input: str) -> bool:
        """处理发文机关"""
        self.content.issuer = user_input.strip()
        self.current_step = DialogStep.RECIPIENT
        return True
    
    def _process_recipient(self, user_input: str) -> bool:
        """处理主送机关"""
        self.content.recipient = user_input.strip()
        self.current_step = DialogStep.TITLE
        return True
    
    def _process_title(self, user_input: str) -> bool:
        """处理标题"""
        subject = user_input.strip()
        self.content.title = f"关于{subject}的{self.content.doc_type}"
        self.current_step = DialogStep.DOC_NUMBER
        return True
    
    def _process_doc_number(self, user_input: str) -> bool:
        """处理发文字号"""
        if user_input.strip():
            self.content.doc_number = user_input.strip()
        self.current_step = DialogStep.DATE
        return True
    
    def _process_date(self, user_input: str) -> bool:
        """处理成文日期"""
        if user_input == "today":
            self.content.date = datetime.now().strftime("%Y年%-m月%-d日")
        else:
            self.current_step = DialogStep.SECRET_LEVEL
            return True
        
        self.current_step = DialogStep.SECRET_LEVEL
        return True
    
    def _process_secret_level(self, user_input: str) -> bool:
        """处理密级"""
        level_mapping = {
            "none": None,
            "confidential": "秘密",
            "secret": "机密",
            "top_secret": "绝密"
        }
        
        self.content.secret_level = level_mapping.get(user_input)
        
        if self.content.secret_level:
            self.current_step = DialogStep.URGENCY_LEVEL
        else:
            self.current_step = DialogStep.URGENCY_LEVEL
        
        return True
    
    def _process_urgency_level(self, user_input: str) -> bool:
        """处理紧急程度"""
        level_mapping = {
            "none": None,
            "normal": "平急",
            "urgent": "加急",
            "extra_urgent": "特急"
        }
        
        self.content.urgency_level = level_mapping.get(user_input)
        
        if self.content.doc_type in ["报告", "请示"]:
            self.current_step = DialogStep.SIGNER
        else:
            self.current_step = DialogStep.BODY
        
        return True
    
    def _process_signer(self, user_input: str) -> bool:
        """处理签发人"""
        if user_input.strip():
            self.content.signer = user_input.strip()
        self.current_step = DialogStep.BODY
        return True
    
    def _process_body(self, user_input: str) -> bool:
        """处理正文"""
        if user_input.strip():
            self.content.body = [line.strip() for line in user_input.split('\n') if line.strip()]
        self.current_step = DialogStep.ATTACHMENT
        return True
    
    def _process_attachment(self, user_input: str) -> bool:
        """处理附件"""
        if user_input == "yes":
            pass
        self.current_step = DialogStep.COPY_TO
        return True
    
    def _process_copy_to(self, user_input: str) -> bool:
        """处理抄送机关"""
        if user_input.strip():
            self.content.copy_to = [org.strip() for org in user_input.split('、') if org.strip()]
        self.current_step = DialogStep.ISSUER_OFFICE
        return True
    
    def _process_issuer_office(self, user_input: str) -> bool:
        """处理印发机关"""
        if user_input.strip():
            self.content.issuer_office = user_input.strip()
        else:
            self.content.issuer_office = f"{self.content.issuer}办公室"
        self.current_step = DialogStep.ISSUE_DATE
        return True
    
    def _process_issue_date(self, user_input: str) -> bool:
        """处理印发日期"""
        if user_input == "same":
            self.content.issue_date = self.content.date
        self.current_step = DialogStep.PREVIEW
        return True
    
    def _process_confirm(self, user_input: str) -> bool:
        """处理确认"""
        if user_input == "confirm":
            self.current_step = DialogStep.COMPLETE
            return False
        else:
            self.current_step = DialogStep.DOC_TYPE
            return True
    
    def _determine_required_steps(self):
        """根据公文类型确定必需步骤"""
        self.required_steps = [
            DialogStep.DOC_TYPE,
            DialogStep.ISSUER,
            DialogStep.RECIPIENT,
            DialogStep.TITLE,
            DialogStep.DATE,
            DialogStep.BODY
        ]
        
        if self.content.doc_type in ["报告", "请示"]:
            self.required_steps.append(DialogStep.SIGNER)
    
    def _generate_preview(self) -> str:
        """生成预览文本"""
        preview = []
        preview.append(f"公文类型：{self.content.doc_type}")
        preview.append(f"发文机关：{self.content.issuer}")
        preview.append(f"主送机关：{self.content.recipient}")
        preview.append(f"标题：{self.content.title}")
        
        if self.content.doc_number:
            preview.append(f"发文字号：{self.content.doc_number}")
        
        preview.append(f"成文日期：{self.content.date}")
        
        if self.content.secret_level:
            preview.append(f"密级：{self.content.secret_level}")
        
        if self.content.urgency_level:
            preview.append(f"紧急程度：{self.content.urgency_level}")
        
        if self.content.signer:
            preview.append(f"签发人：{self.content.signer}")
        
        preview.append(f"\n正文内容：")
        for i, para in enumerate(self.content.body, 1):
            preview.append(f"{i}. {para}")
        
        if self.content.copy_to:
            preview.append(f"\n抄送机关：{'、'.join(self.content.copy_to)}")
        
        preview.append(f"\n印发机关：{self.content.issuer_office}")
        preview.append(f"印发日期：{self.content.issue_date}")
        
        return '\n'.join(preview)
    
    def get_document_content(self) -> Dict[str, Any]:
        """获取公文内容"""
        return {
            "doc_type": self.content.doc_type,
            "issuer": self.content.issuer,
            "recipient": self.content.recipient,
            "title": self.content.title,
            "doc_number": self.content.doc_number,
            "date": self.content.date,
            "secret_level": self.content.secret_level,
            "secret_period": self.content.secret_period,
            "urgency_level": self.content.urgency_level,
            "signer": self.content.signer,
            "body": self.content.body,
            "attachments": self.content.attachments,
            "copy_to": self.content.copy_to,
            "issuer_office": self.content.issuer_office,
            "issue_date": self.content.issue_date,
            "notes": self.content.notes
        }


def create_dialog_manager():
    """创建对话管理器实例"""
    return DocumentDialogManager()
