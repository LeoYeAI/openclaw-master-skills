import sys

def main():
    print("🤖 XtQuant / QMT 实际接口调用演示")
    try:
        from xtquant import xtdata
        print("正在尝试获取板块列表 (如果本地未运行QMT终端可能会失败)...")
        sector_list = xtdata.get_sector_list()
        print(f"✅ 成功获取板块列表，共 {len(sector_list)} 个。")
        print("前5个板块:", sector_list[:5])
    except ImportError:
        print("❌ 未安装 xtquant 包，请先执行 pip install xtquant")
    except Exception as e:
        print(f"❌ 获取数据失败 (请确保QMT/miniQMT客户端已启动并开启了xtdata服务): {e}")

if __name__ == "__main__":
    main()
