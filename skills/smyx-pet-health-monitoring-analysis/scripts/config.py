#!/usr/bin/env python3
# 宠物日常健康监测分析技能配置文件
import os
import sys

from enum import Enum

from skills.smyx_common.scripts.config import ConstantEnum as ConstantEnumBase

from skills.face_analysis.scripts.config import ApiEnum as ApiEnumParent, ConstantEnum as ConstantEnumParent, \
    SceneCodeEnum, ApiEnumCommonAiMixin


class ApiEnum(ApiEnumCommonAiMixin, ApiEnumParent):
    pass


class ConstantEnum(ConstantEnumParent):
    DEFAULT__PET_TYPE = "cat"
    DEFAULT__MONITOR_DAYS = 1

    @classmethod
    def init(cls, config=None):
        super().init(config)
        ConstantEnumParent.DEFAULT__SCENE_CODE = SceneCodeEnum.PET_HEALTH_MONITORING_ANALYSIS.value
