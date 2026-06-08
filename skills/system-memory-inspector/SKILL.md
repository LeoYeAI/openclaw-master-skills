---
name: system-memory-inspector
description: >
  Linux 系统级内存泄漏巡检：定时扫描所有进程内存，记录系统内存全景，
  通过增长趋势分析识别异常进程，输出排查思路和可疑进程列表。
  当用户提到"系统内存巡检"、"全进程内存扫描"、"内存泄漏排查"、"环境内存分析"、
  "定时统计所有进程"、"系统内存记录"、"找出泄漏进程"时触发。
license: MIT
compatibility: >
  Linux 系统，依赖：ps、awk、sort、uniq。无需应用层配合，纯系统级检测。
metadata:
  author: SRE-Team
  version: "1.0.0"
  category: inspection
  tags: [system, memory, inspection, all-processes, trend-analysis]
---

# 系统内存泄漏巡检技能

## 核心逻辑

```
定时扫描所有进程 RSS → 持久化存储 → 跨时间对比 → 识别增长异常进程 → 输出排查清单
```

## 巡检流程

### 1. 数据采集
扫描 `/proc/<pid>/status` 获取所有进程：
- PID、进程名、RSS、VmSize、线程数、运行时间

### 2. 数据存储
按时间戳存储快照：
```
/var/log/memory-inspector/
├── 20240115_090000.snapshot      # 完整快照
├── 20240115_090500.snapshot
└── trending/
    ├── java-app.dat              # 单个进程历史趋势
    ├── python-worker.dat
    └── ...
```

### 3. 分析算法

#### 进程级增长检测
```
对每个进程:
  读取最近N次RSS记录 → 计算增长率 → 标记异常等级
```

#### 系统级健康评分
```
系统评分 = 100 - Σ(异常进程权重)
  确认泄漏进程: -20分/个
  疑似泄漏进程: -10分/个
  高内存进程: -5分/个 (>1GB且持续增长)
```

### 4. 输出报告

**包含内容**:
1. **系统内存概况**: 总内存、已用、缓存、可用
2. **TOP 内存进程**: 当前占用最高的进程
3. **增长异常进程**: 疑似/确认泄漏的进程清单
4. **排查思路**: 针对异常进程的排查建议

---

## 使用方式

```bash
# 手动执行一次巡检
./system-memory-scan.sh

# 定时巡检 (crontab 每5分钟)
*/5 * * * * /path/to/system-memory-scan.sh >> /var/log/memory-inspector/cron.log 2>&1

# 查看最新报告
cat /var/log/memory-inspector/latest-report.txt
```

---

## 输出示例

```
========== 系统内存巡检报告 ==========
巡检时间: 2024-01-15 09:15:00
系统评分: 75/100 (良好)

【系统概况】
总内存: 32GB | 已用: 24GB(75%) | 可用: 6GB | 缓存: 2GB

【TOP 10 内存进程】
PID    进程名              RSS(MB)   运行时间    状态
1234   java-app            8192      3d12h       正常
5678   python-worker       4096      5d08h       疑似泄漏 ⚠️
9012   nginx               512       10d00h      正常
...

【增长异常进程】

⚠️  疑似泄漏 (增长率 30-100MB/h):
  PID 5678 python-worker
    当前RSS: 4096MB (5分钟前: 3950MB)
    增长率: 55MB/h
    趋势: 近1小时持续增长
    建议: 关注业务负载，准备生成堆内存分析

🚨 确认泄漏 (增长率 >100MB/h):
  PID 3456 node-server
    当前RSS: 2048MB (5分钟前: 1800MB)
    增长率: 150MB/h  
    趋势: 近30分钟加速增长
    建议: 立即排查，考虑重启止损

【排查思路】

1. 对于 python-worker (PID 5678):
   - 检查是否有未关闭的数据库连接
   - 查看日志是否有任务积压
   - 使用 `tracemalloc` 生成内存快照对比

2. 对于 node-server (PID 3456):
   - 检查是否有未释放的 Buffer/Stream
   - 查看事件监听器是否累积
   - 使用 Chrome DevTools 生成 heap snapshot

3. 系统级建议:
   - 当前系统内存使用率75%，建议清理缓存或扩容
   - 2个进程存在泄漏风险，建议1小时内处理
```

---

## 核心算法

