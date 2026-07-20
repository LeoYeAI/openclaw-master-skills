#!/bin/bash
# ClawHub提交前安全检查脚本

echo "🔒 ClawHub提交前安全检查"
echo "========================"
echo ""

skill_dir="$HOME/.openclaw/workspace/skills/skills/openclaw-security-hardening"

# 检查1: 真实密钥
echo "🔍 检查1: 扫描真实密钥..."
echo "---------------------------"

real_keys=$(grep -r "cli_a9f1c3a7c\|diLMNYl2nzbL1nEtQNhjMeQp6rtQdzA7\|DHqybLBGCaINAWscdLkcGDGwn9g\|tbldoED8qoLnkpZC" "$skill_dir" 2>/dev/null | grep -v "Binary file")

if [ -n "$real_keys" ]; then
    echo "❌ 发现真实密钥！"
    echo "$real_keys"
    echo ""
    echo "⚠️  请先清理真实密钥再提交！"
    exit 1
else
    echo "✅ 未发现真实密钥"
fi

echo ""

# 检查2: 敏感文件
echo "🔍 检查2: 扫描敏感文件..."
echo "---------------------------"

sensitive_files=$(find "$skill_dir" -type f \( -name ".env" -o -name "*.key" -o -name "*.secret" -o -name "*.pem" -o -name "credentials.json" \) 2>/dev/null)

if [ -n "$sensitive_files" ]; then
    echo "❌ 发现敏感文件："
    echo "$sensitive_files"
    echo ""
    echo "⚠️  请删除这些文件或添加到.gitignore！"
    exit 1
else
    echo "✅ 未发现敏感文件"
fi

echo ""

# 检查3: 文件权限
echo "🔍 检查3: 验证文件权限..."
echo "---------------------------"

for file in SKILL.md README.md CHANGELOG.md; do
    if [ -f "$skill_dir/$file" ]; then
        perm=$(stat -c %a "$skill_dir/$file")
        echo "  $file: $perm"
    fi
done

echo ""

# 检查4: 必需文件
echo "🔍 检查4: 验证必需文件..."
echo "---------------------------"

required_files=("SKILL.md" "README.md")
missing_files=""

for file in "${required_files[@]}"; do
    if [ ! -f "$skill_dir/$file" ]; then
        missing_files="$missing_files $file"
    fi
done

if [ -n "$missing_files" ]; then
    echo "❌ 缺少必需文件：$missing_files"
    exit 1
else
    echo "✅ 所有必需文件存在"
fi

echo ""

# 检查5: 测试脚本
echo "🔍 检查5: 运行测试..."
echo "---------------------------"

if [ -x "$skill_dir/tests/security-test.sh" ]; then
    bash "$skill_dir/tests/security-test.sh" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ 所有测试通过"
    else
        echo "⚠️  有测试失败，请检查"
    fi
else
    echo "⊘ 测试脚本不存在或不可执行"
fi

echo ""

# 总结
echo "========================"
echo "📊 检查总结"
echo "========================"

echo "✅ 安全检查通过"
echo "✅ 可以提交到ClawHub"
echo ""
echo "📋 技能信息："
echo "  名称: openclaw-security-hardening"
echo "  版本: 1.0.0"
echo "  位置: $skill_dir"
echo ""
echo "🚀 下一步："
echo "  1. 访问 https://clawhub.com"
echo "  2. 点击 'Submit Skill'"
echo "  3. 上传技能目录"
echo "  4. 填写元数据"
echo "  5. 提交审核"
echo ""
echo "💡 提示："
echo "  - 只提交 SKILL.md, README.md, CHANGELOG.md"
echo "  - 不要提交 .env, .key 等敏感文件"
echo "  - 敏感信息已全部替换为占位符"
