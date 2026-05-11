#!/usr/bin/env python3
# 中医面诊分析工具配置文件
import os
import sys

from enum import Enum

from skills.smyx_common.scripts.config import ApiEnum as ApiEnumBase, ConstantEnum as ConstantEnumBase

SceneCodeEnum = ConstantEnumBase.SceneCodeEnum


class ApiEnum(ApiEnumBase):
    ANALYSIS_URL = "/web/health-analysis/v2/start-health-analysis"

    ANALYSIS_RESULT_URL = "/web/health-analysis/get-health-analysis-result"

    PAGE_URL = "/web/health-analysis/page-health-analysis-result"

    DETAIL_EXPORT_URL = ApiEnumBase.BASE_URL_HEALTH + "/health/order/api/getReportDetailExport?id="

    @classmethod
    def init(cls, config=None):
        super().init(config)


class ApiEnumCommonAiMixin:

    @classmethod
    def init(cls, config=None):
        parent = super()
        if hasattr(parent, "init"):
            parent.init(config)
        ApiEnum.ANALYSIS_URL = "/web/ai-analysis/v2/start-common-ai-analysis"
        ApiEnum.ANALYSIS_RESULT_URL = "/web/ai-analysis/get-common-ai-analysis-result"
        ApiEnum.PAGE_URL = "/web/ai-analysis/page-common-ai-analysis-result"


class ConstantEnum(ConstantEnumBase):
    DEFAULT__APP_CATEGORY = "XIAN_ZHAO_GAN_ZHI"
