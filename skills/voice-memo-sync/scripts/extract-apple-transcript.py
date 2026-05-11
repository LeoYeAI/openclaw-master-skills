#!/usr/bin/env python3
"""
Apple Voice Memos Transcript Extractor v1.1
从Mac语音备忘录的.qta/.m4a文件中提取Apple原生转录文本

更新 v1.1 (2026-03-09):
- 增强大文件支持 (>100MB)
- 改进JSON边界检测
- 添加时间戳提取支持
- 更好的错误诊断

用法: 
  python3 extract-apple-transcript.py <音频文件>
  python3 extract-apple-transcript.py <音频文件> --json
  python3 extract-apple-transcript.py <音频文件> --with-timestamps

隐私说明:
  - 此脚本仅在本地运行，不上传任何数据
  - 不收集任何用户信息
"""

import sys
import struct
import json
import os
import re
from pathlib import Path

def find_json_in_data(data: bytes, start_patterns: list) -> tuple:
    """
    在二进制数据中查找并提取完整的JSON对象
    返回 (json_str, start_pos) 或 (None, -1)
    """
    for pattern in start_patterns:
        json_start = data.find(pattern)
        if json_start != -1:
            # 找到起始位置，现在找到完整的JSON
            json_data = data[json_start:]
            depth = 0
            in_string = False
            escape = False
            end_pos = 0
            
            for i, b in enumerate(json_data):
                c = chr(b) if b < 128 else ''
                
                if escape:
                    escape = False
                    continue
                    
                if c == '\\' and in_string:
                    escape = True
                    continue
                    
                if c == '"' and not escape:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            end_pos = i + 1
                            break
            
            if end_pos > 0:
                try:
                    json_str = json_data[:end_pos].decode('utf-8', errors='ignore')
                    # 验证JSON有效性
                    json.loads(json_str)
                    return json_str, json_start
                except json.JSONDecodeError:
                    continue
    
    return None, -1

def extract_apple_transcript(filepath, with_timestamps=False):
    """
    从QuickTime文件(.qta/.m4a)中提取Apple原生转录
    
    Apple Voice Memos将转录存储在文件的meta atom中，格式为JSON
    包含attributedString.runs数组，交替存储文字和索引
    
    QTA文件结构:
    - ftyp (文件类型)
    - wide (扩展标记)  
    - mdat (媒体数据，通常很大)
    - moov (元数据容器)
      - mvhd (电影头)
      - trak (轨道，可能有多个)
        - tkhd (轨道头)
        - mdia (媒体)
        - meta (元数据，转录在这里！)
          - hdlr (处理器)
          - keys (键列表)
          - ilst (数据列表)
            - data (包含JSON转录)
    """
    try:
        file_size = os.path.getsize(filepath)
        
        with open(filepath, 'rb') as f:
            # 查找moov atom位置
            moov_pos = None
            moov_size = None
            
            while f.tell() < file_size:
                pos = f.tell()
                header = f.read(8)
                if len(header) < 8:
                    break
                    
                size = struct.unpack('>I', header[:4])[0]
                typ = header[4:8].decode('latin-1', errors='replace')
                
                if size == 0:
                    size = file_size - pos
                elif size == 1:
                    ext = f.read(8)
                    size = struct.unpack('>Q', ext)[0]
                
                if typ == 'moov':
                    moov_pos = pos
                    moov_size = size
                    break
                
                # 跳到下一个atom
                if size < 8:
                    break
                f.seek(pos + size)
            
            if moov_pos is None:
                return None, "未找到moov atom (文件可能已损坏或不是QuickTime格式)"
            
            # 读取整个moov区域
            f.seek(moov_pos)
            moov_data = f.read(moov_size)
            
            # 查找转录JSON (多种可能的起始模式)
            start_patterns = [
                b'{"locale"',
                b'{"attributedString"',
                b'{"runs"',
            ]
            
            json_str, json_pos = find_json_in_data(moov_data, start_patterns)
            
            if json_str is None:
                # 尝试搜索 VoiceMemos.tsrp 标记
                tsrp_pos = moov_data.find(b'VoiceMemos.tsrp')
                if tsrp_pos != -1:
                    # 转录标记存在但JSON未找到，可能还在处理中
                    return None, "转录标记存在但数据不完整 (录音可能仍在处理中)"
                return None, "未找到转录数据 (此录音可能没有启用转录或尚未完成)"
            
            # 解析JSON
            transcript_data = json.loads(json_str)
            
            # 提取纯文本
            if 'attributedString' not in transcript_data:
                return None, "转录数据格式异常 (缺少attributedString)"
            
            attr_string = transcript_data['attributedString']
            runs = attr_string.get('runs', [])
            
            if not runs:
                return None, "转录为空"
            
            # runs格式: [text, index, text, index, ...]
            text_parts = []
            for i in range(0, len(runs), 2):
                if i < len(runs) and isinstance(runs[i], str):
                    text_parts.append(runs[i])
            
            full_text = ''.join(text_parts)
            
            result = {
                'text': full_text,
                'locale': transcript_data.get('locale', {}),
                'word_count': len(text_parts),
                'char_count': len(full_text),
                'has_timestamps': 'attributeTable' in attr_string
            }
            
            # 提取时间戳 (如果请求)
            if with_timestamps and 'attributeTable' in attr_string:
                attr_table = attr_string['attributeTable']
                timestamps = []
                for entry in attr_table:
                    if 'timeRange' in entry:
                        tr = entry['timeRange']
                        if isinstance(tr, list) and len(tr) == 2:
                            timestamps.append({
                                'start': tr[0],
                                'end': tr[1]
                            })
                result['timestamps'] = timestamps
            
            return result, None
            
    except json.JSONDecodeError as e:
        return None, f"JSON解析失败: {e}"
    except MemoryError:
        return None, f"文件过大，内存不足 (文件大小: {file_size / 1024 / 1024:.1f}MB)"
    except Exception as e:
        return None, f"提取失败: {type(e).__name__}: {e}"

def main():
    if len(sys.argv) < 2:
        print("用法: python3 extract-apple-transcript.py <音频文件.qta/.m4a> [选项]")
        print("\n选项:")
        print("  --json            输出JSON格式")
        print("  --with-timestamps 包含时间戳信息")
        print("\n示例:")
        print("  python3 extract-apple-transcript.py recording.qta")
        print("  python3 extract-apple-transcript.py recording.m4a --json")
        print("  python3 extract-apple-transcript.py recording.qta --json --with-timestamps")
        sys.exit(1)
    
    filepath = sys.argv[1]
    output_json = '--json' in sys.argv
    with_timestamps = '--with-timestamps' in sys.argv
    
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    result, error = extract_apple_transcript(filepath, with_timestamps=with_timestamps)
    
    if error:
        print(f"错误: {error}", file=sys.stderr)
        sys.exit(1)
    
    if output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result['text'])

if __name__ == '__main__':
    main()