### 进程增长率计算
```bash
# 读取进程历史 (最近6个采样点)
history=$(tail -6 /var/log/memory-inspector/trending/${pid}.dat)
# 计算线性斜率 (简化: 首尾差分 / 时间跨度)
growth_rate=$(( (current - old) * 3600 / time_span_seconds ))  # MB/h
```

### 异常等级判定
| 增长率 | 等级 | 动作 |
|--------|------|------|
| < 10 MB/h | 正常 | 记录即可 |
| 10-50 MB/h | 关注 | 标记，增加采样频率 |
| 50-100 MB/h | 疑似泄漏 | 输出告警，建议排查 |
| > 100 MB/h | 确认泄漏 | 紧急告警，建议立即处理 |

### 降噪处理
- 过滤短时进程 (< 5分钟，可能是临时命令)
- 过滤系统进程 (kernel、kthreadd 等)
- 过滤已知大内存应用 (如 redis 缓存服务，看配置而非增长)
```
---

## scripts/system-memory-scan.sh

```bash
#!/bin/bash
#
# 系统级内存巡检脚本
# 功能: 扫描所有进程，分析内存增长趋势，生成排查报告
#

set -e

# 配置
INSPECTOR_DIR="/var/log/memory-inspector"
SNAPSHOT_DIR="$INSPECTOR_DIR"
TREND_DIR="$INSPECTOR_DIR/trending"
REPORT_FILE="$INSPECTOR_DIR/latest-report.txt"
MAX_HISTORY=10                    # 保留最近10个快照
SAMPLE_INTERVAL=300               # 默认采样间隔5分钟(用于计算增长率)

# 阈值 (MB/h)
THRESHOLD_NORMAL=10
THRESHOLD_ATTENTION=50
THRESHOLD_SUSPECT=100
THRESHOLD_CONFIRM=100

# 初始化目录
mkdir -p "$SNAPSHOT_DIR" "$TREND_DIR"

# 当前时间
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE_STR=$(date '+%Y%m%d_%H%M%S')

# ==================== 1. 采集所有进程数据 ====================

collect_snapshot() {
    local snapshot_file="$SNAPSHOT_DIR/${DATE_STR}.snapshot"
    
    # 采集: PID, 进程名, RSS(MB), VmSize(MB), 运行时间(秒), 命令行
    echo "# 系统内存快照 $TIMESTAMP" > "$snapshot_file"
    echo "# PID|NAME|RSS|VSZ|TIME|CMD" >> "$snapshot_file"
    
    for pid_dir in /proc/[0-9]*; do
        pid=$(basename "$pid_dir")
        
        # 跳过已消失进程
        [ -f "$pid_dir/status" ] || continue
        
        # 读取数据
        name=$(grep ^Name: "$pid_dir/status" 2>/dev/null | awk '{print $2}' || echo "unknown")
        rss=$(grep ^VmRSS: "$pid_dir/status" 2>/dev/null | awk '{print $2}' || echo "0")  # KB
        vsz=$(grep ^VmSize: "$pid_dir/status" 2>/dev/null | awk '{print $2}' || echo "0") # KB
        
        # 转换为MB
        rss_mb=$((rss / 1024))
        vsz_mb=$((vsz / 1024))
        
        # 运行时间 (从/proc/uptime - /proc/[pid]/stat 计算，简化用ps)
        # 这里用etime的秒数近似
        etime=$(ps -p "$pid" -o etimes= 2>/dev/null | tr -d ' ' || echo "0")
        
        # 命令行 (截断)
        cmd=$(cat "$pid_dir/cmdline" 2>/dev/null | tr '\0' ' ' | cut -c1-50 || echo "[kernel]")
        [ -z "$cmd" ] && cmd="[$name]"
        
        # 过滤系统进程和短时进程
        [ "$etime" -lt 300 ] && continue  # 跳过运行<5分钟的进程
        [[ "$name" == "kthreadd" || "$name" == "migration" || "$name" == "watchdog" ]] && continue
        
        echo "$pid|$name|$rss_mb|$vsz_mb|$etime|$cmd" >> "$snapshot_file"
    done
    
    echo "$snapshot_file"
}

# ==================== 2. 更新进程趋势数据 ====================

update_trends() {
    local snapshot_file=$1
    
    # 读取当前快照中的所有进程
    tail -n +3 "$snapshot_file" | while IFS='|' read -r pid name rss vsz etime cmd; do
        trend_file="$TREND_DIR/${pid}.dat"
        
        # 格式: 时间戳 RSS
        echo "$(date +%s) $rss" >> "$trend_file"
        
        # 只保留最近20个样本 (约100分钟历史)
        tail -n 20 "$trend_file" > "${trend_file}.tmp" && mv "${trend_file}.tmp" "$trend_file"
    done
}

