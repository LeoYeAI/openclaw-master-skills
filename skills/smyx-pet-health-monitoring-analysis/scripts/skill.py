#!/usr/bin/env python3
import json

from .config import ApiEnum, ConstantEnum

from skills.smyx_common.scripts.api_service import ApiService as ApiServiceBase

from skills.face_analysis.scripts.skill import Skill as SkillParent
from skills.smyx_common.scripts.util import JsonUtil


class Skill(SkillParent):
    def __init__(self):
        super().__init__()

    def get_output_analysis_content_head(self, result=None):
        return f"📊 宠物日常健康监测分析结构化结果"

    def get_output_analysis_content_foot(self, result):
        pass


skill = Skill()
