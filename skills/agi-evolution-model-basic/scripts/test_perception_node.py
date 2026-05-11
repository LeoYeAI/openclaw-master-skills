#!/usr/bin/env python3
"""
测试脚本 - 验证感知节点的所有新功能

基于：tool_use_spec.md 接口规范（2026版）
"""

import sys
import os
import json
import asyncio

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from perception_node import PerceptionNode, TOOL_REGISTRY


def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_result(result, indent=0):
    """打印结果"""
    print(json.dumps(result, indent=indent, ensure_ascii=False))


def test_basic_functionality():
    """测试基础功能"""
    print_section("1. 基础功能测试")

    node = PerceptionNode()

    # 测试所有工具
    tools_to_test = [
        ("web_search", {"query": "AGI evolution model"}),
        ("get_weather", {"location": "Shanghai", "unit": "celsius"}),
        ("calculator", {"expression": "10 * (5 + 3)"}),
        ("search_documents", {"query": "machine learning", "limit": 20}),
    ]

    for tool_name, params in tools_to_test:
        print(f"\n工具: {tool_name}")
        print(f"参数: {params}")
        result = node.call_tool(tool_name, params)
        print("结果:")
        print_result(result, indent=2)


def test_trace_id():
    """测试 Trace ID 全链路追踪"""
    print_section("2. Trace ID 全链路追踪测试")

    node = PerceptionNode()

    # 多次调用同一个工具，验证 trace_id 唯一性
    trace_ids = []
    for i in range(5):
        result = node.call_tool("get_weather", {"location": "Beijing"})
        trace_id = result.get('metadata', {}).get('trace_id')
        trace_ids.append(trace_id)
        print(f"调用 {i+1}: {trace_id}")

    # 验证所有 trace_id 都是唯一的
    unique_trace_ids = set(trace_ids)
    print(f"\n总共调用: {len(trace_ids)}")
    print(f"唯一 trace_id: {len(unique_trace_ids)}")
    print(f"是否全部唯一: {len(unique_trace_ids) == len(trace_ids)}")


def test_caching():
    """测试缓存功能"""
    print_section("3. 缓存功能测试")

    node = PerceptionNode()

    # 第一次调用（缓存未命中）
    print("\n第一次调用（缓存未命中）:")
    result1 = node.call_tool("get_weather", {"location": "Beijing"})
    cache_info = result1.get('metadata', {}).get('cache', {})
    print(f"缓存命中: {cache_info.get('hit', False)}")

    # 第二次调用（缓存命中）
    print("\n第二次调用（缓存命中）:")
    result2 = node.call_tool("get_weather", {"location": "Beijing"})
    cache_info = result2.get('metadata', {}).get('cache', {})
    print(f"缓存命中: {cache_info.get('hit', False)}")
    if cache_info.get('hit'):
        print(f"缓存时间: {cache_info.get('cached_at')}")
        print(f"TTL 剩余: {cache_info.get('ttl_remaining', 0):.1f} 秒")

    # 不同参数调用（缓存未命中）
    print("\n不同参数调用（缓存未命中）:")
    result3 = node.call_tool("get_weather", {"location": "Shanghai"})
    cache_info = result3.get('metadata', {}).get('cache', {})
    print(f"缓存命中: {cache_info.get('hit', False)}")


def test_retry_mechanism():
    """测试重试机制"""
    print_section("4. 重试机制测试")

    node = PerceptionNode()

    # 模拟网络错误（通过调用不存在的工具）
    print("\n调用不存在的工具（不重试）:")
    result = node.call_tool("nonexistent_tool", {"param": "value"})
    print(f"成功: {result.get('success')}")
    print(f"错误码: {result.get('error', {}).get('code')}")
    print(f"可重试: {result.get('error', {}).get('retryable', False)}")


def test_pagination():
    """测试分页功能"""
    print_section("5. 分页功能测试")

    node = PerceptionNode()

    # 测试 search_documents 的分页
    print("\n第一页（无 cursor）:")
    result1 = node.call_tool("search_documents", {
        "query": "AGI",
        "limit": 10
    })
    pagination = result1.get('data', {}).get('pagination', {})
    print(f"has_more: {pagination.get('has_more')}")
    print(f"total_count: {pagination.get('total_count')}")
    print(f"next_cursor: {pagination.get('next_cursor')}")

    print("\n第二页（有 cursor）:")
    if pagination.get('next_cursor'):
        result2 = node.call_tool("search_documents", {
            "query": "AGI",
            "limit": 10,
            "cursor": pagination['next_cursor']
        })
        pagination2 = result2.get('data', {}).get('pagination', {})
        print(f"has_more: {pagination2.get('has_more')}")
        print(f"next_cursor: {pagination2.get('next_cursor')}")


