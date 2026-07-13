#!/usr/bin/env python3
"""
extract_nav.py - Navigation Graph 专项提取工具
从 Android Navigation Graph XML 中提取完整的页面路由图

用法:
    python3 extract_nav.py <res/navigation 目录路径>
    python3 extract_nav.py /Users/xxx/MyApp/src/main/res/navigation
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ANDROID_NS = 'http://schemas.android.com/apk/res/android'
RES_AUTO_NS = 'http://schemas.android.com/apk/res-auto'


def _a(attr: str) -> str:
    return f'{{{ANDROID_NS}}}{attr}'


def _r(attr: str) -> str:
    return f'{{{RES_AUTO_NS}}}{attr}'


def clean_id(raw: str) -> str:
    return raw.replace('@+id/', '').replace('@id/', '')


def extract_nav_graph(nav_file: Path) -> dict:
    """解析单个 Navigation Graph 文件"""
    tree = ET.parse(nav_file)
    root = tree.getroot()

    start_dest = clean_id(root.get(_a('startDestination'), ''))
    if not start_dest:
        start_dest = clean_id(root.get(_r('startDestination'), ''))

    destinations = {}
    edges = []

    def process_node(node, parent_id=None):
        tag_raw = node.tag
        tag = tag_raw.split('}')[-1] if '}' in tag_raw else tag_raw

        if tag not in ('fragment', 'activity', 'dialog', 'navigation', 'include'):
            return

        dest_id = clean_id(node.get(_a('id'), '') or node.get(_r('id'), ''))
        dest_name = node.get(_a('name'), '')
        dest_label = node.get(_a('label'), '')

        if dest_id:
            destinations[dest_id] = {
                'id': dest_id,
                'name': dest_name,
                'label': dest_label,
                'type': tag,
                'isStartDestination': dest_id == start_dest,
                'arguments': [],
                'deepLinks': [],
            }

            # arguments
            for arg in node.findall(f'{{{RES_AUTO_NS}}}argument'):
                arg_name = arg.get(_a('name'), '')
                arg_type = arg.get(_r('argType'), 'string')
                arg_default = arg.get(_r('defaultValue'), '')
                destinations[dest_id]['arguments'].append({
                    'name': arg_name,
                    'type': arg_type,
                    'defaultValue': arg_default,
                })

            # deepLinks
            for dl in node.findall(f'{{{RES_AUTO_NS}}}deepLink'):
                dl_uri = dl.get(_r('uri'), '')
                destinations[dest_id]['deepLinks'].append(dl_uri)
            for dl in node.findall('deepLink'):
                dl_uri = dl.get(_a('uri'), '')
                if dl_uri:
                    destinations[dest_id]['deepLinks'].append(dl_uri)

            # actions (edges)
            for action in list(node.findall(f'{{{RES_AUTO_NS}}}action')) + list(node.findall('action')):
                action_id = clean_id(action.get(_a('id'), '') or action.get(_r('id'), ''))
                action_dest_raw = (action.get(_r('destination'), '') or
                                   action.get(_a('destination'), ''))
                action_dest = clean_id(action_dest_raw)
                pop_up_to = clean_id(action.get(_r('popUpTo'), '') or action.get(_a('popUpTo'), ''))
                pop_inclusive = action.get(_r('popUpToInclusive'), 'false') == 'true'

                if dest_id and action_dest:
                    edges.append({
                        'from': dest_id,
                        'to': action_dest,
                        'actionId': action_id,
                        'popUpTo': pop_up_to,
                        'popUpToInclusive': pop_inclusive,
                    })

        # 递归处理嵌套（nested navigation）
        for child in node:
            process_node(child, dest_id)

    for child in root:
        process_node(child)

    return {
        'file': nav_file.stem,
        'startDestination': start_dest,
        'destinations': list(destinations.values()),
        'edges': edges,
    }


def extract_all_nav_graphs(nav_dir: str) -> list:
    """提取目录下所有 Navigation Graph"""
    nav_path = Path(nav_dir)
    if not nav_path.exists():
        print(f"❌ 目录不存在：{nav_dir}")
        return []

    results = []
    xml_files = sorted(nav_path.glob('*.xml'))
    print(f"🔍 找到 {len(xml_files)} 个 Navigation Graph 文件")

    for nav_file in xml_files:
        try:
            graph = extract_nav_graph(nav_file)
            results.append(graph)
            print(f"  ✅ {nav_file.name}: {len(graph['destinations'])} 个目的地，{len(graph['edges'])} 条边")
        except ET.ParseError as e:
            print(f"  ❌ 解析失败：{nav_file.name} ({e})")

    return results


def print_route_summary(graphs: list):
    """打印路由图摘要"""
    print("\n📊 Navigation Graph 摘要")
    print("=" * 60)
    for graph in graphs:
        print(f"\n📄 {graph['file']}.xml")
        print(f"   起始页面: {graph['startDestination']}")
        print(f"   目的地数量: {len(graph['destinations'])}")
        print(f"   路由边数量: {len(graph['edges'])}")

        if graph['destinations']:
            print("   目的地列表:")
            for dest in graph['destinations']:
                marker = "🏠" if dest['isStartDestination'] else "  "
                print(f"     {marker} [{dest['type']}] {dest['id']} → {dest['name']}")

        if graph['edges']:
            print("   路由关系:")
            for edge in graph['edges'][:10]:  # 最多显示 10 条
                print(f"     {edge['from']} ──({edge['actionId']})-→ {edge['to']}")
            if len(graph['edges']) > 10:
                print(f"     ... 还有 {len(graph['edges']) - 10} 条路由")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 extract_nav.py <res/navigation目录路径>")
        print("示例: python3 extract_nav.py /Users/xxx/MyApp/src/main/res/navigation")
        sys.exit(1)

    nav_dir = os.path.expanduser(sys.argv[1])

    # 如果传入的是项目根目录，自动查找 navigation 目录
    if not os.path.basename(nav_dir) == 'navigation':
        candidate = os.path.join(nav_dir, 'src', 'main', 'res', 'navigation')
        if os.path.exists(candidate):
            nav_dir = candidate
            print(f"📁 自动定位到：{nav_dir}")

    graphs = extract_all_nav_graphs(nav_dir)

    if not graphs:
        print("未找到 Navigation Graph 文件")
        sys.exit(0)

    print_route_summary(graphs)

    # 保存结果
    output_path = os.path.join(os.path.dirname(nav_dir), 'nav-graphs.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graphs, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 结果已保存到：{output_path}")

    # stdout 输出
    print("\n--- NAV_GRAPHS_JSON ---")
    print(json.dumps(graphs, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
