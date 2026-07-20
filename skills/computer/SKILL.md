---
name: Computer
description: The universal computer skill - hardware diagnostics, system performance, computational tasks, binary operations, and everything about the physical machine. Use for computer management, optimization, troubleshooting, and understanding the machine itself.
---

# Computer（计算机总控）

这是 **Computer Skill** - 一个统管计算机一切操作的终极技能。它不只是工具集合，更是**数字世界的物理根基**。

---

## 核心理念

> "计算机是执行逻辑与算术操作的机器。"  
> **Computer Skill** 让你与这台机器深度对话。

它覆盖：
- **硬件** - CPU、内存、磁盘、网络、外设
- **固件** - BIOS/UEFI、引导、ACPI
- **系统** - 进程、服务、内核、驱动
- **性能** - 监控、优化、调优、故障排除
- **计算** - 数学、数据处理、模拟
- **二进制** - 0/1世界、内存布局、编码

---

## 适用场景

当你说：
- "检查计算机健康状态"
- "优化系统性能"
- "诊断硬件问题"
- "计算复杂数学"
- "查看内存使用"
- "测试磁盘速度"
- "监控温度"
- "超频/降频"
- "管理系统资源"
- "了解二进制/十六进制"
- "硬件信息查询"

---

## 硬件信息与诊断

### 整机信息
```bash
# 系统摘要
computer summary                 # 全面系统报告
computer hardware --full        # 详细硬件清单
computer specs                  # 快速规格查看

# 等效命令
sudo dmidecode --type system     # DMI表信息（Linux）
system_profiler SPHardwareDataType  # macOS硬件报告
wmic computersystem get name,domain,manufacturer,model  # Windows
```

### CPU信息
```bash
computer cpu                    # CPU详细信息
lscpu                           # 逻辑核心、架构、缓存
cat /proc/cpuinfo               # 原始CPU信息（Linux）
sysctl -a | grep machdep.cpu    # macOS CPU详情
Get-WmiObject Win32_Processor  # Windows
```

**核心信息**
```bash
nproc                          # 逻辑核心数
lscpu | grep "Core(s) per socket"  # 每核核心
lscpu | grep "CPU max MHz"        # 最高频率
cpupower frequency-info         # 当前频率（Linux）
```

### 内存信息
```bash
computer memory                # 内存总览
free -h                        # 使用情况
vmstat -s                      # 虚拟内存统计
cat /proc/meminfo              # 原始内存信息
```

**详细RAM**
```bash
sudo dmidecode --type memory   # 内存模块详情
sudo lshw -C memory           # 硬件层信息
memtester 1M                  # 内存测试（需安装）
```

### 磁盘与存储
```bash
computer disk                 # 磁盘总览
lsblk                         # 块设备树
fdisk -l                      # 分区表
blkid                         # 文件系统识别
df -h                         # 磁盘空间
du -sh *                      # 目录大小
```

**SMART健康**
```bash
smartctl -a /dev/sda         # 完整SMART数据
smartctl -H /dev/sda         # 健康状态
smartctl -t short /dev/sda   # 快速自检
smartctl -l selftest /dev/sda # 自检结果
```

**磁盘性能**
```bash
# 顺序读写
dd if=/dev/zero of=testfile bs=1M count=1000 oflag=direct
dd if=testfile of=/dev/null bs=1M count=1000 iflag=direct

# iozone (综合测试)
iozone -a -g 1G -i 0 -i 1

# fio (灵活测试)
fio --name=randread --filename=test --rw=randread --bs=4k --iodepth=64 --size=1G --numjobs=4 --runtime=60 --group_reporting
```

### GPU与显示
```bash
computer gpu                  # GPU信息
lspci | grep VGA             # PCI设备
nvidia-smi                   # NVIDIA GPU状态
glxinfo | grep "OpenGL"      # OpenGL信息（Linux）
system_profiler SPDisplaysDataType  # macOS显示
Get-WmiObject Win32_VideoController  # Windows
```

### 网络接口
```bash
computer network             # 网络总览
ip addr show                 # IP地址
ethtool eth0                 # 网卡详情（速度、双工）
ethtool -i eth0              # 驱动信息
iwconfig                     # 无线信息（Linux）
networksetup -getinfo Wi-Fi  # macOS Wi-Fi
Get-NetAdapter              # Windows
```

**网卡速度检测**
```bash
ethtool eth0 | grep "Speed"  # 实际协商速度
iperf3 -c server             # 带宽测试
```

