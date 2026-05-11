from io import BytesIO
from zipfile import ZipFile

import requests


__all__ = [
    "save_zip_stream",
]


def save_zip_stream(url: str, tick_file_dir: str) -> None:
    """
    下载并保存 tick 压缩包

    Args:
        url: 下载地址
        tick_file_dir: 保存文件夹
    """

    r = requests.get(url, headers={"User-Agent": "PythonGO BackTesting"})
    
    zip_file = ZipFile(BytesIO(r.content))

    for zf in zip_file.namelist():
        zip_file.extract(zf, tick_file_dir)
    
    zip_file.close()
