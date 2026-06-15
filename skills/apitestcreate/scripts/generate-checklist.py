#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试分析文档生成器
根据接口规格自动生成详细的API测试分析文档
"""

import json
import yaml
import re
import sys
import argparse
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APITestAnalyzer:
    """API测试分析文档生成器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化分析器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.priority_rules = self.config.get('priority_rules', {})

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        default_config = {
            "priority_rules": {
                "required_missing": "P0",
                "sql_injection": "P0",
                "xss": "P0",
                "authorization": "P0",
                "boundary_normal": "P1",
                "boundary_invalid": "P1",
                "optional": "P2"
            }
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"加载配置文件: {config_path}")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}，使用默认配置")

        return default_config

    def analyze_from_openapi(self, openapi_spec: Union[str, Dict[str, Any]],
                             api_name: Optional[str] = None) -> str:
        """
        从OpenAPI规范生成测试分析文档

        Args:
            openapi_spec: OpenAPI规范（字符串或字典）
            api_name: API名称

        Returns:
            Markdown格式的测试分析文档
        """
        try:
            if isinstance(openapi_spec, str):
                spec = self._parse_spec(openapi_spec)
            else:
                spec = openapi_spec

            return self._generate_analysis_markdown(spec, api_name)

        except Exception as e:
            logger.error(f"生成测试分析文档失败: {e}", exc_info=True)
            raise

    def analyze_from_simple(self, simple_def: str) -> str:
        """
        从简化定义生成测试分析文档

        Args:
            simple_def: 简化接口定义

        Returns:
            Markdown格式的测试分析文档
        """
        try:
            parsed = self._parse_simple_definition(simple_def)
            spec = self._convert_to_openapi(parsed)
            return self._generate_analysis_markdown(spec, parsed.get('name'))

        except Exception as e:
            logger.error(f"解析简化定义失败: {e}", exc_info=True)
            raise

    def _parse_spec(self, spec_str: str) -> Dict[str, Any]:
        """解析规范字符串"""
        spec_str = spec_str.strip()
        try:
            if spec_str.startswith('{'):
                return json.loads(spec_str)
            else:
                return yaml.safe_load(spec_str)
        except Exception as e:
            logger.error(f"规范解析失败: {e}")
            raise ValueError(f"无法解析规范: {e}")

    def _parse_simple_definition(self, simple_def: str) -> Dict[str, Any]:
        """解析简化定义"""
        parsed = {
            "name": "",
            "path": "",
            "method": "POST",
            "parameters": [],
            "responses": {},
            "rules": []
        }

        lines = simple_def.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('接口名称:') or line.startswith('API:'):
                parsed["name"] = line.split(':', 1)[1].strip()
            elif line.startswith('接口路径:') or line.startswith('端点:'):
                path_info = line.split(':', 1)[1].strip()
                match = re.match(r'(GET|POST|PUT|DELETE|PATCH)\s+(.+)', path_info, re.IGNORECASE)
                if match:
                    parsed["method"] = match.group(1).upper()
                    parsed["path"] = match.group(2)
                else:
                    parsed["path"] = path_info
            elif line.startswith('-') and ':' in line:
                param_info = self._parse_parameter_line(line)
                if param_info:
                    parsed["parameters"].append(param_info)
            elif line.startswith('-') and '不能' in line:
                parsed["rules"].append(line.strip('- ').strip())

        return parsed

    def _parse_parameter_line(self, line: str) -> Optional[Dict[str, Any]]:
        """解析参数字符串"""
        try:
            line = line.strip('- ').strip()
            if ':' not in line:
                return None

            name_part, def_part = line.split(':', 1)
            name = name_part.strip()
            definition = def_part.strip()

            param = {
                "name": name,
                "type": "string",
                "required": False,
                "description": definition
            }

            type_match = re.search(r'(string|integer|number|boolean|array|object)', definition, re.IGNORECASE)
            if type_match:
                param["type"] = type_match.group(1).lower()

            if '必填' in definition or 'required' in definition:
                param["required"] = True

            length_match = re.search(r'(\d+)\s*-\s*(\d+)\s*字符', definition)
            if length_match:
                param["minLength"] = int(length_match.group(1))
                param["maxLength"] = int(length_match.group(2))

            enum_match = re.search(r'\[([^\]]+)\]', definition)
            if enum_match:
                enum_values = enum_match.group(1).split(',')
                param["enum"] = [v.strip() for v in enum_values]

            return param

        except Exception as e:
            logger.warning(f"解析参数失败 '{line}': {e}")
            return None

    def _convert_to_openapi(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """转换为OpenAPI格式"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": parsed.get("name", "API"),
                "version": "1.0.0"
            },
            "paths": {
                parsed.get("path", "/"): {
                    parsed.get("method", "POST").lower(): {
                        "summary": parsed.get("name", ""),
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": [],
                                        "properties": {}
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "成功"
                            }
                        }
                    }
                }
            }
        }

        properties = spec["paths"][parsed["path"]][parsed["method"].lower()]["requestBody"]["content"]["application/json"]["schema"]["properties"]
        required = spec["paths"][parsed["path"]][parsed["method"].lower()]["requestBody"]["content"]["application/json"]["schema"]["required"]

        for param in parsed.get("parameters", []):
            properties[param["name"]] = {}
            if param["type"] == "string":
                properties[param["name"]]["type"] = "string"
                if "minLength" in param:
                    properties[param["name"]]["minLength"] = param["minLength"]
                if "maxLength" in param:
                    properties[param["name"]]["maxLength"] = param["maxLength"]
            elif param["type"] == "integer":
                properties[param["name"]]["type"] = "integer"

            if param.get("required"):
                required.append(param["name"])

        return spec

    def _generate_analysis_markdown(self, spec: Dict[str, Any], api_name: Optional[str] = None) -> str:
        """生成详细的测试分析文档"""
        lines = []

        # 文档标题
        api_title = api_name or spec.get("info", {}).get("title", "API接口")
        lines.append(f"# {api_title} - API测试分析文档")
        lines.append("")
        lines.append(f"**生成日期**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**文档版本**：v1.0")
        lines.append("")

        # 接口清单
        paths = spec.get("paths", {})
        if len(paths) > 1:
            lines.append("## 接口清单")
            lines.append("")
            lines.append("| 序号 | 接口名称 | 路径 | 方法 | 测试点数 |")
            lines.append("|------|----------|------|------|----------|")

            for idx, (path, path_item) in enumerate(paths.items(), 1):
                for method, operation in path_item.items():
                    summary = operation.get("summary", "未命名接口")
                    lines.append(f"| {idx} | {summary} | {path} | {method.upper()} | 待计算 |")
            lines.append("")

        # 详细接口分析
        lines.append("## 详细测试分析")
        lines.append("")

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                self._analyze_single_endpoint(lines, path, method, operation, spec)

        return "\n".join(lines)

    def _analyze_single_endpoint(self, lines: List[str], path: str, method: str, operation: Dict[str, Any], spec: Dict[str, Any]):
        """分析单个接口"""
        summary = operation.get("summary", "未命名接口")
        description = operation.get("description", "")

        lines.append(f"### {summary}")
        lines.append("")
        lines.append("#### 基本信息")
        lines.append(f"- **接口路径**：{method.upper()} {path}")
        if description:
            lines.append(f"- **接口描述**：{description}")
        lines.append("")

        # 请求参数分析
        self._analyze_request_params(lines, operation, spec)

        # 业务逻辑分析
        self._analyze_business_logic(lines, operation)

        # 响应验证分析
        self._analyze_response(lines, operation)

        # 安全测试分析
        self._analyze_security(lines)

        # 性能测试分析
        self._analyze_performance(lines)

        lines.append("---")
        lines.append("")

    def _analyze_request_params(self, lines: List[str], operation: Dict[str, Any], spec: Dict[str, Any]):
        """分析请求参数"""
        request_body = operation.get("requestBody", {})
        content = request_body.get("content", {})

        if not content:
            return

        lines.append("#### 请求参数分析")
        lines.append("")

        for content_type, schema_def in content.items():
            if content_type != "application/json":
                continue

            schema = schema_def.get("schema", {})
            properties = schema.get("properties", {})
            required_fields = schema.get("required", [])

            if not properties:
                continue

            for param_name, param_spec in properties.items():
                self._analyze_parameter(lines, param_name, param_spec, param_name in required_fields)

    def _analyze_parameter(self, lines: List[str], param_name: str, param_spec: Dict[str, Any], required: bool):
        """分析单个参数"""
        param_type = param_spec.get("type", "string")
        description = param_spec.get("description", "")

        lines.append(f"##### {param_name} ({param_type}, {'必填' if required else '可选'})")
        if description:
            lines.append(f"**参数描述**：{description}")
        lines.append("")

        # 参数约束
        constraints = []
        if "minLength" in param_spec:
            constraints.append(f"最小长度：{param_spec['minLength']}")
        if "maxLength" in param_spec:
            constraints.append(f"最大长度：{param_spec['maxLength']}")
        if "minimum" in param_spec:
            constraints.append(f"最小值：{param_spec['minimum']}")
        if "maximum" in param_spec:
            constraints.append(f"最大值：{param_spec['maximum']}")
        if "enum" in param_spec:
            constraints.append(f"枚举值：{param_spec['enum']}")
        if "pattern" in param_spec:
            constraints.append(f"正则表达式：{param_spec['pattern']}")

        if constraints:
            lines.append("**约束条件**：")
            for constraint in constraints:
                lines.append(f"- {constraint}")
            lines.append("")

        # 参数校验测试点
        lines.append("**参数校验测试点分析**：")
        lines.append("")
        lines.append("| 测试场景 | 测试值说明 | 预期结果 | 优先级 | 测试目的 |")
        lines.append("|----------|------------|----------|--------|----------|")

        test_points = self._get_param_test_points(param_name, param_spec, required)
        for point in test_points:
            lines.append(f"| {point['scenario']} | {point['test_value']} | {point['expected']} | {point['priority']} | {point['purpose']} |")

        lines.append("")

        # 风险分析
        risk_level = self._assess_param_risk(param_spec, required)
        lines.append(f"**风险分析**：{risk_level}")
        lines.append("")

    def _get_param_test_points(self, param_name: str, param_spec: Dict[str, Any], required: bool) -> List[Dict[str, Any]]:
        """获取参数测试点"""
        param_type = param_spec.get("type", "string")
        test_points = []

        if param_type == "string":
            test_points = self._get_string_test_points(param_spec, required)
        elif param_type == "integer":
            test_points = self._get_integer_test_points(param_spec, required)
        elif param_type == "number":
            test_points = self._get_number_test_points(param_spec, required)
        elif param_type == "boolean":
            test_points = self._get_boolean_test_points(param_spec, required)
        elif param_type == "array":
            test_points = self._get_array_test_points(param_spec, required)
        else:
            test_points = self._get_default_test_points(param_spec, required)

        return test_points

    def _get_string_test_points(self, param_spec: Dict[str, Any], required: bool) -> List[Dict[str, Any]]:
        """获取字符串类型测试点"""
        min_len = param_spec.get("minLength", 0)
        max_len = param_spec.get("maxLength", 100)
        enum_values = param_spec.get("enum", [])

        points = []

        if enum_values:
            # 枚举类型
            points.extend([
                {"scenario": "正常值-枚举值", "test_value": f"{enum_values[0]}", "expected": "成功", "priority": "P0", "purpose": "验证有效枚举值"},
                {"scenario": "异常值-非枚举值", "test_value": f"非枚举值", "expected": "参数错误", "priority": "P0", "purpose": "验证枚举约束"},
            ])
        else:
            # 普通字符串
            if min_len > 0:
                points.append({"scenario": "正常值-最小长度", "test_value": f"{'a' * min_len}", "expected": "成功", "priority": "P1", "purpose": "验证下边界"})
                points.append({"scenario": "正常值-典型值", "test_value": f"{'a' * min(min_len + 5, max_len)}", "expected": "成功", "priority": "P0", "purpose": "验证典型场景"})
            if max_len < 1000:
                points.append({"scenario": "正常值-最大长度", "test_value": f"{'a' * max_len}", "expected": "成功", "priority": "P1", "purpose": "验证上边界"})
                points.append({"scenario": "异常值-超过最大长度", "test_value": f"{'a' * (max_len + 1)}", "expected": "参数错误", "priority": "P1", "purpose": "验证越界处理"})

        if required:
            points.extend([
                {"scenario": "异常值-null", "test_value": "null", "expected": "参数错误", "priority": "P0", "purpose": "验证必填约束"},
                {"scenario": "异常值-空字符串", "test_value": '""', "expected": "参数错误", "priority": "P0", "purpose": "验证空值处理"},
            ])
        else:
            points.append({"scenario": "正常值-null（可选）", "test_value": "null", "expected": "成功", "priority": "P2", "purpose": "验证可选参数"})

        # 安全测试点
        points.extend([
            {"scenario": "安全-SQL注入", "test_value": "' OR '1'='1", "expected": "参数错误", "priority": "P0", "purpose": "验证SQL注入防护"},
            {"scenario": "安全-XSS攻击", "test_value": "<script>alert(1)</script>", "expected": "参数错误", "priority": "P0", "purpose": "验证XSS防护"},
            {"scenario": "安全-路径遍历", "test_value": "../../../etc/passwd", "expected": "参数错误", "priority": "P0", "purpose": "验证路径遍历防护"},
            {"scenario": "特殊字符", "test_value": "!@#$%^&*()", "expected": "成功或参数错误", "priority": "P1", "purpose": "验证特殊字符处理"},
        ])

        return points

    def _get_integer_test_points(self, param_spec: Dict[str, Any], required: bool) -> List[Dict[str, Any]]:
        """获取整数类型测试点"""
        min_val = param_spec.get("minimum", 0)
        max_val = param_spec.get("maximum", 100)

        points = [
            {"scenario": "正常值-最小值", "test_value": str(min_val), "expected": "成功", "priority": "P1", "purpose": "验证下边界"},
            {"scenario": "正常值-中间值", "test_value": str((min_val + max_val) // 2), "expected": "成功", "priority": "P0", "purpose": "验证典型场景"},
            {"scenario": "正常值-最大值", "test_value": str(max_val), "expected": "成功", "priority": "P1", "purpose": "验证上边界"},
            {"scenario": "异常值-小于最小值", "test_value": str(min_val - 1), "expected": "参数错误", "priority": "P1", "purpose": "验证越下界"},
            {"scenario": "异常值-大于最大值", "test_value": str(max_val + 1), "expected": "参数错误", "priority": "P1", "purpose": "验证越上界"},
            {"scenario": "异常值-小数", "test_value": "3.14", "expected": "参数错误", "priority": "P1", "purpose": "验证类型检查"},
            {"scenario": "异常值-字符串", "test_value": '"abc"', "expected": "参数错误", "priority": "P1", "purpose": "验证类型检查"},
        ]

        if required:
            points.append({"scenario": "异常值-null", "test_value": "null", "expected": "参数错误", "priority": "P0", "purpose": "验证必填约束"})
        else:
            points.append({"scenario": "正常值-null（可选）", "test_value": "null", "expected": "成功", "priority": "P2", "purpose": "验证可选参数"})

        return points

    def _get_number_test_points(self, param_spec: Dict[str, Any], required: bool) -> List[Dict[str, Any]]:
        """获取数字类型测试点"""
        return self._get_integer_test_points(param_spec, required)

    def _get_boolean_test_points(self, param_spec: Dict[str, Any], required: bool) -> List[Dict[str, Any]]:
        """获取布尔类型测试点"""
        points = [
            {"scenario": "正常值-true", "test_value": "true", "expected": "成功", "priority": "P0", "purpose": "验证true值"},
            {"scenario": "正常值-false", "test_value": "false", "expected": "成功", "priority": "P0", "purpose": "验证false值"},
            {"scenario": "异常值-字符串", "test_value": '"yes"', "expected": "参数错误", "priority": "P1", "purpose": "验证类型检查"},
            {"scenario": "异常值-整数", "test_value": "1", "expected": "参数错误", "priority": "P1", "purpose": "验证类型检查"},
        ]

        if required:
            points.append({"scenario": "异常值-null", "test_value": "null", "expected": "参数错误", "priority": "P0", "purpose": "验证必填约束"})

        return points

    def _get_array_test_points(self, param_spec: Dict[str, Any], required: bool) -> List[Dict[str, Any]]:
        """获取数组类型测试点"""
        points = [
            {"scenario": "正常值-空数组", "test_value": "[]", "expected": "成功", "priority": "P2", "purpose": "验证空数组"},
            {"scenario": "正常值-单元素", "test_value": "[1]", "expected": "成功", "priority": "P0", "purpose": "验证单元素"},
            {"scenario": "正常值-多元素", "test_value": "[1, 2, 3]", "expected": "成功", "priority": "P0", "purpose": "验证多元素"},
            {"scenario": "异常值-非数组", "test_value": "1", "expected": "参数错误", "priority": "P1", "purpose": "验证类型检查"},
            {"scenario": "异常值-字符串", "test_value": '"abc"', "expected": "参数错误", "priority": "P1", "purpose": "验证类型检查"},
        ]

        if required:
            points.append({"scenario": "异常值-null", "test_value": "null", "expected": "参数错误", "priority": "P0", "purpose": "验证必填约束"})

        return points

    def _get_default_test_points(self, param_spec: Dict[str, Any], required: bool) -> List[Dict[str, Any]]:
        """获取默认测试点"""
        return [
            {"scenario": "正常值", "test_value": "有效值", "expected": "成功", "priority": "P0", "purpose": "验证基本功能"},
            {"scenario": "异常值-null", "test_value": "null", "expected": "参数错误", "priority": "P0" if required else "P2", "purpose": "验证null处理"},
        ]

    def _assess_param_risk(self, param_spec: Dict[str, Any], required: bool) -> str:
        """评估参数风险等级"""
        risk_factors = []

        if required:
            risk_factors.append("必填参数")

        if param_spec.get("type") == "string":
            if not param_spec.get("pattern") and not param_spec.get("enum"):
                risk_factors.append("无格式验证")
            if param_spec.get("maxLength", 0) > 1000:
                risk_factors.append("长度过大")

        if len(risk_factors) == 0:
            return "🟢 低风险"
        elif len(risk_factors) <= 2:
            return "🟡 中风险"
        else:
            return "🔴 高风险"

    def _analyze_business_logic(self, lines: List[str], operation: Dict[str, Any]):
        """分析业务逻辑"""
        description = operation.get("description", "")
        summary = operation.get("summary", "")
        text = f"{summary} {description}"

        lines.append("#### 业务逻辑测试点分析")
        lines.append("")

        scenarios = []

        # 唯一性规则
        if "唯一" in text or "unique" in text.lower():
            scenarios.extend([
                {"name": "唯一性校验-首次创建", "precondition": "数据不存在", "action": "创建数据", "expected": "成功", "priority": "P0", "purpose": "验证唯一性约束"},
                {"name": "唯一性校验-重复创建", "precondition": "数据已存在", "action": "创建相同数据", "expected": "业务错误（已存在）", "priority": "P0", "purpose": "验证重复检测"},
            ])

        # 状态转换规则
        if "状态" in text or "status" in text.lower():
            scenarios.extend([
                {"name": "状态转换-合法转换", "precondition": "源状态合法", "action": "执行状态转换", "expected": "转换成功", "priority": "P0", "purpose": "验证合法状态流转"},
                {"name": "状态转换-非法转换", "precondition": "源状态不合法", "action": "执行状态转换", "expected": "业务错误", "priority": "P1", "purpose": "验证非法状态拦截"},
            ])

        # 权限规则
        if "权限" in text or "permission" in text.lower():
            scenarios.extend([
                {"name": "权限校验-有权限", "precondition": "已登录且有权限", "action": "访问接口", "expected": "成功", "priority": "P0", "purpose": "验证权限控制"},
                {"name": "权限校验-无权限", "precondition": "已登录但无权限", "action": "访问接口", "expected": "权限错误", "priority": "P0", "purpose": "验证权限拦截"},
                {"name": "权限校验-未登录", "precondition": "未登录", "action": "访问接口", "expected": "认证错误", "priority": "P0", "purpose": "验证认证控制"},
            ])

        # 默认场景
        if not scenarios:
            scenarios.extend([
                {"name": "正常业务流程", "precondition": "数据准备完成", "action": "执行业务操作", "expected": "业务成功", "priority": "P0", "purpose": "验证核心功能"},
                {"name": "业务规则违反", "precondition": "不满足业务条件", "action": "执行业务操作", "expected": "业务错误", "priority": "P1", "purpose": "验证规则校验"},
            ])

        lines.append("| 测试场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 测试目的 |")
        lines.append("|----------|----------|----------|----------|--------|----------|")

        for scenario in scenarios:
            lines.append(f"| {scenario['name']} | {scenario['precondition']} | {scenario['action']} | {scenario['expected']} | {scenario['priority']} | {scenario['purpose']} |")

        lines.append("")

    def _analyze_response(self, lines: List[str], operation: Dict[str, Any]):
        """分析响应验证"""
        lines.append("#### 响应验证测试点分析")
        lines.append("")

        # 成功响应
        lines.append("**成功响应（2xx）验证**：")
        lines.append("")
        lines.append("| 验证项 | 验证内容 | 优先级 | 验证方法 |")
        lines.append("|--------|----------|--------|----------|")
        lines.append("| 响应结构 | 包含code, message, data字段 | P0 | 检查JSON结构 |")
        lines.append("| 状态码 | 与业务结果匹配（200/201） | P0 | 检查HTTP状态码 |")
        lines.append("| 响应时间 | 符合性能要求 | P1 | 记录响应时间 |")
        lines.append("| 数据完整性 | 返回完整业务数据 | P0 | 检查data字段 |")
        lines.append("| 字段类型 | 每个字段匹配规格 | P1 | 验证字段类型 |")
        lines.append("")

        # 错误响应
        lines.append("**错误响应（4xx/5xx）验证**：")
        lines.append("")
        lines.append("| 错误场景 | 状态码 | 响应体验证 | 优先级 |")
        lines.append("|----------|--------|------------|--------|")
        lines.append("| 参数缺失 | 400 | code=400, message包含'必填' | P0 |")
        lines.append("| 参数格式错误 | 400 | code=400, message包含'格式' | P0 |")
        lines.append("| 参数类型错误 | 400 | code=400, message包含'类型' | P0 |")
        lines.append("| 业务规则违反 | 409 | code=409, message包含'已存在' | P0 |")
        lines.append("| 未认证 | 401 | code=401, message包含'认证' | P0 |")
        lines.append("| 无权限 | 403 | code=403, message包含'权限' | P0 |")
        lines.append("| 资源不存在 | 404 | code=404, message包含'不存在' | P0 |")
        lines.append("| 服务器异常 | 500 | code=500, message不包含敏感信息 | P0 |")
        lines.append("")

    def _analyze_security(self, lines: List[str]):
        """分析安全测试"""
        lines.append("#### 安全测试点分析")
        lines.append("")

        # 认证安全
        lines.append("**认证安全**：")
        lines.append("")
        lines.append("| 测试场景 | 测试操作 | 预期结果 | 风险等级 | 测试目的 |")
        lines.append("|----------|----------|----------|----------|----------|")
        lines.append("| 未认证访问 | 不携带Token调用接口 | 返回401 Unauthorized | 🔴 高 | 验证认证拦截 |")
        lines.append("| Token过期 | 使用过期Token | 返回401, message提示Token过期 | 🔴 高 | 验证Token过期处理 |")
        lines.append("| Token篡改 | 修改Token签名 | 返回401, message提示Token无效 | 🔴 高 | 验证Token完整性 |")
        lines.append("| Token刷新 | 使用RefreshToken获取新Token | 返回新Token, 旧Token失效 | 🟡 中 | 验证Token刷新机制 |")
        lines.append("")

        # 授权安全
        lines.append("**授权安全**：")
        lines.append("")
        lines.append("| 测试场景 | 测试操作 | 预期结果 | 风险等级 | 测试目的 |")
        lines.append("|----------|----------|----------|----------|----------|")
        lines.append("| 越权访问 | 用户A访问用户B的数据 | 返回403 Forbidden | 🔴 高 | 验证水平越权防护 |")
        lines.append("| 垂直越权 | 普通用户访问管理员接口 | 返回403 Forbidden | 🔴 高 | 验证垂直越权防护 |")
        lines.append("| 权限变更 | 权限变更后访问接口 | 按新权限控制 | 🟡 中 | 验证权限变更生效 |")
        lines.append("")

        # 数据安全
        lines.append("**数据安全**：")
        lines.append("")
        lines.append("| 测试场景 | 测试操作 | 预期结果 | 风险等级 | 测试目的 |")
        lines.append("|----------|----------|----------|----------|----------|")
        lines.append("| SQL注入 | 输入SQL特殊字符 | 返回400, 不被注入 | 🔴 高 | 验证SQL注入防护 |")
        lines.append("| XSS攻击 | 输入<script>标签 | 返回400, 内容被转义 | 🔴 高 | 验证XSS防护 |")
        lines.append("| 敏感数据泄露 | 检查响应字段 | 密码、密钥不返回 | 🔴 高 | 验证数据脱敏 |")
        lines.append("| 日志脱敏 | 检查日志文件 | 敏感信息被脱敏 | 🟡 中 | 验证日志安全 |")
        lines.append("")

    def _analyze_performance(self, lines: List[str]):
        """分析性能测试"""
        lines.append("#### 性能测试点分析")
        lines.append("")

        lines.append("**响应时间要求**：")
        lines.append("")
        lines.append("- **P0优先级接口**：< 200ms (95分位)")
        lines.append("- **P1优先级接口**：< 500ms (95分位)")
        lines.append("- **P2优先级接口**：< 1000ms (95分位)")
        lines.append("- **P3优先级接口**：< 2000ms (95分位)")
        lines.append("")

        lines.append("**压力测试场景**：")
        lines.append("")
        lines.append("| 场景 | 并发数 | 持续时间 | 预期结果 | 关注点 |")
        lines.append("|------|--------|----------|----------|--------|")
        lines.append("| 基准测试 | 1 | 10分钟 | 响应稳定 | 基准响应时间 |")
        lines.append("| 负载测试 | 10 | 30分钟 | 成功率>99.9% | 系统负载 |")
        lines.append("| 压力测试 | 50 | 15分钟 | 成功率>99% | 系统瓶颈 |")
        lines.append("| 峰值测试 | 100 | 5分钟 | 不崩溃 | 最大承载能力 |")
        lines.append("")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='API测试分析文档生成器')
    parser.add_argument('--input', '-i', required=True, help='输入文件（OpenAPI/Swagger/简化定义）')
    parser.add_argument('--output', '-o', help='输出Markdown文件（默认：stdout）')
    parser.add_argument('--format', '-f', choices=['openapi', 'simple'], default='openapi',
                        help='输入格式（默认：openapi）')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--api-name', '-n', help='API名称')

    args = parser.parse_args()

    try:
        analyzer = APITestAnalyzer(args.config)

        if Path(args.input).exists():
            with open(args.input, 'r', encoding='utf-8') as f:
                input_content = f.read()
        else:
            input_content = args.input

        if args.format == 'openapi':
            analysis = analyzer.analyze_from_openapi(input_content, args.api_name)
        else:
            analysis = analyzer.analyze_from_simple(input_content)

        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(analysis)
            logger.info(f"测试分析文档已保存到: {args.output}")
        else:
            print(analysis)

    except Exception as e:
        logger.error(f"生成失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
