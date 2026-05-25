"""测试自动滑块验证"""
from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
from qvxianjiuguo.xhs.cdp import Browser
from qvxianjiuguo.flight.platforms import get_platform_handler
import time

print("=" * 60)
print("测试自动滑块验证")
print("=" * 60)

# 启动 Chrome
print('\n[1] 启动 Chrome...')
ensure_chrome(port=9222, headless=not has_display())

browser = Browser(host='127.0.0.1', port=9222)
browser.connect()
page = browser.new_page()

handler = get_platform_handler('qunar')

# 导航到登录页面
print(f'\n[2] 导航到登录页面: {handler.login_url}')
page.navigate(handler.login_url)
page.wait_for_load()
time.sleep(3)

# 输入手机号
print('\n[3] 输入手机号...')
test_phone = '13012344249'
result = page.evaluate(f"(() => {{ const input = document.querySelector('input[placeholder*=\"手机号\"]'); if (input) {{ input.value = '{test_phone}'; input.dispatchEvent(new Event('input', {{ bubbles: true }})); return {{ success: true }}; }} return {{ success: false }}; }})()")
print(f'   输入结果: {result}')
time.sleep(1)

# 点击获取验证码
print('\n[4] 点击获取验证码...')
result = page.evaluate("(() => { const allBtns = document.querySelectorAll('button, a, span, div, [role=\"button\"]'); let bestMatch = null; for (const btn of allBtns) { const text = (btn.innerText || '').trim(); if (text === '获取验证码' || text === '获取') { if (!bestMatch || text.length < bestMatch.text.length) { bestMatch = { el: btn, text: text }; } } } if (bestMatch) { bestMatch.el.click(); return { success: true, text: bestMatch.text }; } return { success: false }; })()")
print(f'   点击结果: {result}')
time.sleep(1)

# 检查滑块
print('\n[5] 检查滑块...')
slider_info = page.evaluate("(() => { const sliderBtn = document.querySelector('._1Ew2tq3rLusero3Pp4uJ6l'); const sliderContainer = document.querySelector('.wD_3tFwzy2MynVVzMZSmv'); if (!sliderBtn || !sliderContainer) { return { found: false }; } const btnRect = sliderBtn.getBoundingClientRect(); const containerRect = sliderContainer.getBoundingClientRect(); return { found: true, btnX: btnRect.x, btnY: btnRect.y + btnRect.height / 2, btnWidth: btnRect.width, containerWidth: containerRect.width, slideDistance: containerRect.width - btnRect.width - 10 }; })()")
print(f'   滑块信息: {slider_info}')

if slider_info and slider_info.get("found"):
    # 执行自动滑块
    print('\n[6] 执行自动滑块验证...')
    start_x = slider_info["btnX"] + slider_info["btnWidth"] / 2
    start_y = slider_info["btnY"]
    end_x = start_x + slider_info["slideDistance"]
    end_y = start_y
    
    print(f'   拖动: ({start_x:.1f}, {start_y:.1f}) -> ({end_x:.1f}, {end_y:.1f})')
    
    page.mouse_drag(start_x, start_y, end_x, end_y, steps=30)
    
    time.sleep(2)
    
    # 检查结果
    print('\n[7] 检查验证结果...')
    
    # 检查是否有倒计时
    countdown = page.evaluate("(() => { const allBtns = document.querySelectorAll('button, a, span, div'); for (const btn of allBtns) { const text = (btn.innerText || '').trim(); if (text.match(/\\d+s/) || text.includes('秒后重发')) { return true; } } return false; })()")
    
    if countdown:
        print('   ✓ 验证码已发送！（检测到倒计时）')
    else:
        print('   未检测到倒计时，检查其他状态...')
        
        # 检查滑块是否消失
        slider_gone = page.evaluate("(() => { const sliderBtn = document.querySelector('._1Ew2tq3rLusero3Pp4uJ6l'); return !sliderBtn || sliderBtn.offsetParent === null; })()")
        if slider_gone:
            print('   ✓ 滑块已消失')
        else:
            print('   滑块仍然存在，可能需要重试')

print('\n' + '=' * 60)
print('测试完成！')
print('=' * 60)

browser.close_page(page)
browser.close()