### 温度与传感器
```bash
computer temp                # 温度监控
sensors                      # LM-Sensors（Linux）
sudo turbostat --all          # Intel CPU功耗、温度
powermetrics --samplers smc  # macOS传感器
coretemp                     # 核心温度
```

**风扇速度**
```bash
sensors -u                   # 包括风扇
cat /proc/acpi/ibm/fan       # ThinkPad风扇
```

---

## 系统性能监控

### 实时监控
```bash
computer monitor            # 启动监控仪表板
top                         # 进程排名（CPU、内存）
htop                        # 增强版top
glances                     # 全系统仪表板（网络、磁盘、进程）
atop                       # 高级系统监控（历史记录）

# 自定义监控
watch -n 1 'ps aux --sort=-%cpu | head -10'  # 每1秒查看CPU Top10
watch -n 1 'free -h && df -h'  # 内存和磁盘
```

### 性能数据
```bash
# sar（系统活动报告，历史分析）
sar -u 1 10                 # CPU每1秒10次
sar -r 1 10                 # 内存
sar -b 1 10                 # I/O

# pidstat（进程级统计）
pidstat -u 1 10             # CPU使用
pidstat -r 1 10             # 内存使用

# vmstat（虚拟内存统计）
vmstat 1 10                 # 每秒输出
```

### 性能分析工具
```bash
perf top                    # 实时perf分析（内核函数）
strace -p PID               # 跟踪系统调用
ltrace -p PID               # 跟踪库调用
tcpdump -i eth0 port 80     # 网络抓包
wireshark                   # 图形化抓包
```

---

## 计算功能

### 数学计算
```bash
computer calculate 123 * 456  # 基本运算
computer calc --mode float "sin(pi/4)"  # 浮点数学
computer convert 0xFF  # 十六进制转换
computer bit --and 0b1100 0b1010  # 位运算
```

**bc计算器（精确）**
```bash
echo "scale=10; sqrt(2)" | bc -l
echo "2^32" | bc
```

**Python一行计算**
```bash
python -c "print(2**32-1)"
python -c "import math; print(math.sin(math.pi/4))"
```

**单位转换**
```bash
# 体积、长度、温度
computer units --from GB --to MB 1
computer convert --temp 100 C F
```

### 位运算
```bash
# Bash位运算（整数）
echo $((0b1100 & 0b1010))  # AND → 1000 (8)
echo $((0b1100 | 0b1010))  # OR  → 1110 (14)
echo $((0b1100 ^ 0b1010))  # XOR → 0110 (6)
echo $((0b1100 << 2))      # 左移 → 110000 (48)
echo $((0b1100 >> 2))      # 右移 → 0011 (3)

# 反码
echo $((~0b1010))  # 负数表示（补码）
```

**十六进制/二进制/八进制**
```bash
printf "%x\n" 255      # 十六进制 → ff
printf "%o\n" 255      # 八进制 → 377
printf "%b\n" "\x48\x65\x78"  # 二进制解码 → Hex
echo "obase=16; 255" | bc  # 十进制转十六进制
echo "ibase=16; FF" | bc   # 十六进制转十进制
```

### 算法与模拟
```bash
# 快速排序（演示）
computer algo --sort quick --array "5,2,8,1,9"

# 斐波那契数列
fib() { a=0 b=1; for ((i=0;i<$1;i++)); do echo -n "$a "; c=$((a+b)); a=$b; b=$c; done; echo; }
fib 20

# 质数检测
computer prime 9973
```

---

## 系统管理

### 进程管理
```bash
computer processes          # 进程全景图
ps aux --sort=-%cpu | head -20  # CPU排行
ps aux --sort=-%mem | head -20  # 内存排行
pstree -p                  # 进程树
pgrep -l "process_name"    # 精确查找
```

**进程控制**
```bash
kill -15 PID               # 优雅终止
kill -9 PID                # 强制杀死
kill -STOP PID             # 暂停（SIGSTOP）
kill -CONT PID             # 继续（SIGCONT）
renice -n 19 -p PID        # 降低优先级
renice -n -20 -p PID       # 提高优先级（需root）
```

### 服务管理
```bash
computer services          # 服务状态总览
systemctl list-units --type=service --state=running  # 运行中服务
systemctl status service_name
systemctl restart service_name
journalctl -u service_name -f  # 实时日志
```

