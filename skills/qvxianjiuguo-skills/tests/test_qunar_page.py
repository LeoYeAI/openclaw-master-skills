"""测试去哪儿登录页面 - 详细版"""
from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
from qvxianjiuguo.xhs.cdp import Browser
import time

print('启动 Chrome...')
ensure_chrome(port=9222, headless=not has_display())

print('连接到 Chrome...')
browser = Browser(host='127.0.0.1', port=9222)
browser.connect()

print('创建页面...')
page = browser.new_page()

print('导航到去哪儿登录页...')
page.navigate('https://user.qunar.com/passport/login.jsp')
page.wait_for_load()
time.sleep(5)

# 测试 evaluate 方法
print('\n=== 测试 evaluate 方法 ===')

print('1. 获取 document.title:')
result = page.evaluate('document.title')
print(f'   结果: {repr(result)}')

print('2. 获取 input 数量:')
result = page.evaluate('document.querySelectorAll("input").length')
print(f'   结果: {result}')

print('3. 获取 input placeholder 列表:')
result = page.evaluate('[...document.querySelectorAll("input")].map(i => i.placeholder)')
print(f'   结果: {result}')

print('4. 获取 input type 列表:')
result = page.evaluate('[...document.querySelectorAll("input")].map(i => i.type)')
print(f'   结果: {result}')

print('5. 获取 input name 列表:')
result = page.evaluate('[...document.querySelectorAll("input")].map(i => i.name)')
print(f'   结果: {result}')

print('6. 测试返回对象:')
result = page.evaluate('(() => { return {a: 1, b: 2}; })()')
print(f'   结果: {result}')

print('7. 测试返回数组:')
result = page.evaluate('[1, 2, 3]')
print(f'   结果: {result}')

print('8. 测试复杂对象:')
result = page.evaluate("""(() => {
    const inputs = [];
    document.querySelectorAll('input').forEach(el => {
        inputs.push(el.placeholder || el.name || el.type);
    });
    return inputs;
})()""")
print(f'   结果: {result}')

print('9. 获取所有包含"手机"的元素:')
result = page.evaluate("""(() => {
    const elements = [];
    document.querySelectorAll('*').forEach(el => {
        const text = el.innerText || '';
        if (text.includes('手机') || text.includes('验证码')) {
            elements.push(text.trim().substring(0, 50));
        }
    });
    return [...new Set(elements)];
})()""")
print(f'   结果: {result}')

print('10. 获取所有按钮文字:')
result = page.evaluate("""(() => {
    const texts = [];
    document.querySelectorAll('button, a, span[onclick], div[onclick]').forEach(el => {
        const text = (el.innerText || '').trim();
        if (text && text.length < 30) {
            texts.push(text);
        }
    });
    return [...new Set(texts)];
})()""")
print(f'   结果: {result}')

browser.close_page(page)
browser.close()
print('\n测试完成!')
