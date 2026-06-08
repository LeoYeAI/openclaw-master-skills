---
name: skill-advisor
description: Evaluate OpenClaw skills before installation. Use when user wants to check a skill's safety, dependencies, popularity, or get an installation recommendation. Generates a pre-install assessment report with security status, metrics, and usage guidance.
version: 1.1.0
license: MIT-0
metadata: {"openclaw": {"emoji": "🔍", "requires": {"bins": ["curl"]}}}
---

# Skill Advisor

Pre-install assessment tool for OpenClaw skills. Generate comprehensive evaluation reports to help users decide whether to install a skill.

## Features

- 🔒 **Security Status**: Check ClawHub official scan results
- 📊 **Popularity Metrics**: Downloads, stars, install count
- 🔄 **Maintenance Status**: Last update time, activity level
- 📦 **Dependency Analysis**: Required tools, libraries, complexity
- 💰 **API Cost Assessment**: Free/paid API requirements
- 🎯 **Installation Recommendation**: Clear go/no-go guidance

## Trigger Conditions

- "Check this skill before installing" / "安装前检查这个skill"
- "Is {skill-name} safe?" / "{skill-name}安全吗"
- "Evaluate skill {skill-name}" / "评估skill {skill-name}"
- "What does {skill-name} need?" / "{skill-name}需要什么依赖"
- "Should I install {skill-name}?" / "要不要安装{skill-name}"
- "skill-advisor {skill-name}"
- "帮我看看这个skill怎么样"

---

## Language Support

This skill supports multiple languages. Output language automatically matches the user's conversation language with OpenClaw.

**Supported Languages:**
- 中文 (Chinese)
- English

**Detection:**
- If user writes in Chinese → Output Chinese report
- If user writes in English → Output English report
- Default: Match the user's input language

---

## Step 1: Get Skill Information

When user provides a skill name, fetch its metadata:

```bash
SKILL_NAME="user-provided-skill-name"

# Get skill metadata from ClawHub
echo "📡 Fetching skill information..."
clawhub inspect "$SKILL_NAME" 2>/dev/null

# Alternative: Use ClawHub API directly
curl -s "https://clawhub.ai/api/v1/skills/$SKILL_NAME" | python3 -m json.tool 2>/dev/null
```

---

## Step 2: Fetch SKILL.md Content

Get the actual SKILL.md to analyze dependencies and functionality:

```bash
# Fetch SKILL.md content
SKILL_CONTENT=$(curl -s "https://clawhub.ai/api/v1/skills/$SKILL_NAME" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'skill' in data and 'content' in data['skill']:
        print(data['skill']['content'])
    elif 'content' in data:
        print(data['content'])
    else:
        print('CONTENT_NOT_FOUND')
except:
    print('PARSE_ERROR')
" 2>/dev/null)

echo "$SKILL_CONTENT"
```

---

## Step 3: Analyze and Generate Report

Parse the skill data and generate the assessment report in the user's language:

