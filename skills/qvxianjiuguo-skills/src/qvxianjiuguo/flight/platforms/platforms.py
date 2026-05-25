"""机票搜索平台处理器

支持四个平台：
- qunar: 去哪儿
- ctrip: 携程
- fliggy: 飞猪
- ly: 同程
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger("flight-search")

# 调试模式：保存页面HTML用于分析
DEBUG_SAVE_HTML = os.environ.get("DEBUG_SAVE_HTML", "").lower() in ("1", "true", "yes")


class PlatformHandler(ABC):
    """平台处理器基类"""

    name: str = ""
    url: str = ""
    login_url: str = ""
    cookie_domain: str = ""  # Cookie 作用域名，子类需要设置

    @abstractmethod
    def search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """搜索航班

        Args:
            page: CDP Page 对象
            departure_city: 出发城市
            arrival_city: 到达城市
            date: 日期 (YYYY-MM-DD)

        Returns:
            航班列表
        """
        pass

    def search_without_navigation(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """在已导航的页面上搜索（跳过页面导航）

        子类可重写此方法以优化重复搜索。
        """
        return self.search(page, departure_city, arrival_city, date)

    def check_login(self, page) -> bool:
        """检查登录状态

        Returns:
            True 已登录，False 未登录
        """
        # 默认实现：检查是否有登录按钮
        try:
            login_btn = page.evaluate(
                "document.querySelector('.login-btn, .login-btn-pc, #login-btn') !== null"
            )
            return not login_btn
        except Exception:
            return False

    def _load_cookies_from_file(self, page) -> bool:
        """从本地文件加载 cookie 到浏览器
        
        Args:
            page: CDP Page 对象
            
        Returns:
            True 加载成功，False 加载失败或文件不存在
        """
        if not self.cookie_domain:
            logger.debug(f"未设置 cookie_domain，跳过 cookie 加载")
            return False
            
        # cookie 文件路径
        cookie_dir = os.path.join(os.path.expanduser("~"), ".qvxian")
        cookie_file = os.path.join(cookie_dir, f"{self.cookie_domain.split('.')[0]}_cookies.json")
        
        if not os.path.exists(cookie_file):
            logger.debug(f"Cookie 文件不存在: {cookie_file}")
            return False
        
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            cookies = cookie_data.get("cookies", {})
            if not cookies:
                logger.warning("Cookie 文件中没有有效的 cookie")
                return False
            
            # 先导航到目标域名（设置 cookie 需要在同域下）
            current_url = page.evaluate("window.location.href")
            if self.cookie_domain not in current_url:
                page.navigate(self.url)
                time.sleep(1)
            
            # 使用 CDP Network.setCookie 设置 cookie（支持特殊字符）
            success_count = 0
            for name, value in cookies.items():
                try:
                    if page.set_cookie(name, value, f".{self.cookie_domain}"):
                        success_count += 1
                except Exception as e:
                    logger.debug(f"设置 cookie {name} 失败: {e}")
            
            logger.info(f"已从本地加载 {success_count}/{len(cookies)} 个 cookie")
            time.sleep(0.5)
            return success_count > 0
            
        except Exception as e:
            logger.warning(f"加载 cookie 文件失败: {e}")
            return False


class QunarHandler(PlatformHandler):
    """去哪儿平台处理器"""

    name = "去哪儿"
    url = "https://flight.qunar.com/"
    login_url = "https://user.qunar.com/passport/login.jsp"
    cookie_domain = "qunar.com"

    def search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """搜索去哪儿航班"""
        # 尝试自动加载 cookie
        logger.info("尝试加载本地 cookie...")
        self._load_cookies_from_file(page)
        
        # 检查登录状态
        logger.info("检查登录状态...")
        if not self.check_login(page):
            logger.error("未登录！请先保存 cookie：\n1. 在 Chrome 中手动登录去哪儿\n2. 运行: qvxian flight-save-cookie --platform qunar")
            return [{
                "error": "未登录",
                "message": "请先登录去哪儿账号才能搜索航班。推荐使用 cookie 登录：\n1. 启动 Chrome: python -m qvxianjiuguo.chrome_launcher\n2. 在 Chrome 中手动登录去哪儿\n3. 保存 cookie: qvxian flight-save-cookie --platform qunar",
                "login_required": True
            }]
        
        # 尝试直接导航到搜索结果页面（更可靠）
        # 构建搜索URL
        search_url = f"https://flight.qunar.com/site/oneway_list.htm?searchDepartureAirport={departure_city}&searchArrivalAirport={arrival_city}&searchDepartureTime={date}"
        logger.info(f"直接导航到搜索页面: {search_url}")
        
        try:
            page.navigate(search_url)
            page.wait_for_load()
            
            # 智能等待航班元素加载
            max_wait = 10  # 最多等待10秒
            for i in range(max_wait):
                time.sleep(1)
                # 检查是否有航班元素
                has_flights = page.evaluate(
                    """(() => {
                        const selectors = ['.b-airfly', '.m-airfly-lst', '.flight-item', '.e-airfly', '[class*="airfly"]'];
                        for (const sel of selectors) {
                            if (document.querySelector(sel)) return true;
                        }
                        // 检查页面内容长度
                        return document.body.innerHTML.length > 200000;
                    })()"""
                )
                if has_flights:
                    logger.info(f"航班元素已加载（等待 {i+1}s）")
                    break
            
            # 额外等待确保数据稳定
            time.sleep(2)
            
            # 检查是否成功导航
            current_url = page.evaluate("window.location.href")
            if "oneway_list" in current_url:
                logger.info("成功导航到搜索结果页面")
                return self._parse_results(page)
        except Exception as e:
            logger.warning(f"直接导航失败: {e}，尝试传统搜索方式")
        
        # 回退到传统搜索方式
        page.navigate(self.url)
        page.wait_for_load()
        time.sleep(2)

        return self._do_search(page, departure_city, arrival_city, date)

    def search_without_navigation(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """在已导航的页面上搜索"""
        return self._do_search(page, departure_city, arrival_city, date)

    def _do_search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """执行搜索"""
        logger.info(f"开始搜索: {departure_city} -> {arrival_city}, 日期: {date}")
        
        # 0. 清除可能的反爬虫覆盖层和弹窗
        try:
            page.evaluate(
                """(() => {
                    // 移除可能的覆盖层
                    const overlays = document.querySelectorAll('[style*="pointer-events: none"], [style*="z-index: 2147483647"]');
                    overlays.forEach(el => el.remove());
                    
                    // 点击关闭可能的弹窗
                    const closeBtns = document.querySelectorAll('.close-btn, .close, [class*="close"], .modal-close, .dialog-close');
                    closeBtns.forEach(btn => {
                        try { btn.click(); } catch(e) {}
                    });
                    
                    // 移除可能的遮罩层
                    const masks = document.querySelectorAll('[class*="mask"], [class*="overlay"], [class*="modal-backdrop"]');
                    masks.forEach(el => el.remove());
                    
                    return true;
                })()"""
            )
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. 选择单程（如果需要）
        try:
            page.evaluate(
                """(() => {
                    const singleBtn = document.querySelector('#searchTypeSng, .js-searchtype-oneway');
                    if (singleBtn && !singleBtn.checked) {
                        singleBtn.click();
                    }
                })()"""
            )
            time.sleep(0.3)
        except Exception as e:
            logger.debug(f"选择单程失败（可能已选中）: {e}")

        # 2. 输入出发城市
        logger.info(f"输入出发城市: {departure_city}")
        try:
            # 点击出发城市输入框
            page.evaluate(
                """(() => {
                    const selectors = [
                        'input[name="fromCity"]',
                        '.textbox[name="fromCity"]',
                        '.qcbox.qcity',
                        '.js-fromcity'
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            el.click();
                            el.focus();
                            return true;
                        }
                    }
                    return false;
                })()"""
            )
            time.sleep(0.5)
            
            # 输入城市名
            page.evaluate(
                f"""(() => {{
                    const activeEl = document.activeElement;
                    if (activeEl) {{
                        activeEl.value = {json.dumps(departure_city)};
                        activeEl.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        activeEl.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                    
                    // 也尝试直接设置输入框
                    const inputs = document.querySelectorAll('input[name="fromCity"], .textbox[name="fromCity"]');
                    inputs.forEach(el => {{
                        el.value = {json.dumps(departure_city)};
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }});
                }})()"""
            )
            time.sleep(0.8)
            
            # 选择下拉选项
            page.evaluate(
                """(() => {
                    const selectors = [
                        '.city-suggest li',
                        '.qcbox-city-list li',
                        '.js-citylist li',
                        '.suggest-item',
                        '[data-city]'
                    ];
                    for (const sel of selectors) {
                        const items = document.querySelectorAll(sel);
                        if (items.length > 0) {
                            items[0].click();
                            return true;
                        }
                    }
                    return false;
                })()"""
            )
            time.sleep(0.3)
            
            # 发送 ESC 键关闭下拉框
            try:
                page.press_key("Escape")
            except Exception:
                pass
            time.sleep(0.3)
        except Exception as e:
            logger.warning(f"输入出发城市失败: {e}")

        # 3. 输入到达城市
        logger.info(f"输入到达城市: {arrival_city}")
        try:
            page.evaluate(
                """(() => {
                    const selectors = [
                        'input[name="toCity"]',
                        '.textbox[name="toCity"]',
                        '.qcbox.qcity:last-of-type',
                        '.js-tocity'
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            el.click();
                            el.focus();
                            return true;
                        }
                    }
                    return false;
                })()"""
            )
            time.sleep(0.5)
            
            page.evaluate(
                f"""(() => {{
                    const activeEl = document.activeElement;
                    if (activeEl) {{
                        activeEl.value = {json.dumps(arrival_city)};
                        activeEl.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        activeEl.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                    
                    const inputs = document.querySelectorAll('input[name="toCity"], .textbox[name="toCity"]');
                    inputs.forEach(el => {{
                        el.value = {json.dumps(arrival_city)};
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }});
                }})()"""
            )
            time.sleep(0.8)
            
            # 选择下拉选项
            page.evaluate(
                """(() => {
                    const selectors = [
                        '.city-suggest li',
                        '.qcbox-city-list li',
                        '.js-citylist li',
                        '.suggest-item',
                        '[data-city]'
                    ];
                    for (const sel of selectors) {
                        const items = document.querySelectorAll(sel);
                        if (items.length > 0) {
                            items[0].click();
                            return true;
                        }
                    }
                    return false;
                })()"""
            )
            time.sleep(0.3)
            
            # 发送 ESC 键关闭下拉框
            try:
                page.press_key("Escape")
            except Exception:
                pass
            time.sleep(0.3)
        except Exception as e:
            logger.warning(f"输入到达城市失败: {e}")

        # 4. 输入日期
        logger.info(f"输入日期: {date}")
        try:
            # 点击日期输入框
            page.evaluate(
                """(() => {
                    const selectors = [
                        '#fromDate',
                        'input[name="fromDate"]',
                        '.textbox[name="fromDate"]'
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            el.click();
                            el.focus();
                            return true;
                        }
                    }
                    return false;
                })()"""
            )
            time.sleep(0.3)
            
            # 输入日期
            page.evaluate(
                f"""(() => {{
                    const dateInputs = document.querySelectorAll('#fromDate, input[name="fromDate"]');
                    dateInputs.forEach(el => {{
                        el.value = {json.dumps(date)};
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }});
                    
                    // 关闭日历弹窗
                    document.body.click();
                }})()"""
            )
            time.sleep(0.3)
        except Exception as e:
            logger.warning(f"输入日期失败: {e}")

        # 5. 点击搜索按钮并等待页面导航
        logger.info("点击搜索按钮")
        start_url = page.evaluate("window.location.href")
        logger.debug(f"当前URL: {start_url}")
        
        try:
            clicked = page.evaluate(
                """(() => {
                    const selectors = [
                        '.btn_search',
                        'button.btn_search',
                        '.search-btn',
                        '#searchBtn'
                    ];
                    for (const sel of selectors) {
                        const btn = document.querySelector(sel);
                        if (btn) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                })()"""
            )
            if not clicked:
                logger.error("未找到搜索按钮")
        except Exception as e:
            logger.error(f"点击搜索按钮失败: {e}")
        
        # 等待页面导航到结果页
        logger.info("等待页面导航...")
        time.sleep(2)
        
        nav_timeout = 15
        nav_start = time.time()
        navigated = False
        
        while time.time() - nav_start < nav_timeout:
            try:
                current_url = page.evaluate("window.location.href")
                # 检查URL是否变化到搜索结果页
                if "oneway_list" in current_url or current_url != start_url:
                    logger.info(f"页面已导航到: {current_url}")
                    navigated = True
                    break
                time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        
        if not navigated:
            logger.warning("页面导航超时，尝试继续解析")
        
        # 等待页面加载完成
        time.sleep(3)
        try:
            page.wait_for_load()
        except Exception:
            pass
        
        # 6. 等待结果加载 - 智能等待
        logger.info("等待航班结果加载...")
        time.sleep(2)
        
        # 尝试多种方式等待航班列表出现
        max_wait = 20  # 最大等待20秒
        start_time = time.time()
        flight_found = False
        
        while time.time() - start_time < max_wait:
            try:
                # 检查是否有航班元素或加载完成
                check_result = page.evaluate(
                    """(() => {
                        // 检查各种航班列表选择器
                        const selectors = [
                            '.flight-list', '.flight-item', '.m-flight-item', '.b-airflight',
                            '[data-flight]', '.airflight', '.flightList', '.flight_content',
                            '.flight-card', '.flightCard', '.list-item', '.air-line',
                            '[class*="flight"]', '[class*="Flight"]', '[class*="airline"]'
                        ];
                        
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el) {
                                return { found: true, selector: sel, html_length: el.innerHTML.length };
                            }
                        }
                        
                        // 检查是否有加载中状态
                        const loadingEl = document.querySelector('.loading, .spinner, [class*="loading"], [class*="Loading"]');
                        if (loadingEl) {
                            return { found: false, loading: true };
                        }
                        
                        // 检查是否有无结果提示
                        const noResultEl = document.querySelector('.no-result, .empty-result, [class*="no-result"], [class*="empty"]');
                        if (noResultEl) {
                            return { found: false, noResult: true, text: noResultEl.innerText };
                        }
                        
                        return { found: false, loading: false };
                    })()"""
                )
                
                if check_result:
                    if check_result.get('found'):
                        logger.info(f"找到航班列表: {check_result.get('selector')}")
                        flight_found = True
                        break
                    elif check_result.get('noResult'):
                        logger.warning(f"搜索无结果: {check_result.get('text')}")
                        break
                    elif check_result.get('loading'):
                        logger.debug("页面正在加载中...")
                    
                time.sleep(1)
            except Exception as e:
                logger.debug(f"等待检查异常: {e}")
                time.sleep(1)
        
        if not flight_found:
            logger.warning("等待航班列表超时，尝试解析当前页面")
        
        time.sleep(2)  # 额外等待确保页面稳定

        # 7. 解析结果
        return self._parse_results(page)

    def _parse_results(self, page) -> list[dict]:
        """解析搜索结果"""
        results = []

        # 调试：保存页面HTML
        if DEBUG_SAVE_HTML:
            try:
                html_content = page.evaluate("document.documentElement.outerHTML")
                debug_path = os.path.join(os.getcwd(), "debug_page.html")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"页面HTML已保存到: {debug_path}")
            except Exception as e:
                logger.warning(f"保存页面HTML失败: {e}")

        # 首先获取页面URL和基本结构信息
        page_info = page.evaluate(
            """(() => {
                const url = window.location.href;
                const title = document.title;
                
                // 检查是否有错误提示
                const errorEl = document.querySelector('.error-msg, .no-result, .empty-result, [class*="error"]');
                const errorMsg = errorEl ? errorEl.innerText : null;
                
                // 检查页面主要区域
                const mainAreas = [];
                const selectors = ['#flightList', '.flight-list', '.b-airflight', '.m-flight-item', 
                                   '.flight-item', '[data-flight]', '.airflight', '.result-list',
                                   '.flight-list-container', '.search-result', '#flight_list',
                                   '.flightlist', '.list-content', '.flight-content',
                                   '.flight-list-wrapper', '.flight-content-list', '.m-main',
                                   '[class*="flightList"]', '[class*="flight-list"]'];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        mainAreas.push({selector: sel, count: el.querySelectorAll('*').length});
                    }
                }
                
                // 获取页面所有主要元素的信息
                const bodyInfo = {
                    childCount: document.body.children.length,
                    innerHTML_length: document.body.innerHTML.length
                };
                
                // 获取所有包含 flight 或 air 的类名
                const flightClasses = [];
                document.querySelectorAll('[class*="flight"], [class*="air"], [class*="list"], [class*="Flight"]').forEach(el => {
                    if (flightClasses.length < 50) {
                        flightClasses.push(el.className.split(' ').slice(0, 2).join(' '));
                    }
                });
                
                // 检查是否有 loading 状态
                const loadingEl = document.querySelector('.loading, [class*="loading"], [class*="wait"]');
                const isLoading = !!loadingEl;
                
                // 获取所有带data属性的元素（可能包含航班数据）
                const dataElements = [];
                document.querySelectorAll('[data-flight], [data-flightno], [data-price], [data-index]').forEach(el => {
                    if (dataElements.length < 20) {
                        dataElements.push({
                            tag: el.tagName,
                            class: el.className.split(' ').slice(0, 2).join(' '),
                            dataAttrs: Object.keys(el.dataset).slice(0, 5)
                        });
                    }
                });
                
                return { url, title, errorMsg, mainAreas, bodyInfo, flightClasses, isLoading, dataElements };
            })()"""
        )
        logger.info(f"页面信息: {page_info}")
        
        # 如果还在加载，等待一下再解析
        if page_info.get('isLoading'):
            logger.info("页面正在加载，等待...")
            time.sleep(3)
        
        # 智能等待：如果页面内容较短，多等待一会儿
        inner_length = page_info.get('bodyInfo', {}).get('innerHTML_length', 0)
        if inner_length < 250000:
            logger.info(f"页面内容较少({inner_length})，额外等待...")
            time.sleep(5)
        
        if page_info.get('errorMsg'):
            logger.warning(f"页面显示错误: {page_info.get('errorMsg')}")
            return []

        # 尝试多种航班列表选择器
        flight_items = page.evaluate(
            """(() => {
                // 去哪儿常见的航班列表选择器 - 更全面的选择器
                const containerSelectors = [
                    // 新版去哪儿 - 正确的类名
                    '.b-airfly',
                    '.m-airfly-lst .b-airfly',
                    '.e-airfly',
                    // 旧版可能的选择器
                    '.flight-item',
                    '.m-flight-item', 
                    '.b-airflight',
                    '[data-flight]',
                    '.flight-list .flight-item',
                    '.flight-list-item',
                    '.airflight',
                    '.flight-box',
                    'tr[data-flightno]',
                    // 通用
                    '[class*="flight"][class*="item"]',
                    '[class*="airflight"]',
                    // 更多选择器
                    '.flight-segment',
                    '.seg-item',
                    '.segitem',
                    '.flightSegment',
                    '[class*="FlightItem"]',
                    '[class*="flightItem"]',
                    '[class*="flightItem"]',
                    '[class*="FlightCard"]',
                    '[class*="flight-card"]',
                    '.list-item',
                    '.item-content',
                    '.flight',
                    '.air-line',
                    '.airline-item',
                    '[class*="airline"]',
                    '[class*="Item"][class*="flight"]',
                    'li[class*="flight"]',
                    'div[class*="flight"][class*="row"]',
                    'tr[class*="flight"]'
                ];
                
                let items = [];
                let usedSelector = '';
                for (const sel of containerSelectors) {
                    try {
                        const found = document.querySelectorAll(sel);
                        if (found.length > 0) {
                            items = found;
                            usedSelector = sel;
                            break;
                        }
                    } catch (e) {
                        // 忽略无效选择器
                    }
                }
                
                if (items.length === 0) {
                    // 记录页面结构用于调试
                    const bodyClasses = document.body.className;
                    const mainContent = document.querySelector('main, .main, .content, #content, .flight-container');
                    
                    // 尝试获取更多页面内容
                    const allClasses = [];
                    document.querySelectorAll('[class]').forEach(el => {
                        const cls = el.className.split(' ').filter(c => c.length > 0);
                        allClasses.push(...cls.slice(0, 3));
                    });
                    const uniqueClasses = [...new Set(allClasses)].slice(0, 50);
                    
                    return { 
                        error: '未找到航班列表', 
                        bodyClasses,
                        mainContentClass: mainContent?.className,
                        uniqueClasses,
                        sampleHTML: document.body.innerHTML.substring(0, 3000)
                    };
                }
                
                return Array.from(items).slice(0, 30).map(item => {
                    // 去哪儿新版选择器 - 航空公司
                    let airline = '';
                    const airEl = item.querySelector('.d-air .air span');
                    if (airEl) {
                        airline = airEl.innerText?.trim() || '';
                    } else {
                        // 旧版选择器
                        airline = item.querySelector('.airline-name, .flight-airline, .airline, .f-company, .com-name, [class*="airline"], .carrier')?.innerText?.trim() || '';
                    }
                    
                    // 去哪儿新版选择器 - 航班号
                    let flightNo = '';
                    const flightNoEl = item.querySelector('.d-air .num .n');
                    if (flightNoEl) {
                        flightNo = flightNoEl.innerText?.trim() || '';
                    } else {
                        flightNo = item.querySelector('.flight-no, .flight-number, .f-num, .flightNo, [class*="flightNo"], .flightnum')?.innerText?.trim() || '';
                    }
                    
                    // 去哪儿新版选择器 - 出发时间
                    let depTime = '';
                    const depTimeEl = item.querySelector('.sep-lf h2');
                    if (depTimeEl) {
                        depTime = depTimeEl.innerText?.trim() || '';
                    } else {
                        depTime = item.querySelector('.dep-time, .departure-time, .f-dpt, .dpt-time, [class*="dpt"], .depart-time')?.innerText?.trim() || '';
                    }
                    
                    // 去哪儿新版选择器 - 到达时间
                    let arrTime = '';
                    const arrTimeEl = item.querySelector('.sep-rt h2');
                    if (arrTimeEl) {
                        arrTime = arrTimeEl.innerText?.trim() || '';
                    } else {
                        arrTime = item.querySelector('.arr-time, .arrival-time, .f-arr, .arr-time, [class*="arr"], .arrive-time')?.innerText?.trim() || '';
                    }
                    
                    // 时长 - 去哪儿新版
                    let duration = '';
                    const durationEl = item.querySelector('.sep-ct .range');
                    if (durationEl) {
                        duration = durationEl.innerText?.trim() || '';
                    } else {
                        duration = item.querySelector('.duration, .flight-duration, .f-time, [class*="duration"], .fly-time')?.innerText?.trim() || '';
                    }
                    
                    // 价格 - 去哪儿使用字体反爬，真实价格在 <i> 标签的 title 属性中
                    let price = 0;
                    
                    // 方法1: 从 <i> 标签的 title 属性获取真实价格（字体反爬）
                    const priceContainer = item.querySelector('.col-price, .b-price, .e-price, .prc, [class*="price"]');
                    if (priceContainer) {
                        const iElements = priceContainer.querySelectorAll('i[title]');
                        if (iElements.length > 0) {
                            // 获取第一个 <i> 标签的 title 属性作为价格
                            const titlePrice = iElements[0].getAttribute('title');
                            if (titlePrice) {
                                price = parseFloat(titlePrice) || 0;
                            }
                        }
                    }
                    
                    // 方法2: 如果方法1失败，尝试从 b 标签的 title 属性获取
                    if (price === 0) {
                        const bWithTitle = item.querySelector('b[title]');
                        if (bWithTitle) {
                            const titlePrice = bWithTitle.getAttribute('title');
                            if (titlePrice) {
                                price = parseFloat(titlePrice) || 0;
                            }
                        }
                    }
                    
                    // 方法3: 兜底方案 - 从 innerText 获取（可能不准确）
                    if (price === 0) {
                        const priceSelectors = [
                            '.col-price .price em', '.col-price em', '.b-price em',
                            '.e-price em', '.prc em',
                            '.price em', '.b-price', '.flight-price em', 
                            '.f-price', '.price', '[class*="price"] em',
                            '.sale-price', '.low-price', '.em_price'
                        ];
                        for (const sel of priceSelectors) {
                            const priceEl = item.querySelector(sel);
                            if (priceEl) {
                                const priceText = priceEl.innerText?.trim() || '';
                                if (priceText) {
                                    price = parseFloat(priceText.replace(/[^0-9.]/g, '')) || 0;
                                    if (price > 0) break;
                                }
                            }
                        }
                    }
                    
                    // 去哪儿新版选择器 - 出发机场
                    let depAirport = '';
                    const depAirportEl = item.querySelector('.sep-lf .airport span');
                    if (depAirportEl) {
                        depAirport = depAirportEl.innerText?.trim() || '';
                    } else {
                        depAirport = item.querySelector('.dep-airport, .departure-airport, .f-dpt-airport, [class*="depAirport"], .from-airport')?.innerText?.trim() || '';
                    }
                    
                    // 去哪儿新版选择器 - 到达机场
                    let arrAirport = '';
                    const arrAirportEl = item.querySelector('.sep-rt .airport span');
                    if (arrAirportEl) {
                        arrAirport = arrAirportEl.innerText?.trim() || '';
                    } else {
                        arrAirport = item.querySelector('.arr-airport, .arrival-airport, .f-arr-airport, [class*="arrAirport"], .to-airport')?.innerText?.trim() || '';
                    }
                    
                    // 去哪儿新版选择器 - 中转信息
                    let transferInfo = '';
                    const transferEl = item.querySelector('.trans .g-up-tips .t');
                    if (transferEl) {
                        transferInfo = transferEl.innerText?.trim() || '';
                    } else {
                        const oldTransferEl = item.querySelector('.transfer, .stopover, .trans, [class*="trans"], .stop');
                        transferInfo = oldTransferEl ? oldTransferEl.innerText?.trim() : '';
                    }
                    const isDirect = !transferInfo || transferInfo === '';
                    
                    return { 
                        airline, flightNo, departure_time: depTime, arrival_time: arrTime, 
                        duration, price, departure_airport: depAirport, arrival_airport: arrAirport, 
                        is_direct: isDirect, transfer_info: transferInfo 
                    };
                });
            })()"""
        )

        # 处理返回结果
        if isinstance(flight_items, dict) and flight_items.get('error'):
            logger.warning(f"解析问题: {flight_items.get('error')}")
            logger.debug(f"页面class列表: {flight_items.get('uniqueClasses')}")
        elif flight_items:
            for item in flight_items:
                if isinstance(item, dict) and item.get("price", 0) > 0:
                    results.append(item)

        logger.info(f"去哪儿解析到 {len(results)} 个航班")
        return results

    def check_login(self, page) -> bool:
        """检查去哪儿登录状态
        
        检测逻辑：
        1. 检查页面是否有"登录"按钮/链接（有则未登录）
        2. 检查是否有用户信息（手机号、用户名等）
        3. 检查 cookie 中是否有登录凭证
        """
        try:
            # 等待页面加载
            time.sleep(1)
            
            result = page.evaluate(
                """(() => {
                    const debug = [];
                    
                    // 方法1: 检查 cookies 中是否有登录信息
                    const cookies = document.cookie;
                    debug.push('cookies length: ' + cookies.length);
                    
                    // 去哪儿登录相关的 cookie
                    const loginCookies = ['QN1', 'QN2', 'QN5', 'QN277', '_vi', '_q', '_t'];
                    let hasLoginCookie = false;
                    for (const ck of loginCookies) {
                        if (cookies.includes(ck + '=')) {
                            debug.push('found cookie: ' + ck);
                            hasLoginCookie = true;
                        }
                    }
                    
                    // 方法2: 检查 localStorage 中的登录信息
                    try {
                        const userInfo = localStorage.getItem('userInfo') || localStorage.getItem('_user');
                        if (userInfo) {
                            debug.push('found localStorage userInfo');
                            return { result: true, debug };
                        }
                    } catch (e) {}
                    
                    // 方法3: 检查是否有登录按钮（有则未登录）
                    const allLinks = document.querySelectorAll('a, button, span');
                    let foundLoginBtn = false;
                    for (const el of allLinks) {
                        const text = (el.innerText || '').trim();
                        // 精确匹配"登录"按钮，排除"登录后查看"等
                        if (text === '登录' || text === '请登录') {
                            debug.push('found login button: "' + text + '"');
                            foundLoginBtn = true;
                            break;
                        }
                    }
                    if (foundLoginBtn) {
                        return { result: false, debug };
                    }
                    
                    // 方法4: 检查是否有用户名或手机号显示
                    const bodyText = document.body.innerText || '';
                    const phoneMatch = bodyText.match(/1[3-9]\\d{9}/);
                    if (phoneMatch) {
                        const phone = phoneMatch[0];
                        // 排除页面上的示例手机号（通常在登录提示区域）
                        const loginArea = document.querySelector('.login-panel, .passport-content, .user-login');
                        if (!loginArea) {
                            debug.push('found phone in page: ' + phone);
                            return { result: true, debug };
                        }
                    }
                    
                    // 方法5: 检查是否有"退出"按钮（有则已登录）
                    for (const el of allLinks) {
                        const text = (el.innerText || '').trim();
                        if (text.includes('退出') || text === '注销' || text.includes('退出登录')) {
                            debug.push('found logout button: ' + text);
                            return { result: true, debug };
                        }
                    }
                    
                    // 方法6: 检查页面右上角用户区域
                    const userArea = document.querySelector('.user-area, .header-right, .top-right, .login-status, .user-status');
                    if (userArea) {
                        const userText = userArea.innerText || '';
                        debug.push('userArea text: ' + userText.substring(0, 50));
                        // 如果用户区域不包含"登录"字样，说明已登录
                        if (!userText.includes('登录') && !userText.includes('注册') && userText.length > 0) {
                            return { result: true, debug };
                        }
                    }
                    
                    // 方法7: 检查是否有"我的"相关链接
                    for (const el of allLinks) {
                        const text = (el.innerText || '').trim();
                        if (text.includes('我的订单') || text.includes('我的机票') || text.includes('个人中心')) {
                            debug.push('found my-page link: ' + text);
                            return { result: true, debug };
                        }
                    }
                    
                    // 如果有登录 cookie 但没找到登录按钮，认为已登录
                    if (hasLoginCookie && !foundLoginBtn) {
                        debug.push('has login cookies, no login button, assume logged in');
                        return { result: true, debug };
                    }
                    
                    debug.push('no login indicators found');
                    return { result: false, debug };
                })()"""
            )
            
            if isinstance(result, dict):
                login_status = result.get('result', False)
                debug_info = result.get('debug', [])
                logger.info(f"登录检测结果: {login_status}, 调试信息: {debug_info}")
            else:
                login_status = bool(result)
                logger.info(f"登录检测结果: {login_status}")
            
            if login_status:
                logger.info("去哪儿已登录")
            else:
                logger.info("去哪儿未登录")
            
            return login_status
        except Exception as e:
            logger.warning(f"检查登录状态失败: {e}")
            return False



class CtripHandler(PlatformHandler):
    """携程平台处理器
    
    注意：此平台不会持续更新适配，仅提供基础支持。
    如遇问题，建议使用去哪儿平台。
    """

    name = "携程"
    url = "https://flights.ctrip.com/"
    login_url = "https://passport.ctrip.com/user/login"
    cookie_domain = "ctrip.com"

    def search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """搜索携程航班"""
        # 尝试加载本地 cookie
        logger.info("尝试加载本地 cookie...")
        self._load_cookies_from_file(page)
        
        # 导航到首页
        page.navigate(self.url)
        page.wait_for_load()
        time.sleep(2)

        return self._do_search(page, departure_city, arrival_city, date)

    def search_without_navigation(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """在已导航的页面上搜索"""
        return self._do_search(page, departure_city, arrival_city, date)

    def _do_search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """执行搜索"""
        time.sleep(2)  # 等待页面完全加载
        
        # 尝试点击单程选项
        logger.info("选择单程选项")
        try:
            # 携程的单程选择器
            page.evaluate(
                """(() => {
                    // 尝试多种方式点击单程
                    const selectors = [
                        '.radio-label input[value="single"]',
                        'input[name="flightType"][value="1"]',
                        '.flight-type-item.oneway',
                        '[data-flighttype="oneway"]',
                        '.single-trip'
                    ];
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el) { el.click(); return; }
                    }
                    // 查找包含"单程"文字的元素
                    const allElements = document.querySelectorAll('label, span, div, a');
                    for (const el of allElements) {
                        if (el.innerText === '单程') {
                            el.click();
                            return;
                        }
                    }
                })()"""
            )
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"点击单程选项失败: {e}")

        # 输入出发城市
        logger.info(f"输入出发城市: {departure_city}")
        try:
            # 先找到出发城市输入框
            dep_input = page.evaluate(
                f"""(() => {{
                    const selectors = [
                        'input[name="owDCity"]',
                        'input[placeholder*="出发"]',
                        'input[placeholder*="请输入出发地"]',
                        '.form-input-v3[name="owDCity"]',
                        '#flt_fromText',
                        '.dep-city input'
                    ];
                    for (const selector of selectors) {{
                        const el = document.querySelector(selector);
                        if (el) return selector;
                    }}
                    return null;
                }})()"""
            )
            
            if dep_input:
                page.click_element(dep_input)
                time.sleep(0.3)
                # 清空并输入
                page.evaluate(
                    f"""(() => {{
                        const el = document.querySelector({json.dumps(dep_input)});
                        if (el) {{
                            el.value = '';
                            el.focus();
                            el.value = {json.dumps(departure_city)};
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }})()"""
                )
                time.sleep(0.8)
                # 点击下拉选项
                page.evaluate(
                    """(() => {
                        const options = document.querySelectorAll('.city-suggest li, .ui-citysuggest li, .suggest-item, .city-item');
                        if (options.length > 0) options[0].click();
                    })()"""
                )
                time.sleep(0.5)
        except Exception as e:
            logger.warning(f"输入出发城市失败: {e}")

        # 输入到达城市
        logger.info(f"输入到达城市: {arrival_city}")
        try:
            arr_input = page.evaluate(
                f"""(() => {{
                    const selectors = [
                        'input[name="owACity"]',
                        'input[placeholder*="到达"]',
                        'input[placeholder*="请输入目的地"]',
                        '.form-input-v3[name="owACity"]',
                        '#flt_toText',
                        '.arr-city input'
                    ];
                    for (const selector of selectors) {{
                        const el = document.querySelector(selector);
                        if (el) return selector;
                    }}
                    return null;
                }})()"""
            )
            
            if arr_input:
                page.click_element(arr_input)
                time.sleep(0.3)
                page.evaluate(
                    f"""(() => {{
                        const el = document.querySelector({json.dumps(arr_input)});
                        if (el) {{
                            el.value = '';
                            el.focus();
                            el.value = {json.dumps(arrival_city)};
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }})()"""
                )
                time.sleep(0.8)
                # 点击下拉选项
                page.evaluate(
                    """(() => {
                        const options = document.querySelectorAll('.city-suggest li, .ui-citysuggest li, .suggest-item, .city-item');
                        if (options.length > 0) options[0].click();
                    })()"""
                )
                time.sleep(0.5)
        except Exception as e:
            logger.warning(f"输入到达城市失败: {e}")

        # 输入日期
        logger.info(f"输入日期: {date}")
        try:
            date_input = page.evaluate(
                f"""(() => {{
                    const selectors = [
                        'input[name="date"]',
                        'input[placeholder*="日期"]',
                        'input[placeholder*="yyyy-mm-dd"]',
                        '.date-input input',
                        '#flt_date'
                    ];
                    for (const selector of selectors) {{
                        const el = document.querySelector(selector);
                        if (el) return selector;
                    }}
                    return null;
                }})()"""
            )
            
            if date_input:
                page.click_element(date_input)
                time.sleep(0.3)
                page.evaluate(
                    f"""(() => {{
                        const el = document.querySelector({json.dumps(date_input)});
                        if (el) {{
                            el.value = {json.dumps(date)};
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }})()"""
                )
                time.sleep(0.5)
        except Exception as e:
            logger.warning(f"输入日期失败: {e}")

        # 点击搜索按钮
        logger.info("点击搜索按钮")
        try:
            page.evaluate(
                """(() => {
                    const selectors = [
                        '.search-btn',
                        'button[type="submit"]',
                        '.btn-search',
                        '#flt_search',
                        'button:contains("搜索")'
                    ];
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el) { el.click(); return; }
                    }
                    // 查找包含"搜索"文字的按钮
                    const allBtns = document.querySelectorAll('button, a.btn');
                    for (const btn of allBtns) {
                        if (btn.innerText.includes('搜索')) {
                            btn.click();
                            return;
                        }
                    }
                })()"""
            )
        except Exception as e:
            logger.warning(f"点击搜索按钮失败: {e}")

        # 等待结果加载
        logger.info("等待搜索结果...")
        time.sleep(5)
        try:
            page.wait_for_element(
                ".flight-list, .flight-item, .search-result, .flight-row, [class*='flight']", 
                timeout=20
            )
        except Exception:
            logger.warning("等待结果超时")
        time.sleep(2)

        # 解析结果
        return self._parse_results(page)

    def _parse_results(self, page) -> list[dict]:
        """解析搜索结果"""
        results = []

        flight_items = page.evaluate(
            """(() => {
                // 尝试多种选择器组合
                const itemSelectors = [
                    '.flight-list .flight-item',
                    '.search-result .flight-row',
                    '[class*="flight-item"]',
                    '[class*="FlightItem"]',
                    '.flight-card',
                    'tr[class*="flight"]'
                ];
                
                let items = [];
                for (const selector of itemSelectors) {
                    const found = document.querySelectorAll(selector);
                    if (found.length > items.length) {
                        items = found;
                    }
                }
                
                if (items.length === 0) {
                    // 尝试更通用的方式查找航班元素
                    const allDivs = document.querySelectorAll('div, li, tr');
                    const flightDivs = [];
                    for (const div of allDivs) {
                        // 检查是否包含价格元素
                        const priceEl = div.querySelector('[class*="price"]');
                        if (priceEl && div.innerText.includes(':')) {
                            flightDivs.push(div);
                        }
                    }
                    if (flightDivs.length > 0) {
                        items = flightDivs;
                    }
                }
                
                return Array.from(items).slice(0, 20).map(item => {
                    // 尝试多种选择器提取信息
                    const getText = (selectors) => {
                        for (const s of selectors) {
                            const el = item.querySelector(s);
                            if (el && el.innerText) return el.innerText.trim();
                        }
                        return '';
                    };
                    
                    const airline = getText(['.airline-name', '.flight-airline', '[class*="airline"]', '[class*="Airline"]']);
                    const flightNo = getText(['.flight-no', '.flight-number', '[class*="flightNo"]', '[class*="flight-no"]']);
                    const depTime = getText(['.dep-time', '.departure-time', '[class*="depTime"]', '[class*="depart"]']);
                    const arrTime = getText(['.arr-time', '.arrival-time', '[class*="arrTime"]', '[class*="arrive"]']);
                    const duration = getText(['.duration', '.flight-duration', '[class*="duration"]']);
                    
                    // 价格提取 - 尝试多种方式
                    let price = 0;
                    const priceSelectors = ['.price', '.flight-price em', '[class*="price"]', '[class*="Price"]'];
                    for (const s of priceSelectors) {
                        const el = item.querySelector(s);
                        if (el) {
                            const text = el.innerText || '';
                            const match = text.match(/\\d+/);
                            if (match) {
                                price = parseFloat(match[0]);
                                if (price > 0) break;
                            }
                        }
                    }
                    
                    const depAirport = getText(['.dep-airport', '.departure-airport', '[class*="depAirport"]']);
                    const arrAirport = getText(['.arr-airport', '.arrival-airport', '[class*="arrAirport"]']);
                    const isDirect = !item.querySelector('.transfer, .stopover, [class*="transfer"]');
                    const transferInfo = getText(['.transfer', '.stopover', '[class*="transfer"]']);
                    
                    return { 
                        airline, flightNo, departure_time: depTime, arrival_time: arrTime, 
                        duration, price, departure_airport: depAirport, arrival_airport: arrAirport, 
                        is_direct: isDirect, transfer_info: transferInfo 
                    };
                });
            })()"""
        )

        if flight_items:
            for item in flight_items:
                if item.get("price", 0) > 0:
                    results.append(item)

        logger.info(f"携程解析到 {len(results)} 个航班")
        return results

    def check_login(self, page) -> bool:
        """检查携程登录状态"""
        try:
            has_user = page.evaluate(
                """(() => {
                    return document.querySelector('.user-name, .user-info, .login-user') !== null;
                })()"""
            )
            return has_user
        except Exception:
            return False


class FliggyHandler(PlatformHandler):
    """飞猪平台处理器
    
    注意：此平台不会持续更新适配，仅提供基础支持。
    如遇问题，建议使用去哪儿平台。
    """

    name = "飞猪"
    url = "https://flight.fliggy.com/"
    login_url = "https://login.fliggy.com/"
    cookie_domain = "fliggy.com"

    def search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """搜索飞猪航班"""
        # 尝试加载本地 cookie
        logger.info("尝试加载本地 cookie...")
        self._load_cookies_from_file(page)
        
        # 导航到首页
        page.navigate(self.url)
        page.wait_for_load()
        time.sleep(2)

        return self._do_search(page, departure_city, arrival_city, date)

    def search_without_navigation(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """在已导航的页面上搜索"""
        return self._do_search(page, departure_city, arrival_city, date)

    def _do_search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """执行搜索"""
        # 选择单程
        page.evaluate(
            """(() => {
                const singleBtn = document.querySelector('.tab-item[data-type="single"], .search-type .single');
                if (singleBtn) singleBtn.click();
            })()"""
        )
        time.sleep(0.5)

        # 输入出发城市
        dep_selectors = [
            '#fromCity',
            'input[placeholder*="出发"]',
            '.dep-city input',
        ]
        for selector in dep_selectors:
            try:
                if page.has_element(selector):
                    page.click_element(selector)
                    time.sleep(0.3)
                    page.evaluate(
                        f"""(() => {{
                            const el = document.querySelector({json.dumps(selector)});
                            if (el) {{
                                el.value = {json.dumps(departure_city)};
                                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }})()"""
                    )
                    time.sleep(0.5)
                    page.evaluate(
                        """(() => {
                            const item = document.querySelector('.city-list li, .suggest-item');
                            if (item) item.click();
                        })()"""
                    )
                    time.sleep(0.3)
                    break
            except Exception:
                continue

        # 输入到达城市
        arr_selectors = [
            '#toCity',
            'input[placeholder*="到达"]',
            '.arr-city input',
        ]
        for selector in arr_selectors:
            try:
                if page.has_element(selector):
                    page.click_element(selector)
                    time.sleep(0.3)
                    page.evaluate(
                        f"""(() => {{
                            const el = document.querySelector({json.dumps(selector)});
                            if (el) {{
                                el.value = {json.dumps(arrival_city)};
                                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }})()"""
                    )
                    time.sleep(0.5)
                    page.evaluate(
                        """(() => {
                            const item = document.querySelector('.city-list li, .suggest-item');
                            if (item) item.click();
                        })()"""
                    )
                    time.sleep(0.3)
                    break
            except Exception:
                continue

        # 输入日期
        date_selectors = [
            '#depDate',
            'input[placeholder*="日期"]',
            '.date-input input',
        ]
        for selector in date_selectors:
            try:
                if page.has_element(selector):
                    page.click_element(selector)
                    time.sleep(0.3)
                    page.evaluate(
                        f"""(() => {{
                            const el = document.querySelector({json.dumps(selector)});
                            if (el) {{
                                el.value = {json.dumps(date)};
                                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }})()"""
                    )
                    time.sleep(0.3)
                    break
            except Exception:
                continue

        # 点击搜索
        page.evaluate(
            """(() => {
                const btn = document.querySelector('.search-btn, #searchBtn, button[type="submit"]');
                if (btn) btn.click();
            })()"""
        )
        time.sleep(3)

        # 等待结果加载
        try:
            page.wait_for_element(
                ".flight-list, .flight-item, .result-list", timeout=15
            )
        except Exception:
            pass
        time.sleep(2)

        # 解析结果
        return self._parse_results(page)

    def _parse_results(self, page) -> list[dict]:
        """解析搜索结果"""
        results = []

        flight_items = page.evaluate(
            """(() => {
                const items = document.querySelectorAll('.flight-list .flight-item, .result-list .flight-row');
                return Array.from(items).slice(0, 20).map(item => {
                    const airline = item.querySelector('.airline-name, .flight-airline')?.innerText?.trim() || '';
                    const flightNo = item.querySelector('.flight-no, .flight-number')?.innerText?.trim() || '';
                    const depTime = item.querySelector('.dep-time, .departure-time')?.innerText?.trim() || '';
                    const arrTime = item.querySelector('.arr-time, .arrival-time')?.innerText?.trim() || '';
                    const duration = item.querySelector('.duration, .flight-duration')?.innerText?.trim() || '';
                    const priceText = item.querySelector('.price, .flight-price em')?.innerText?.trim() || '0';
                    const price = parseFloat(priceText.replace(/[^0-9.]/g, '')) || 0;
                    const depAirport = item.querySelector('.dep-airport, .departure-airport')?.innerText?.trim() || '';
                    const arrAirport = item.querySelector('.arr-airport, .arrival-airport')?.innerText?.trim() || '';
                    const isDirect = !item.querySelector('.transfer, .stopover');
                    const transferInfo = item.querySelector('.transfer, .stopover')?.innerText?.trim() || '';
                    
                    return { airline, flightNo, departure_time: depTime, arrival_time: arrTime, duration, price, departure_airport: depAirport, arrival_airport: arrAirport, is_direct: isDirect, transfer_info: transferInfo };
                });
            })()"""
        )

        if flight_items:
            for item in flight_items:
                if item.get("price", 0) > 0:
                    results.append(item)

        logger.info(f"飞猪解析到 {len(results)} 个航班")
        return results

    def check_login(self, page) -> bool:
        """检查飞猪登录状态"""
        try:
            has_user = page.evaluate(
                """(() => {
                    return document.querySelector('.user-name, .member-name, .login-user') !== null;
                })()"""
            )
            return has_user
        except Exception:
            return False


class LyHandler(PlatformHandler):
    """同程平台处理器
    
    注意：此平台不会持续更新适配，仅提供基础支持。
    如遇问题，建议使用去哪儿平台。
    """

    name = "同程"
    url = "https://www.ly.com/"
    login_url = "https://www.ly.com/user/login"
    cookie_domain = "ly.com"

    def search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """搜索同程航班"""
        # 尝试加载 cookie
        logger.info("尝试加载本地 cookie...")
        self._load_cookies_from_file(page)
        
        # 导航到机票首页
        page.navigate("https://www.ly.com/flight/")
        page.wait_for_load()
        time.sleep(2)

        return self._do_search(page, departure_city, arrival_city, date)

    def search_without_navigation(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """在已导航的页面上搜索"""
        return self._do_search(page, departure_city, arrival_city, date)

    def _do_search(
        self, page, departure_city: str, arrival_city: str, date: str
    ) -> list[dict]:
        """执行搜索"""
        # 选择单程
        page.evaluate(
            """(() => {
                const singleBtn = document.querySelector('.search-type .single, [data-type="oneWay"]');
                if (singleBtn) singleBtn.click();
            })()"""
        )
        time.sleep(0.5)

        # 输入出发城市
        dep_selectors = [
            '#txtFromCity',
            'input[placeholder*="出发"]',
            '.dep-city input',
        ]
        for selector in dep_selectors:
            try:
                if page.has_element(selector):
                    page.click_element(selector)
                    time.sleep(0.3)
                    page.evaluate(
                        f"""(() => {{
                            const el = document.querySelector({json.dumps(selector)});
                            if (el) {{
                                el.value = {json.dumps(departure_city)};
                                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }})()"""
                    )
                    time.sleep(0.5)
                    page.evaluate(
                        """(() => {
                            const item = document.querySelector('.city-list li, .suggest-item');
                            if (item) item.click();
                        })()"""
                    )
                    time.sleep(0.3)
                    break
            except Exception:
                continue

        # 输入到达城市
        arr_selectors = [
            '#txtToCity',
            'input[placeholder*="到达"]',
            '.arr-city input',
        ]
        for selector in arr_selectors:
            try:
                if page.has_element(selector):
                    page.click_element(selector)
                    time.sleep(0.3)
                    page.evaluate(
                        f"""(() => {{
                            const el = document.querySelector({json.dumps(selector)});
                            if (el) {{
                                el.value = {json.dumps(arrival_city)};
                                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }})()"""
                    )
                    time.sleep(0.5)
                    page.evaluate(
                        """(() => {
                            const item = document.querySelector('.city-list li, .suggest-item');
                            if (item) item.click();
                        })()"""
                    )
                    time.sleep(0.3)
                    break
            except Exception:
                continue

        # 输入日期
        date_selectors = [
            '#txtDepartDate',
            'input[placeholder*="日期"]',
            '.date-input input',
        ]
        for selector in date_selectors:
            try:
                if page.has_element(selector):
                    page.click_element(selector)
                    time.sleep(0.3)
                    page.evaluate(
                        f"""(() => {{
                            const el = document.querySelector({json.dumps(selector)});
                            if (el) {{
                                el.value = {json.dumps(date)};
                                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }})()"""
                    )
                    time.sleep(0.3)
                    break
            except Exception:
                continue

        # 点击搜索
        page.evaluate(
            """(() => {
                const btn = document.querySelector('.search-btn, #btnSearch, button[type="submit"]');
                if (btn) btn.click();
            })()"""
        )
        time.sleep(3)

        # 等待结果加载
        try:
            page.wait_for_element(
                ".flight-list, .flight-item, .result-list", timeout=15
            )
        except Exception:
            pass
        time.sleep(2)

        # 解析结果
        return self._parse_results(page)

    def _parse_results(self, page) -> list[dict]:
        """解析搜索结果"""
        results = []

        flight_items = page.evaluate(
            """(() => {
                const items = document.querySelectorAll('.flight-list .flight-item, .result-list .flight-row');
                return Array.from(items).slice(0, 20).map(item => {
                    const airline = item.querySelector('.airline-name, .flight-airline')?.innerText?.trim() || '';
                    const flightNo = item.querySelector('.flight-no, .flight-number')?.innerText?.trim() || '';
                    const depTime = item.querySelector('.dep-time, .departure-time')?.innerText?.trim() || '';
                    const arrTime = item.querySelector('.arr-time, .arrival-time')?.innerText?.trim() || '';
                    const duration = item.querySelector('.duration, .flight-duration')?.innerText?.trim() || '';
                    const priceText = item.querySelector('.price, .flight-price em')?.innerText?.trim() || '0';
                    const price = parseFloat(priceText.replace(/[^0-9.]/g, '')) || 0;
                    const depAirport = item.querySelector('.dep-airport, .departure-airport')?.innerText?.trim() || '';
                    const arrAirport = item.querySelector('.arr-airport, .arrival-airport')?.innerText?.trim() || '';
                    const isDirect = !item.querySelector('.transfer, .stopover');
                    const transferInfo = item.querySelector('.transfer, .stopover')?.innerText?.trim() || '';
                    
                    return { airline, flightNo, departure_time: depTime, arrival_time: arrTime, duration, price, departure_airport: depAirport, arrival_airport: arrAirport, is_direct: isDirect, transfer_info: transferInfo };
                });
            })()"""
        )

        if flight_items:
            for item in flight_items:
                if item.get("price", 0) > 0:
                    results.append(item)

        logger.info(f"同程解析到 {len(results)} 个航班")
        return results

    def check_login(self, page) -> bool:
        """检查同程登录状态"""
        try:
            has_user = page.evaluate(
                """(() => {
                    return document.querySelector('.user-name, .login-user, .member-info') !== null;
                })()"""
            )
            return has_user
        except Exception:
            return False


# 平台注册表
PLATFORMS: dict[str, type[PlatformHandler]] = {
    "qunar": QunarHandler,
    "ctrip": CtripHandler,
    "fliggy": FliggyHandler,
    "ly": LyHandler,
}


def get_platform_handler(platform: str) -> Optional[PlatformHandler]:
    """获取平台处理器实例

    Args:
        platform: 平台名称 (qunar, ctrip, fliggy, ly)

    Returns:
        平台处理器实例，如果平台不支持则返回 None
    """
    handler_class = PLATFORMS.get(platform.lower())
    if handler_class:
        return handler_class()
    return None
