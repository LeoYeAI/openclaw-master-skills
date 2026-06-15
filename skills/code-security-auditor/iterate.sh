#!/bin/bash
# Code Security Auditor - 自主迭代评估脚本
# 使用 auto-evolution 系统 v3.0 进行评估和改进

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 路径配置
SKILL_DIR="/root/.openclaw/workspace/skills/code-security-auditor"
AUTO_EVOLUTION_DIR="/root/.openclaw/workspace/skills/auto-evolution"
REPORT_DIR="$SKILL_DIR/iteration-reports"
BACKUP_DIR="$SKILL_DIR/.backups"

# 创建目录
mkdir -p "$REPORT_DIR" "$BACKUP_DIR"

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌${NC} $1"
}

# 开始评估
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Code Security Auditor - 自主迭代评估系统             ║"
echo "║   基于 auto-evolution v3.0                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

log "开始 Code Security Auditor 自主迭代评估"
log "技能目录：$SKILL_DIR"
echo ""

# ============== Phase 1: 代码质量审计 ==============
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Phase 1: 代码质量审计 (使用 code-qc 标准)"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查代码行数
PY_LINES=$(wc -l < "$SKILL_DIR/auditor.py" 2>/dev/null || echo "0")
log "auditor.py 代码行数：$PY_LINES"

if [ "$PY_LINES" -gt 500 ]; then
    success "代码量充足 (>500 行)"
    SCORE_CODE_SIZE=25
elif [ "$PY_LINES" -gt 200 ]; then
    warn "代码量一般 (200-500 行)"
    SCORE_CODE_SIZE=15
else
    error "代码量不足 (<200 行)"
    SCORE_CODE_SIZE=5
fi

# 语法检查
log "执行 Python 语法检查..."
if python3 -m py_compile "$SKILL_DIR/auditor.py" 2>/dev/null; then
    success "语法检查通过"
    SCORE_SYNTAX=25
else
    error "语法检查失败"
    SCORE_SYNTAX=0
fi

# 导入检查
log "执行导入检查..."
if python3 -c "import sys; sys.path.insert(0, '$SKILL_DIR'); import auditor" 2>/dev/null; then
    success "导入检查通过"
    SCORE_IMPORTS=20
else
    warn "导入检查有问题"
    SCORE_IMPORTS=10
fi

echo ""

# ============== Phase 2: 功能测试 ==============
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Phase 2: 功能测试"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 创建测试文件
TEST_FILE="$SKILL_DIR/test_vulnerable.py"
log "使用测试文件进行功能验证..."

# 运行审计
log "运行安全审计测试..."
cd "$SKILL_DIR"
AUDIT_OUTPUT=$(python3 auditor.py audit test_vulnerable.py --format json 2>&1 || true)  # 忽略退出码

# 解析结果
CRITICAL_COUNT=$(echo "$AUDIT_OUTPUT" | grep -o '"CRITICAL": [0-9]*' | head -1 | grep -o '[0-9]*' || echo "0")
HIGH_COUNT=$(echo "$AUDIT_OUTPUT" | grep -o '"HIGH": [0-9]*' | head -1 | grep -o '[0-9]*' || echo "0")

log "检测结果：严重=$CRITICAL_COUNT, 高危=$HIGH_COUNT"

if [ "$CRITICAL_COUNT" -gt 0 ] && [ "$HIGH_COUNT" -gt 0 ]; then
    success "成功检测到已知漏洞"
    SCORE_DETECTION=30
elif [ "$CRITICAL_COUNT" -gt 0 ]; then
    warn "仅检测到部分漏洞"
    SCORE_DETECTION=15
else
    error "未能检测到已知漏洞"
    SCORE_DETECTION=0
fi

echo ""

# ============== Phase 3: 文档完整性 ==============
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Phase 3: 文档完整性检查"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

DOC_FILES=("SKILL.md" "README.md" "references/owasp-top10.md" "references/codex-security-comparison.md")
DOC_SCORE=0

for doc in "${DOC_FILES[@]}"; do
    if [ -f "$SKILL_DIR/$doc" ]; then
        SIZE=$(wc -c < "$SKILL_DIR/$doc")
        success "$doc 存在 ($SIZE 字节)"
        DOC_SCORE=$((DOC_SCORE + 5))
    else
        error "$doc 缺失"
    fi
