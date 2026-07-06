# drpy源代码格式化与压缩

## 为什么要格式化代码

1. **减小文件体积**：压缩后的源文件加载更快
2. **统一代码风格**：便于维护和共享
3. **去除冗余信息**：移除注释和空白字符
4. **保护代码**：混淆变量名增加安全性

## 工具选择

### uglify-js（推荐）
最常用的JavaScript压缩工具，支持丰富选项。

### terser
uglify-es的替代品，支持ES6+。

### 在线工具
适用于快速测试和小文件处理。

## uglify-js使用指南

### 安装
```bash
# 全局安装
npm install uglify-js -g

# 查看版本
uglifyjs --version
```

### 基本压缩
```bash
# 压缩单个文件
uglifyjs source.js -o source.min.js

# 压缩并混淆变量名
uglifyjs source.js -o source.min.js --mangle

# 压缩、混淆并启用高级压缩
uglifyjs source.js -o source.min.js -c -m
```

### 常用选项

| 选项 | 简写 | 说明 |
|------|------|------|
| `--compress` | `-c` | 启用代码压缩 |
| `--mangle` | `-m` | 混淆变量名 |
| `--output <file>` | `-o` | 指定输出文件 |
| `--beautify` | `-b` | 美化输出（与压缩相反） |
| `--comments` | | 保留特定注释 |
| `--source-map` | | 生成source map |

### 完整压缩命令
```bash
# 推荐配置
uglifyjs drpy-source.js -o drpy-source.min.js \
  --compress \
  --mangle \
  --comments '/@license|@preserve/' \
  --source-map "url='drpy-source.min.js.map',includeSources"
```

## WebStorm集成配置

### 步骤1：找到uglifyjs路径
```bash
# Windows CMD
where uglifyjs

# Windows PowerShell
Get-Command uglifyjs | Select-Object -ExpandProperty Source

# 结果示例
C:\Users\用户名\AppData\Roaming\npm\uglifyjs.cmd
```

### 步骤2：配置外部工具
1. **文件 → 设置 → 工具 → 外部工具**
2. **点击"+"添加新工具**
3. 配置如下：

```
名称: UglifyJS
程序: C:\Users\用户名\AppData\Roaming\npm\uglifyjs.cmd
实参: $FileName$ -o $FileNameWithoutExtension$.min.js
工作目录: $FileDir$
```

### 步骤3：使用快捷键
- 选中JS文件
- 右键 → 外部工具 → UglifyJS
- 或配置键盘快捷键

## 手动格式化技巧

### 删除注释
```javascript
// 开发时的详细注释
var rule = {
  // 这里是类型定义
  类型: '影视',  // 影视源
};
```

压缩后：
```javascript
var rule={类型:"影视"};
```

### 简化空格和换行
```javascript
// 原始代码
var rule = {
  title : '示例源',
  host  : 'https://example.com'
};

// 压缩后
var rule={title:"示例源",host:"https://example.com"};
```

### 函数简化
```javascript
// 原始函数
推荐: async function () {
  let {input} = this;
  return [];
},

// 压缩后（匿名函数）
推荐:async function(){return[]},
```

## drpy特定压缩注意事项

### 保留必要属性名
drpy中的中文属性名必须保留：
```javascript
// 不要混淆这些属性名
属性名保留列表: [
  '类型', '标题', 'host', 'url', 'searchUrl',
  'class_name', 'class_url', 'play_parse',
  '推荐', '一级', '二级', '搜索', 'lazy'
]
```

### 配置示例
```bash
# 使用--mangle-props保留重要属性
uglifyjs source.js -o source.min.js -m reserved=['类型','标题','host']
```

### 模板继承代码
模板继承代码可能有特殊结构，压缩时需要测试：
```javascript
// 压缩前
var rule = Object.assign(muban.mxpro, {
  title: '示例源',
  host: 'https://example.com',
});

// 压缩后应保持结构完整
var rule=Object.assign(muban.mxpro,{title:"示例源",host:"https://example.com"});
```

## 压缩前后对比

### 压缩前示例
```javascript
/**
 * 鸭奈飞影视源
 * 最后更新: 2024-01-01
 */

var rule = {
  // 源类型
  类型: '影视',
  
  // 源信息
  title: '鸭奈飞',
  
  // 域名
  host: 'https://yanetflix.com',
  
  // 首页
  homeUrl: '/',
  
  // 分类页模板
  url: '/vod/show/id/fyclass/page/fypage.html',
  
  // 搜索页模板
  searchUrl: '/vodsearch/紧箍咒/page/fypage.html',
  
  // 函数定义
  推荐: async function () {
    let {input} = this;
    return [];
  },
};
```

### 压缩后示例
```javascript
var rule={类型:"影视",title:"鸭奈飞",host:"https://yanetflix.com",homeUrl:"/",url:"/vod/show/id/fyclass/page/fypage.html",searchUrl:"/vodsearch/紧箍咒/page/fypage.html",推荐:async function(){return[]}};
```

**文件大小对比**：
- 原始文件: 约 500 字节
- 压缩文件: 约 200 字节
- 压缩率: 约 60%

## 高级压缩策略

### 分阶段压缩
```bash
# 阶段1：基础压缩
uglifyjs source.js -o stage1.js -c

# 阶段2：混淆变量
uglifyjs stage1.js -o stage2.js -m

# 阶段3：进一步优化
uglifyjs stage2.js -o final.min.js -c passes=2
```

### 批量压缩脚本
创建`batch_minify.bat`（Windows）：
```batch
@echo off
echo 开始压缩drpy源文件...

for %%f in (*.js) do (
  if not "%%f" == "*.min.js" (
    echo 压缩 %%f ...
    uglifyjs "%%f" -o "%%~nf.min.js" -c -m
  )
)

echo 压缩完成！
pause
```

或`batch_minify.sh`（Linux/macOS）：
```bash
#!/bin/bash
echo "开始压缩drpy源文件..."

for file in *.js; do
  if [[ $file != *.min.js ]]; then
    echo "压缩 $file ..."
    uglifyjs "$file" -o "${file%.js}.min.js" -c -m
  fi
done

echo "压缩完成！"
```

## 常见问题

### Q: 压缩后源不工作
A:
1. 检查是否混淆了drpy必需的属性名
2. 尝试不使用`--mangle`选项
3. 分段压缩，定位问题步骤
4. 保留开发版本用于调试

### Q: 压缩后的代码无法阅读
A:
1. 保留source map文件
2. 开发时使用未压缩版本
3. 使用`--beautify`选项生成格式化的压缩版

### Q: uglifyjs命令不存在
A:
1. 确认已全局安装：`npm install uglify-js -g`
2. 检查PATH环境变量包含npm全局目录
3. Windows用户可能需要重启终端

### Q: 压缩效率不满意
A:
1. 手动删除不必要的注释和空格
2. 简化代码结构
3. 使用更激进的压缩选项：`-c unsafe=true`

## 最佳实践

1. **保留开发版本**：始终保留未压缩的源代码
2. **版本控制**：将.min.js文件加入.gitignore
3. **测试验证**：压缩后务必测试功能是否正常
4. **逐步压缩**：先压缩再混淆，便于问题定位
5. **备份重要注释**：使用`/*! 重要注释 */`格式

## 替代方案

### 在线压缩工具
- [JavaScript Minifier](https://javascript-minifier.com/)
- [UglifyJS Online](https://skalman.github.io/UglifyJS-online/)

### 使用构建工具
Webpack、Rollup等构建工具集成压缩功能。

### 编辑器插件
VS Code、WebStorm等编辑器有代码格式化插件。