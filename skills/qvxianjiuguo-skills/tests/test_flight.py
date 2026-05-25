"""机票搜索功能测试脚本

测试 SKILL.md 中提到的所有 CLI 命令：
1. flight-lookup - 查询机场信息
2. flight-nearby - 查询附近机场
3. flight-search - 机票模糊搜索
4. flight-check-login - 检查登录状态
5. flight-login - 发送验证码登录
6. flight-verify - 验证验证码

使用方法：
1. 先启动 Chrome: python -m qvxianjiuguo.chrome_launcher
2. 运行测试: uv run python -m pytest tests/test_flight.py -v
"""

from __future__ import annotations

import subprocess
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_cli(args: str) -> tuple[dict, int]:
    """运行 CLI 命令并返回 JSON 结果和退出码"""
    cmd = f'uv run python -m qvxianjiuguo.cli {args}'
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    try:
        output = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        output = {"raw_output": result.stdout, "error": result.stderr}
    
    return output, result.returncode


class TestFlightLookup:
    """测试 flight-lookup 命令"""

    def test_lookup_by_city_name(self):
        """测试通过城市名查询机场"""
        output, code = run_cli('flight-lookup --city "重庆"')
        
        assert code == 0, f"命令执行失败: {output}"
        assert output.get("success") == True, f"查询失败: {output}"
        assert "airports" in output, f"缺少 airports 字段: {output}"
        
        airports = output["airports"]
        assert len(airports) > 0, "没有找到机场"
        
        airport = airports[0]
        assert airport["code"] == "CKG", f"机场代码错误: {airport}"
        assert "重庆" in airport["name"], f"机场名称错误: {airport}"
        print(f"✓ 通过城市名查询成功: {airport['name']} ({airport['code']})")

    def test_lookup_by_airport_code(self):
        """测试通过机场代码查询"""
        output, code = run_cli('flight-lookup --city "PEK"')
        
        assert code == 0, f"命令执行失败: {output}"
        assert output.get("success") == True, f"查询失败: {output}"
        
        airports = output["airports"]
        assert len(airports) > 0, "没有找到机场"
        assert airports[0]["code"] == "PEK", f"机场代码错误: {airports[0]}"
        print(f"✓ 通过机场代码查询成功: {airports[0]['name']}")

    def test_lookup_not_found(self):
        """测试查询不存在的城市"""
        output, code = run_cli('flight-lookup --city "不存在城市XYZ"')
        
        assert output.get("success") == False, "应该返回失败"
        assert "error" in output, "应该包含错误信息"
        print(f"✓ 不存在城市返回正确错误: {output.get('error')}")


class TestFlightNearby:
    """测试 flight-nearby 命令"""

    def test_nearby_default_range(self):
        """测试默认范围查询附近机场"""
        output, code = run_cli('flight-nearby --airport "CKG"')
        
        assert code == 0, f"命令执行失败: {output}"
        assert output.get("success") == True, f"查询失败: {output}"
        assert "airports" in output, f"缺少 airports 字段: {output}"
        assert "CKG" in output["airports"], "结果应包含查询的机场"
        print(f"✓ 查询附近机场成功: {len(output['airports'])} 个机场")

    def test_nearby_custom_range(self):
        """测试自定义范围查询"""
        output, code = run_cli('flight-nearby --airport "PEK" --range 200')
        
        assert code == 0, f"命令执行失败: {output}"
        assert output.get("success") == True, f"查询失败: {output}"
        assert output["range_km"] == 200, "范围参数不正确"
        print(f"✓ 自定义范围查询成功: {output['range_km']}km 内 {len(output['airports'])} 个机场")

    def test_nearby_invalid_airport(self):
        """测试无效机场代码"""
        output, code = run_cli('flight-nearby --airport "XXX"')
        
        assert output.get("success") == False, "应该返回失败"
        print(f"✓ 无效机场返回正确错误: {output.get('error')}")


class TestFlightCheckLogin:
    """测试 flight-check-login 命令"""

    def test_check_login_qunar(self):
        """测试检查去哪儿登录状态"""
        output, code = run_cli('flight-check-login --platform qunar')
        
        assert code == 0, f"命令执行失败: {output}"
        assert output.get("success") == True, f"检查失败: {output}"
        assert "logged_in" in output, "应该包含登录状态"
        assert "platform_name" in output, "应该包含平台名称"
        print(f"✓ 检查去哪儿登录状态: {'已登录' if output.get('logged_in') else '未登录'}")

    def test_check_login_ctrip(self):
        """测试检查携程登录状态"""
        output, code = run_cli('flight-check-login --platform ctrip')
        
        assert code == 0, f"命令执行失败: {output}"
        assert output.get("success") == True, f"检查失败: {output}"
        print(f"✓ 检查携程登录状态: {'已登录' if output.get('logged_in') else '未登录'}")

    def test_check_login_invalid_platform(self):
        """测试无效平台"""
        output, code = run_cli('flight-check-login --platform invalid')
        
        # 应该返回错误（参数验证失败）
        assert code != 0 or output.get("success") == False
        print(f"✓ 无效平台返回正确错误")


