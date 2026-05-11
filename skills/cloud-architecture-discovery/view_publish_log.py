#!/usr/bin/env python3
"""查看和管理发布记录"""
import json
from pathlib import Path

PUBLISH_LOG = Path(__file__).parent / "publish_log.json"

def main():
    if not PUBLISH_LOG.exists():
        print("❌ 发布记录文件不存在，尚未开始发布")
        return
    
    with open(PUBLISH_LOG, encoding="utf-8") as f:
        log_data = json.load(f)
    
    print("=" * 60)
    print("📊 发布统计")
    print("=" * 60)
    print(f"✅ 成功: {log_data['stats']['success']}")
    print(f"❌ 失败: {log_data['stats']['fail']}")
    print(f"📝 总计: {log_data['stats']['total']}")
    print()
    
    if log_data['stats']['success'] > 0:
        print("=" * 60)
        print("✅ 已成功发布的技能")
        print("=" * 60)
        for slug, info in sorted(log_data["skills"].items()):
            if info["status"] == "success":
                print(f"  {slug}")
                print(f"    名称: {info['name']}")
                print(f"    Token: #{info['token_index'] + 1}")
                print(f"    时间: {info['timestamp']}")
                print()
    
    if log_data['stats']['fail'] > 0:
        print("=" * 60)
        print("❌ 发布失败的技能（可重试）")
        print("=" * 60)
        for slug, info in sorted(log_data["skills"].items()):
            if info["status"] == "failed":
                print(f"  {slug}")
                print(f"    名称: {info['name']}")
                print(f"    Token: #{info['token_index'] + 1}")
                print(f"    时间: {info['timestamp']}")
                if info.get("error"):
                    print(f"    错误: {info['error'][:100]}")
                print()
    
    print("=" * 60)
    print("💡 提示")
    print("=" * 60)
    print(f"• 记录文件: {PUBLISH_LOG}")
    print(f"• 重新运行 batch_publish.py 可继续发布未成功的技能")
    print(f"• 如需重新发布已成功的技能，请编辑 {PUBLISH_LOG} 并删除对应条目")

if __name__ == "__main__":
    main()
