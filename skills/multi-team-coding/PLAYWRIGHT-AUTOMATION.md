# Playwright 自动化测试集成

基于 Claude Code + Playwright CLI 实现端到端测试自动化。

## 核心优势

### 1. 效率对比

| 方案 | Token 消耗 | 上下文管理 | 并行支持 |
|------|-----------|-----------|---------|
| Playwright CLI | ~26K | 磁盘持久化 | ✅ |
| Playwright MCP | ~114K | 内存占用 | ❌ |
| Chrome 扩展 | 不稳定 | 无 | ❌ |

**结论**：Playwright CLI 是最优选择

### 2. 关键特性

- **无头模式**：后台运行，不占用屏幕
- **并行会话**：同时运行多个测试
- **持久化登录**：保存认证状态，避免重复登录
- **可访问性树**：基于 DOM 结构，比截图更可靠

## 快速开始

### 安装 Playwright CLI

```bash
# 安装 Playwright
npm install -D @playwright/test

# 安装浏览器
npx playwright install

# 验证安装
npx playwright --version
```

### 配置 Claude Code

```bash
# 在项目根目录创建配置
cat > playwright.config.ts << 'EOF'
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
EOF
```

## 集成到多团队工作流

### 1. 自动生成测试

当 Claude Code 完成功能开发后，自动生成 E2E 测试：

```bash
# 在 claude-code-teams.sh 中添加
generate_e2e_tests() {
  local issue_num=$1
  local feature_name=$2
  
  echo "🧪 为 #$issue_num 生成 E2E 测试..."
  
  # 使用 Claude Code 生成测试
  bash pty:true command:"claude '
【任务】为以下功能生成 Playwright E2E 测试

功能: $feature_name
Issue: #$issue_num

【要求】
1. 使用 Playwright Test 框架
2. 测试关键用户流程
3. 包含正常和异常场景
4. 使用 Page Object Model 模式
5. 添加清晰的测试描述

【测试文件位置】
tests/e2e/${feature_name}.spec.ts

【示例结构】
\`\`\`typescript
import { test, expect } from \"@playwright/test\";

test.describe(\"$feature_name\", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(\"/\");
  });

  test(\"should complete main user flow\", async ({ page }) => {
    // 测试步骤
  });

  test(\"should handle error cases\", async ({ page }) => {
    // 错误处理测试
  });
});
\`\`\`

【完成后】
git add tests/e2e/${feature_name}.spec.ts
git commit -m \"test(#$issue_num): add E2E tests for $feature_name\"
'"
}
```

### 2. 并行运行测试

```bash
# 在多个浏览器中并行测试
run_parallel_tests() {
  echo "🚀 并行运行 E2E 测试..."
  
  # 运行所有测试（自动并行）
  npx playwright test --workers=4
  
  # 生成报告
  npx playwright show-report
}
```

### 3. 持久化登录状态

```bash
# 保存认证状态
save_auth_state() {
  echo "🔐 保存认证状态..."
  
  bash pty:true command:"claude '
【任务】创建认证状态保存脚本

【要求】
1. 使用 Playwright 登录应用
2. 保存认证状态到 auth.json
3. 在测试中复用认证状态

【实现】
\`\`\`typescript
// tests/auth.setup.ts
import { test as setup } from \"@playwright/test\";

const authFile = \"playwright/.auth/user.json\";

setup(\"authenticate\", async ({ page }) => {
  await page.goto(\"/login\");
  await page.fill(\"input[name=email]\", process.env.TEST_USER_EMAIL);
  await page.fill(\"input[name=password]\", process.env.TEST_USER_PASSWORD);
  await page.click(\"button[type=submit]\");
  
  await page.waitForURL(\"/dashboard\");
  await page.context().storageState({ path: authFile });
});
\`\`\`

【配置】
在 playwright.config.ts 中添加：
\`\`\`typescript
export default defineConfig({
  projects: [
    { name: \"setup\", testMatch: /.*\\.setup\\.ts/ },
    {
      name: \"chromium\",
      use: { 
        ...devices[\"Desktop Chrome\"],
        storageState: \"playwright/.auth/user.json\",
      },
      dependencies: [\"setup\"],
    },
  ],
});
\`\`\`
'"
}
```

## 完整工作流示例

### 场景：电商网站测试