# ==================== 3. 分析增长率 ====================

calculate_growth_rate() {
    local pid=$1
    local trend_file="$TREND_DIR/${pid}.dat"
    
    [ -f "$trend_file" ] || return
    
    local line_count=$(wc -l < "$trend_file")
    [ "$line_count" -lt 3 ] && return  # 需要至少3个点
    
    # 读取首尾计算斜率 (简化算法)
    local first=$(head -1 "$trend_file")
    local last=$(tail -1 "$trend_file")
    
    local first_time=$(echo "$first" | awk '{print $1}')
    local first_rss=$(echo "$first" | awk '{print $2}')
    local last_time=$(echo "$last" | awk '{print $1}')
    local last_rss=$(echo "$last" | awk '{print $2}')
    
    local time_diff=$((last_time - first_time))
    [ "$time_diff" -lt 60 ] && return  # 时间跨度太小
    
    local rss_diff=$((last_rss - first_rss))
    
    # 计算 MB/h
    local rate=$(( rss_diff * 3600 / time_diff ))
    
    # 只返回正增长
    [ "$rate" -gt 0 ] && echo "$rate" || echo "0"
}

# ==================== 4. 生成报告 ====================

generate_report() {
    local snapshot_file=$1
    local report="$REPORT_FILE"
    
    # 系统内存信息
    local mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local mem_available=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
    local mem_used=$((mem_total - mem_available))
    local mem_percent=$((mem_used * 100 / mem_total))
    
    mem_total_gb=$((mem_total / 1024 / 1024))
    mem_used_gb=$((mem_used / 1024 / 1024))
    mem_avail_gb=$((mem_available / 1024 / 1024))
    
    # 系统评分计算
    local score=100
    local confirm_count=0
    local suspect_count=0
    
    # 收集异常进程信息
    local confirm_list=""
    local suspect_list=""
    local attention_list=""
    
    # 处理每个进程
    while IFS='|' read -r pid name rss vsz etime cmd; do
        [ -z "$pid" ] && continue
        
        rate=$(calculate_growth_rate "$pid" || echo "0")
        
        # 判定等级
        if [ "$rate" -ge "$THRESHOLD_CONFIRM" ]; then
            confirm_list="${confirm_list}${pid}|${name}|${rss}|${rate}|${cmd}\n"
            ((score-=20))
            ((confirm_count++))
        elif [ "$rate" -ge "$THRESHOLD_SUSPECT" ]; then
            suspect_list="${suspect_list}${pid}|${name}|${rss}|${rate}|${cmd}\n"
            ((score-=10))
            ((suspect_count++))
        elif [ "$rate" -ge "$THRESHOLD_ATTENTION" ]; then
            attention_list="${attention_list}${pid}|${name}|${rss}|${rate}|${cmd}\n"
            ((score-=5))
        fi
    done < <(tail -n +3 "$snapshot_file")
    
    # 确保分数不为负
    [ "$score" -lt 0 ] && score=0
    
    # 写入报告
    {
        echo "========== 系统内存巡检报告 =========="
        echo "巡检时间: $TIMESTAMP"
        echo "系统评分: ${score}/100 ($(get_score_desc $score))"
        echo ""
        echo "【系统概况】"
        echo "总内存: ${mem_total_gb}GB | 已用: ${mem_used_gb}GB(${mem_percent}%) | 可用: ${mem_avail_gb}GB"
        echo ""
        
        echo "【TOP 10 内存进程】"
        echo "PID    进程名              RSS(MB)   增长率(MB/h)  状态"
        echo "------ ------------------- --------- ------------- --------"
        
        # 排序输出TOP10
        tail -n +3 "$snapshot_file" | sort -t'|' -k3 -nr | head -10 | while IFS='|' read -r pid name rss vsz etime cmd; do
            rate=$(calculate_growth_rate "$pid" || echo "0")
            status=$(get_status_label "$rate")
            printf "%-6s %-19s %-9s %-13s %s\n" "$pid" "$name" "$rss" "${rate}" "$status"
        done
        
        echo ""
        echo "【增长异常进程】"
        echo ""
        
        # 确认泄漏
        if [ -n "$confirm_list" ] && [ "$confirm_list" != "\n" ]; then
            echo "🚨 确认泄漏 (增长率 >${THRESHOLD_CONFIRM}MB/h):"
            echo "$confirm_list" | grep -v '^$' | while IFS='|' read -r pid name rss rate cmd; do
                echo "  PID $pid $name"
                echo "    当前RSS: ${rss}MB | 增长率: ${rate}MB/h"
                echo "    命令: $cmd"
                echo "    建议: 立即排查，考虑重启止损，生成内存dump分析"
                echo ""
            done
        fi
        
        # 疑似泄漏
        if [ -n "$suspect_list" ] && [ "$suspect_list" != "\n" ]; then
            echo "⚠️  疑似泄漏 (增长率 ${THRESHOLD_SUSPECT}-${THRESHOLD_CONFIRM}MB/h):"
            echo "$suspect_list" | grep -v '^$' | while IFS='|' read -r pid name rss rate cmd; do
                echo "  PID $pid $name"
                echo "    当前RSS: ${rss}MB | 增长率: ${rate}MB/h"
                echo "    命令: $cmd"
                echo "    建议: 关注业务负载，准备生成堆内存分析，检查近期变更"
                echo ""
            done
        fi
        
        # 关注级别
        if [ -n "$attention_list" ] && [ "$attention_list" != "\n" ]; then
            echo "ℹ️  值得关注 (增长率 ${THRESHOLD_ATTENTION}-${THRESHOLD_SUSPECT}MB/h):"
            echo "$attention_list" | grep -v '^$' | while IFS='|' read -r pid name rss rate cmd; do
                echo "  PID $pid $name - ${rss}MB - ${rate}MB/h"
            done
            echo ""
        fi
        
        if [ -z "$confirm_list" ] && [ -z "$suspect_list" ] && [ -z "$attention_list" ]; then
            echo "✅ 未发现明显内存增长异常进程"
            echo ""
        fi
        
        echo "【排查思路总结】"
        echo ""
        
        if [ "$confirm_count" -gt 0 ] || [ "$suspect_count" -gt 0 ]; then
            echo "针对检测到的异常进程，建议按以下步骤排查："
            echo ""
            echo "1. 确认进程业务属性:"
            echo "   - 该进程是什么服务？是否关键业务？"
            echo "   - 近期是否有版本发布或配置变更？"
            echo "   - 业务负载是否有异常（QPS突增、任务积压）？"
            echo ""
            echo "2. 快速止损方案:"
            echo "   - 如为无状态服务，可考虑重启（会中断业务）"
            echo "   - 如为有状态服务，先限流或扩容，避免OOM"
            echo "   - 临时增加系统内存或清理缓存争取时间"
            echo ""
            echo "3. 根因分析（根据进程类型选择工具）:"
            echo "   Java进程: 使用 jmap -dump:format=b,file=... <pid> 生成hprof文件，"
            echo "             用 Eclipse MAT 分析 dominator tree"
            echo "   Python进程: 发送 SIGUSR1 触发 tracemalloc 快照，"
            echo "               或使用 py-spy 实时分析"
            echo "   Node.js进程: 启动时加 --inspect，用 Chrome DevTools 拍heap snapshot"
            echo "   Go进程: 访问 /debug/pprof/heap 获取pprof文件，go tool pprof分析"
            echo "   其他进程: 使用 valgrind --leak-check=full 或 asan 重新编译检测"
            echo ""
            echo "4. 常见泄漏模式速查:"
            echo "   - 缓存无限增长: 检查是否有TTL机制"
            echo "   - 连接未关闭: 数据库/Redis/HTTP连接池"
            echo "   - 事件监听器累积: 注册未注销的回调"
            echo "   - 大对象未释放: 批量处理任务后未清空"
            echo ""
        fi
        
        echo "系统级建议:"
        if [ "$mem_percent" -gt 90 ]; then
            echo "⚠️  系统内存使用率超过90%，建议立即清理缓存或紧急扩容"
        elif [ "$mem_percent" -gt 80 ]; then
            echo "⚠️  系统内存使用率超过80%，建议关注并准备扩容"
        else
            echo "✅ 系统内存使用率正常(${mem_percent}%)"
        fi
        
        if [ "$confirm_count" -gt 0 ]; then
            echo "🚨 发现 ${confirm_count} 个确认泄漏进程，建议1小时内处理"
        elif [ "$suspect_count" -gt 0 ]; then
            echo "⚠️  发现 ${suspect_count} 个疑似泄漏进程，建议4小时内排查"
        else
            echo "✅ 未发现泄漏风险进程"
        fi
        
        echo ""
        echo "========== 巡检完成 =========="
        
    } > "$report"
    
    # 同时输出到控制台
    cat "$report"
}

