#!/opt/anaconda3/bin/python3
"""
增量同步脚本 - 扫描文件变化并更新 Khoj 知识库
支持进度显示、增量更新、多编码支持和错误详情记录
"""

import argparse
import json
import os
import sys
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional

try:
    import requests
except ImportError:
    print("错误: requests 未安装")
    print("请运行: pip install requests")
    sys.exit(1)

try:
    from markitdown import MarkItDown
except ImportError:
    print("错误: markitdown 未安装")
    print("请运行: pip install 'markitdown[xlsx,pptx]'")
    sys.exit(1)

try:
    import base64
    HAS_BASE64 = True
except ImportError:
    HAS_BASE64 = False


KHOJ_URL = os.environ.get("KHOJ_URL", "http://localhost:42110")
KHOJ_API_KEY = os.environ.get("KHOJ_API_KEY", "")

SUPPORTED_FORMATS = {'.xlsx', '.xls', '.pptx', '.ppt', '.docx', '.doc', '.pdf', '.md', '.txt', '.csv'}
SYNC_STATE_FILE = Path.home() / ".khoj" / "sync_state.json"
LOG_FILE = Path.home() / ".khoj" / "sync.log"

# 配置
MAX_FILE_SIZE_MB = 1000  # 最大文件大小限制（MB）
CONVERSION_TIMEOUT = 600  # 转换超时时间（秒）
API_TIMEOUT = 600  # API 超时时间（秒）

# 本地 OCR 配置（使用 Tesseract，无需云 API）
OCR_LANGUAGES = os.environ.get("OCR_LANGUAGES", "chi_sim+eng")  # 中文简体 + 英文
OCR_DPI = int(os.environ.get("OCR_DPI", "200"))  # OCR 分辨率
OCR_MAX_PAGES = int(os.environ.get("OCR_MAX_PAGES", "20"))  # 最大处理页数

# MIME 类型映射
MIME_TYPES = {
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.doc': 'application/msword',
    '.pdf': 'application/pdf',
    '.md': 'text/markdown',
    '.txt': 'text/plain',
    '.csv': 'text/csv',
}


class TimeoutError(Exception):
    """超时错误"""
    pass


def timeout_handler(signum, frame):
    """超时信号处理器"""
    raise TimeoutError("操作超时")


