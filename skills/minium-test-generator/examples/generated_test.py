# -*- coding: utf-8 -*-
"""
示例测试用例 - 通用模板
生成时间：2026-03-23
录制脚本：FirstTest.minium

说明：这是一个通用示例，展示如何使用生成器技能
实际使用时请替换为你自己的页面类和测试逻辑
"""

from base.basepage import BasePage
from base.basedef import BaseDef
from pages.pages.home.home import Home
from pages.pages.detail.detail import Detail
from time import sleep


class TestExample(BasePage):
    """示例测试用例类"""

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.Home = Home(self)
        self.Detail = Detail(self)

    def test_example_flow(self):
        """
        示例测试流程
        
        录制脚本步骤：X 步（一个不漏）
        
        流程说明:
            step_1: 首页操作
            step_2-5: 详情页操作
            step_6-10: 表单填写和提交
        """
        
        # ========== step_1: 首页 - 打开页面 ==========
        self.Home.goto_page()
        
        # ========== step_2-5: 详情页 - 完整流程 ==========
        self.Detail.fill_form_and_submit()
        
        # ========== step_6-10: 提交后操作 ==========
        # 根据实际业务逻辑编写
        
        self.logger.info("示例流程执行完成")
