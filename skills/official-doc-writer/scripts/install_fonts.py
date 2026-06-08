# -*- coding: utf-8 -*-
"""
公文字体安装脚本
用于安装GB/T 9704-2012标准所需的公文格式字体
"""

import os
import sys
import shutil
import platform
from pathlib import Path
from typing import List, Dict, Tuple


class FontInstaller:
    """字体安装器"""
    
    def __init__(self, fonts_dir: str = None):
        """
        初始化字体安装器
        
        Args:
            fonts_dir: 字体文件所在目录，默认为脚本所在目录的fonts子目录
        """
        if fonts_dir is None:
            self.fonts_dir = Path(__file__).parent.parent / "fonts"
        else:
            self.fonts_dir = Path(fonts_dir)
        
        self.system = platform.system()
        self.installed_fonts = []
        self.failed_fonts = []
        
        # 定义所需字体
        self.required_fonts = {
            "方正小标宋_GBK": {
                "files": ["FZXBSJW.TTF", "FZXBSJW_GB.TTF", "方正小标宋GBK.TTF", "方正小标宋_GBK.TTF"],
                "description": "用于发文机关标志、标题",
                "required": True
            },
            "仿宋_GB2312": {
                "files": ["SIMFANG.TTF", "FANGSONG.TTF"],
                "description": "用于正文、发文字号",
                "required": True
            },
            "黑体": {
                "files": ["SIMHEI.TTF", "HEITI.TTF"],
                "description": "用于一级标题、密级",
                "required": True
            },
            "楷体_GB2312": {
                "files": ["SIMKAI.TTF", "KAITI.TTF"],
                "description": "用于二级标题、签发人姓名",
                "required": True
            },
            "宋体": {
                "files": ["SIMSUN.TTF", "SONGTI.TTF", "SIMSUN.TTC", "simsun.ttc"],
                "description": "用于页码",
                "required": True
            }
        }
    
    def check_system_fonts(self) -> Dict[str, bool]:
        """
        检查系统已安装的字体
        
        Returns:
            字体名称到是否已安装的映射
        """
        installed = {}
        
        if self.system == "Windows":
            fonts_paths = [
                Path("C:/Windows/Fonts"),
                Path.home() / "AppData/Local/Microsoft/Windows/Fonts"
            ]
            for font_name, font_info in self.required_fonts.items():
                found = False
                for fonts_path in fonts_paths:
                    for font_file in font_info["files"]:
                        if (fonts_path / font_file).exists():
                            found = True
                            break
                    if found:
                        break
                installed[font_name] = found
        elif self.system == "Darwin":  # macOS
            fonts_paths = [
                Path("/Library/Fonts"),
                Path("/System/Library/Fonts"),
                Path.home() / "Library/Fonts"
            ]
            for font_name, font_info in self.required_fonts.items():
                found = False
                for fonts_path in fonts_paths:
                    for font_file in font_info["files"]:
                        if (fonts_path / font_file).exists():
                            found = True
                            break
                    if found:
                        break
                installed[font_name] = found
        else:  # Linux
            fonts_paths = [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts"
            ]
            for font_name, font_info in self.required_fonts.items():
                found = False
                for fonts_path in fonts_paths:
                    for font_file in font_info["files"]:
                        if (fonts_path / font_file).exists():
                            found = True
                            break
                    if found:
                        break
                installed[font_name] = found
        
        return installed
    
    def install_font(self, font_file: Path) -> bool:
        """
        安装单个字体文件
        
        Args:
            font_file: 字体文件路径
            
        Returns:
            是否安装成功
        """
        try:
            if self.system == "Windows":
                # Windows系统：复制到Windows\Fonts目录
                dest = Path("C:/Windows/Fonts") / font_file.name
                shutil.copy2(font_file, dest)
                
                # 注册字体（需要管理员权限）
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
                    0,
                    winreg.KEY_SET_VALUE
                )
                font_name = font_file.stem
                winreg.SetValueEx(key, font_name, 0, winreg.REG_SZ, str(dest))
                winreg.CloseKey(key)
                
            elif self.system == "Darwin":  # macOS
                # macOS系统：复制到用户字体目录
                dest = Path.home() / "Library/Fonts" / font_file.name
                shutil.copy2(font_file, dest)
                
            else:  # Linux
                # Linux系统：复制到用户字体目录
                dest_dir = Path.home() / ".fonts"
                dest_dir.mkdir(exist_ok=True)
                dest = dest_dir / font_file.name
                shutil.copy2(font_file, dest)
                
                # 更新字体缓存
                os.system("fc-cache -fv")
            
            return True
            
        except Exception as e:
            print(f"安装字体失败: {font_file.name}, 错误: {str(e)}")
            return False
    
    def copy_fonts_from_system(self) -> Dict[str, bool]:
        """
        从系统字体目录复制字体文件到skill的fonts目录
        
        Returns:
            字体名称到是否复制成功的映射
        """
        copied = {}
        
        # 定义系统字体目录列表
        if self.system == "Windows":
            system_fonts_paths = [
                Path("C:/Windows/Fonts"),
                Path.home() / "AppData/Local/Microsoft/Windows/Fonts"
            ]
        elif self.system == "Darwin":  # macOS
            system_fonts_paths = [
                Path("/Library/Fonts"),
                Path("/System/Library/Fonts"),
                Path.home() / "Library/Fonts"
            ]
        else:  # Linux
            system_fonts_paths = [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts"
            ]
        
        print(f"从系统字体目录复制字体文件...")
        print("-" * 60)
        
        # 确保fonts目录存在
        self.fonts_dir.mkdir(exist_ok=True)
        
        for font_name, font_info in self.required_fonts.items():
            copied[font_name] = False
            
            # 检查skill的fonts目录是否已有该字体
            skill_has_font = False
            for font_file in font_info["files"]:
                if (self.fonts_dir / font_file).exists():
                    skill_has_font = True
                    break
            
            if skill_has_font:
                print(f"  {font_name}: skill目录已存在，跳过")
                copied[font_name] = True
                continue
            
            # 从系统目录复制（遍历所有可能的目录）
            for system_fonts_path in system_fonts_paths:
                if not system_fonts_path.exists():
                    continue
                    
                for font_file in font_info["files"]:
                    system_font_path = system_fonts_path / font_file
                    if system_font_path.exists():
                        try:
                            dest_path = self.fonts_dir / font_file
                            shutil.copy2(system_font_path, dest_path)
                            print(f"  ✓ {font_name}: 从系统复制 {font_file}")
                            copied[font_name] = True
                            break
                        except Exception as e:
                            print(f"  ✗ {font_name}: 复制失败 - {str(e)}")
                
                if copied[font_name]:
                    break
        
        print("-" * 60)
        return copied
    
    def install_all_fonts(self) -> Tuple[List[str], List[str]]:
        """
        安装所有所需字体
        
        Returns:
            (成功安装的字体列表, 安装失败的字体列表)
        """
        print(f"字体文件目录: {self.fonts_dir}")
        print(f"操作系统: {self.system}")
        print("-" * 60)
        
        # 首先尝试从系统复制字体文件
        self.copy_fonts_from_system()
        
        # 检查系统已安装的字体
        installed = self.check_system_fonts()
        print("系统字体检查结果:")
        for font_name, is_installed in installed.items():
            status = "✓ 已安装" if is_installed else "✗ 未安装"
            print(f"  {font_name}: {status}")
        print("-" * 60)
        
        # 安装缺失的字体
        for font_name, font_info in self.required_fonts.items():
            if installed.get(font_name, False):
                print(f"跳过 {font_name}（已安装）")
                continue
            
            print(f"正在安装 {font_name}...")
            
            # 查找字体文件
            font_found = False
            for font_file in font_info["files"]:
                font_path = self.fonts_dir / font_file
                if font_path.exists():
                    if self.install_font(font_path):
                        self.installed_fonts.append(font_name)
                        font_found = True
                        print(f"  ✓ {font_file} 安装成功")
                        break
                    else:
                        print(f"  ✗ {font_file} 安装失败")
            
            if not font_found:
                self.failed_fonts.append(font_name)
                print(f"  ✗ 字体文件未找到")
        
        print("-" * 60)
        print(f"安装完成: {len(self.installed_fonts)} 个字体")
        if self.failed_fonts:
            print(f"安装失败: {len(self.failed_fonts)} 个字体")
            print("请手动下载并安装以下字体:")
            for font_name in self.failed_fonts:
                font_info = self.required_fonts[font_name]
                print(f"  - {font_name}: {font_info['description']}")
        
        return self.installed_fonts, self.failed_fonts
    
    def generate_font_list(self) -> str:
        """
        生成字体列表文档
        
        Returns:
            字体列表文档内容
        """
        content = []
        content.append("# 公文字体清单")
        content.append("")
        content.append("根据GB/T 9704-2012《党政机关公文格式》标准，公文生成需要以下字体：")
        content.append("")
        content.append("| 字体名称 | 用途 | 文件名 | 是否必需 |")
        content.append("|---------|------|--------|---------|")
        
        for font_name, font_info in self.required_fonts.items():
            required = "是" if font_info["required"] else "否"
            files = ", ".join(font_info["files"])
            content.append(f"| {font_name} | {font_info['description']} | {files} | {required} |")
        
        content.append("")
        content.append("## 字体下载说明")
        content.append("")
        content.append("### 方式1：从系统字体目录复制")
        content.append("")
        content.append("Windows系统字体目录：`C:\\Windows\\Fonts`")
        content.append("")
        content.append("### 方式2：从官方渠道下载")
        content.append("")
        content.append("1. **方正小标宋_GBK**")
        content.append("   - 官方网站：http://www.foundertype.com/")
        content.append("   - 说明：方正字库官方提供，需要授权使用")
        content.append("")
        content.append("2. **仿宋_GB2312、黑体、楷体_GB2312、宋体**")
        content.append("   - Windows系统自带，可直接从系统字体目录复制")
        content.append("   - 或从微软官网下载")
        content.append("")
        content.append("## 安装方法")
        content.append("")
        content.append("### Windows系统")
        content.append("```powershell")
        content.append("# 以管理员身份运行PowerShell")
        content.append("python scripts/install_fonts.py")
        content.append("```")
        content.append("")
        content.append("### macOS系统")
        content.append("```bash")
        content.append("python scripts/install_fonts.py")
        content.append("```")
        content.append("")
        content.append("### Linux系统")
        content.append("```bash")
        content.append("python scripts/install_fonts.py")
        content.append("```")
        
        return "\n".join(content)


def main():
    """主函数"""
    print("=" * 60)
    print("公文格式字体安装工具")
    print("符合GB/T 9704-2012《党政机关公文格式》标准")
    print("=" * 60)
    print()
    
    # 创建字体安装器
    installer = FontInstaller()
    
    # 安装字体
    installed, failed = installer.install_all_fonts()
    
    # 生成字体列表文档
    fonts_list_path = Path(__file__).parent.parent / "fonts" / "FONTS_LIST.md"
    fonts_list_path.parent.mkdir(exist_ok=True)
    with open(fonts_list_path, "w", encoding="utf-8") as f:
        f.write(installer.generate_font_list())
    
    print()
    print(f"字体列表文档已生成: {fonts_list_path}")
    
    # 返回状态码
    if failed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
