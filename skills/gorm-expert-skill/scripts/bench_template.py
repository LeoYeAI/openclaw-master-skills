#!/usr/bin/env python3
"""
bench_template.py — 为 GORM 函数生成 Go benchmark + pprof 启动代码
用法:
  python3 bench_template.py --func "GetUserByID(db *gorm.DB, id uint) (*User, error)"
  python3 bench_template.py --func "CreateOrder" --package service --file order_service.go
  python3 bench_template.py --scenario bulk_insert --table orders --batch 500

磁盘写入：默认输出到 stdout，仅在用户传 --output <file> 时写磁盘。
外部依赖：无（纯标准库，不调用任何 API）。
"""

import argparse
import re
import sys
from typing import Optional
from datetime import datetime

# ── 场景模板库 ───────────────────────────────────────────────────────────────
SCENARIO_TEMPLATES = {
    "query_by_id": {
        "desc": "主键查询性能",
        "setup": """
    // 预插入测试数据
    users := make([]User, 100)
    for i := range users {
        users[i] = User{Name: fmt.Sprintf("user_%d", i), Email: fmt.Sprintf("u%d@test.com", i)}
    }
    db.CreateInBatches(&users, 50)
    testID := users[0].ID""",
        "bench_body": """
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        var u User
        db.First(&u, testID)
    }""",
    },

    "query_with_preload": {
        "desc": "Preload 关联查询性能",
        "setup": """
    // 预插入用户和订单
    user := User{Name: "bench_user"}
    db.Create(&user)
    orders := make([]Order, 20)
    for i := range orders {
        orders[i] = Order{UserID: user.ID, Amount: int64(i * 100)}
    }
    db.CreateInBatches(&orders, 20)
    testID := user.ID""",
        "bench_body": """
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        var u User
        db.Preload("Orders").First(&u, testID)
    }""",
    },

    "bulk_insert": {
        "desc": "批量插入性能",
        "setup": "    batchSize := {batch}",
        "bench_body": """
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        b.StopTimer()
        records := make([]User, batchSize)
        for j := range records {
            records[j] = User{Name: fmt.Sprintf("u_%d_%d", i, j)}
        }
        b.StartTimer()
        db.CreateInBatches(&records, batchSize)
    }""",
    },

    "pagination": {
        "desc": "游标分页 vs OFFSET 对比",
        "setup": """
    // 插入 10000 条测试数据
    total := 10000
    for i := 0; i < total; i += 500 {
        batch := make([]User, 500)
        for j := range batch {
            batch[j] = User{Name: fmt.Sprintf("user_%d", i+j)}
        }
        db.CreateInBatches(&batch, 500)
    }""",
        "bench_body": """
    b.Run("CursorPagination", func(b *testing.B) {
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            var users []User
            db.Where("id > ?", 5000).Order("id").Limit(20).Find(&users)
        }
    })

    b.Run("OffsetPagination", func(b *testing.B) {
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            var users []User
            db.Offset(5000).Limit(20).Find(&users)
        }
    })""",
    },

    "update_compare": {
        "desc": "Save vs Updates(map) vs Update(单字段) 对比",
        "setup": """
    user := User{Name: "bench", Email: "bench@test.com"}
    db.Create(&user)""",
        "bench_body": """
    b.Run("Save_FullStruct", func(b *testing.B) {
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            user.Name = fmt.Sprintf("name_%d", i)
            db.Save(&user)
        }
    })

    b.Run("Updates_Map", func(b *testing.B) {
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            db.Model(&user).Updates(map[string]any{"name": fmt.Sprintf("name_%d", i)})
        }
    })

    b.Run("Update_SingleField", func(b *testing.B) {
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            db.Model(&user).Update("name", fmt.Sprintf("name_%d", i))
        }
    })""",
    },
}


def generate_custom_bench(func_sig: str, package: str) -> str:
    """根据函数签名生成 benchmark"""
    # 解析函数名
    func_name_m = re.match(r'(\w+)', func_sig.strip())
    func_name = func_name_m.group(1) if func_name_m else "TargetFunc"

    # 解析参数
    params_m = re.search(r'\(([^)]*)\)', func_sig)
    params_str = params_m.group(1) if params_m else ""
    params = [p.strip() for p in params_str.split(',') if p.strip()]

    # 构建调用参数
    call_args = []
    setup_lines = []
    for p in params:
        parts = p.split()
        if len(parts) < 2:
            continue
        pname, ptype = parts[0], parts[-1]
        if "gorm.DB" in ptype:
            call_args.append(pname)
        elif ptype in ("uint", "int", "int64", "uint64"):
            setup_lines.append(f"\tvar {pname} {ptype} = 1  // TODO: 设置测试 ID")
            call_args.append(pname)
        elif ptype == "string":
            setup_lines.append(f'\t{pname} := "test_value"  // TODO: 设置测试参数')
            call_args.append(pname)
        else:
            setup_lines.append(f"\tvar {pname} {ptype}  // TODO: 初始化测试数据")
            call_args.append(pname)

    setup_code = "\n".join(setup_lines) if setup_lines else "\t// TODO: 初始化测试数据"
    call_code = f'{package}.{func_name}({", ".join(call_args)})' if package else f'{func_name}({", ".join(call_args)})'

    return f'''func Benchmark{func_name}(b *testing.B) {{
    db := setupBenchDB(b)

{setup_code}

    b.ResetTimer()
    b.ReportAllocs()  // 报告内存分配次数
    for i := 0; i < b.N; i++ {{
        result, err := {call_code}
        if err != nil {{
            b.Fatal(err)
        }}
        _ = result
    }}
}}'''