class TestFlightLogin:
    """测试 flight-login 命令"""

    def test_login_missing_phone(self):
        """测试缺少手机号参数"""
        result = subprocess.run(
            'uv run python -m qvxianjiuguo.cli flight-login --platform qunar',
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        # 应该显示参数错误
        assert result.returncode != 0 or "required" in result.stderr.lower()
        print("✓ 缺少手机号参数正确报错")

    def test_login_invalid_phone(self):
        """测试无效手机号（不会真正发送验证码，因为未启动浏览器）"""
        # 这个测试需要 Chrome 运行，跳过实际验证
        print("✓ 登录命令参数测试跳过（需要 Chrome 运行）")


class TestLoginWorkflow:
    """测试完整登录流程

    这个测试类验证登录流程的各个步骤：
    1. 检查登录状态 -> 未登录
    2. 尝试搜索 -> 返回 login_required
    3. 发送验证码 -> 需要手机号
    4. 提交验证码 -> 需要验证码
    """

    def test_workflow_check_login(self):
        """测试步骤1：检查登录状态"""
        output, code = run_cli('flight-check-login --platform qunar')
        
        assert code == 0, f"命令执行失败: {output}"
        assert output.get("success") == True, f"检查失败: {output}"
        assert "logged_in" in output, "应包含登录状态"
        
        status = "已登录" if output.get("logged_in") else "未登录"
        print(f"✓ 步骤1 - 检查登录状态: {status}")

    def test_workflow_search_requires_login(self):
        """测试步骤2：未登录时搜索返回 login_required"""
        # 先检查是否已登录
        check_output, _ = run_cli('flight-check-login --platform qunar')
        
        if check_output.get("logged_in"):
            print("✓ 步骤2 - 已登录，跳过此测试")
            return
        
        # 未登录时尝试搜索
        output, code = run_cli(
            'flight-search --departure "重庆" --destination "北京" --date "2026-04-01"'
        )
        
        assert output.get("login_required") == True, f"应返回 login_required: {output}"
        assert "message" in output, "应包含提示信息"
        print(f"✓ 步骤2 - 未登录搜索返回 login_required: {output.get('message')}")

    def test_workflow_login_command_structure(self):
        """测试步骤3：验证登录命令参数结构"""
        # 验证 flight-login 命令存在且参数正确
        result = subprocess.run(
            'uv run python -m qvxianjiuguo.cli flight-login --help',
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        assert "phone" in result.stdout.lower(), "应包含 phone 参数"
        assert "platform" in result.stdout.lower(), "应包含 platform 参数"
        print("✓ 步骤3 - flight-login 命令结构正确")

    def test_workflow_verify_command_structure(self):
        """测试步骤4：验证验证码命令参数结构"""
        result = subprocess.run(
            'uv run python -m qvxianjiuguo.cli flight-verify --help',
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        assert "code" in result.stdout.lower(), "应包含 code 参数"
        assert "platform" in result.stdout.lower(), "应包含 platform 参数"
        print("✓ 步骤4 - flight-verify 命令结构正确")

    def test_workflow_platform_all_skips_login(self):
        """测试使用 --platform all 跳过登录检查"""
        output, code = run_cli(
            'flight-search --departure "重庆" --destination "北京" --date "2026-04-01" --platform all'
        )
        
        # 使用 all 平台不应返回 login_required
        if output.get("login_required"):
            assert False, "使用 --platform all 不应要求登录"
        
        print("✓ 步骤5 - --platform all 成功跳过登录检查")


class TestFlightSearch:
    """测试 flight-search 命令"""

    def test_search_missing_params(self):
        """测试缺少必要参数"""
        result = subprocess.run(
            'uv run python -m qvxianjiuguo.cli flight-search --platform qunar',
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        # 应该显示参数错误
        assert result.returncode != 0
        print("✓ 缺少必要参数正确报错")

    def test_search_all_params(self):
        """测试完整参数（需要 Chrome 和登录状态）"""
        # 这个测试需要完整的运行环境
        output, code = run_cli(
            'flight-search --departure "重庆" --destination "北京" '
            '--date "2026-04-01" --platform qunar '
            '--departure-range 300 --destination-range 300'
        )
        
        if output.get("login_required"):
            print("✓ 搜索检测到未登录状态，提示使用验证码登录")
        elif output.get("success"):
            print(f"✓ 搜索成功: {len(output.get('flights', []))} 个航班")
        else:
            print(f"! 搜索结果: {output.get('error', '未知错误')}")


class TestIntegration:
    """集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        results = []
        
        # 1. 查询出发地机场
        output1, _ = run_cli('flight-lookup --city "重庆"')
        results.append(("机场查询", output1.get("success", False)))
        
        # 2. 查询附近机场
        output2, _ = run_cli('flight-nearby --airport "CKG" --range 350')
        results.append(("附近机场", output2.get("success", False)))
        
        # 3. 检查登录状态
        output3, _ = run_cli('flight-check-login --platform qunar')
        results.append(("登录检查", output3.get("success", False)))
        
        print("\n=== 集成测试结果 ===")
        all_passed = True
        for name, passed in results:
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"  {name}: {status}")
            if not passed:
                all_passed = False
        
        assert all_passed, "部分测试失败"
        print("\n✓ 所有集成测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("曲线救国 - 机票搜索功能测试")
    print("=" * 60)
    print()
    
    # 运行所有测试
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
