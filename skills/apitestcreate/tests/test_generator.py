#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试：API测试生成器
"""

import pytest
import sys
import os
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_checklist import APITestGenerator


class TestAPITestGenerator:
    """测试APITestGenerator类"""

    @pytest.fixture
    def generator(self):
        """创建生成器实例"""
        return APITestGenerator()

    def test_init(self, generator):
        """测试初始化"""
        assert generator is not None
        assert isinstance(generator.config, dict)
        assert "priority_rules" in generator.config

    def test_generate_from_openapi_simple(self, generator):
        """测试从简单的OpenAPI生成"""
        openapi_spec = """
        {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "post": {
                        "summary": "Test endpoint",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "minLength": 3,
                                                "maxLength": 20
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        result = generator.generate_from_openapi(openapi_spec, "Test API")
        assert "接口：Test API" in result
        assert "参数校验测试点" in result
        assert "name" in result

    def test_generate_string_tests(self, generator):
        """测试字符串参数测试生成"""
        spec = {
            "type": "string",
            "minLength": 3,
            "maxLength": 20
        }

        tests = generator._generate_param_tests("username", spec, True)
        assert len(tests) > 0

        # 检查是否包含关键测试场景
        scenarios = [test["scenario"] for test in tests]
        assert "正常值" in scenarios
        assert "边界值-最小长度" in scenarios
        assert "边界值-最大长度" in scenarios
        assert "SQL注入" in scenarios

    def test_generate_integer_tests(self, generator):
        """测试整数参数测试生成"""
        spec = {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        }

        tests = generator._generate_param_tests("age", spec, True)
        assert len(tests) > 0

        scenarios = [test["scenario"] for test in tests]
        assert "正常值" in scenarios
        assert "边界值-最小" in scenarios
        assert "边界值-最大" in scenarios

    def test_generate_business_logic_tests(self, generator):
        """测试业务逻辑测试生成"""
        spec = {
            "paths": {
                "/test": {
                    "post": {
                        "summary": "创建唯一数据",
                        "description": "数据必须唯一"
                    }
                }
            }
        }

        tests = generator._generate_business_logic_tests(spec)
        assert len(tests) > 0

        scenarios = [test["scenario"] for test in tests]
        assert any("唯一" in scenario for scenario in scenarios)

    def test_generate_security_tests(self, generator):
        """测试安全测试生成"""
        spec = {}
        tests = generator._generate_security_tests(spec)
        assert len(tests) > 0

        scenarios = [test["scenario"] for test in tests]
        assert any("SQL注入" in scenario for scenario in scenarios)
        assert any("XSS" in scenario for scenario in scenarios)

    def test_parse_simple_definition(self, generator):
        """测试简化定义解析"""
        simple_def = """
        接口名称: 测试接口
        接口路径: POST /api/test
        请求参数:
          - name: string, 必填, 3-20字符
          - age: integer, 可选, 0-150
        返回字段:
          - id: integer
          - name: string
        业务规则:
          - 名称不能重复
        """

        parsed = generator._parse_simple_definition(simple_def)
        assert parsed["name"] == "测试接口"
        assert parsed["path"] == "/api/test"
        assert parsed["method"] == "POST"
        assert len(parsed["parameters"]) == 2
        assert len(parsed["rules"]) == 1

    def test_parse_parameter_line(self, generator):
        """测试参数字符串解析"""
        # 测试字符串参数
        result = generator._parse_parameter_line("- username: string, 必填, 3-20字符")
        assert result is not None
        assert result["name"] == "username"
        assert result["type"] == "string"
        assert result["required"] is True
        assert result["minLength"] == 3
        assert result["maxLength"] == 20

        # 测试整数参数
        result = generator._parse_parameter_line("- age: integer, 可选, 0-150")
        assert result is not None
        assert result["name"] == "age"
        assert result["type"] == "integer"
        assert result["required"] is False

        # 测试枚举参数
        result = generator._parse_parameter_line("- status: enum, 可选, [active, inactive, pending]")
        assert result is not None
        assert result["name"] == "status"
        assert "enum" in result
        assert len(result["enum"]) == 3

    def test_convert_to_openapi(self, generator):
        """测试转换为OpenAPI格式"""
        parsed = {
            "name": "测试接口",
            "path": "/api/test",
            "method": "POST",
            "parameters": [
                {
                    "name": "username",
                    "type": "string",
                    "required": True,
                    "minLength": 3,
                    "maxLength": 20
                }
            ],
            "rules": []
        }

        openapi = generator._convert_to_openapi(parsed)
        assert "openapi" in openapi
        assert "paths" in openapi
        assert "/api/test" in openapi["paths"]

    def test_generate_markdown(self, generator):
        """测试Markdown生成"""
        api_info = {
            "name": "测试API",
            "path": "/api/test",
            "method": "POST",
            "description": "测试接口"
        }

        test_points = {
            "parameter_tests": [
                {
                    "param": "username",
                    "scenario": "正常值",
                    "value": "testuser",
                    "expected": "成功",
                    "priority": "P0"
                }
            ],
            "business_logic_tests": [
                {
                    "scenario": "正常流程",
                    "precondition": "无",
                    "action": "提交数据",
                    "expected": "成功",
                    "priority": "P0"
                }
            ],
            "response_tests": [
                {
                    "item": "结构",
                    "verification": "包含code, message, data",
                    "priority": "P0"
                }
            ],
            "security_tests": [
                {
                    "scenario": "SQL注入",
                    "value": "' OR '1'='1",
                    "expected": "参数错误",
                    "priority": "P0"
                }
            ]
        }

        markdown = generator._generate_markdown(api_info, test_points)
        assert "接口：测试API" in markdown
        assert "参数校验测试点" in markdown
        assert "业务逻辑测试点" in markdown
        assert "安全测试点" in markdown
        assert "总计" in markdown

    def test_generate_from_simple(self, generator):
        """测试从简化定义生成"""
        simple_def = """
        接口名称: 用户登录
        接口路径: POST /api/login
        请求参数:
          - username: string, 必填, 3-20字符
          - password: string, 必填, 6-20字符
        返回字段:
          - token: string
        """

        result = generator.generate_from_simple(simple_def)
        assert "接口：用户登录" in result
        assert "username" in result
        assert "password" in result

    def test_error_handling(self, generator):
        """测试错误处理"""
        # 测试无效的OpenAPI
        with pytest.raises((ValueError, Exception)):
            generator.generate_from_openapi("invalid json")

        # 测试无效的简化定义
        with pytest.raises((ValueError, Exception)):
            generator.generate_from_simple("invalid format")


class TestUtils:
    """测试工具函数"""

    def test_generate_test_value(self):
        """测试生成测试值"""
        from utils import generate_test_value

        # 测试字符串
        value = generate_test_value("string", {"minLength": 3, "maxLength": 20})
        assert isinstance(value, str)
        assert len(value) >= 3
        assert len(value) <= 20

        # 测试整数
        value = generate_test_value("integer", {"minimum": 0, "maximum": 100})
        assert isinstance(value, int)
        assert value >= 0
        assert value <= 100

        # 测试布尔
        value = generate_test_value("boolean")
        assert isinstance(value, bool)

    def test_generate_invalid_value(self):
        """测试生成无效值"""
        from utils import generate_invalid_value

        # 测试字符串
        value = generate_invalid_value("string", {"minLength": 3})
        assert value == ""

        # 测试整数
        value = generate_invalid_value("integer", {"minimum": 0})
        assert value == -1

    def test_security_checks(self):
        """测试安全检测函数"""
        from utils import is_sql_injection, is_xss

        # SQL注入检测
        assert is_sql_injection("' OR '1'='1") is True
        assert is_sql_injection("admin'--") is True
        assert is_sql_injection("normal_user") is False

        # XSS检测
        assert is_xss("<script>alert(1)</script>") is True
        assert is_xss("<img src=x onerror=alert(1)>") is True
        assert is_xss("normal text") is False

    def test_format_validation(self):
        """测试格式验证"""
        from utils import validate_email, validate_phone, validate_uuid

        # 邮箱验证
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False

        # 手机号验证
        assert validate_phone("13800138000") is True
        assert validate_phone("12345678901") is False

        # UUID验证
        import uuid
        assert validate_uuid(str(uuid.uuid4())) is True
        assert validate_uuid("invalid-uuid") is False

    def test_calculate_boundary_values(self):
        """测试边界值计算"""
        from utils import calculate_boundary_values

        boundaries = calculate_boundary_values(0, 100)
        assert boundaries["minimum"] == 0
        assert boundaries["maximum"] == 100
        assert boundaries["just_below_minimum"] == -1
        assert boundaries["just_above_maximum"] == 101


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