### 用户与会话
```bash
computer users             # 登录用户
who                         # 当前登录
w                           # 更详细信息（负载、进程）
last                        # 登录历史
lastlog                     # 所有用户最后登录
```

### 任务调度
```bash
computer crontab           # crontab概览
crontab -l                  # 当前用户计划任务
crontab -e                  # 编辑
at now + 1 minute          # 一次性任务
atrm job_number            # 取消at任务
```

---

## 系统优化

### CPU调优
```bash
# 查看当前策略
cat /proc/sys/kernel/sched_latency_ns

# 调整调度器参数（需root）
echo 150000 > /proc/sys/kernel/sched_min_granularity_ns

# 启用CPU加速
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 节能模式
echo "powersave" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### 内存优化
```bash
# 查看缓存
free -h
cat /proc/meminfo | grep -E "MemFree|Cached|Buffers"

# 清理缓存（谨慎）
echo 3 | sudo tee /proc/sys/vm/drop_caches

# 调整swap倾向
sysctl vm.swappiness=10    # 0-100，越小越避免swap
```

### I/O优化
```bash
# 查看I/O等待
iostat -x 1 10
pidstat -d 1 10

# 调整调度器（SSD）
echo noop | sudo tee /sys/block/sda/queue/scheduler

# 预读调整（SSD禁用）
echo 0 | sudo tee /sys/block/sda/queue/read_ahead_kb
```

### 网络优化
```bash
# 查看网络队列
ethtool -S eth0

# 调整缓冲区
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
```

---

## 故障排除

### 启动问题
```bash
computer boot --diagnose   # 启动诊断
dmesg | tail -50           # 内核日志
journalctl -b -1           # 上一次启动日志
systemd-analyze blame      # 启动耗时分析
```

### 资源瓶颈
```bash
# 发现CPU瓶颈
top (按P排序)
mpstat -P ALL 1

# 内存瓶颈
free -h
vmstat 1

# I/O瓶颈
iotop
iostat -x 1

# 网络瓶颈
iftop
nethogs
```

### 硬件故障
```bash
# SMART错误
smartctl -a /dev/sda | grep -i error

# 内存错误
dmesg | grep -i memory

# 过热
sensors | grep -i "temp\|crit"

# PCI总线错误
lspci -v
```

### 死机/冻结
```bash
# 查看系统负载
uptime
cat /proc/loadavg

# 检查不可中断睡眠
ps aux | awk '$8=="D"'  # D状态进程

# 查看D状态原因
strace -p PID
```

---

## 二进制与底层

### 字节/位级操作
```bash
computer hexdump file.bin
computer bits --set 3 --on file  # 设置特定位
computer endian --check        # 检测字节序
```

**十六进制编辑**
```bash
hexdump -C file.bin | head -20
xxd file.bin | head -20
vim -b file.bin               # 二进制模式
bless                         # GUI十六进制编辑器
```

**字节序转换**
```bash
# 小端→大端
printf "\x01\x02\x03\x04" | dd bs=1 skip=0 count=4 2>/dev/null | tac | od -An -t x1

# Python转换
python -c "import struct; print(struct.pack('>I', 0x01020304).hex())"
```

### 内存布局查看
```bash
# /proc/pid/maps
cat /proc/self/maps

# objdump（ELF文件）
objdump -d a.out | head -30
readelf -S a.out             # 节头
readelf -l a.out             # 程序头
```

### 二进制分析
```bash
# strings提取
strings binary | grep "password"

# nm符号表
nm binary | grep main

# strace系统调用
strace ./program

# ltrace库调用
ltrace ./program
```

---

## 性能基准测试

### CPU基准
```bash
# sysbench（CPU）
sysbench cpu --cpu-max-prime=20000 run

# stress-ng（压力测试）
stress-ng --cpu 4 --timeout 60s

# 7-zip（压缩基准）
7z b -mmt=on
```

### 内存基准
```bash
# 内存带宽
mbw 1024

# latency测试
lmbench all
```

### 磁盘基准
```bash
# hdparm（顺序）
sudo hdparm -tT /dev/sda

# fio（随机/顺序）
fio --name=seqwrite --filename=test --rw=write --bs=1M --size=1G --numjobs=1 --time_based --runtime=60
```

### GPU基准
```bash
# glxgears（OpenGL）
glxgears -info

