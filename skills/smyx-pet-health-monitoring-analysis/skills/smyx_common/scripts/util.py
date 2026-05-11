#!/usr/bin/env python3
import json
import os
import traceback

import requests
from .config import ApiEnum, ConstantEnum, sys, YamlUtil

from .base import BaseUtil
import time
import logging
from typing import Any, Callable, Optional, TypeVar, Dict
import pydash as _

if ConstantEnum.is_debug():
    import http.client

    # 【关键代码】开启调试模式
    http.client.HTTPConnection.debuglevel = 1
    # 可选：如果你希望日志更整洁，可以配合 logging 模块（否则打印会比较乱）
    import logging

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class StringUtil(BaseUtil):

    @staticmethod
    def camel_to_snake(name):
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def snake_to_pascal(name):
        import re
        name = re.sub(r'^([a-z])', lambda m: m.group(1).upper(), name)
        return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), name)

    @staticmethod
    def snake_to_camel(name):
        import re
        # 逻辑：匹配 '_[a-z]' (下划线+小写字母)，将其替换为对应的大写字母（去掉下划线）
        return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), name)


class FileUtil(BaseUtil):

    @staticmethod
    def get_fullname(path):
        try:
            return os.path.basename(path)
        except Exception as e:
            CommonUtil.trace_exception_stack(e)
            return ""

    @staticmethod
    def get_name(path):
        try:
            return os.path.splitext(os.path.basename(path))[0]
        except Exception as e:
            CommonUtil.trace_exception_stack(e)

    @staticmethod
    def get_ext(path):
        try:
            return os.path.splitext(os.path.basename(path))[1]
        except Exception as e:
            CommonUtil.trace_exception_stack(e)

    @staticmethod
    def open(path):
        try:
            return open(path, 'w', encoding='utf-8')
        except Exception as e:
            CommonUtil.trace_exception_stack(e)

    @staticmethod
    def mkdir(path):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            CommonUtil.trace_exception_stack(e)


class JsonUtil(BaseUtil):

    @staticmethod
    def stringify(json_obj, default_str=""):
        try:
            return json.dumps(json_obj, ensure_ascii=False, indent=2)
        except Exception as e:
            CommonUtil.trace_exception_stack(e)
            pass
        return default_str

    @staticmethod
    def parse(json_str, default_json={}):
        try:
            return json.loads(json_str)
        except Exception as e:
            CommonUtil.trace_exception_stack(e)
            pass
        return default_json


class CommonUtil(BaseUtil):

    @staticmethod
    def trace_exception_stack(e):
        if ConstantEnum.is_debug():
            print(f"❌ 错误描述: {str(e)}, 堆栈跟踪:")
            traceback.print_stack()

    @staticmethod
    def polling(
            action: Callable[[], Any],
            check_condition: Callable[[Any], bool],
            on_success: Optional[Callable[[Any], None]] = None,
            on_retry: Optional[Callable[[Any, int], None]] = None,
            on_error: Optional[Callable[[Exception], None]] = None,
            interval: float = 1.0,
            max_attempts: int = 5,
            description: str = "轮询任务"
    ) -> Optional[Any]:
        """
        通用的轮询处理函数

        :param action:
            [必填] 执行动作的回调函数。
            例如：发送 HTTP 请求、查询数据库状态等。
            必须返回一个结果对象供 check_condition 使用。

        :param check_condition:
            [必填] 检查是否结束的回调函数。
            接收 action 的返回值，返回 True 表示“满足结束条件”，False 表示“继续轮询”。
            例如：lambda res: res.get('need_refresh') is False

        :param on_success:
            [可选] 当 check_condition 返回 True 时执行的回调（通常用于记录日志或处理最终数据）。

        :param on_retry:
            [可选] 当需要继续轮询时执行的回调。
            参数：(当前结果, 当前尝试次数)。可用于打印进度。

        :param on_error:
            [可选] 当 action 抛出异常时执行的回调。
            参数：(异常对象)。

        :param interval:
            每次轮询之间的等待时间（秒）。

        :param max_attempts:
            最大尝试次数，防止死循环。

        :param description:
            任务描述，用于日志输出。

        :return:
            如果成功，返回 action 的最后一次返回值；如果超时或失败，返回 None。
        """

        attempts = 0

        print(f"🚀 开始执行 [{description}]...")

        while attempts < max_attempts:
            attempts += 1

            try:
                # 1. 执行动作
                result = action()
                last_result = result

                # 2. 检查条件
                if check_condition(result):
                    print(f"✅ [{description}] 成功！条件已满足 (尝试次数: {attempts}, 耗时{interval * attempts}秒)")
                    if on_success:
                        on_success(result)
                    return result

                # 3. 条件未满足，准备重试
                if on_retry:
                    on_retry(result, attempts)
                else:
                    # 默认日志行为
                    print(
                        f"⏳ [{description}] 条件未满足，{interval}秒后重试... ({attempts}/{max_attempts}, 耗时{interval * attempts}秒)")

                time.sleep(interval)

            except Exception as e:
                # 4. 异常处理
                if on_error:
                    on_error(e)
                else:
                    # 默认错误行为：打印错误并继续
                    logging.error(f"❌ [{description}] 发生异常: {e}")
                    print(f"⚠️ [{description}] 遇到错误，{interval}秒后重试...")

                time.sleep(interval)

        # 5. 超时处理
        print(f"⚠️ [{description}] 失败：达到最大尝试次数 ({max_attempts})，强制停止。")
        return None

    @staticmethod
    def is_empty(data):
        # 1. 如果是 None (对应 JSON 的 null)
        if data is None:
            return True

        # 2. 如果是字典或列表，且长度为 0 (对应 {} 或 [])
        if isinstance(data, (dict, list)) and len(data) == 0:
            return True


