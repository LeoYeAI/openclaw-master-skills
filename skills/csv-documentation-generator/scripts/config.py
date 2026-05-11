"""Configuration management for CSV documentation generator"""

import os
from datetime import datetime
from typing import Dict, Any, Optional


class Config:
    """Configuration class for document generation"""

    # System type to GAMP category mapping
    SYSTEM_TYPES = {
        "edc": {
            "category": "4/5",
            "name": "Electronic Data Capture",
            "name_cn": "电子数据采集",
        },
        "ctms": {
            "category": "4",
            "name": "Clinical Trial Management System",
            "name_cn": "临床试验管理系统",
        },
        "lims": {
            "category": "4/5",
            "name": "Laboratory Information Management System",
            "name_cn": "实验室信息管理系统",
        },
        "mes": {
            "category": "4",
            "name": "Manufacturing Execution System",
            "name_cn": "制造执行系统",
        },
        "erp": {
            "category": "4",
            "name": "Enterprise Resource Planning",
            "name_cn": "企业资源计划",
        },
        "scada": {"category": "2/3", "name": "SCADA/DCS", "name_cn": "工业控制系统"},
        "custom": {"category": "3/4", "name": "Custom Software", "name_cn": "自研软件"},
    }

    # Document types
    DOCUMENT_TYPES = {
        "vp": {"name": "Validation Plan", "name_cn": "验证计划", "format": "docx"},
        "urs": {
            "name": "User Requirements Specification",
            "name_cn": "用户需求规格",
            "format": "docx",
        },
        "fs": {
            "name": "Functional Specification",
            "name_cn": "功能规格",
            "format": "docx",
        },
        "ts": {
            "name": "Technical Specification",
            "name_cn": "技术规格",
            "format": "docx",
        },
        "ra": {"name": "Risk Assessment", "name_cn": "风险评估", "format": "docx"},
        "iq": {
            "name": "Installation Qualification",
            "name_cn": "安装确认",
            "format": "docx",
        },
        "oq": {
            "name": "Operational Qualification",
            "name_cn": "操作确认",
            "format": "docx",
        },
        "pq": {
            "name": "Performance Qualification",
            "name_cn": "性能确认",
            "format": "docx",
        },
        "rtm": {"name": "Traceability Matrix", "name_cn": "追溯矩阵", "format": "xlsx"},
        "vsr": {
            "name": "Validation Summary Report",
            "name_cn": "验证总结报告",
            "format": "docx",
        },
        "checklist": {
            "name": "Validation Checklist",
            "name_cn": "验证检查清单",
            "format": "xlsx",
        },
        "test-case": {
            "name": "Test Case Template",
            "name_cn": "测试用例模板",
            "format": "xlsx",
        },
    }

    def __init__(
        self,
        project: str,
        system: str,
        category: int,
        bilingual: bool = True,
        language: str = "zh",
        output: str = "./output",
        format: str = "both",
        **kwargs,
    ):
        self.project = project
        self.system = system
        self.category = str(category)
        self.bilingual = bilingual
        self.language = language
        self.output = output
        self.format = format
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_variables(self) -> Dict[str, str]:
        """Get template variables"""
        return {
            "PROJECT_NAME": self.project,
            "SYSTEM_NAME": self.system,
            "SYSTEM_VERSION": self.system.split("v")[-1]
            if "v" in self.system
            else "1.0",
            "GAMP_CATEGORY": self.category,
            "DATE": self.date,
            "DATETIME": self.datetime,
            "AUTHOR": getattr(self, "author", "[Author]"),
            "REVIEWER": getattr(self, "reviewer", "[Reviewer]"),
            "APPROVER": getattr(self, "approver", "[Approver]"),
            "DOC_ID": getattr(self, "doc_id", "[DOC-XXX]"),
            "VERSION": getattr(self, "version", "1.0"),
            "LANGUAGE": self.language,
            "BILINGUAL": "true" if self.bilingual else "false",
        }

    @classmethod
    def get_system_info(cls, system_type: str) -> Dict[str, str]:
        """Get system type information"""
        system_type_lower = system_type.lower()
        if system_type_lower in cls.SYSTEM_TYPES:
            return cls.SYSTEM_TYPES[system_type_lower]
        return {"category": "4", "name": system_type, "name_cn": system_type}

    @classmethod
    def get_document_info(cls, doc_type: str) -> Dict[str, str]:
        """Get document type information"""
        if doc_type in cls.DOCUMENT_TYPES:
            return cls.DOCUMENT_TYPES[doc_type]
        return {"name": doc_type, "name_cn": doc_type, "format": "docx"}


def get_gamp_category_description(category: str) -> Dict[str, str]:
    """Get GAMP category description"""
    categories = {
        "1": {"name": "Infrastructure Software", "name_cn": "基础设施软件"},
        "2": {"name": "Firmware", "name_cn": "固件"},
        "3": {"name": "Commercial-off-the-shelf (COTS)", "name_cn": "商用现货软件"},
        "4": {"name": "Configured COTS", "name_cn": "配置型COTS"},
        "5": {"name": "Custom/Critical Application", "name_cn": "定制/关键应用"},
    }
    return categories.get(str(category), {"name": "Unknown", "name_cn": "未知"})