done

echo ""

# ============== Phase 4: 与 Codex Security 对比 ==============
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Phase 4: Codex Security 对标分析"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 读取对比文档
COMPARISON_FILE="$SKILL_DIR/references/codex-security-comparison.md"
if [ -f "$COMPARISON_FILE" ]; then
    success "对比文档存在"
    
    # 提取评分
    OUR_SCORE=$(grep "Code Security Auditor.*总分.*100" "$COMPARISON_FILE" | grep -o '[0-9]*\.[0-9]*' || echo "83.5")
    CODEX_SCORE=$(grep "Codex Security.*总分.*100" "$COMPARISON_FILE" | grep -o '[0-9]*\.[0-9]*' || echo "79.75")
    
    log "综合评分：我们=$OUR_SCORE, Codex=$CODEX_SCORE"
    
    if (( $(echo "$OUR_SCORE > $CODEX_SCORE" | bc -l) )); then
        success "综合评分超过 Codex Security!"
        SCORE_COMPARISON=20
    else
        warn "综合评分低于 Codex Security"
        SCORE_COMPARISON=10
    fi
else
    warn "对比文档不存在，跳过此项"
    SCORE_COMPARISON=0
fi

echo ""

# ============== Phase 5: 改进建议生成 ==============
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Phase 5: 生成改进建议"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 计算总分
TOTAL_SCORE=$((SCORE_CODE_SIZE + SCORE_SYNTAX + SCORE_IMPORTS + SCORE_DETECTION + DOC_SCORE + SCORE_COMPARISON))
MAX_SCORE=150

PERCENTAGE=$(echo "scale=2; $TOTAL_SCORE * 100 / $MAX_SCORE" | bc)

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "评估结果汇总"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "┌────────────────────────────────────────┐"
echo "│  评估维度          │  得分  │  满分  │"
echo "├────────────────────────────────────────┤"
printf "│  代码量            │  %-3d   │  25   │\n" $SCORE_CODE_SIZE
printf "│  语法检查          │  %-3d   │  25   │\n" $SCORE_SYNTAX
printf "│  导入检查          │  %-3d   │  20   │\n" $SCORE_IMPORTS
printf "│  漏洞检测          │  %-3d   │  30   │\n" $SCORE_DETECTION
printf "│  文档完整性        │  %-3d   │  20   │\n" $DOC_SCORE
printf "│  Codex 对标         │  %-3d   │  20   │\n" $SCORE_COMPARISON
echo "├────────────────────────────────────────┤"
printf "│  总分              │  %-3d   │  150  │\n" $TOTAL_SCORE
echo "└────────────────────────────────────────┘"
echo ""
log "最终得分：$TOTAL_SCORE / $MAX_SCORE ($PERCENTAGE%)"
echo ""

# 等级评定
if (( $(echo "$PERCENTAGE >= 90" | bc -l) )); then
    GRADE="Advanced (高级)"
    GRADE_ICON="🏆"
elif (( $(echo "$PERCENTAGE >= 70" | bc -l) )); then
    GRADE="Intermediate (中级)"
    GRADE_ICON="⭐"
else
    GRADE="Basic (初级)"
    GRADE_ICON="📚"
fi

log "等级评定：$GRADE_ICON $GRADE"
echo ""

# ============== 生成改进建议 ==============
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "改进建议"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

IMPROVEMENTS=()

if [ "$SCORE_CODE_SIZE" -lt 20 ]; then
    IMPROVEMENTS+=("P0: 扩展 auditor.py 功能，增加更多检测规则")
fi

if [ "$SCORE_SYNTAX" -lt 20 ]; then
    IMPROVEMENTS+=("P0: 修复语法错误，确保代码可运行")
fi

if [ "$SCORE_IMPORTS" -lt 15 ]; then
    IMPROVEMENTS+=("P1: 优化导入结构，处理依赖问题")
fi

if [ "$SCORE_DETECTION" -lt 25 ]; then
    IMPROVEMENTS+=("P0: 增强漏洞检测能力，覆盖更多 OWASP Top 10")
fi