```bash
python3 << 'PYEOF'
import json
import re
import sys
from datetime import datetime

# Detect user language from input (passed as argument)
USER_LANG = "en"  # Default to English, will be overridden by agent

# Simulated skill data (replace with actual API response)
skill_data = {
    "name": "SKILL_NAME_PLACEHOLDER",
    "description": "DESCRIPTION_PLACEHOLDER",
    "version": "1.0.0",
    "owner": "AUTHOR_PLACEHOLDER",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-03-20T00:00:00Z",
    "downloads": 0,
    "stars": 0,
    "license": "MIT-0",
    "security_status": "unknown"
}

skill_content = """
SKILL_MD_CONTENT_PLACEHOLDER
"""

# Labels for different languages
LABELS = {
    "zh": {
        "conclusion_header": "🎯 结论",
        "recommend_install": "✅ 推荐安装",
        "caution_install": "⚠️ 可以安装，请注意事项",
        "not_recommend": "❌ 不建议安装",
        "score": "综合评分",
        "security_pass": "通过",
        "security_review": "需审查",
        "deps_light": "轻量",
        "deps_heavy": "较重",
        "report_title": "📋 Skill 评估报告",
        "metrics": "综合指标",
        "official_security": "🔒 官方安全",
        "benign": "✅ Benign（ClawHub扫描通过）",
        "suspicious": "⚠️ Suspicious（需要审查）",
        "security_unknown": "❓ 未知（未扫描）",
        "popularity": "📈 流行度",
        "downloads": "downloads",
        "stars": "stars",
        "maintenance": "🔄 维护状态",
        "active_maintain": "天前更新（活跃维护）",
        "normal_maintain": "天前更新（正常维护）",
        "less_maintain": "天前更新（维护较少）",
        "stop_maintain": "天前更新（可能停止维护）",
        "maintenance_unknown": "❓ 未知",
        "dep_burden": "📦 依赖负担",
        "no_dep": "无需额外依赖",
        "light_dep": "轻量",
        "heavy_dep": "较重",
        "deps_count": "个依赖",
        "api_cost": "💰 API成本",
        "no_api": "无需外部API",
        "api_required": "需要",
        "description": "📝 功能说明",
        "env_req": "⚙️ 环境要求",
        "cli_tools": "命令行工具",
        "python_pkg": "Python包",
        "node_pkg": "Node包",
        "api_key": "API密钥",
        "no_special_req": "无特殊要求",
        "usage_note": "⚠️ 使用注意",
        "data_upload": "📤 文档/数据会上传到",
        "external_service": "📤 会访问外部服务",
        "sensitive_data": "🔐 敏感数据请谨慎处理",
        "install_advice": "💡 安装建议",
        "safe_install": "可安全安装。",
        "caution_install_text": "可以安装，但请注意上述事项。",
        "not_install_text": "不建议安装，请寻找替代方案。",
        "need_config": "需要配置API Key",
        "meta_info": "ℹ️ 元信息",
        "author": "作者",
        "version": "版本",
        "license": "许可证",
        "score_time": "评分时间",
    },
    "en": {
        "conclusion_header": "🎯 Conclusion",
        "recommend_install": "✅ Recommended",
        "caution_install": "⚠️ Install with Caution",
        "not_recommend": "❌ Not Recommended",
        "score": "Overall Score",
        "security_pass": "Passed",
        "security_review": "Review Needed",
        "deps_light": "Light",
        "deps_heavy": "Heavy",
        "report_title": "📋 Skill Assessment Report",
        "metrics": "Metrics",
        "official_security": "🔒 Official Security",
        "benign": "✅ Benign (ClawHub scan passed)",
        "suspicious": "⚠️ Suspicious (needs review)",
        "security_unknown": "❓ Unknown (not scanned)",
        "popularity": "📈 Popularity",
        "downloads": "downloads",
        "stars": "stars",
        "maintenance": "🔄 Maintenance",
        "active_maintain": "days ago (actively maintained)",
        "normal_maintain": "days ago (normal maintenance)",
        "less_maintain": "days ago (less maintained)",
        "stop_maintain": "days ago (possibly abandoned)",
        "maintenance_unknown": "❓ Unknown",
        "dep_burden": "📦 Dependencies",
        "no_dep": "No dependencies required",
        "light_dep": "Light",
        "heavy_dep": "Heavy",
        "deps_count": "dependencies",
        "api_cost": "💰 API Cost",
        "no_api": "No external API required",
        "api_required": "Requires",
        "description": "📝 Description",
        "env_req": "⚙️ Requirements",
        "cli_tools": "CLI Tools",
        "python_pkg": "Python Packages",
        "node_pkg": "Node Packages",
        "api_key": "API Keys",
        "no_special_req": "No special requirements",
        "usage_note": "⚠️ Usage Notes",
        "data_upload": "📤 Data uploads to",
        "external_service": "📤 Accesses external services",
        "sensitive_data": "🔐 Handle sensitive data with care",
        "install_advice": "💡 Installation Advice",
        "safe_install": "Safe to install.",
        "caution_install_text": "Can be installed, but please note the above.",
        "not_install_text": "Not recommended. Consider alternatives.",
        "need_config": "API Key configuration required",
        "meta_info": "ℹ️ Metadata",
        "author": "Author",
        "version": "Version",
        "license": "License",
        "score_time": "Scored at",
    }
}

def get_label(key, lang="en"):
    """Get localized label"""
    return LABELS.get(lang, LABELS["en"]).get(key, key)

def calculate_security_score(content, security_status):
    score = 100
    if security_status == "benign":
        return 100
    elif security_status == "suspicious":
        return 50
    
    dangerous_patterns = [
        (r'curl\s+-fsSL.*\|.*bash', 30),
        (r'sudo\s+(apt|yum|dnf)\s+install', 15),
        (r'eval\s*\(', 20),
        (r'exec\s*\(', 15),
    ]
    
    for pattern, penalty in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            score -= penalty
    
    return max(0, score)

def calculate_popularity_score(downloads, stars):
    score = 0
    if downloads >= 10000: score += 60
    elif downloads >= 1000: score += 50
    elif downloads >= 100: score += 40
    elif downloads >= 10: score += 30
    else: score += 20
    
    if stars >= 50: score += 40
    elif stars >= 10: score += 30
    elif stars >= 1: score += 20
    else: score += 10
    
    return score

def calculate_maintenance_score(updated_at):
    try:
        last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        now = datetime.now(last_update.tzinfo)
        days = (now - last_update).days
        
        if days <= 7: return 100
        elif days <= 30: return 80
        elif days <= 90: return 60
        else: return 40
    except:
        return 50

def extract_dependencies(content):
    deps = {"bins": [], "env_vars": [], "pip_packages": [], "npm_packages": [], "complexity": "unknown"}
    
    bins_match = re.search(r'"bins"\s*:\s*\[(.*?)\]', content)
    if bins_match:
        deps["bins"] = [b.strip().strip('"') for b in bins_match.group(1).split(',') if b.strip()]
    
    env_match = re.search(r'"env"\s*:\s*\[(.*?)\]', content)
    if env_match:
        deps["env_vars"] = [e.strip().strip('"') for e in env_match.group(1).split(',') if e.strip()]
    
    pip_patterns = re.findall(r'pip\s+install\s+([\w-]+)', content)
    deps["pip_packages"] = list(set(pip_patterns))
    
    npm_patterns = re.findall(r'npm\s+(?:install|i)\s+(?:-g\s+)?([\w-]+)', content)
    deps["npm_packages"] = list(set(npm_patterns))
    
    lines = len(content.split('\n'))
    if lines < 100: deps["complexity"] = "simple"
    elif lines < 250: deps["complexity"] = "medium"
    else: deps["complexity"] = "complex"
    
    return deps

def calculate_dependency_score(deps):
    score = 100
    bin_count = len(deps["bins"])
    if bin_count <= 2: score -= 10
    elif bin_count <= 4: score -= 20
    elif bin_count > 4: score -= 30
    
    pkg_count = len(deps["pip_packages"]) + len(deps["npm_packages"])
    if pkg_count > 5: score -= 20
    elif pkg_count > 0: score -= 10
    
    return max(0, score)

def calculate_api_cost_score(deps, content):
    if not deps["env_vars"]:
        return 100
    
    free_indicators = ["免费", "free", "免费额度", "new user", "free tier"]
    has_free = any(indicator in content.lower() for indicator in free_indicators)
    
    return 80 if has_free else 60

def generate_report(skill_data, skill_content, lang="en"):
    L = lambda k: get_label(k, lang)
    
    name = skill_data.get("name", "unknown")
    description = skill_data.get("description", "No description")
    version = skill_data.get("version", "?.?.?")
    owner = skill_data.get("owner", "unknown")
    downloads = skill_data.get("downloads", 0)
    stars = skill_data.get("stars", 0)
    updated_at = skill_data.get("updated_at", "")
    security_status = skill_data.get("security_status", "unknown")
    license_type = skill_data.get("license", "unknown")
    
    security_score = calculate_security_score(skill_content, security_status)
    popularity_score = calculate_popularity_score(downloads, stars)
    maintenance_score = calculate_maintenance_score(updated_at)
    deps = extract_dependencies(skill_content)
    dependency_score = calculate_dependency_score(deps)
    api_cost_score = calculate_api_cost_score(deps, skill_content)
    
    total_score = (
        security_score * 0.30 +
        popularity_score * 0.25 +
        maintenance_score * 0.20 +
        dependency_score * 0.15 +
        api_cost_score * 0.10
    )
    
    if total_score >= 80:
        grade = "A"
        recommendation = L("recommend_install")
        rec_icon = "✅"
    elif total_score >= 60:
        grade = "B"
        recommendation = L("caution_install")
        rec_icon = "⚠️"
    else:
        grade = "C"
        recommendation = L("not_recommend")
        rec_icon = "❌"
    
    if security_status == "benign":
        security_text = L("benign")
    elif security_status == "suspicious":
        security_text = L("suspicious")
    else:
        security_text = L("security_unknown")
    
    try:
        last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        now = datetime.now(last_update.tzinfo)
        days = (now - last_update).days
        if days <= 7:
            maintenance_text = f"✅ {days}{L('active_maintain')}"
        elif days <= 30:
            maintenance_text = f"✅ {days}{L('normal_maintain')}"
        elif days <= 90:
            maintenance_text = f"⚠️ {days}{L('less_maintain')}"
        else:
            maintenance_text = f"⚠️ {days}{L('stop_maintain')}"
    except:
        maintenance_text = L("maintenance_unknown")
    
    all_deps = deps["bins"] + deps["pip_packages"] + deps["npm_packages"]
    if not all_deps:
        deps_text = L("no_dep")
    elif len(all_deps) <= 3:
        deps_text = f"{L('light_dep')}（{', '.join(all_deps)}）"
    else:
        deps_text = f"{L('heavy_dep')}（{len(all_deps)}{L('deps_count')}）"
    
    if not deps["env_vars"]:
        api_text = L("no_api")
    else:
        api_text = f"{L('api_required')} {', '.join(deps['env_vars'])}"
    
    data_warnings = []
    if "api.siliconflow.cn" in skill_content or "siliconflow" in skill_content.lower():
        data_warnings.append(f"{L('data_upload')} api.siliconflow.cn")
    if "curl" in skill_content and "https://" in skill_content:
        urls = re.findall(r'https?://[^\s"\'\)]+', skill_content)
        external_domains = set()
        for url in urls:
            if "clawhub" not in url and "github" not in url and "openclaw" not in url:
                domain = url.split("//")[1].split("/")[0]
                external_domains.add(domain)
        if external_domains:
            data_warnings.append(f"{L('external_service')}：{', '.join(list(external_domains)[:3])}")
    
    report = f"""
┌─────────────────────────────────────────────────────────┐
│  {L('conclusion_header')}：{rec_icon} {recommendation.ljust(30)}│
│  {L('score')}：{total_score:.0f}/100 ({grade}级) | {L('official_security').replace('🔒 ', '')}：{L('security_pass') if security_score >= 80 else L('security_review')} | {L('dep_burden').replace('📦 ', '')}：{L('deps_light') if dependency_score >= 80 else L('deps_heavy')}           │
└─────────────────────────────────────────────────────────┘

━━━ {L('report_title')}：{name} ━━━━━━━━━━━━━━━━━━━━━━━━━

📊 {L('metrics')}
├─ {L('official_security')}：{security_text}
├─ {L('popularity')}：⭐ {downloads} {L('downloads')} | ⭐ {stars} {L('stars')}
├─ {L('maintenance')}：{maintenance_text}
├─ {L('dep_burden')}：{deps_text}
└─ {L('api_cost')}：{api_text}

{L('description')}
{description[:150]}{'...' if len(description) > 150 else ''}

{L('env_req')}"""

    if deps["bins"]:
        report += f"\n├─ {L('cli_tools')}：{', '.join(deps['bins'])}"
    if deps["pip_packages"]:
        report += f"\n├─ {L('python_pkg')}：{', '.join(deps['pip_packages'])}"
    if deps["npm_packages"]:
        report += f"\n├─ {L('node_pkg')}：{', '.join(deps['npm_packages'])}"
    if deps["env_vars"]:
        report += f"\n└─ {L('api_key')}：{', '.join(deps['env_vars'])}"
    elif not deps["bins"] and not deps["pip_packages"] and not deps["npm_packages"]:
        report += f"\n└─ {L('no_special_req')}"

    if data_warnings:
        report += f"\n\n{L('usage_note')}"
        for warning in data_warnings:
            report += f"\n├─ {warning}"
        report += f"\n└─ {L('sensitive_data')}"

    report += f"\n\n{L('install_advice')}"
    if total_score >= 80:
        report += f"\n{L('safe_install')}"
    elif total_score >= 60:
        report += f"\n{L('caution_install_text')}"
    else:
        report += f"\n{L('not_install_text')}"
    
    if deps["env_vars"]:
        report += f"\n{L('need_config')}：{', '.join(deps['env_vars'])}"
    
    report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{L('meta_info')}
├─ {L('author')}：{owner}
├─ {L('version')}：{version}
├─ {L('license')}：{license_type}
└─ {L('score_time')}：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    return report

# Example usage - English
print("=== English Report ===")
print(generate_report(skill_data, skill_content, "en"))

print("\n\n=== 中文报告 ===")
print(generate_report(skill_data, skill_content, "zh"))
PYEOF
```

