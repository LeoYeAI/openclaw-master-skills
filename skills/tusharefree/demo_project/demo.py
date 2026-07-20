import tushare as ts

def main():
    print("🤖 Tushare 实际数据获取演示")
    try:
        print("注意：Tushare Pro 需要 Token，这里演示基础配置方法...")
        # ts.set_token('YOUR_TOKEN_HERE')
        pro = ts.pro_api()
        
        print("正在尝试获取交易日历 (可能需要有效Token)...")
        df = pro.trade_cal(exchange='', start_date='20230101', end_date='20230110')
        if df.empty:
            print("⚠️ 获取数据为空！")
        else:
            print(f"✅ 成功获取交易日历数据。")
            print(df.head())
    except Exception as e:
        print(f"❌ 获取数据失败 (大概率是因为未配置有效 Token): {e}")

if __name__ == "__main__":
    main()
