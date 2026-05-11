#!/usr/bin/env python3
"""清理发布记录（用于重新开始）"""
import json
from pathlib import Path
from datetime import datetime

PUBLISH_LOG = Path(__file__).parent / "publish_log.json"

def main():
    if not PUBLISH_LOG.exists():
        print("✅ 发布记录文件不存在，无需清理")
        return
    
    # 备份现有记录
    backup_file = PUBLISH_LOG.parent / f"publish_log_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(PUBLISH_LOG, encoding="utf-8") as f:
        backup_data = f.read()
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(backup_data)
    print(f"✅ 已备份现有记录到: {backup_file}")
    
    # 清空记录
    empty_log = {
        "skills": {},
        "stats": {"success": 0, "fail": 0, "total": 0}
    }
    with open(PUBLISH_LOG, "w", encoding="utf-8") as f:
        json.dump(empty_log, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已清空发布记录: {PUBLISH_LOG}")
    print("💡 现在可以重新开始发布流程")

if __name__ == "__main__":
    main()
