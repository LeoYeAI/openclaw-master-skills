#!/bin/bash

# 发布脚本
# 使用方法: ./scripts/publish.sh

echo "📦 准备发布 finloop-news-skills 到 npm..."

# 检查是否已登录 npm
if ! npm whoami &> /dev/null; then
  echo "❌ 错误: 请先登录 npm"
  echo "   运行: npm login"
  exit 1
fi

# 检查版本号
VERSION=$(node -p "require('./package.json').version")
echo "📌 当前版本: $VERSION"

# 询问是否继续
read -p "是否发布到 npm? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "❌ 发布已取消"
  exit 1
fi

# 发布 (scoped package 需要 --access public)
echo "🚀 正在发布..."
npm publish --access public

if [ $? -eq 0 ]; then
  echo "✅ 发布成功!"
  echo "📦 用户现在可以使用以下命令安装:"
  echo "   npx finloop-news-skills install finloop-news-skill"
else
  echo "❌ 发布失败"
  exit 1
fi

