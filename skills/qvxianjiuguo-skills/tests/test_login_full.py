"""完整登录测试"""
from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
from qvxianjiuguo.xhs.cdp import Browser
from qvxianjiuguo.flight.platforms import get_platform_handler
import time

print("=" * 60)
print("去哪儿登录完整测试")
print("=" * 60)

# 启动 Chrome
print('\n[1] 启动 Chrome...')
ensure_chrome(port=9222, headless=not has_display())

browser = Browser(host='127.0.0.1', port=9222)
browser.connect()
page = browser.new_page()

# 获取处理器
handler = get_platform_handler('qunar')

# 导航到登录页面
print(f'\n[2] 导航到登录页面: {handler.login_url}')
page.navigate(handler.login_url)
page.wait_for_load()
time.sleep(3)

# 切换到手机登录
print('\n[3] 切换到手机号登录...')
has_phone_input = page.has_element('input[placeholder*="手机号"]')
print(f'   当前是否有手机号输入框: {has_phone_input}')

if not has_phone_input:
    result = page.evaluate("(() => { const allElements = document.querySelectorAll('a, button, span, div, li, label'); for (const el of allElements) { const text = (el.innerText || '').trim(); if (text.includes('手机号登录') || text.includes('手机登录')) { el.click(); return text; } } return null; })()")
    print(f'   点击切换按钮: {result}')
    time.sleep(2)

has_phone_input = page.has_element('input[placeholder*="手机号"]')
print(f'   切换后是否有手机号输入框: {has_phone_input}')

# 检查输入框
print('\n[4] 检查输入框...')
inputs = page.evaluate('[...document.querySelectorAll("input")].map(i => ({type: i.type, placeholder: i.placeholder}))')
print(f'   当前输入框: {inputs}')

# 输入手机号
print('\n[5] 输入手机号...')
test_phone = '13012344249'
result = page.evaluate(f"(() => {{ const input = document.querySelector('input[placeholder*=\"手机号\"]'); if (input) {{ input.value = '{test_phone}'; input.dispatchEvent(new Event('input', {{ bubbles: true }})); input.dispatchEvent(new Event('change', {{ bubbles: true }})); return {{ success: true, value: input.value }}; }} return {{ success: false }}; }})()")
print(f'   输入结果: {result}')

time.sleep(1)

# 查找获取验证码按钮
print('\n[6] 查找获取验证码按钮...')
buttons = page.evaluate("(() => { const texts = []; document.querySelectorAll('button, a, span, div, [role=\"button\"]').forEach(el => { const text = (el.innerText || '').trim(); if (text.includes('获取') || text.includes('验证码') || text.includes('发送')) { texts.push(text.substring(0, 30)); } }); return [...new Set(texts)]; })()")
print(f'   找到的按钮: {buttons}')

# 点击获取验证码
print('\n[7] 点击获取验证码...')
# 使用更精确的选择器：找到文字长度较短的元素
result = page.evaluate("(() => { const allBtns = document.querySelectorAll('button, a, span, div, [role=\"button\"]'); let bestMatch = null; for (const btn of allBtns) { const text = (btn.innerText || '').trim(); if (text === '获取验证码' || text === '获取') { if (!bestMatch || text.length < bestMatch.text.length) { bestMatch = { el: btn, text: text }; } } } if (bestMatch) { bestMatch.el.click(); return { success: true, text: bestMatch.text }; } return { success: false, reason: '未找到按钮' }; })()")
print(f'   点击结果: {result}')

time.sleep(2)

# 检查滑块
print('\n[8] 检查滑块验证...')
slider = page.evaluate("(() => { const selectors = ['._1Ew2tq3rLusero3Pp4uJ6l', '.NrgjHeg7YBdiFd3U9T_j_', '.wD_3tFwzy2MynVVzMZSmv', '[class*=\"slide\"]', '[class*=\"slider\"]']; for (const sel of selectors) { const el = document.querySelector(sel); if (el && el.offsetParent !== null) { return { found: true, selector: sel }; } } return { found: false }; })()")
print(f'   滑块状态: {slider}')

# 检查验证码输入框
print('\n[9] 检查验证码输入框...')
code_input = page.evaluate("(() => { const input = document.querySelector('input[placeholder*=\"验证码\"]'); return input ? { found: true, placeholder: input.placeholder } : { found: false }; })()")
print(f'   验证码输入框: {code_input}')

print('\n' + '=' * 60)
print('测试完成！')
print('=' * 60)

browser.close_page(page)
browser.close()