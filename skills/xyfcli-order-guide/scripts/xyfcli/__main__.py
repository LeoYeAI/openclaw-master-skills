"""CLI 入口点"""

import sys
from pathlib import Path

# 添加父目录到路径，允许直接运行
sys.path.insert(0, str(Path(__file__).parent.parent))

from xyfcli.main import app

if __name__ == "__main__":
    app()
