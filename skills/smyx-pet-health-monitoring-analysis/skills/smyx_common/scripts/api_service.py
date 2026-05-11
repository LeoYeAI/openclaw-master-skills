#!/usr/bin/env python3

from .config import ApiEnum

from .base import BaseApiService
from .util import RequestUtil, CommonUtil


class ApiService(BaseApiService):

    def __init__(self):
        super().__init__()

    def get_download_url(self, tosKey, expireSeconds=3600):
        return RequestUtil.http_post(
            ApiEnum.GET_DOWNLOAD_URL__URL,
            params={
                "tosKey": tosKey,
                "expireSeconds": expireSeconds * 24
            }
        )

    def page(self, url, pageNum=None, pageSize=None, *args, **argss):
        data = args[0] if len(args) > 0 else argss.get('data') if argss.get('data') is not None else {}
        if pageNum is None:
            pageNum = 1
        if pageSize is None:
            pageSize = ApiEnum.DEFAULT__PAGE_SIZE
        paramsPage = {
            'pageNum': int(pageNum),
            'pageSize': int(pageSize)
        }
        data.update({
            "page": paramsPage
        })
        if not CommonUtil.is_empty(data):
            if (len(args) == 0):
                argss.setdefault("data", data)
        response = RequestUtil.http_post(
            url,
            *args, **argss
        )
        return response

    def list(self, url=None, *args, **argss):
        if url is not None:
            argss["url"] = url
        return self.page(1, ApiEnum.DEFAULT__PAGE_SIZE_MAX, *args, **argss)

    def add(self, url=None, *args, **argss):
        response = RequestUtil.http_post(
            url,
            *args, **argss
        )
        return response

    def edit(self, url=None, *args, **argss):
        response = RequestUtil.http_post(
            url,
            *args, **argss
        )
        return response

    def delete(self, url=None, *args, **argss):
        response = RequestUtil.http_post(
            url,
            *args, **argss
        )
        return response

    def http_post(self, url=None, *args, **argss):
        return RequestUtil.http_post(
            url,
            *args, **argss
        )

    def http_put(self, url=None, *args, **argss):
        return RequestUtil.http_put(
            url,
            *args, **argss
        )

    def http_get(self, url=None, *args, **argss):
        return RequestUtil.http_get(
            url,
            *args, **argss
        )

        return response

    def http_delete(self, url=None, *args, **argss):
        return RequestUtil.http_delete(
            url,
            *args, **argss
        )
        return response
