"""去哪儿登录流程测试

测试登录流程的各个步骤。

使用方法：
1. 先启动 Chrome: python -m qvxianjiuguo.chrome_launcher
2. 运行测试: python tests/test_login_flow.py
"""

from __future__ import annotations

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置日志
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def test_login_flow():
    """测试完整登录流程"""
    from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
    from qvxianjiuguo.xhs.cdp import Browser
    from qvxianjiuguo.flight.platforms import get_platform_handler
    import time
    
    print("=" * 60)
    print("去哪儿登录流程测试")
    print("=" * 60)
    
    # 1. 启动Chrome
    print("\n[1] 启动 Chrome...")
    if not ensure_chrome(port=9222, headless=not has_display()):
        print("❌ 无法启动 Chrome")
        return False
    print("✓ Chrome 已启动")
    
    # 2. 连接浏览器
    print("\n[2] 连接浏览器...")
    browser = Browser(host="127.0.0.1", port=9222)
    browser.connect()
    page = browser.get_or_create_page()
    print("✓ 已连接到浏览器")
    
    try:
        handler = get_platform_handler("qunar")
        
        # 3. 导航到登录页面
        print(f"\n[3] 导航到登录页面: {handler.login_url}")
        if not handler.navigate_to_login(page):
            print("❌ 导航到登录页面失败")
            return False
        print("✓ 已到达登录页面")
        time.sleep(3)  # 等待页面完全加载
        
        # 4. 切换到手机号登录
        print("\n[4] 尝试切换到手机号登录...")
        result = handler.switch_to_phone_login(page)
        if result:
            print("✓ 已切换到手机号登录")
        else:
            print("⚠️  切换失败，可能默认就是手机登录")
        time.sleep(1)
        
        # 5. 等待用户输入手机号
        print("\n[5] 请在浏览器中查看登录页面")
        print("    请输入您的手机号进行测试:")
        phone = input("    手机号: ").strip()
        
        if phone.lower() == 'q' or not phone:
            print("跳过手机号输入测试")
            return False
        
        # 6. 输入手机号
        print(f"\n[6] 输入手机号: {phone[:3]}****{phone[-4:]}")
        if not handler.input_phone(page, phone):
            print("❌ 输入手机号失败")
            # 打印页面上的输入框信息
            print("    页面上的输入框:")
            page.evaluate(
                """() => {
                    const inputs = document.querySelectorAll('input');
                    inputs.forEach((input, i) => {
                        console.log(`${i}: type=${input.type}, placeholder="${input.placeholder}", name=${input.name}`);
                    });
                }"""
            )
            return False
        print("✓ 已输入手机号")
        time.sleep(1)
        
        # 7. 点击获取验证码
        print("\n[7] 点击获取验证码...")
        result = handler.click_get_code(page)
        print(f"    结果: {result}")
        
        if not result.get("success"):
            print(f"❌ 点击获取验证码失败: {result.get('error')}")
            # 提供手动操作选项
            print("\n    请在浏览器中手动点击获取验证码按钮")
            print("    完成后按回车继续...")
            input()
        elif result.get("slider_required"):
            print("⚠️  需要完成滑块验证")
            print("    请在浏览器中手动完成滑块验证...")
            
            # 等待用户完成滑块验证
            slider_done = handler.handle_slider(page)
            if slider_done:
                print("✓ 滑块验证完成")
            else:
                print("⚠️  滑块验证超时，请手动完成")
                print("    完成后按回车继续...")
                input()
        else:
            print("✓ 验证码已发送")
        
        # 8. 勾选协议
        print("\n[8] 勾选用户协议...")
        handler.check_agreement(page)
        time.sleep(0.5)
        
        # 9. 等待用户输入验证码
        print("\n[9] 请查看手机短信，输入验证码:")
        code = input("    验证码: ").strip()
        
        if not code:
            print("跳过验证码输入")
            return False
        
        # 10. 提交验证码
        print(f"\n[10] 提交验证码: {code}")
        result = handler.do_verify_code(page, code)
        
        if result.get("success") and result.get("logged_in"):
            print("✓ 登录成功！")
            return True
        else:
            print(f"❌ 登录失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n[结束] 关闭浏览器连接...")
        browser.close_page(page)
        browser.close()


def test_search_after_login():
    """测试登录后的搜索功能"""
    from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
    from qvxianjiuguo.xhs.cdp import Browser
    from qvxianjiuguo.flight.search import search_flights, SearchParams
    from qvxianjiuguo.flight.platforms import get_platform_handler
    import time
    
    print("\n" + "=" * 60)
    print("测试登录后的搜索功能")
    print("=" * 60)
    
    # 启动Chrome
    if not ensure_chrome(port=9222, headless=not has_display()):
        print("❌ 无法启动 Chrome")
        return False
    
    browser = Browser(host="127.0.0.1", port=9222)
    browser.connect()
    page = browser.get_or_create_page()
    
    try:
        handler = get_platform_handler("qunar")
        
        # 检查登录状态
        page.navigate(handler.url)
        time.sleep(3)
        logged_in = handler.check_login(page)
        
        if not logged_in:
            print("❌ 未登录，请先运行 test_login_flow() 登录")
            return False
        
        print("✓ 已登录，开始搜索测试...")
        
        # 执行搜索
        params = SearchParams(
            departure="重庆",
            destination="北京",
            date="2026-04-01",
            platform="qunar",
            departure_range=300,
            destination_range=300,
        )
        
        result = search_flights(page, params)
        
        if result.success:
            print(f"✓ 搜索成功: {len(result.flights)} 个航班")
            for f in result.flights[:5]:
                print(f"  - {f.airline} {f.flight_no}: {f.departure_city}→{f.arrival_city} ¥{f.price}")
            return True
        else:
            print(f"❌ 搜索失败: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False
    finally:
        browser.close_page(page)
        browser.close()


if __name__ == "__main__":
    print("\n选择测试模式:")
    print("1. 测试登录流程")
    print("2. 测试搜索功能（需已登录）")
    print("3. 全部测试")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        test_login_flow()
    elif choice == "2":
        test_search_after_login()
    elif choice == "3":
        if test_login_flow():
            test_search_after_login()
    else:
        print("无效选择")
