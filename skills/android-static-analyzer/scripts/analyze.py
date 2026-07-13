#!/usr/bin/env python3
"""
Android Static Analyzer - 语义版
核心：LLM 读懂 Kotlin 源码，输出业务语义，而不是结构解析

用法：
  python3 analyze.py <Android项目路径> [平台地址]

输出：
  --- METADATA ---
  {"appPackage": "...", "sourceFiles": N, "analyzedFiles": N, "manifestPath": "...", "platformUrl": null}
  --- LLM_PROMPT ---
  <发给 LLM 的完整 Prompt，含源码>

说明：
  脚本不调用 LLM，由 OpenClaw Agent 读取 LLM_PROMPT 后自行调用 LLM 分析。
"""

import os
import sys
import json
import re
from pathlib import Path


def find_manifest(project_root):
    """找 AndroidManifest.xml（跳过 build/ 等无关目录）"""
    skip_dirs = {'build', '.gradle', '.git', 'node_modules', '.idea', '.cxx', 'intermediates'}
    for root, dirs, files in os.walk(project_root):
        # 过滤掉不需要扫描的目录
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        if 'AndroidManifest.xml' in files and 'src/main' in root.replace('\\', '/'):
            return os.path.join(root, 'AndroidManifest.xml')
    return None


def get_package_from_manifest(manifest_path):
    """从 AndroidManifest.xml 读取包名"""
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(manifest_path)
        pkg = tree.getroot().get('package', '')
        if pkg:
            return pkg
    except Exception:
        pass
    return None


def get_package_from_gradle(manifest_path):
    """从 build.gradle / build.gradle.kts 读取 namespace（新版 AGP 方式）"""
    # manifest 通常在 app/src/main/，往上找 app/build.gradle
    search_dirs = [
        os.path.dirname(manifest_path),           # app/src/main
        os.path.join(os.path.dirname(manifest_path), '..', '..'),  # app/
        os.path.join(os.path.dirname(manifest_path), '..', '..', '..'),  # project root
    ]
    for d in search_dirs:
        for name in ['build.gradle.kts', 'build.gradle']:
            path = os.path.normpath(os.path.join(d, name))
            if os.path.exists(path):
                try:
                    content = Path(path).read_text(errors='ignore')
                    m = re.search(r'namespace\s*[=:]\s*["\']([^"\']+)["\']', content)
                    if m:
                        return m.group(1)
                    # applicationId 作为备选
                    m = re.search(r'applicationId\s*[=:]\s*["\']([^"\']+)["\']', content)
                    if m:
                        return m.group(1)
                except Exception:
                    pass
    return 'unknown'


def find_kotlin_files(manifest_path):
    """找所有 Kotlin/Java 源文件（仅 src/main/kotlin 和 src/main/java）"""
    src_root = os.path.dirname(manifest_path)  # app/src/main
    kt_files = []
    for lang_dir in ['kotlin', 'java']:
        src_dir = os.path.join(src_root, lang_dir)
        if os.path.exists(src_dir):
            for f in Path(src_dir).rglob('*.kt'):
                kt_files.append(str(f))
            for f in Path(src_dir).rglob('*.java'):
                kt_files.append(str(f))
    return kt_files


def read_source_files(kt_files, max_chars=80000):
    """
    读取源码（限制总长度，优先读 Activity 文件）
    去掉空行和单行注释以减少 token，但保留代码结构。
    """
    # 优先读 Activity 文件，其次 Fragment/ViewModel，最后其他
    def priority(f):
        name = os.path.basename(f)
        if 'Activity' in name:
            return 0
        if 'Fragment' in name or 'ViewModel' in name:
            return 1
        return 2

    ordered = sorted(kt_files, key=priority)

    source_code = {}
    total = 0

    for f in ordered:
        if total >= max_chars:
            break
        try:
            content = Path(f).read_text(encoding='utf-8', errors='ignore')
            # 去掉纯注释行和空行，减少 token
            lines = []
            for line in content.split('\n'):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
                    continue
                lines.append(line)
            condensed = '\n'.join(lines)

            remaining = max_chars - total
            if len(condensed) > remaining:
                condensed = condensed[:remaining]

            filename = os.path.basename(f)
            source_code[filename] = condensed
            total += len(condensed)
        except Exception:
            pass

    return source_code