def test_observability():
    """测试可观测性"""
    print_section("6. 可观测性测试")

    node = PerceptionNode()

    # 调用一些工具
    for i in range(3):
        node.call_tool("get_weather", {"location": "Beijing"})

    # 获取指标
    metrics = node.get_metrics()
    print("\n可观测性指标:")
    print_result(metrics, indent=2)


def test_debug_mode():
    """测试调试模式"""
    print_section("7. 调试模式测试")

    node = PerceptionNode()

    print("\n正常模式:")
    result1 = node.call_tool("get_weather", {"location": "Beijing"})
    has_debug_info = 'debug_info' in result1
    print(f"包含调试信息: {has_debug_info}")

    print("\n调试模式:")
    result2 = node.call_tool("get_weather", {"location": "Beijing"}, debug=True)
    has_debug_info = 'debug_info' in result2
    print(f"包含调试信息: {has_debug_info}")
    if has_debug_info:
        print("\n调试信息:")
        print_result(result2.get('debug_info'), indent=2)


def test_error_handling():
    """测试错误处理"""
    print_section("8. 错误处理测试")

    node = PerceptionNode()

    # 测试各种错误情况
    error_cases = [
        ("缺少必需参数", "get_weather", {}),
        ("无效参数类型", "calculator", {"expression": "not a number"}),
        ("工具不存在", "unknown_tool", {"param": "value"}),
        ("分页参数无效", "search_documents", {"query": "test", "limit": 999}),
    ]

    for description, tool_name, params in error_cases:
        print(f"\n{description}:")
        result = node.call_tool(tool_name, params)
        print(f"成功: {result.get('success')}")
        print(f"状态: {result.get('status')}")
        if not result.get('success'):
            error = result.get('error', {})
            print(f"错误码: {error.get('code')}")
            print(f"错误消息: {error.get('message')}")
            print(f"可重试: {error.get('retryable', False)}")


def test_tool_registry():
    """测试工具注册表"""
    print_section("9. 工具注册表测试")

    print("\n注册的工具:")
    for tool_name, config in TOOL_REGISTRY.items():
        print(f"\n工具: {tool_name}")
        print(f"  描述: {config.description}")
        print(f"  版本: {config.version}")
        print(f"  可缓存: {config.cacheable}")
        print(f"  流式: {config.streaming}")
        print(f"  Token 预估: {config.estimated_tokens}")


async def test_streaming():
    """测试流式响应（模拟）"""
    print_section("10. 流式响应测试（模拟）")

    node = PerceptionNode()

    print("\n流式调用工具:")
    stream = node.call_tool_with_streaming("get_weather", {"location": "Beijing"})

    async for event in stream:
        print(f"\n事件: {event.get('event')}")
        if event.get('event') == 'tool_progress':
            data = event.get('data', {})
            print(f"  进度: {data.get('progress')}%")
            print(f"  消息: {data.get('message')}")
        elif event.get('event') == 'tool_result':
            print(f"  结果: {event.get('data', {}).get('success')}")
        elif event.get('event') == 'tool_error':
            print(f"  错误: {event.get('data', {}).get('error', {}).get('message')}")


def test_performance():
    """测试性能"""
    print_section("11. 性能测试")

    node = PerceptionNode()

    import time

    # 测试工具调用性能
    iterations = 100
    print(f"\n执行 {iterations} 次工具调用...")

    start_time = time.time()
    for i in range(iterations):
        node.call_tool("get_weather", {"location": "Beijing"})
    end_time = time.time()

    total_time = end_time - start_time
    avg_time = total_time / iterations

    print(f"总时间: {total_time:.3f} 秒")
    print(f"平均时间: {avg_time*1000:.3f} 毫秒")
    print(f"吞吐量: {iterations/total_time:.1f} 调用/秒")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  感知节点完整功能测试套件")
    print("  基于：tool_use_spec.md 接口规范（2026版）")
    print("="*70)

    try:
        # 运行所有测试
        test_basic_functionality()
        test_trace_id()
        test_caching()
        test_retry_mechanism()
        test_pagination()
        test_observability()
        test_debug_mode()
        test_error_handling()
        test_tool_registry()
        asyncio.run(test_streaming())
        test_performance()

        print("\n" + "="*70)
        print("  所有测试完成！")
        print("="*70)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