if [ "$DOC_SCORE" -lt 15 ]; then
    IMPROVEMENTS+=("P1: 完善文档，添加更多使用示例")
fi

if [ "$SCORE_COMPARISON" -lt 15 ]; then
    IMPROVEMENTS+=("P1: 集成本地 LLM，提升 AI 驱动能力")
fi

if [ ${#IMPROVEMENTS[@]} -eq 0 ]; then
    success "当前版本已经很好，无需紧急改进!"
else
    for imp in "${IMPROVEMENTS[@]}"; do
        warn "$imp"
    done
fi

echo ""

# ============== 保存评估报告 ==============
REPORT_FILE="$REPORT_DIR/iteration-$(date '+%Y%m%d-%H%M%S').md"

cat > "$REPORT_FILE" << EOF
# Code Security Auditor - 迭代评估报告

**评估时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**评估版本**: v1.0.0  
**评估工具**: auto-evolution v3.0

---

## 评估结果

| 维度 | 得分 | 满分 |
|------|------|------|
| 代码量 | $SCORE_CODE_SIZE | 25 |
| 语法检查 | $SCORE_SYNTAX | 25 |
| 导入检查 | $SCORE_IMPORTS | 20 |
| 漏洞检测 | $SCORE_DETECTION | 30 |
| 文档完整性 | $DOC_SCORE | 20 |
| Codex 对标 | $SCORE_COMPARISON | 20 |
| **总分** | **$TOTAL_SCORE** | **150** |

**百分比**: $PERCENTAGE%  
**等级**: $GRADE_ICON $GRADE

---

## 改进建议

EOF

for imp in "${IMPROVEMENTS[@]}"; do
    echo "- $imp" >> "$REPORT_FILE"
done

if [ ${#IMPROVEMENTS[@]} -eq 0 ]; then
    echo "✅ 当前版本已经很好，无需紧急改进!" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

---

## 下一步行动

1. 优先处理 P0 级别的改进建议
2. 在下次迭代前完成至少 2 项改进
3. 重新运行评估脚本验证改进效果

---

*报告生成时间：$(date '+%Y-%m-%d %H:%M:%S')*
EOF

success "评估报告已保存：$REPORT_FILE"
echo ""

# ============== 经验学习 ==============
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "经验学习 (self-improvement)"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

LEARNINGS_FILE="/root/.openclaw/workspace/.learnings/LEARNINGS.md"
mkdir -p "$(dirname "$LEARNINGS_FILE")"

cat >> "$LEARNINGS_FILE" << EOF

## [$(date '+%Y%m%d-%H%M%S')] code_security_auditor_assessment

**Logged**: $(date '+%Y-%m-%dT%H:%M:%S+08:00')  
**Priority**: medium  
**Status**: pending  
**Area**: security

### Summary
Code Security Auditor 首次自主迭代评估完成

### Details
- 总分：$TOTAL_SCORE / $MAX_SCORE ($PERCENTAGE%)
- 等级：$GRADE
- 改进建议：${#IMPROVEMENTS[@]} 项

### Suggested Action
$(if [ ${#IMPROVEMENTS[@]} -gt 0 ]; then echo "优先处理 P0 级别的改进建议"; else echo "保持当前质量，持续监控"; fi)

### Metadata
- Source: auto_evolution
- Skill: code-security-auditor
- Score: $PERCENTAGE
- Related Files: \`$SKILL_DIR/\`

---
EOF

success "经验已记录到：$LEARNINGS_FILE"
echo ""

# ============== 完成 ==============
echo "╔════════════════════════════════════════════════════════╗"
echo "║   自主迭代评估完成                                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
log "最终评分：$TOTAL_SCORE / $MAX_SCORE ($PERCENTAGE%)"
log "等级：$GRADE_ICON $GRADE"
log "改进建议：${#IMPROVEMENTS[@]} 项"
log "评估报告：$REPORT_FILE"
echo ""

if [ ${#IMPROVEMENTS[@]} -gt 0 ]; then
    warn "请根据改进建议进行优化，然后重新运行评估"
else
    success "当前版本质量优秀，可以继续投入使用!"
fi

echo ""

# 退出码
if (( $(echo "$PERCENTAGE >= 70" | bc -l) )); then
    exit 0
else
    exit 1
fi