# cuBLAS（CUDA）
bandwidthTest
deviceQuery
```

---

## 虚拟化与容器

### 虚拟化检查
```bash
computer virtual --check    # 是否处于虚拟机
virt-what                   # 检测虚拟化平台
systemd-detect-virt        # systemd检测

# LXC
lxc-ls -f

# Docker
docker info
docker stats
```

### 容器资源
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## 电源与电池（笔记本）

```bash
computer power             # 电源状态
upower -e                  # 所有电源设备
upower -i /org/freedesktop/UPower/devices/battery_BAT0  # 电池详情
cat /sys/class/power_supply/BAT0/capacity  # 电量百分比
cat /sys/class/power_supply/BAT0/status    # 状态
```

**功耗监控**
```bash
powerstat -R 10 5          # 10秒间隔5次功耗样本
sensors | grep -i "power"  # 功耗（某些传感器）
```

---

## 安全与权限

### 硬件访问权限
```bash
# 设备文件权限
ls -l /dev/sda
ls -l /dev/mem

# 需要root的设备操作
sudo smartctl -a /dev/sda
sudo hdparm -I /dev/sda

# 权限最小化
chmod 660 device_file
chown root:dialout device_file
```

### 安全启动
```bash
computer secureboot --status  # Secure Boot状态
mokutil --sb-state             # 验证状态
```

---

## 自动化与脚本

### 系统信息脚本
```bash
#!/usr/bin/env bash
# computer-report - 生成系统报告
computer summary --format json > system_report_$(hostname)_$(date +%F).json
computer hardware --export hardware.html
```

### 定时健康检查
```bash
# cron每日报告
0 8 * * * /usr/local/bin/computer health --email admin@example.com
```

### 异常检测
```bash
computer monitor --alert "CPU>90% for 5m" --notify slack
```

---

## 跨平台差异

| 命令 | Linux | macOS | Windows |
|------|-------|-------|---------|
| CPU信息 | lscpu | sysctl | Get-WmiObject |
| 内存 | free -h | vm_stat | Get-Counter |
| 磁盘SMART | smartctl | smartctl (需安装) | wmic diskdrive |
| 温度 | sensors | powermetrics | CoreTemp（第三方）|
| 驱动 | lspci -k | system_profiler SPUSBDataType | driverquery |

---

## Computer vs 其他Skills

| Skill | 范围 | 对比Computer |
|-------|------|--------------|
| **i (Info)** | 信息查询 | Computer更底层，包含优化、诊断、计算 |
| **l (List)** | 列出项目 | Computer提供性能和硬件特定列表 |
| **0 (Zero)** | 初始化 | Computer关注实际硬件状态和归零管理 |
| **m (Move)** | 移动/管理包 | Computer管理硬件资源和性能 |

> **Computer 是 i 的进化版，l 的深层版，0 的监控版，m 的硬件版。**

---

## 哲学层面

Computer Skill不仅仅是工具集合，它代表**人類與機器的對話**：

- **控制**：不是被动使用，而是主动管理
- **理解**：不只看表面指标，要看底层原理
- **优化**：从能用到高效，从高效到卓越
- **诊断**：从现象到根因，从根因到解决
- **敬畏**：硬件是物理世界，不可藐视其极限

---

## 快速命令参考

```
computer summary        # 系统摘要
computer hardware       # 硬件详情
computer cpu            # CPU信息
computer memory         # 内存状态
computer disk           # 磁盘情况
computer temp           # 温度监控
computer monitor        # 实时监控
computer benchmark      # 性能测试
computer optimize       # 优化建议
computer diagnose       # 自动诊断
computer report --json  # 生成报告
computer power          # 电源检查
computer network        # 网络接口
computer gpu            # 显卡信息
```

---

## 终极提示

1. **查看手册**
   ```bash
   computer --help
   computer [command] --help
   ```

2. **输出格式**
   ```bash
   computer summary --format json   # JSON输出
   computer summary --format yaml   # YAML输出
   computer summary --format html   # HTML报告
   ```

3. **远程计算机**
   ```bash
   computer remote --host server01 --command "summary"
   ssh admin@server01 "computer summary"
   ```

---

> **Computer Skill 让你成为机器的主人，而不是奴隶。**  
> 从知道存在，到理解原理，到主动调优，最终与机器合一。

---

**最后一句话**:  
当你能**听见**硬盘的磁头移动，**看见**CPU缓存的行命中，**感受**内存带宽的流动，你就真正理解了Computer Skill的真谛。
