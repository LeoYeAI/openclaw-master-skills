# 报告管理

## 目录结构

```
项目目录/
├── reports/
│   ├── analysis_B07PQFT83F_US_20260302.md
│   ├── analysis_B08N5WRWNW_US_20260302.md
│   └── archive/
│       ├── 2025/
│       │   ├── analysis_xxx_US_20251215.md
│       │   └── ...
│       └── 2024/
│           └── ...
└── .claude/
    └── skills/
        └── amazon-analyse/
```

## 报告生命周期

| 阶段 | 时间范围 | 处理方式 |
|------|----------|----------|
| **活跃期** | 最近30天 | 保持在 `reports/` 根目录 |
| **参考期** | 1-6个月 | 移至 `reports/archive/YYYY/` |
| **归档期** | 6个月以上 | 可压缩归档或删除 |

## 报告对比分析

**纵向对比**：同一ASIN不同时期的报告
```bash
# 对比同一产品在不同时间的数据变化
diff reports/analysis_xxx_US_20260101.md \
     reports/analysis_xxx_US_20260301.md
```

**横向对比**：不同ASIN在同一时期的报告
```bash
# 对比竞品之间的数据差异
ls -la reports/analysis_*_US_20260302.md
```

## 报告应用场景

1. **竞品追踪**：定期分析同一竞品，监控其策略变化
2. **市场研究**：积累多个产品报告，发现行业趋势
3. **团队分享**：将报告发送给运营、产品团队
4. **决策支持**：基于历史数据制定定价、选品策略

## 报告导出格式

报告默认保存为 Markdown 格式，可转换为：
- PDF（用于打印/分享）
- HTML（用于网页展示）
- Excel（用于数据提取）

## 报告保存最佳实践

1. 每次分析都保存独立文件，便于历史对比
2. 文件名包含日期，支持多次分析同一产品
3. 报告开头包含分析时间戳，确保数据时效性
4. 建议定期整理旧报告，归档到 `reports/archive/` 目录

## 报告文件命名规则

```
analysis_{ASIN}_{站点}_{日期}.md
例如: analysis_B07PQFT83F_US_20260302.md
```

## 保存位置

```
项目目录/reports/
```

## 保存命令

```bash
# 1. 先检查/创建 reports 目录
mkdir -p reports/

# 2. 生成报告文件路径（使用当前日期）
FILENAME="reports/analysis_${ASIN}_${站点}_$(date +%Y%m%d).md"

# 3. 使用 Write 工具保存完整报告内容
Write $FILENAME
```