---

## Step 4: Output Report

The report is displayed directly to the user. No files are created.

```
🎯 结论：✅ 推荐安装
综合评分：85/100 (A级) | 安全：通过 | 依赖：轻量

━━━ 📋 Skill 评估报告：{skill-name} ━━━━━━━━━━━━━━━━━
...
```

---

## Usage Flow

```
User (Chinese): "帮我看看 china-doc-ocr 这个skill怎么样"

Agent:
1. Detect user language → Chinese
2. Run: clawhub inspect china-doc-ocr
3. Fetch SKILL.md content from ClawHub API
4. Parse and analyze
5. Generate report in Chinese
6. Display report to user

---

User (English): "Is skill-xyz safe to install?"

Agent:
1. Detect user language → English
2. Run: clawhub inspect skill-xyz
3. Fetch SKILL.md content from ClawHub API
4. Parse and analyze
5. Generate report in English
6. Display report to user
```

---

## Error Handling

```
Skill not found        → "❌ 未找到该skill，请检查名称"
ClawHub API error      → "❌ 无法连接ClawHub，请稍后重试"
Parse error            → "⚠️ 部分信息解析失败，报告可能不完整"
```

---

## Notes

- No files are generated (pure text output)
- Report shows conclusion first, then details
- Security status uses ClawHub's official scan results
- Scores are calculated dynamically based on multiple factors
- All data fetched in real-time from ClawHub