def with_timeout(seconds):
    """超时装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 设置信号处理器
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            return result
        return wrapper
    return decorator


class ProgressBar:
    """进度条显示"""
    
    def __init__(self, total: int, width: int = 40):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, current: int, message: str = ""):
        self.current = current
        percent = current / self.total if self.total > 0 else 0
        filled = int(self.width * percent)
        bar = '=' * filled + '>' + ' ' * (self.width - filled - 1)
        
        line = f"\r[{bar}] {percent*100:.1f}% ({current}/{self.total})"
        if message:
            line += f" {message[:30]}"
        
        print(line, end='', flush=True)
    
    def finish(self):
        print()


class SyncState:
    """同步状态管理"""
    
    def __init__(self, state_file: Path = SYNC_STATE_FILE):
        self.state_file = state_file
        self.state: Dict[str, dict] = {}
        self.load()
    
    def load(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except:
                self.state = {}
    
    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def get_file_hash(self, file_path: Path) -> str:
        """计算文件哈希（修改时间 + 大小）"""
        stat = file_path.stat()
        return f"{stat.st_mtime}_{stat.st_size}"
    
    def needs_sync(self, file_path: Path) -> bool:
        """检查文件是否需要同步"""
        key = str(file_path)
        current_hash = self.get_file_hash(file_path)
        
        if key not in self.state:
            return True
        
        # 如果之前失败，应该重试
        if not self.state[key].get('success', True):
            return True
        
        return self.state[key].get('hash') != current_hash
    
    def mark_synced(self, file_path: Path, success: bool = True, error: str = ""):
        """标记文件已同步"""
        key = str(file_path)
        self.state[key] = {
            'hash': self.get_file_hash(file_path),
            'last_sync': datetime.now().isoformat(),
            'success': success,
            'error': error if error else None
        }
    
    def remove_file(self, file_path: Path):
        """移除文件记录"""
        key = str(file_path)
        if key in self.state:
            del self.state[key]


class KhojSyncClient:
    """Khoj 同步客户端"""
    
    def __init__(self, base_url: str = KHOJ_URL):
        self.base_url = base_url.rstrip('/')
        self.headers = {}
        if KHOJ_API_KEY:
            self.headers["Authorization"] = f"Bearer {KHOJ_API_KEY}"
    
    def is_running(self) -> bool:
        """检查服务是否运行"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_indexed_files(self) -> Set[str]:
        """获取已索引的文件列表"""
        try:
            response = requests.get(
                f"{self.base_url}/api/content",
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return {item.get('file', '') for item in data if isinstance(data, list)}
        except:
            pass
        return set()
    
    def index_file(self, file_path: Path, converted_content: Optional[str] = None, verbose: bool = False) -> Tuple[bool, str]:
        """索引单个文件
        
        Returns:
            (success, error_message)
        """
        try:
            # 获取 MIME 类型
            ext = file_path.suffix.lower()
            mime_type = MIME_TYPES.get(ext, 'application/octet-stream')
            
            if converted_content:
                files = {'files': (file_path.name, converted_content, mime_type)}
            else:
                with open(file_path, 'rb') as f:
                    files = {'files': (file_path.name, f.read(), mime_type)}
            
            response = requests.patch(
                f"{self.base_url}/api/content",
                headers=self.headers,
                files=files,
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                return True, ""
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                if verbose:
                    print(f"\n  API 错误: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.Timeout:
            return False, f"请求超时（{API_TIMEOUT}秒）"
        except Exception as e:
            return False, str(e)


def scan_files(directory: Path) -> List[Path]:
    """扫描目录下的支持文件"""
    files = []
    for ext in SUPPORTED_FORMATS:
        files.extend(directory.rglob(f'*{ext}'))
    return sorted(files)


def read_text_with_fallback(file_path: Path) -> Tuple[bool, str]:
    """使用多种编码尝试读取文本文件
    
    Returns:
        (success, content_or_error)
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    for encoding in encodings:
        try:
            content = file_path.read_text(encoding=encoding)
            return True, content
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            return False, f"读取错误: {e}"
    
    return False, "无法识别文件编码（尝试了 utf-8, gbk, gb2312, latin-1）"


def convert_file_with_timeout(file_path: Path, md: MarkItDown, timeout: int = CONVERSION_TIMEOUT) -> Tuple[bool, str]:
    """带超时的文件转换
    
    Returns:
        (success, content_or_error)
    """
    try:
        # 设置超时
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = md.convert(file_path)
            content = result.text_content
            
            # 验证内容
            if not content or len(content.strip()) == 0:
                # 如果是PDF且内容为空，可能是扫描版PDF，尝试本地OCR处理
                if file_path.suffix.lower() == '.pdf':
                    return process_scanned_pdf_with_ocr(file_path)
                return False, "转换结果为空"
            
            return True, content
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            
    except TimeoutError:
        return False, f"转换超时（{timeout}秒）- 文件可能太大或太复杂"
    except Exception as e:
        error_str = str(e)
        # 检查是否是 xlsx 样式错误，尝试用 pandas 回退
        if 'Fill' in error_str or 'TypeError' in error_str:
            return try_xlsx_with_pandas(file_path)
        return False, f"转换错误: {error_str[:200]}"


def process_scanned_pdf_with_ocr(file_path: Path) -> Tuple[bool, str]:
    """使用本地 OCR (Tesseract) 处理扫描版 PDF
    
    将 PDF 页面转换为图片，然后使用 Tesseract OCR 提取文本内容
    无需云 API，完全本地运行
    
    Returns:
        (success, content_or_error)
    """
    try:
        # 使用 pdf2image 将 PDF 转换为图片
        try:
            from pdf2image import convert_from_path
        except ImportError:
            return False, "需要安装 pdf2image: pip install pdf2image"
        
        # 使用 pytesseract 进行 OCR
        try:
            import pytesseract
        except ImportError:
            return False, "需要安装 pytesseract: pip install pytesseract"
        
        # 转换 PDF 为图片
        pages = convert_from_path(
            file_path, 
            first_page=1, 
            last_page=OCR_MAX_PAGES, 
            dpi=OCR_DPI
        )
        
        if not pages:
            return False, "PDF 无法转换为图片"
        
        content_parts = []
        
        for i, page_image in enumerate(pages, 1):
            # 使用 Tesseract 进行 OCR
            try:
                text = pytesseract.image_to_string(
                    page_image, 
                    lang=OCR_LANGUAGES
                )
                
                if text and text.strip():
                    content_parts.append(f"## Page {i}\n\n{text.strip()}\n\n")
                else:
                    content_parts.append(f"## Page {i}\n\n[OCR 未识别到文字]\n\n")
            except Exception as e:
                content_parts.append(f"## Page {i}\n\n[OCR 处理错误: {str(e)[:50]}]\n\n")
        
        if not content_parts:
            return False, "OCR 未能提取任何内容"
        
        content = "".join(content_parts)
        return True, content
        
    except Exception as e:
        return False, f"OCR 处理错误: {str(e)[:100]}"


def convert_doc_with_libreoffice(file_path: Path) -> Tuple[bool, str]:
    """使用 LibreOffice 将 .doc 文件转换为文本
    
    Returns:
        (success, content_or_error)
    """
    import subprocess
    import tempfile
    import shutil
    
    try:
        # 检查 LibreOffice 是否可用
        soffice_path = shutil.which('soffice')
        if not soffice_path:
            return False, "需要安装 LibreOffice: brew install libreoffice"
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 使用 LibreOffice 转换为 txt
            result = subprocess.run(
                [soffice_path, '--headless', '--convert-to', 'txt:Text', 
                 '--outdir', temp_dir, str(file_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return False, f"LibreOffice 转换失败: {result.stderr[:100]}"
            
            # 读取转换后的文件
            txt_file = Path(temp_dir) / (file_path.stem + '.txt')
            if txt_file.exists():
                content = txt_file.read_text(encoding='utf-8', errors='replace')
                if content.strip():
                    return True, content
                return False, "转换结果为空"
            else:
                return False, "转换后的文件不存在"
                
    except subprocess.TimeoutExpired:
        return False, "LibreOffice 转换超时"
    except Exception as e:
        return False, f"转换错误: {str(e)[:100]}"


def try_xlsx_with_pandas(file_path: Path) -> Tuple[bool, str]:
    """使用直接 XML 提取读取 xlsx 文件（作为 markitdown 的回退方案）
    
    用于处理样式损坏的 xlsx 文件，直接从 ZIP 中提取数据
    
    Returns:
        (success, content_or_error)
    """
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        
        ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        with zipfile.ZipFile(file_path, 'r') as z:
            # 读取共享字符串
            shared_strings = []
            shared_strings_file = 'xl/sharedStrings.xml'
            if shared_strings_file in z.namelist():
                with z.open(shared_strings_file) as f:
                    for event, elem in ET.iterparse(f):
                        if elem.tag == '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t':
                            shared_strings.append(elem.text or '')
                        elem.clear()
            
            # 读取工作表
            content_parts = []
            max_rows = 500  # 限制行数
            max_cols = 50   # 限制列数
            
            for name in sorted(z.namelist()):
                if name.startswith('xl/worksheets/') and name.endswith('.xml'):
                    sheet_name = name.split('/')[-1].replace('.xml', '')
                    content_parts.append(f"## {sheet_name}\n")
                    
                    with z.open(name) as f:
                        tree = ET.parse(f)
                        root = tree.getroot()
                        
                        rows = root.findall('.//ns:row', ns)
                        rows_content = []
                        
                        for i, row in enumerate(rows):
                            if i >= max_rows:
                                rows_content.append(f"... (truncated at {max_rows} rows)")
                                break
                            
                            cells = row.findall('ns:c', ns)
                            row_values = []
                            
                            for j, cell in enumerate(cells):
                                if j >= max_cols:
                                    break
                                
                                cell_type = cell.get('t', '')
                                value_elem = cell.find('ns:v', ns)
                                
                                if value_elem is not None:
                                    value = value_elem.text or ''
                                    if cell_type == 's' and value.isdigit():
                                        idx = int(value)
                                        if idx < len(shared_strings):
                                            value = shared_strings[idx]
                                    row_values.append(value[:100])  # 限制单元格内容长度
                                else:
                                    row_values.append('')
                            
                            if row_values:
                                rows_content.append(' | '.join(row_values))
                        
                        if rows_content:
                            content_parts.append('\n'.join(rows_content))
                        content_parts.append("\n")
            
            if not content_parts:
                return False, "工作表为空"
            
            content = "\n".join(content_parts)
            return True, content
            
    except Exception as e:
        return False, f"XML 提取失败: {str(e)[:100]}"


def log_message(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass


def sync_directory(
    input_dir: str,
    output_dir: str = None,
    full_sync: bool = False,
    verbose: bool = False
) -> dict:
    """
    同步目录到 Khoj 知识库
    
    返回:
        {
            'total': 总文件数,
            'indexed': 已索引数,
            'synced': 本次同步数,
            'success': 成功数,
            'failed': 失败数,
            'skipped': 跳过数,
            'errors': [错误列表]
        }
    """
    input_path = Path(input_dir).expanduser().resolve()
    output_path = Path(output_dir).expanduser() if output_dir else Path("/tmp/khoj_sync")
    
    if not input_path.exists():
        print(f"错误: 目录不存在 - {input_dir}")
        sys.exit(1)
    
    # 检查服务
    client = KhojSyncClient()
    if not client.is_running():
        print("错误: Khoj 服务未运行")
        print(f"请先启动服务: khoj --anonymous-mode")
        sys.exit(1)
    
    # 初始化
    output_path.mkdir(parents=True, exist_ok=True)
    sync_state = SyncState()
    md = MarkItDown()
    
    # 扫描文件
    print(f"扫描目录: {input_path}")
    all_files = scan_files(input_path)
    print(f"找到文件: {len(all_files)} 个")
    
    # 获取已索引文件
    indexed_files = client.get_indexed_files()
    print(f"已索引: {len(indexed_files)} 个")
    
    # 确定需要同步的文件
    if full_sync:
        files_to_sync = all_files
    else:
        files_to_sync = [f for f in all_files if sync_state.needs_sync(f)]
    
    print(f"需要同步: {len(files_to_sync)} 个\n")
    
    if not files_to_sync:
        print("所有文件已是最新，无需同步")
        return {
            'total': len(all_files),
            'indexed': len(indexed_files),
            'synced': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    # 开始同步
    progress = ProgressBar(len(files_to_sync))
    success_count = 0
    failed_count = 0
    skipped_count = 0
    errors = []
    
    for i, file_path in enumerate(files_to_sync):
        progress.update(i + 1, file_path.name)
        
        # 检查文件大小
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            skip_msg = f"文件过大 ({file_size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB)"
            skipped_count += 1
            errors.append(f"{file_path.name}: {skip_msg}")
            sync_state.mark_synced(file_path, success=False, error=skip_msg)
            sync_state.save()
            log_message(f"跳过: {file_path.name} - {skip_msg}", "WARN")
            continue
        
        # 根据文件类型处理
        ext = file_path.suffix.lower()
        
        if ext in {'.xlsx', '.xls', '.pptx', '.ppt', '.docx', '.pdf'}:
            # Office/PDF 文件需要转换
            ok, content_or_error = convert_file_with_timeout(file_path, md)
            if not ok:
                failed_count += 1
                errors.append(f"{file_path.name}: {content_or_error}")
                sync_state.mark_synced(file_path, success=False, error=content_or_error)
                sync_state.save()
                log_message(f"转换失败: {file_path.name} - {content_or_error}", "ERROR")
                continue
            content = content_or_error
            
        elif ext == '.doc':
            # .doc 文件使用 LibreOffice 转换
            ok, content_or_error = convert_doc_with_libreoffice(file_path)
            if not ok:
                failed_count += 1
                errors.append(f"{file_path.name}: {content_or_error}")
                sync_state.mark_synced(file_path, success=False, error=content_or_error)
                sync_state.save()
                log_message(f"转换失败: {file_path.name} - {content_or_error}", "ERROR")
                continue
            content = content_or_error
            
        elif ext in {'.md', '.txt', '.csv'}:
            # 文本文件直接读取（支持多种编码）
            ok, content_or_error = read_text_with_fallback(file_path)
            if not ok:
                failed_count += 1
                errors.append(f"{file_path.name}: {content_or_error}")
                sync_state.mark_synced(file_path, success=False, error=content_or_error)
                sync_state.save()
                log_message(f"读取失败: {file_path.name} - {content_or_error}", "ERROR")
                continue
            content = content_or_error
        else:
            # 不支持的格式
            skip_msg = f"不支持的格式: {ext}"
            skipped_count += 1
            errors.append(f"{file_path.name}: {skip_msg}")
            sync_state.mark_synced(file_path, success=False, error=skip_msg)
            sync_state.save()
            continue
        
        # 索引文件
        success, error_msg = client.index_file(
            file_path, 
            content if ext in {'.xlsx', '.xls', '.pptx', '.ppt', '.docx', '.doc', '.pdf'} else None,
            verbose=verbose
        )
        
        if success:
            success_count += 1
            sync_state.mark_synced(file_path, success=True)
            if verbose:
                print(f"\n  ✓ {file_path.name}")
            log_message(f"成功: {file_path.name}", "INFO")
        else:
            failed_count += 1
            errors.append(f"{file_path.name}: {error_msg}")
            sync_state.mark_synced(file_path, success=False, error=error_msg)
            if verbose:
                print(f"\n  ✗ {file_path.name}: {error_msg}")
            log_message(f"索引失败: {file_path.name} - {error_msg}", "ERROR")
        
        # 每处理完一个文件就保存状态，防止中断丢失
        sync_state.save()
    
    progress.finish()
    
    # 输出结果
    print(f"\n{'='*50}")
    print(f"同步结果:")
    print(f"  ✓ 成功: {success_count}")
    print(f"  ✗ 失败: {failed_count}")
    print(f"  ⊘ 跳过: {skipped_count}")
    print(f"  总计: {success_count + failed_count + skipped_count}")
    
    if errors:
        print(f"\n错误/跳过列表 ({len(errors)} 个):")
        for err in errors[:20]:
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... 还有 {len(errors) - 20} 个")
    
    # 计算成功率
    total_processed = success_count + failed_count + skipped_count
    if total_processed > 0:
        success_rate = success_count / total_processed * 100
        print(f"\n成功率: {success_rate:.1f}%")
    
    print("\n同步完成！")
    log_message(f"同步完成: 成功 {success_count}, 失败 {failed_count}, 跳过 {skipped_count}", "INFO")
    
    return {
        'total': len(all_files),
        'indexed': len(indexed_files),
        'synced': len(files_to_sync),
        'success': success_count,
        'failed': failed_count,
        'skipped': skipped_count,
        'errors': errors
    }


def main():
    parser = argparse.ArgumentParser(
        description="增量同步文件到 Khoj 知识库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 增量同步（只同步有变化的文件）
  python sync.py ~/Documents
  
  # 全量同步（强制重新索引所有文件）
  python sync.py ~/Documents --full
  
  # 详细输出（显示每个文件的处理结果）
  python sync.py ~/Documents --verbose
  
  # 组合使用
  python sync.py ~/Documents --full --verbose
"""
    )
    
    parser.add_argument(
        "directory",
        help="要同步的目录路径"
    )
    parser.add_argument(
        "-o", "--output",
        default="/tmp/khoj_sync",
        help="转换后 Markdown 输出目录 (默认: /tmp/khoj_sync)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="强制全量同步（忽略增量判断）"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    sync_directory(
        args.directory,
        args.output,
        args.full,
        args.verbose
    )


if __name__ == "__main__":
    main()