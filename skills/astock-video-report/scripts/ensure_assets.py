#!/usr/bin/env python3
"""
ensure_assets.py — 检查并自动下载 skill 所需的静态资产（字体、BGM）

用法：
  - 其他脚本 import: from ensure_assets import ensure_all
  - 直接运行: python3 ensure_assets.py

资产存放于 skill 的 assets/ 目录下。如果已存在则跳过下载。
"""
import os, sys, urllib.request
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
ASSETS_DIR = SKILL_ROOT / 'assets'

# ── 资产清单 ──────────────────────────────────────────
# 格式: (相对路径, 下载URL, 预期大小下限bytes, 描述)
ASSETS = [
    {
        'path': 'fonts/NotoSansSC-Regular.ttf',
        'urls': [
            'https://cdn.jsdelivr.net/fontsource/fonts/noto-sans-sc@latest/chinese-simplified-400-normal.woff2',
            'https://cdn.jsdelivr.net/gh/fontsource/font-files@main/fonts/google/noto-sans-sc/chinese-simplified-400-normal.woff2',
            'https://github.com/eddiexux/astock-video-report-assets/releases/download/v1.0.0/NotoSansSC-Regular.woff2',
        ],
        'min_size': 500_000,
        'desc': 'Noto Sans SC 中文字体 (SIL OFL 1.1)',
        'post_process': 'woff2_to_ttf',
    },
    {
        'path': 'bgm/eliveta-technology-474054.mp3',
        'urls': [
            'https://github.com/eddiexux/astock-video-report-assets/releases/download/v1.0.0/eliveta-technology-474054.mp3',
        ],
        'manual_fallback': '如自动下载失败，请从 https://pixabay.com/music/ 搜索 "eliveta technology" 手动下载，放入 assets/bgm/ 目录',
        'min_size': 4_000_000,
        'desc': 'BGM 音乐 (Pixabay Content License)',
        'post_process': None,
    },
]

def download_file(url, dest, desc=''):
    """下载文件，带进度提示"""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f'  ⬇️  正在下载 {desc or os.path.basename(dest)}...')
    print(f'     来源: {url}')
    try:
        urllib.request.urlretrieve(url, dest)
        size_mb = os.path.getsize(dest) / 1024 / 1024
        print(f'  ✅ 下载完成 ({size_mb:.1f} MB)')
        return True
    except Exception as e:
        print(f'  ❌ 下载失败: {e}')
        if os.path.exists(dest):
            os.remove(dest)
        return False

def woff2_to_ttf(woff2_path):
    """将 woff2 字体转换为 ttf（Pillow 不支持 woff2）"""
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        print('  ⚠️  需要 fonttools 来转换字体格式，正在安装...')
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'fonttools', 'brotli', '-q'])
        from fontTools.ttLib import TTFont

    ttf_path = str(woff2_path).replace('.woff2', '.ttf') if '.woff2' in str(woff2_path) else str(woff2_path) + '.converted'
    
    # 先检查是否确实是 woff2
    with open(woff2_path, 'rb') as f:
        sig = f.read(4)
    
    if sig == b'wOF2':
        print('  🔄 转换 woff2 → ttf...')
        font = TTFont(str(woff2_path))
        font.flavor = None
        font.save(str(woff2_path))  # 直接覆盖
        print('  ✅ 字体转换完成')
    else:
        print('  ✅ 字体已是 TTF 格式，无需转换')

def ensure_asset(asset):
    """确保单个资产存在，支持多 URL fallback"""
    dest = ASSETS_DIR / asset['path']
    
    if dest.exists() and dest.stat().st_size >= asset['min_size']:
        return True
    
    if dest.exists():
        print(f'  ⚠️  {asset["path"]} 文件异常（过小），重新下载')
        dest.unlink()
    
    # 支持单个 url 或多个 urls
    urls = asset.get('urls', [asset['url']] if 'url' in asset else [])
    ok = False
    for url in urls:
        ok = download_file(url, str(dest), asset['desc'])
        if ok:
            break
        print(f'  🔄 尝试备用下载源...')
    
    if ok and asset.get('post_process') == 'woff2_to_ttf':
        woff2_to_ttf(dest)
    
    # 验证
    if dest.exists() and dest.stat().st_size >= asset['min_size']:
        return True
    
    # 转换后的文件可能大小变化，放宽检查
    if dest.exists() and dest.stat().st_size > 0:
        return True
        
    print(f'  ❌ {asset["path"]} 资产不可用')
    if asset.get('manual_fallback'):
        print(f'  💡 {asset["manual_fallback"]}')
    return False

def ensure_all():
    """确保所有资产就绪，返回 (成功数, 总数)"""
    total = len(ASSETS)
    ok = 0
    need_download = []
    
    for asset in ASSETS:
        dest = ASSETS_DIR / asset['path']
        if dest.exists() and dest.stat().st_size > 0:
            ok += 1
        else:
            need_download.append(asset)
    
    if not need_download:
        return ok, total
    
    print(f'\n📦 需要下载 {len(need_download)} 个资产文件...')
    for asset in need_download:
        if ensure_asset(asset):
            ok += 1
    
    print(f'\n📦 资产检查完成: {ok}/{total}')
    return ok, total

def ensure_font():
    """仅确保字体可用，返回字体路径或 None"""
    font_asset = next(a for a in ASSETS if 'font' in a['path'].lower())
    dest = ASSETS_DIR / font_asset['path']
    if dest.exists() and dest.stat().st_size > 0:
        return str(dest)
    if ensure_asset(font_asset):
        return str(dest)
    return None

def ensure_bgm():
    """仅确保 BGM 可用，返回 BGM 路径或 None"""
    bgm_asset = next(a for a in ASSETS if 'bgm' in a['path'].lower())
    dest = ASSETS_DIR / bgm_asset['path']
    if dest.exists() and dest.stat().st_size > 0:
        return str(dest)
    if ensure_asset(bgm_asset):
        return str(dest)
    return None

if __name__ == '__main__':
    print('🔍 检查 astock-video-report 资产文件...\n')
    ok, total = ensure_all()
    if ok == total:
        print('\n✅ 所有资产就绪！')
    else:
        print(f'\n⚠️  {total - ok} 个资产缺失，部分功能可能受限')
        print('   可手动下载后放入 assets/ 目录')
        sys.exit(1)
