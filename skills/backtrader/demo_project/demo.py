import backtrader as bt

class DummyStrategy(bt.Strategy):
    def next(self):
        pass

def main():
    print("🤖 Backtrader 实际回测引擎演示")
    try:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(DummyStrategy)
        print("✅ 成功初始化 Cerebro 引擎并加载了测试策略。")
        print("您可以继续使用 cerebro.adddata() 加载数据，然后调用 cerebro.run() 执行回测。")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

if __name__ == "__main__":
    main()
