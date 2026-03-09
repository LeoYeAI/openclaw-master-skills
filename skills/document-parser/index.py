#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Parser Skill - OpenClaw
从 PDF、图片、Word 文档中高精度提取结构化数据
"""

import os
import sys
import json
import requests
from pathlib import Path

# 配置
DEFAULT_BASE_URL = "http://47.111.146.164:8088"
DEFAULT_API_PATH = "/taidp/v1/idp/general_parse"
CONFIG_FILE = Path(__file__).parent / "config.json"

def get_config():
    """获取配置（环境变量优先）"""
    config = {
        "api_key": os.environ.get("DOCUMENT_PARSER_API_KEY", ""),
        "base_url": os.environ.get("DOCUMENT_PARSER_BASE_URL", DEFAULT_BASE_URL)
    }
    
    # 从配置文件加载
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"⚠️ 配置文件读取失败：{e}", file=sys.stderr)
    
    return config

def parse_document(file_path, layout_analysis=True, table_recognition=True, 
                   seal_recognition=False, output_format="json", page_range=None):
    """
    解析文档
    
    Args:
        file_path: 文件路径
        layout_analysis: 版面分析
        table_recognition: 表格识别
        seal_recognition: 印章检测
        output_format: 输出格式 (json/markdown/both)
        page_range: 页码范围
    
    Returns:
        解析结果
    """
    config = get_config()
    base_url = config["base_url"].rstrip("/")
    api_url = f"{base_url}{DEFAULT_API_PATH}"
    
    # API Key 可选（有些服务不需要）
    if not config["api_key"]:
        print("[WARN] 未配置 API Key，尝试直接请求...")
    
    if not Path(file_path).exists():
        return {"error": f"文件不存在：{file_path}"}
    
    # 准备请求
    headers = {}
    if config["api_key"]:
        headers["Authorization"] = f"Bearer {config['api_key']}"
    
    # 读取文件
    try:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f)}
            
            data: dict = {
                "layout_analysis_en": 1 if layout_analysis else 0,
                "table_reco_en": 1 if table_recognition else 0,
                "seal_reco_en": 1 if seal_recognition else 0,
            }
            
            if output_format and output_format != "json":
                data["md_image_format"] = "url"
            
            if page_range:
                data["page_range"] = page_range
            
            response = requests.post(
                api_url,
                headers=headers,
                files=files,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                # 支持多种成功码
                if result.get("code") == 10000 or result.get("message") == "Success":
                    return {"success": True, "data": result}
                elif result.get("code"):
                    return {"error": f"API 错误：{result.get('message', '未知错误')}", "code": result.get("code")}
                else:
                    return {"success": True, "data": result}
            else:
                return {"error": f"HTTP 错误：{response.status_code}", "response": response.text}
                
    except requests.exceptions.RequestException as e:
        return {"error": f"请求失败：{str(e)}"}
    except Exception as e:
        return {"error": f"解析失败：{str(e)}"}

def get_task_status(task_id):
    """查询任务状态"""
    config = get_config()
    
    if not config["api_key"]:
        return {"error": "未配置 API Key"}
    
    try:
        response = requests.get(
            f"{config['base_url']}/{task_id}",
            headers={"Authorization": f"Bearer {config['api_key']}"}
        )
        return response.json()
    except Exception as e:
        return {"error": f"查询失败：{str(e)}"}

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法：document-parser <command> [args]")
        print("命令:")
        print("  parse <文件路径> [选项]  - 解析文档")
        print("  status <任务 ID>         - 查询任务状态")
        print("\n选项:")
        print("  --layout     启用版面分析")
        print("  --table      启用表格识别")
        print("  --seal       启用印章检测")
        print("  --output     输出格式 (json/markdown/both)")
        print("  --pages      页码范围")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "parse":
        if len(sys.argv) < 3:
            print("❌ 请提供文件路径")
            sys.exit(1)
        
        file_path = sys.argv[2]
        
        # 解析选项
        layout = "--layout" in sys.argv
        table = "--table" in sys.argv
        seal = "--seal" in sys.argv
        output = "json"
        pages = None
        
        for i, arg in enumerate(sys.argv[3:], 3):
            if arg == "--output" and i + 1 < len(sys.argv):
                output = sys.argv[i + 1]
            elif arg == "--pages" and i + 1 < len(sys.argv):
                pages = sys.argv[i + 1]
        
        print(f"[DOC] 解析文档：{file_path}")
        result = parse_document(file_path, layout, table, seal, output, pages)
        
        if result.get("success"):
            print("[OK] 解析成功!")
            # 输出到文件避免编码问题
            output_file = Path(file_path).stem + "_parsed.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result["data"], f, ensure_ascii=False, indent=2)
            print(f"[INFO] 结果已保存到：{output_file}")
            # 显示简要信息
            data = result["data"]
            if "data" in data:
                print(f"[INFO] 页数：{len(data.get('data', {}).get('pages', []))}")
                print(f"[INFO] 元素数量：{len(data.get('data', {}).get('elements', []))}")
        else:
            print(f"[ERROR] {result.get('error', '未知错误')}")
            sys.exit(1)
    
    elif command == "status":
        if len(sys.argv) < 3:
            print("[ERROR] 请提供任务 ID")
            sys.exit(1)
        
        task_id = sys.argv[2]
        result = get_task_status(task_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"[ERROR] 未知命令：{command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
