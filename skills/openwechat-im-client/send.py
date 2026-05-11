#!/usr/bin/env python3
"""
发送消息脚本：绑定 ../openwechat_im_client/config.json 身份，通过代码发消息。
支持 if __name__ == "__main__" 直接执行，而非命令行参数。
"""
import json
import os
import time
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "openwechat_im_client")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_config() -> dict | None:
    """加载 ../openwechat_im_client/config.json"""
    if not os.path.isfile(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def send(to_id: int, content: str, *, base_url: str | None = None, token: str | None = None) -> dict:
    """
    发送消息给指定用户。

    Args:
        to_id: 接收方用户 ID
        content: 消息内容
        base_url: 可选，覆盖 config 中的 base_url
        token: 可选，覆盖 config 中的 token

    Returns:
        {"ok": True} 或抛出异常

    Raises:
        FileNotFoundError: config.json 不存在
        urllib.error.HTTPError: 请求失败（如 403、404）
    """
    cfg = load_config()
    if not cfg:
        raise FileNotFoundError(f"未找到配置文件: {CONFIG_PATH}")

    url = (base_url or cfg.get("base_url", "")).rstrip("/") + "/send"
    tok = token or cfg.get("token", "")

    if not url or not tok:
        raise ValueError("config.json 缺少 base_url 或 token")

    data = json.dumps({"to_id": to_id, "content": content}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Token": tok,
        },
    )

    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        # 服务端返回 PlainTextResponse（如 "发送成功"），非 JSON
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"ok": True, "message": body}


# 测试用例：各种格式内容，用于验证乱码/编码问题
TEST_CASES = [
    ("ASCII", "Hello, world!"),
    ("中文", "你好，这是中文测试"),
    ("中文混合", "Hello 123 你好 世界"),
    ("Emoji", "😀 😎 🎉 🚀"),
    ("Emoji 混合", "你好😀世界🎉"),
    ("特殊符号", "~!@#$%^&*()_+-=[]{}|;':\",./<>?"),
    ("Unicode 符号", "© ® ™ € § ¶ † ‡"),
    ("日文", "こんにちは 世界"),
    ("韩文", "안녕하세요"),
    ("阿拉伯文 RTL", "مرحبا بالعالم"),
    ("零宽字符", "隐藏\u200b\u200c\u200d\u00ad"),
    ("换行", "第一行\n第二行\n第三行"),
    ("Tab 制表", "列1\t列2\t列3"),
    ("长文本", "A" * 500),
    ("空内容", ""),
]

if __name__ == "__main__":
    # 直接执行：加载身份并发送各种格式测试消息
    ensure_data_dir()
    cfg = load_config()
    if not cfg:
        print(f"错误: 未找到 {CONFIG_PATH}，请参考 SKILL.md 创建 config.json 并填写 base_url 和 token")
        exit(1)

    my_id = cfg.get("my_id")
    my_name = cfg.get("my_name", "unknown")
    print(f"当前身份: #{my_id} ({my_name})")
    print("发送目标: 用户 8")
    print("-" * 50)

    to_id = 8
    ok_count = 0
    fail_count = 0

    for i, (name, content) in enumerate(TEST_CASES):
        if i > 0:
            time.sleep(11)
        preview = repr(content[:30]) + ("..." if len(content) > 30 else "")
        try:
            result = send(to_id, content)
            print(f"[OK] {name}: {preview}.{result}")
            ok_count += 1
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"[FAIL] {name}: HTTP {e.code} {body[:80]}")
            fail_count += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            fail_count += 1

    print("-" * 50)
    print(f"完成: {ok_count} 成功, {fail_count} 失败")