def generate_full_file(
    package: str,
    func_sig: Optional[str],
    scenario: Optional[str],
    table: str,
    batch: int,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d")

    benchmarks = []
    if func_sig:
        benchmarks.append(generate_custom_bench(func_sig, ""))

    if scenario and scenario in SCENARIO_TEMPLATES:
        tmpl = SCENARIO_TEMPLATES[scenario]
        setup = tmpl["setup"].replace("{batch}", str(batch))
        bench_body = tmpl["bench_body"]
        func_name = "".join(w.capitalize() for w in scenario.split("_"))
        benchmarks.append(f'''// Benchmark{func_name} — {tmpl["desc"]}
func Benchmark{func_name}(b *testing.B) {{
    db := setupBenchDB(b)
{setup}

{bench_body}
}}''')

    bench_code = "\n\n".join(benchmarks) if benchmarks else '''func BenchmarkYourFunction(b *testing.B) {
    db := setupBenchDB(b)
    // TODO: 添加测试数据
    b.ResetTimer()
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        // TODO: 调用被测函数
    }
}'''

    return f'''// Code generated by bench_template.py on {now}
// 运行: go test -bench=. -benchmem -count=3 -cpuprofile=cpu.prof -memprofile=mem.prof
// 分析: go tool pprof -http=:8080 cpu.prof
package {package}

import (
\t"fmt"
\t"os"
\t"runtime/pprof"
\t"testing"

\t"gorm.io/driver/sqlite"
\t"gorm.io/gorm"
\t"gorm.io/gorm/logger"
)

// setupBenchDB 创建内存 SQLite DB（快速，适合基准测试）
// 如需测试 MySQL 真实性能，替换为 mysql.Open(dsn)
func setupBenchDB(b *testing.B) *gorm.DB {{
\tb.Helper()
\tdb, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{{
\t\tLogger:                 logger.Default.LogMode(logger.Silent),
\t\tSkipDefaultTransaction: true,
\t\tPrepareStmt:            true,
\t}})
\tif err != nil {{
\t\tb.Fatal("setupBenchDB:", err)
\t}}
\t// 迁移你的 Model
\t// db.AutoMigrate(&User{{}}, &Order{{}})

\tb.Cleanup(func() {{
\t\tsqlDB, _ := db.DB()
\t\tsqlDB.Close()
\t}})
\treturn db
}}

// BenchmarkMain 启动 pprof 采集（可选，需要时取消注释）
func BenchmarkMain(m *testing.M) {{
\t// CPU profile
\tcpuF, _ := os.Create("cpu.prof")
\tpprof.StartCPUProfile(cpuF)
\tdefer pprof.StopCPUProfile()

\tcode := m.Run()

\t// Memory profile
\tmemF, _ := os.Create("mem.prof")
\tpprof.WriteHeapProfile(memF)
\tmemF.Close()

\tos.Exit(code)
}}

{bench_code}
'''


def print_usage_tips(scenario: Optional[str], func_name: str) -> None:
    print("\n" + "─" * 60)
    print("📋 使用说明:")
    print()
    print("  # 运行 benchmark（-count=3 减少噪声，-benchtime=3s 延长采样）")
    print(f"  go test -bench=Benchmark{func_name} -benchmem -count=3 -benchtime=3s ./...")
    print()
    print("  # 同时采集 CPU / 内存 profile")
    print(f"  go test -bench=Benchmark{func_name} -benchmem \\")
    print("    -cpuprofile=cpu.prof -memprofile=mem.prof ./...")
    print()
    print("  # 可视化分析（浏览器打开火焰图）")
    print("  go tool pprof -http=:8080 cpu.prof")
    print("  go tool pprof -http=:8081 mem.prof")
    print()
    print("  # 对比两次结果（需要 benchstat）")
    print("  go install golang.org/x/perf/cmd/benchstat@latest")
    print("  go test -bench=. -count=10 > old.txt")
    print("  # ... 修改代码 ...")
    print("  go test -bench=. -count=10 > new.txt")
    print("  benchstat old.txt new.txt")
    print("─" * 60)


def main():
    parser = argparse.ArgumentParser(description="GORM Benchmark + pprof 模板生成器")
    parser.add_argument("--func", dest="func_sig", help="函数签名，如 'GetUser(db *gorm.DB, id uint) (*User, error)'")
    parser.add_argument("--scenario", choices=list(SCENARIO_TEMPLATES.keys()),
                        help=f"预设场景: {', '.join(SCENARIO_TEMPLATES.keys())}")
    parser.add_argument("--package", default="repository_test", help="Go package 名（默认 repository_test）")
    parser.add_argument("--table", default="users", help="主要测试表名（默认 users）")
    parser.add_argument("--batch", type=int, default=500, help="批量操作大小（默认 500）")
    parser.add_argument("--output", default="-", help="输出文件路径（默认 stdout）")
    args = parser.parse_args()

    if not args.func_sig and not args.scenario:
        parser.print_help()
        print("\n示例:")
        print('  python3 bench_template.py --func "GetUserByID(db *gorm.DB, id uint) (*User, error)"')
        print("  python3 bench_template.py --scenario bulk_insert --batch 200")
        print("  python3 bench_template.py --scenario pagination")
        sys.exit(1)

    code = generate_full_file(
        package=args.package,
        func_sig=args.func_sig,
        scenario=args.scenario,
        table=args.table,
        batch=args.batch,
    )

    if args.output == "-":
        print(code)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✅ 已生成: {args.output}")

    # 提取函数名用于提示
    func_name = "YourFunction"
    if args.func_sig:
        m = re.match(r'(\w+)', args.func_sig)
        if m:
            func_name = m.group(1)
    elif args.scenario:
        func_name = "".join(w.capitalize() for w in args.scenario.split("_"))

    print_usage_tips(args.scenario, func_name)



if __name__ == "__main__":
    main()
