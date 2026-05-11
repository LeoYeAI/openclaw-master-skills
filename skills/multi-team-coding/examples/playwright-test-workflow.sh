#!/bin/bash
# 集成 Playwright 自动化测试到多团队工作流

set -e

PROJECT_ROOT=$(pwd)
WORKSPACE_BASE=/tmp/playwright-teams-$(date +%s)
mkdir -p $WORKSPACE_BASE/{teams,logs,reports}

echo "🎭 Playwright 自动化测试工作流"
echo ""

# ============================================
# Playwright 配置检查
# ============================================

check_playwright_setup() {
  echo "🔍 检查 Playwright 环境..."
  
  if ! command -v npx &> /dev/null; then
    echo "  ❌ Node.js 未安装"
    exit 1
  fi
  
  if [ ! -f "package.json" ]; then
    echo "  ⚠️  未找到 package.json，初始化项目..."
    npm init -y
  fi
  
  if ! npm list @playwright/test &> /dev/null; then
    echo "  📦 安装 Playwright..."
    npm install -D @playwright/test
    npx playwright install
  fi
  
  echo "  ✅ Playwright 环境就绪"
}

# ============================================
# 自动生成测试团队
# ============================================

start_test_generation_team() {
  local feature_name=$1
  local feature_description=$2
  local test_type=$3  # e2e, visual, api, performance
  
  local work_dir="$WORKSPACE_BASE/teams/test-${feature_name}"
  
  echo "  🧪 启动测试生成团队: $feature_name ($test_type)"
  
  # 创建工作目录
  mkdir -p $work_dir
  cd $work_dir
  ln -s $PROJECT_ROOT/node_modules ./node_modules 2>/dev/null || true
  
  # 生成测试提示词
  local prompt="
【任务】为功能生成 Playwright 测试

【功能名称】$feature_name
【功能描述】$feature_description
【测试类型】$test_type

【要求】
1. 使用 Playwright Test 框架
2. 遵循 Page Object Model 模式
3. 包含正常和异常场景
4. 添加清晰的测试描述和注释
5. 使用可靠的选择器（优先 getByRole）

【测试文件结构】
"

  case $test_type in
    e2e)
      prompt="$prompt
tests/e2e/${feature_name}.spec.ts
tests/pages/${feature_name}Page.ts

【E2E 测试要求】
- 测试完整用户流程
- 包含登录/认证（如需要）
- 验证关键元素和交互
- 截图失败场景
- 生成测试报告

