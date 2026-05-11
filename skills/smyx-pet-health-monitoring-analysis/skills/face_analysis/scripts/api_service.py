#!/usr/bin/env python3

import os
import sys

from .config import ApiEnum, ConstantEnum
from skills.smyx_common.scripts.api_service import ApiService as ApiServiceBase


class ApiService(ApiServiceBase):

    def __init__(self):
        super().__init__()
        self.analysis_url = ApiEnum.ANALYSIS_URL

    def analysis_result(self, scene_code=ConstantEnum.DEFAULT__SCENE_CODE, *args, **argss):
        params = argss.setdefault("params", {})
        scene_code and params.setdefault("sceneCode", scene_code)
        return self.http_post(ApiEnum.ANALYSIS_RESULT_URL, *args, **argss)

    def analysis(self, scene_code=ConstantEnum.DEFAULT__SCENE_CODE, *args, **argss):
        params = argss.setdefault("params", {})
        options = {
            "dataAsParams": True
        }
        scene_code and params.setdefault("sceneCode", scene_code)
        params.setdefault("appCategory", ConstantEnum.DEFAULT__APP_CATEGORY)
        return self.http_post(self.analysis_url, options=options, *args, **argss)

    def page(self, pageNum=None, pageSize=None, *args, **argss):
        data = argss.setdefault("data", {})
        ConstantEnum.DEFAULT__SCENE_CODE and data.setdefault("sceneCode", ConstantEnum.DEFAULT__SCENE_CODE)
        data.setdefault("orderBy", {
            "fieldName": "createTime",
            "isAsc": False
        })
        return super().page(ApiEnum.PAGE_URL, pageNum, pageSize, *args, **argss)

    def list(self, *args, **argss):
        return super().list(None, *args, **argss)

    def add(self, item: dict):
        return super().add(ApiEnum.ADD_URL, item)

    def edit(self, item: dict):
        return super().edit(ApiEnum.EDIT_URL, item)

    def delete(self, cameraSn):
        data = {
            "cameraSn": cameraSn
        }
        return super().delete(ApiEnum.DELETE_URL, data, options={"dataAsParams": True})