```bash
#!/bin/bash
# e2e-test-workflow.sh

PROJECT_ROOT=$(pwd)

echo "🛒 电商网站 E2E 测试工作流"
echo ""

# 1. 生成测试用例
echo "📝 生成测试用例..."
bash pty:true command:"claude '
【任务】为电商网站生成完整的 E2E 测试套件

【测试场景】
1. 用户注册和登录
2. 浏览商品列表
3. 搜索商品
4. 添加到购物车
5. 结账流程
6. 订单确认

【要求】
- 使用 Page Object Model
- 每个场景独立测试文件
- 包含正常和异常流程
- 添加截图和视频录制
- 生成详细的测试报告

【文件结构】
tests/
  ├── e2e/
  │   ├── auth.spec.ts
  │   ├── products.spec.ts
  │   ├── cart.spec.ts
  │   └── checkout.spec.ts
  └── pages/
      ├── LoginPage.ts
      ├── ProductsPage.ts
      ├── CartPage.ts
      └── CheckoutPage.ts
'"

# 2. 并行运行测试
echo ""
echo "🚀 并行运行测试（4 个 worker）..."
npx playwright test --workers=4 --reporter=html,json

# 3. 生成报告
echo ""
echo "📊 生成测试报告..."
npx playwright show-report

# 4. 检查结果
if [ $? -eq 0 ]; then
  echo "✅ 所有测试通过"
else
  echo "❌ 部分测试失败，查看报告"
  exit 1
fi
```

## 高级特性

### 1. 视觉回归测试

```typescript
// tests/visual/homepage.spec.ts
import { test, expect } from '@playwright/test';

test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  
  // 截图对比
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100,
  });
});
```

### 2. API 测试集成

```typescript
// tests/api/products.spec.ts
import { test, expect } from '@playwright/test';

test('API: get products', async ({ request }) => {
  const response = await request.get('/api/products');
  expect(response.ok()).toBeTruthy();
  
  const products = await response.json();
  expect(products).toHaveLength(10);
});
```

### 3. 移动端测试

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
});
```

### 4. 性能测试

```typescript
// tests/performance/load-time.spec.ts
import { test, expect } from '@playwright/test';

test('page load time', async ({ page }) => {
  const startTime = Date.now();
  await page.goto('/');
  const loadTime = Date.now() - startTime;
  
  expect(loadTime).toBeLessThan(3000); // 3 秒内加载
});
```

## 集成到 CI/CD

### GitHub Actions

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Run E2E tests
        run: npx playwright test
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

## 最佳实践

### 1. 测试组织

```
tests/
├── e2e/              # 端到端测试
│   ├── auth/
│   ├── products/
│   └── checkout/
├── pages/            # Page Objects
├── fixtures/         # 测试数据
└── utils/            # 辅助函数
```

### 2. 命名规范

```typescript
// ✅ 好的命名
test('user can complete checkout with valid credit card', async ({ page }) => {
  // ...
});

// ❌ 不好的命名
test('test1', async ({ page }) => {
  // ...
});
```

### 3. 等待策略

```typescript
// ✅ 使用内置等待
await page.click('button');
await page.waitForURL('/dashboard');

// ❌ 避免硬编码延迟
await page.click('button');
await page.waitForTimeout(5000);
```

### 4. 错误处理

```typescript
test('handle network errors gracefully', async ({ page }) => {
  // 模拟网络错误
  await page.route('**/api/products', route => route.abort());
  
  await page.goto('/products');
  
  // 验证错误提示
  await expect(page.locator('.error-message')).toBeVisible();
});
```

## 性能优化

### 1. 复用浏览器上下文

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    // 复用浏览器实例
    launchOptions: {
      args: ['--disable-dev-shm-usage'],
    },
  },
});
```

### 2. 并行执行

```bash
# 最大化并行
npx playwright test --workers=100%

# 或指定数量
npx playwright test --workers=4
```

### 3. 选择性运行

```bash
# 只运行特定测试
npx playwright test auth

# 只运行失败的测试
npx playwright test --last-failed
```

## 故障排查

### 问题 1：测试不稳定

```typescript
// 增加重试次数
test.describe.configure({ retries: 2 });

// 增加超时时间
test.setTimeout(60000);
```

### 问题 2：元素找不到

```typescript
// 使用更可靠的选择器
await page.getByRole('button', { name: 'Submit' }).click();

// 而不是
await page.click('#submit-btn');
```

### 问题 3：CI 环境失败

```bash
# 使用 Docker 保证环境一致
docker run -it --rm \
  -v $(pwd):/work \
  -w /work \
  mcr.microsoft.com/playwright:v1.40.0-focal \
  npx playwright test
```

## 总结

Playwright CLI + Claude Code 的组合提供了：

- **高效**：26K tokens vs 114K tokens
- **可靠**：基于可访问性树，不依赖截图
- **并行**：多浏览器、多测试同时运行
- **持久化**：保存认证状态，避免重复登录
- **自动化**：Claude Code 自动生成测试代码

这是 AI 驱动浏览器自动化测试的未来！🚀