# 辅助函数：根据分数获取描述
get_score_desc() {
    local score=$1
    if [ "$score" -ge 90 ]; then echo "优秀"; 
    elif [ "$score" -ge 75 ]; then echo "良好"; 
    elif [ "$score" -ge 60 ]; then echo "一般"; 
    else echo "危险"; fi
}

# 辅助函数：根据增长率获取状态标签
get_status_label() {
    local rate=$1
    if [ "$rate" -ge "$THRESHOLD_CONFIRM" ]; then echo "确认泄漏 🚨";
    elif [ "$rate" -ge "$THRESHOLD_SUSPECT" ]; then echo "疑似泄漏 ⚠️";
    elif [ "$rate" -ge "$THRESHOLD_ATTENTION" ]; then echo "关注 ℹ️";
    else echo "正常 ✅"; fi
}

# ==================== 5. 清理旧数据 ====================

cleanup_old_data() {
    # 只保留最近 $MAX_HISTORY 个快照
    cd "$SNAPSHOT_DIR" && ls -t *.snapshot 2>/dev/null | tail -n +$((MAX_HISTORY+1)) | xargs -r rm -f
    
    # 清理已不存在进程的趋势文件
    for trend_file in "$TREND_DIR"/*.dat; do
        [ -f "$trend_file" ] || continue
        pid=$(basename "$trend_file" .dat)
        if ! ps -p "$pid" > /dev/null 2>&1; then
            # 进程已退出，保留但标记，或删除（这里保留最后数据）
            mv "$trend_file" "${trend_file}.exited"
        fi
    done
}

# ==================== 主流程 ====================

main() {
    echo "开始系统内存巡检... $TIMESTAMP"
    
    # 1. 采集
    snapshot=$(collect_snapshot)
    echo "已采集 $(($(wc -l < "$snapshot") - 2)) 个进程"
    
    # 2. 更新趋势
    update_trends "$snapshot"
    
    # 3. 生成报告
    generate_report "$snapshot"
    
    # 4. 清理
    cleanup_old_data
    
    echo "巡检完成，报告保存至: $REPORT_FILE"
}

main
```

---

## 核心设计

### 数据采集
- 扫描 `/proc/*/status` 获取所有进程
- 过滤内核线程和短时进程 (<5分钟)
- 记录：PID、名称、RSS、虚拟内存、运行时间、命令行

### 存储结构
```
/var/log/memory-inspector/
├── 20240115_090000.snapshot     # 完整快照（所有进程当前状态）
├── 20240115_090500.snapshot
└── trending/
    ├── 1234.dat                 # PID 1234 的历史 RSS 趋势
    ├── 5678.dat
    └── ...
```

### 分析算法
```bash
# 极简斜率计算
growth_rate = (current_rss - old_rss) * 3600 / time_diff_seconds
# 输出 MB/h
```

### 异常分级
| 增长率 | 扣分 | 等级 | 排查紧急度 |
|--------|------|------|-----------|
| >100 MB/h | -20 | 🚨 确认泄漏 | 立即处理 |
| 50-100 MB/h | -10 | ⚠️ 疑似泄漏 | 4小时内 |
| 10-50 MB/h | -5 | ℹ️ 关注 | 24小时内 |

### 系统评分
- 满分100，异常进程扣分
- 90+ 优秀 | 75-90 良好 | 60-75 一般 | <60 危险

---

## 典型输出

```
========== 系统内存巡检报告 ==========
巡检时间: 2024-01-15 14:30:00
系统评分: 65/100 (一般)

【系统概况】
总内存: 64GB | 已用: 58GB(91%) | 可用: 6GB

【增长异常进程】

🚨 确认泄漏:
  PID 3456 java-order-service
    当前RSS: 12288MB | 增长率: 180MB/h
    建议: 立即排查，考虑重启止损，生成内存dump分析

⚠️  疑似泄漏:
  PID 7890 python-report-generator
    当前RSS: 4096MB | 增长率: 75MB/h
    建议: 关注业务负载，准备生成堆内存分析

【排查思路总结】
...