from datetime import date, datetime


class DatetimeUtil(BaseUtil):
    FORMAT__DATETIME = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def now_str():
        return DatetimeUtil.format(DatetimeUtil.now())

    @staticmethod
    def today_str():
        return DatetimeUtil.format_date(DatetimeUtil.today())

    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def today():
        return DatetimeUtil.now().replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def format(date):
        return date.strftime('%Y-%m-%d %H:%M:%S') if type(date) == datetime else date

    @staticmethod
    def format_date(date):
        return date.strftime('%Y-%m-%d') if type(date) == datetime else date

    @staticmethod
    def parse(date_str):
        if type(date_str) == int:
            return datetime.fromtimestamp(date_str)
        return datetime.strptime(date_str, DatetimeUtil.FORMAT__DATETIME) if type(date_str) == str else date_str

    @staticmethod
    def timestamp(date=now()):
        return int(date.timestamp() * 1000)


class RequestUtil(BaseUtil):
    BASE_URL = ApiEnum.BASE_URL_OPEN_API
    AUTHORIZATION_RETRY_COUNT_MAX = 3
    authorization_retry_count = 0

    @classmethod
    def http_post(cls, url, data=None, params=None, headers=None, *args, **argss):
        return cls.http_request("post", url, data=data, params=params, headers=headers, *args, **argss)

    @classmethod
    def http_put(cls, url, data=None, params=None, headers=None, *args, **argss):
        return cls.http_request("put", url, data=data, params=params, headers=headers, *args, **argss)

    @classmethod
    def http_delete(cls, url, data=None, params=None, headers=None, *args, **argss):
        return cls.http_request("delete", url, data=data, params=params, headers=headers, *args, **argss)

    @classmethod
    def http_get(cls, url, params=None, headers=None, *args, **argss):
        return cls.http_request("get", url, params=params, headers=headers, *args, **argss)

    @classmethod
    def http_request(cls, method, url, data=None, params=None, headers=None, options=None, *args,
                     timeout=ApiEnum.DEFAULT__REQUEST_TIMEOUT, **argss):
        def _get_or_create_user(username):
            _url = ApiEnum.BASE_URL_HEALTH + "/sys/phoneLogin"
            open_id = username
            _data = {
                "silent": 1,
                "register": 1,
                "openId": open_id,
                "mobile": username
            }
            try:
                _response = requests.post(_url, json=_data)
                if _response.status_code == 200:
                    _response_json = _response.json()
                    if _response_json and _response_json.get("success"):
                        return _response_json and _response_json.get("result")
            except Exception as _e:
                CommonUtil.trace_exception_stack(_e)
            return {}

        try:
            headers = headers or {}
            if not url.startswith("https://") and not url.startswith("http://"):
                url = cls.BASE_URL + url
            headers['App-Id'] = ConstantEnum.APP__ID
            # ConstantEnum.CURRENT__USER_NAME = ConstantEnum.CURRENT__OPEN_ID = "ou_86fdd8e0d5f116c18a9dd550abefe6d2"
            current__user_name = ApiEnum.API_SECRET_KEY or ConstantEnum.CURRENT__USER_NAME or ConstantEnum.CURRENT__OPEN_ID
            found_user = None
            if (not ApiEnum.TOKEN or not ApiEnum.OPEN_TOKEN) and current__user_name:
                try:
                    from .dao import UserDao, User
                    user_dao = UserDao()
                    found_user = user_dao.get_by_username(current__user_name)
                    if found_user:
                        ApiEnum.TOKEN = found_user.token
                        ApiEnum.OPEN_TOKEN = found_user.open_token
                    if not ApiEnum.TOKEN or not ApiEnum.OPEN_TOKEN:
                        new_current_user = _get_or_create_user(current__user_name)
                        if new_current_user:
                            ApiEnum.TOKEN = new_current_user.get("token")
                            ApiEnum.OPEN_TOKEN = new_current_user.get("openToken")

                            current_user_info = new_current_user.get("userInfo")
                            if current_user_info:
                                current_user_info["token"] = new_current_user.get("token")
                                current_user_info["openToken"] = new_current_user.get(
                                    "openToken")
                                user_model = User.load(current_user_info)

                                user = user_dao.save(
                                    user_model
                                )

                except Exception as e:
                    CommonUtil.trace_exception_stack(e)
                    raise

            headers.setdefault("X-Access-Token", ApiEnum.TOKEN)
            headers.setdefault("X-Api-Key", ApiEnum.API_SECRET_KEY)
            headers.setdefault("Authorization", ApiEnum.OPEN_TOKEN)

            data = data or {}
            params = params or {}
            options = options or {}
            ConstantEnum.CURRENT__TENTANT_CODE and data.setdefault('tenantCode', ConstantEnum.CURRENT__TENTANT_CODE)
            ConstantEnum.DEFAULT__SKILL_HUB_NAME and data.setdefault('skillHubName',
                                                                     ConstantEnum.DEFAULT__SKILL_HUB_NAME)
            ConstantEnum.DEFAULT__SKILL_PLATFORM_NAME and data.setdefault('skillPlatform',
                                                                          ConstantEnum.DEFAULT__SKILL_PLATFORM_NAME)
            if current__user_name:
                data.setdefault('pnaUserName', current__user_name)

            if bool(options.get("dataAsParams")):
                params.update(data)

            print(f"🔄 请求拦截, URL:{url}", "method", method, "params", params, "data", data, "headers", headers,
                  "options", options,
                  "timeout",
                  timeout)
            response = requests.request(method, url, *args, json=data, params=params, headers=headers,
                                        timeout=int(timeout), **argss)
            response_text0 = response.text
            response_text = response_text0 if ConstantEnum.is_debug() else response
            status_code = response.status_code
            if current__user_name == "13800000000":
                status_code = 402
            if status_code == 401 and cls.authorization_retry_count < cls.AUTHORIZATION_RETRY_COUNT_MAX:
                # print(f"❌ 请求拦截, 鉴权失败:{response_text}, url:{url}", "method", method, "params", params,
                #       "data",
                #       data,
                #       "headers",
                #       headers,
                #       "timeout",
                #       timeout)
                ApiEnum.TOKEN = ApiEnum.OPEN_TOKEN = None
                if found_user:
                    found_user.token = found_user.open_token = None
                    user_dao.update(found_user)
                cls.authorization_retry_count += 1
                return cls.http_request(method, url, data, params, headers, options, *args, timeout=timeout, **argss)
            elif status_code == 402:
                print(f"❌ 请求拦截, 使用失败:{response_text}, url:{url}", "method", method, "params", params,
                      "data",
                      data,
                      "headers",
                      headers,
                      "timeout",
                      timeout)
                return f'''⚠️ 因账户余额不足, 技能使用失败, 请按照如下步骤进行充值: 
👉 1. 先输入命令 "安装支付技能 smyx-payment", 等待安装完成. (如果已经安装支付技能过则忽略此步骤)
👉 2. 再输入命令 "技能账户充值", 然后跟随系统提示操作后即可继续使用技能.
{response_text0 or ""}
'''
                # f'请先输入命令 "技能账户充值", 请先确确保安装生命涌现支付技能 请先输入命令 "技能账户充值", 跟随系统提示进行充值后即可继续使用技能(). {response_text0 or ""}')
            elif status_code != 200:
                raise requests.exceptions.RequestException(
                    response, response=response)
            response_json = response.json()
            if not bool(response_json['success']):
                raise requests.exceptions.RequestException(
                    response, response=response)
            response_json_data = response_json.get("data", response_json.get("result"))
            response_json_data = response_json_data.get("records") if response_json_data and type(
                response_json_data) == dict and "records" in response_json_data else response_json_data
            print(f"✅ 请求拦截, 成功:{response_text}, url:{url}", "method", method, "params", params,
                  "data",
                  data,
                  "headers",
                  headers,
                  "timeout",
                  timeout)
            return response_json_data
        except Exception as e:
            CommonUtil.trace_exception_stack(e)
            response_text = _.get(e.args, '0.text')
            print(
                f"❌ 请求拦截, 失败: {e}, e.response.text: {response_text}, url:{url}",
                "method",
                method,
                "params",
                params,
                "data", data, "headers",
                "response", hasattr(e, 'response') and e.response,
                headers,
                "timeout",
                timeout)
            raise
