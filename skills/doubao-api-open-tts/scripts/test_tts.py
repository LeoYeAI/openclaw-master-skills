#!/usr/bin/env python3
"""
火山引擎TTS测试脚本 - 测试多种配置
"""

import os
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载 .env 文件
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

from tts import VolcanoTTS

def test_tts_configs():
    """测试多种TTS配置"""
    
    # 从环境变量获取配置
    app_id = os.environ.get('VOLCANO_TTS_APPID')
    access_token = os.environ.get('VOLCANO_TTS_ACCESS_TOKEN')
    secret_key = os.environ.get('VOLCANO_TTS_SECRET_KEY')
    
    print("=" * 60)
    print("火山引擎语音合成测试 - 多配置测试")
    print("=" * 60)
    
    # 检查配置
    if not all([app_id, access_token, secret_key]):
        print("\n❌ 错误: 缺少API配置")
        print("请设置以下环境变量:")
        print("  - VOLCANO_TTS_APPID")
        print("  - VOLCANO_TTS_ACCESS_TOKEN")
        print("  - VOLCANO_TTS_SECRET_KEY")
        return False
    
    print(f"\n✓ 配置检查通过")
    print(f"  AppID: {app_id[:4]}****")
    
    # 测试配置列表
    test_configs = [
        # (voice_type, cluster, description)
        ("BV001_streaming", "volcano_tts", "默认音色 (volcano_tts)"),
        ("BV001_streaming", "volcano", "默认音色 (volcano)"),
        ("BV002_streaming", "volcano_tts", "音色2 (volcano_tts)"),
        ("zh_female_qingxin", "volcano_tts", "中文女声 - 清新"),
        ("zh_female_lively", "volcano_tts", "中文女声 - 活泼"),
    ]
    
    # 测试文本
    test_text = "你好，这是火山引擎语音合成测试。"
    
    try:
        # 初始化TTS客户端
        print("\n[初始化] 创建TTS客户端...")
        tts = VolcanoTTS(app_id=app_id, access_token=access_token, secret_key=secret_key)
        print("  ✓ 初始化成功")
        
        # 测试每种配置
        for i, (voice_type, cluster, desc) in enumerate(test_configs, 1):
            print(f"\n{'=' * 60}")
            print(f"[测试 {i}/{len(test_configs)}] {desc}")
            print(f"{'=' * 60}")
            print(f"  音色: {voice_type}")
            print(f"  集群: {cluster}")
            print(f"  文本: {test_text}")
            
            try:
                output_path = tts.synthesize(
                    text=test_text,
                    voice_type=voice_type,
                    encoding="mp3",
                    cluster=cluster,
                    output_file=f"test_{i}_{voice_type}.mp3"
                )
                
                # 验证文件
                import os as os_module
                if os_module.path.exists(output_path):
                    file_size = os_module.path.getsize(output_path)
                    print(f"  ✅ 成功! 文件: {output_path} ({file_size} 字节)")
                    
                    # 第一个成功的配置就返回
                    print(f"\n{'=' * 60}")
                    print("✅ 找到可用配置!")
                    print(f"   推荐配置: voice_type={voice_type}, cluster={cluster}")
                    print(f"{'=' * 60}")
                    return True
                    
            except Exception as e:
                print(f"  ❌ 失败: {e}")
                continue
        
        print(f"\n{'=' * 60}")
        print("❌ 所有配置测试失败")
        print("可能原因:")
        print("  1. API Token没有TTS权限")
        print("  2. 账户余额不足")
        print("  3. 音色/集群配置不正确")
        print(f"{'=' * 60}")
        return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tts_configs()
    sys.exit(0 if success else 1)