【示例】
\`\`\`typescript
import { test, expect } from '@playwright/test';
import { ${feature_name}Page } from '../pages/${feature_name}Page';

test.describe('${feature_name}', () => {
  let page: ${feature_name}Page;

  test.beforeEach(async ({ page: p }) => {
    page = new ${feature_name}Page(p);
    await page.goto();
  });

  test('should complete main flow', async () => {
    await page.performMainAction();
    await expect(page.successMessage).toBeVisible();
  });

  test('should handle errors', async () => {
    await page.triggerError();
    await expect(page.errorMessage).toBeVisible();
  });
});
\`\`\`
"
      ;;
      
    visual)
      prompt="$prompt
tests/visual/${feature_name}.spec.ts

【视觉回归测试要求】
- 截图关键页面状态
- 对比基准图片
- 设置合理的差异阈值
- 测试不同视口尺寸

【示例】
\`\`\`typescript
import { test, expect } from '@playwright/test';

test('${feature_name} visual regression', async ({ page }) => {
  await page.goto('/${feature_name}');
  
  // 等待页面稳定
  await page.waitForLoadState('networkidle');
  
  // 截图对比
  await expect(page).toHaveScreenshot('${feature_name}.png', {
    maxDiffPixels: 100,
  });
});
\`\`\`
"
      ;;
      
    api)
      prompt="$prompt
tests/api/${feature_name}.spec.ts

【API 测试要求】
- 测试所有 API 端点
- 验证请求和响应格式
- 测试错误处理
- 性能基准测试

【示例】
\`\`\`typescript
import { test, expect } from '@playwright/test';

test.describe('${feature_name} API', () => {
  test('GET /${feature_name}', async ({ request }) => {
    const response = await request.get('/api/${feature_name}');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('id');
  });

  test('POST /${feature_name}', async ({ request }) => {
    const response = await request.post('/api/${feature_name}', {
      data: { name: 'test' }
    });
    expect(response.status()).toBe(201);
  });
});
\`\`\`
"
      ;;
      
    performance)
      prompt="$prompt
tests/performance/${feature_name}.spec.ts

【性能测试要求】
- 测试页面加载时间
- 测试 API 响应时间
- 测试资源大小
- 生成性能报告

【示例】
\`\`\`typescript
import { test, expect } from '@playwright/test';

test('${feature_name} performance', async ({ page }) => {
  const startTime = Date.now();
  await page.goto('/${feature_name}');
  const loadTime = Date.now() - startTime;
  
  expect(loadTime).toBeLessThan(3000);
  
  // 检查资源大小
  const metrics = await page.evaluate(() => 
    performance.getEntriesByType('resource')
  );
  
  const totalSize = metrics.reduce((sum, r) => sum + r.transferSize, 0);
  expect(totalSize).toBeLessThan(5 * 1024 * 1024); // 5MB
});
\`\`\`
"
      ;;
  esac

  prompt="$prompt

【完成后】
1. 将测试文件保存到 $PROJECT_ROOT/tests/
2. 运行测试验证
3. 提交代码

npx playwright test tests/${test_type}/${feature_name}.spec.ts
git add tests/
git commit -m 'test: add ${test_type} tests for ${feature_name}'
"

  # 启动 Claude Code
  bash pty:true workdir:$PROJECT_ROOT background:true \
    command:"claude '$prompt'" \
    > $WORKSPACE_BASE/logs/test-${feature_name}.log 2>&1 &
  
  echo $! > $WORKSPACE_BASE/teams/test-${feature_name}.pid
  echo "     ✅ 已启动 (PID: $!)"
}

# ============================================
# 批量生成测试
# ============================================

generate_all_tests() {
  echo "📝 批量生成测试..."
  echo ""
  
  # 从项目中识别需要测试的功能
  # 这里假设有一个功能列表
  declare -A FEATURES=(
    ["auth"]="用户认证：注册、登录、登出"
    ["products"]="商品管理：列表、详情、搜索"
    ["cart"]="购物车：添加、删除、更新"
    ["checkout"]="结账流程：地址、支付、确认"
  )
  
  # 为每个功能生成不同类型的测试
  for feature in "${!FEATURES[@]}"; do
    echo "功能: $feature"
    
    # E2E 测试
    start_test_generation_team "$feature" "${FEATURES[$feature]}" "e2e"
    sleep 2
    
    # API 测试
    start_test_generation_team "$feature" "${FEATURES[$feature]}" "api"
    sleep 2
    
    # 视觉回归测试（仅前端功能）
    if [[ "$feature" != "api" ]]; then
      start_test_generation_team "$feature" "${FEATURES[$feature]}" "visual"
      sleep 2
    fi
  done
  
  echo ""
  echo "✅ 所有测试生成任务已启动"
}

# ============================================
# 并行运行测试
# ============================================

run_parallel_tests() {
  echo ""
  echo "🚀 并行运行所有测试..."
  
  cd $PROJECT_ROOT
  
  # 运行测试（自动并行）
  npx playwright test \
    --workers=4 \
    --reporter=html,json \
    --output=test-results
  
  local exit_code=$?
  
  # 生成报告
  echo ""
  echo "📊 生成测试报告..."
  npx playwright show-report
  
  return $exit_code
}

# ============================================
# 生成测试覆盖率报告
# ============================================

generate_coverage_report() {
  echo ""
  echo "📈 生成测试覆盖率报告..."
  
  local report_file="$WORKSPACE_BASE/reports/coverage-$(date +%Y%m%d-%H%M%S).md"
  
  cat > $report_file << 'EOF'
# Playwright 测试覆盖率报告

## 测试统计

EOF
  
  # 统计测试数量
  local total_tests=$(find $PROJECT_ROOT/tests -name "*.spec.ts" | wc -l)
  local e2e_tests=$(find $PROJECT_ROOT/tests/e2e -name "*.spec.ts" 2>/dev/null | wc -l)
  local api_tests=$(find $PROJECT_ROOT/tests/api -name "*.spec.ts" 2>/dev/null | wc -l)
  local visual_tests=$(find $PROJECT_ROOT/tests/visual -name "*.spec.ts" 2>/dev/null | wc -l)
  
  cat >> $report_file << EOF
- 总测试文件: $total_tests
- E2E 测试: $e2e_tests
- API 测试: $api_tests
- 视觉测试: $visual_tests

## 测试结果

EOF
  
  # 解析测试结果
  if [ -f "$PROJECT_ROOT/test-results/results.json" ]; then
    local passed=$(jq '[.suites[].specs[] | select(.ok == true)] | length' $PROJECT_ROOT/test-results/results.json)
    local failed=$(jq '[.suites[].specs[] | select(.ok == false)] | length' $PROJECT_ROOT/test-results/results.json)
    local total=$(( passed + failed ))
    local pass_rate=$(( passed * 100 / total ))
    
    cat >> $report_file << EOF
- 通过: $passed
- 失败: $failed
- 通过率: ${pass_rate}%

## 失败测试

EOF
    
    jq -r '.suites[].specs[] | select(.ok == false) | "- [\(.title)](\(.file))"' \
      $PROJECT_ROOT/test-results/results.json >> $report_file
  fi
  
  echo "  ✅ 报告已生成: $report_file"
  cat $report_file
}

# ============================================
# 主流程
# ============================================

main() {
  # 1. 检查环境
  check_playwright_setup
  
  echo ""
  echo "🎯 选择模式："
  echo "  1. 生成测试"
  echo "  2. 运行测试"
  echo "  3. 完整流程（生成 + 运行）"
  echo ""
  
  read -p "请选择 (1-3): " mode
  
  case $mode in
    1)
      generate_all_tests
      
      echo ""
      echo "⏳ 等待测试生成完成..."
      wait
      
      echo "✅ 测试生成完成"
      ;;
      
    2)
      if run_parallel_tests; then
        echo "✅ 所有测试通过"
        generate_coverage_report
      else
        echo "❌ 部分测试失败"
        generate_coverage_report
        exit 1
      fi
      ;;
      
    3)
      # 生成测试
      generate_all_tests
      
      echo ""
      echo "⏳ 等待测试生成完成..."
      wait
      
      # 运行测试
      if run_parallel_tests; then
        echo "✅ 所有测试通过"
        generate_coverage_report
      else
        echo "❌ 部分测试失败"
        generate_coverage_report
        exit 1
      fi
      ;;
      
    *)
      echo "❌ 无效选择"
      exit 1
      ;;
  esac
  
  echo ""
  echo "🎊 完成！"
}

# 运行
main "$@"
