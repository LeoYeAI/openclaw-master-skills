#!/usr/bin/env python3
import datetime
import os
import sys

from .config import ApiEnum, ConstantEnum

from .api_service import ApiService

from skills.smyx_common.scripts.util import CommonUtil, JsonUtil
from skills.smyx_common.scripts.config import ApiEnum as ApiEnumBase
from skills.smyx_common.scripts.base import BaseSkill
from skills.smyx_common.scripts.api_service import ApiService as ApiServiceBase


class Skill(BaseSkill, ApiService):
    def __init__(self):
        super().__init__()

    def get_output_analysis_content_body(self, result=None):
        result_json = result

        result_json_pure_text = result_json.get("pureText")
        if result_json_pure_text:
            result_json = JsonUtil.parse(result_json_pure_text, result_json_pure_text)

        result_json_common_ai_response = result_json.get("commonAiResponse")
        if result_json_common_ai_response:
            result_json = result_json_common_ai_response

        result_json_health_ai_response = result_json.get("healthAiResponse")
        if result_json_health_ai_response:
            result_json = result_json_health_ai_response

        result_json = JsonUtil.stringify(result_json, result_json)
        return result_json

    def get_output_analysis_content_head(self, result=None):
        return f"📊 面诊分析结构化结果"

    def get_output_analysis_content_foot(self, result):
        result_id = result.get('id', {})
        output_content_export_url = ApiEnum.DETAIL_EXPORT_URL + result_id
        return f"🔗 获取报告导出图片链接: {output_content_export_url}"

    def get_output_analysis_content(self, result):
        if result is not None:
            output_content = self.get_output_analysis_content_body(result) or ""
            output_content_head = self.get_output_analysis_content_head(result)
            output_content_foot = self.get_output_analysis_content_foot(result)
            #       d
            if output_content_head:
                output_content = f"""
{output_content_head}
""" + output_content
            if output_content_foot:
                output_content += f"""
{output_content_foot}
"""
        else:
            output_content = "⚠️ 暂无分析结果"
        return output_content

    def get_output_analysis(self, input_path, params={}):
        response = self.get_analysis(
            input_path, params
        )

        def _analysis_result():
            return self.analysis_result(
                data=response
            )

        output_content = response
        if response is dict:
            new_response = CommonUtil.polling(_analysis_result,
                                              check_condition=lambda res: res.get('needPageRefresh') is False,
                                              interval=5,
                                              max_attempts=24)
            output_content = self.get_output_analysis_content(new_response)
        return output_content

    def get_analysis(self, input_path, params={}):
        import mimetypes

        def _validate_file(file_path):
            """验证输入文件是否合法"""
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"文件没有读权限: {file_path}")

            ext = os.path.splitext(file_path)[1].lower()[1:]
            if ext not in ConstantEnum.SUPPORTED_FORMATS:
                raise ValueError(f"不支持的文件格式，支持的格式: {', '.join(ConstantEnum.SUPPORTED_FORMATS)}")

            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > ConstantEnum.MAX_FILE_SIZE_MB:
                raise ValueError(
                    f"文件过大，最大支持 {ConstantEnum.MAX_FILE_SIZE_MB}MB，当前文件大小: {file_size_mb:.1f}MB")

            return True

        files = None

        if not input_path:
            raise ValueError("必须提供本地视频路径(--input)或网络视频URL(--url)")

        if (input_path.startswith("http://") or input_path.startswith("https://")):
            params.update({
                "videoUrl": input_path
            })
        else:
            _validate_file(input_path)

            # 自动检测 MIME 类型
            mime_type, _ = mimetypes.guess_type(input_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'

            # 读取文件内容
            with open(input_path, 'rb') as f:
                file_content = f.read()

            # 构建 multipart/form-data 格式的请求
            files = {
                'file': (os.path.basename(input_path), file_content, mime_type)
            }

        response = self.analysis(
            params=params,
            files=files
        )

        return response

    def get_output_analysis_list(self, pageNum=None, pageSize=None, *args, **argss):
        """获取面诊报告清单
        优化规则：只要API服务接口返回面诊报告清单，直接输出API返回的结果，
        无需汇总上下文中的面诊分析报告，以接口返回为准
        """

        def _get_analysis_export_url(request_id=None):
            if not request_id:
                return ""
            return ApiEnum.DETAIL_EXPORT_URL + request_id

        response = self.page(pageNum, pageSize, *args, **argss)

        if response:
            for item in response:
                if item.get("commonAiResponse") or item.get("healthAiResponse"):
                    item["reportImageUrl"] = _get_analysis_export_url(item.get("id"))

        response_text = JsonUtil.stringify(response)

        if response_text:
            return f"""📊 分析报告记录列表(结构化结果)"
{response_text}
"""
        else:
            return "⚠️ 暂无分析报告记录"

    def __get_output_analysis_list(self, pageNum=None, pageSize=None, *args, **argss):
        """获取面诊报告清单
        优化规则：只要API服务接口返回面诊报告清单，直接输出API返回的结果，
        无需汇总上下文中的面诊分析报告，以接口返回为准
        """

        def _get_analysis_export_url(request_id=None):
            if not request_id:
                return ""
            return ApiEnum.DETAIL_EXPORT_URL + request_id

        # open_id 仅用于本地识别，不传给API - 参数已经在argss中，page方法会正确处理
        open_id = argss.pop('open_id', None)
        # if not open_id:
        #     return "⚠️ 错误：缺少 open_id 参数"

        # 获取总页数，然后循环获取所有页
        output_all = ""
        # 先获取第一页来获取总页数
        # page 方法在基类中已经处理过，我们需要兼容两种返回结果：
        # 1. 完整响应：{"success": true, "data": {"records": [...], "total": ...}}
        # 2. 已经提取好的数据：直接返回 data 对象或 records 列表
        response = self.page(pageNum or 1, pageSize or 30, *args, **argss)

        if response is None:
            return "⚠️ 获取报告列表失败：response is None"

        # 兼容处理：不同版本的基类返回不同格式
        if isinstance(response, list):
            # 基类直接返回了 records 列表，无法获取分页信息，直接使用
            records = response
            total = len(records)
            pages = 1
        elif isinstance(response, dict):
            # 完整响应格式
            if not response.get('success'):
                error_msg = response.get('errorMsg', '未知错误')
                return f"⚠️ 获取报告列表失败：{error_msg}"
            data = response.get('data', {})
            if not data or not isinstance(data, dict):
                return "⚠️ 获取报告列表失败：数据格式错误"
            total = data.get('total', 0)
            pages = data.get('pages', 1)
            records = data.get('records', [])
        else:
            return f"⚠️ 获取报告列表失败：response type={type(response)}"

        if not records:
            return "⚠️ 暂无面诊分析报告记录"

        output_all = f"📋 历史面诊分析报告清单（共 {total} 份）\n\n"
        output_all += "| 报告名称 | 分析时间 | 体质判断 | 点击查看 |\n"
        output_all += "|----------|----------|----------|----------|\n"

        # 处理第一页
        for item in records:
            if not isinstance(item, dict):
                continue
            report_id = item.get('id', '')
            create_time = item.get('createTimeString', '未知时间')
            # 提取体质判断 - 优先从 healthAiResponse 获取，如果没有再从 faceAnalysisResponse 获取
            health_ai = item.get('healthAiResponse', {}) or {}
            if health_ai:
                health_assessment = health_ai.get('healthAssessment', {}) or {}
                subject = health_assessment.get('subject', '未知')
            else:
                face_ai = item.get('faceAnalysisResponse', {}) or {}
                health_assessment = face_ai.get('healthAssessment', {}) or {}
                subject = health_assessment.get('subject', '未知')
            report_name = f"面诊分析报告-{report_id}"
            report_url = _get_analysis_export_url(report_id)
            output_all += f"| {report_name} | {create_time} | {subject} | [🔗 查看报告]({report_url}) |\n"

        # 处理剩余页
        for current_page in range(2, pages + 1):
            response = self.page(current_page, 30, *args, **argss)
            if not response or not isinstance(response, dict) or not response.get('success'):
                continue
            data = response.get('data', {})
            if not data or not isinstance(data, dict):
                continue
            records = data.get('records', [])
            for item in records:
                if not isinstance(item, dict):
                    continue
                report_id = item.get('id', '')
                create_time = item.get('createTimeString', '未知时间')
                # 提取体质判断 - 优先从 healthAiResponse 获取，如果没有再从 faceAnalysisResponse 获取
                health_ai = item.get('healthAiResponse', {}) or {}
                if health_ai:
                    health_assessment = health_ai.get('healthAssessment', {}) or {}
                    subject = health_assessment.get('subject', '未知')
                else:
                    face_ai = item.get('faceAnalysisResponse', {}) or {}
                    health_assessment = face_ai.get('healthAssessment', {}) or {}
                    subject = health_assessment.get('subject', '未知')
                report_name = f"面诊分析报告-{report_id}"
                report_url = _get_analysis_export_url(report_id)
                output_all += f"| {report_name} | {create_time} | {subject} | [🔗 查看报告]({report_url}) |\n"

        output_all += "\n> 注：面诊分析结果仅供健康参考，不能替代专业医疗诊断。"
        return output_all


skill = Skill()