def build_llm_prompt(app_package, source_code):
    """
    构建发给 LLM 的 Prompt。
    Agent 拿到这个 Prompt 后，自己调用 LLM，不是由脚本调用。
    """
    # 拼接源码块
    source_text = '\n\n'.join(
        f'// === {name} ===\n{code}'
        for name, code in source_code.items()
    )

    prompt = f"""你是一个资深 Android 测试专家。请仔细阅读以下 Android 应用源码（包名：{app_package}），输出一份供 AI 自动化测试 Agent 直接使用的**测试先验知识**。

## 分析重点

1. **业务类型**：这是什么类型的 App（电商/工具/社交/金融/内容等）
2. **核心业务流程**：列出完整的用户操作路径，每一步写清楚要点击哪个控件（用控件 ID）
3. **业务约束条件**：哪些按钮/操作有前置条件才能触发（例如：购物车必须选中商品才能结算）
4. **死路（测试时跳过）**：哪些控件点击后没有真正跳转，只弹 Toast 或什么都不做——这些是测试陷阱，AI Agent 不应该点击
5. **测试优先级**：按 P0/P1/P2/P3 排列，P0 是必须验证的核心链路
6. **测试数据**：代码中硬编码的账号、密码、优惠码、枚举值等

## 输出格式

**严格只输出以下 JSON，不要输出任何其他内容，不要加 markdown 代码块：**

{{
  "businessType": "业务类型（例：移动电商）",
  "businessSummary": "一句话描述 App 的核心功能",
  "criticalFlows": [
    {{
      "name": "流程名称",
      "priority": "P0-必测 / P1-重要 / P2-一般",
      "steps": ["操作步骤1", "操作步骤2"],
      "preconditions": ["执行该流程所需的前置条件"],
      "keyControls": ["关键控件的 resource-id（不含包名前缀）"],
      "expectedResult": "该流程成功完成后的预期状态"
    }}
  ],
  "businessConstraints": [
    {{
      "activity": "Activity 类名（不含包名）",
      "constraint": "约束条件的完整描述",
      "testImplication": "测试时需要提前准备什么，或需要注意什么"
    }}
  ],
  "deadEnds": [
    {{
      "activity": "Activity 类名（不含包名）",
      "control": "控件的 resource-id",
      "reason": "为什么这是死路（功能未实现、仅 Toast、跳转被注释等）",
      "testImplication": "AI 测试 Agent 应该跳过此控件，不要浪费步骤"
    }}
  ],
  "testPriorities": [
    "P0: 核心流程描述",
    "P1: 次要流程描述",
    "P2: 边界/异常场景描述"
  ],
  "testData": {{
    "说明": "填写从源码中发现的硬编码测试数据"
  }}
}}

## 源码

{source_text}"""

    return prompt


def main():
    if len(sys.argv) < 2:
        print("用法: python3 analyze.py <Android项目路径> [平台地址]", file=sys.stderr)
        sys.exit(1)

    project_root = os.path.abspath(sys.argv[1])
    platform_url = sys.argv[2] if len(sys.argv) > 2 else None

    # 1. 定位 AndroidManifest.xml
    manifest_path = find_manifest(project_root)
    if not manifest_path:
        print(json.dumps({"error": "未找到 AndroidManifest.xml，请确认这是一个有效的 Android 项目目录"}))
        sys.exit(1)

    # 2. 获取包名
    app_package = get_package_from_manifest(manifest_path)
    if not app_package:
        app_package = get_package_from_gradle(manifest_path)

    # 3. 找源码文件
    kt_files = find_kotlin_files(manifest_path)

    # 4. 读取源码（限制总量，优先 Activity）
    source_code = read_source_files(kt_files, max_chars=80000)

    # 5. 构建 LLM Prompt
    prompt = build_llm_prompt(app_package, source_code)

    # 6. 输出 metadata 和 LLM prompt（分隔符格式，供 Agent 解析）
    metadata = {
        "appPackage": app_package,
        "sourceFiles": len(kt_files),
        "analyzedFiles": len(source_code),
        "manifestPath": manifest_path,
        "platformUrl": platform_url,
    }

    print("--- METADATA ---")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    print("--- LLM_PROMPT ---")
    print(prompt)


if __name__ == '__main__':
    main()
