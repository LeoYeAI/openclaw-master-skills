# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from pathlib import Path


def clean_tmp_dir(target_dir: str = None, hours: int = 6):
    """
    用于清理诊断报告临时文件。
    :param target_dir: 目标目录路径
    :param hours: 超过多少小时视为“旧文件”
    """
    try:
        target_path = Path(target_dir or _get_tmp_dir())
        if not target_path.exists():
            return

        if not target_path.is_dir():
            return

        cutoff_time = time.time() - hours * 3600

        for file_path in target_path.rglob('*'):
            if file_path.is_file():
                # 使用 st_mtime（最后修改时间）
                file_mtime = file_path.stat().st_mtime
                if file_mtime < cutoff_time:
                    try:
                        file_path.unlink(missing_ok=True)
                    except Exception as e:
                        pass
    except Exception as e:
        pass

def _get_tmp_dir():
    return str(Path(__file__).resolve().parent.parent.parent / "tmp")



