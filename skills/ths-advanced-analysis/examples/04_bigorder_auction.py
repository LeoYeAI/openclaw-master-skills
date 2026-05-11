"""
案例4：大单流向 + 竞价异动监控
场景A：盘中监控某股大单动向（主力在买还是在卖）
场景B：开盘前（9:15~9:25）扫描全市场竞价异动
场景C：实时分时 + 盘口深度
"""

from thsdk import THS
import pandas as pd

# ═══════════════════════════════════════════════════════════
# 场景A：单只股票大单流向
# ═══════════════════════════════════════════════════════════

TARGET = "USZA300750"  # 宁德时代（已知 ths_code 可直接用）

with THS() as ths:

    # A-1. 大单流向
    resp = ths.big_order_flow(TARGET)
    df = resp.df
    # 主要字段：
    # 主动买入特大单量 / 主动卖出特大单量
    # 主动买入特大单金额 / 主动卖出特大单金额
    # 主动买入大单量 / 主动卖出大单量
    # 资金流入 / 资金流出
    # 主动买入特大单笔数 / 主动卖出特大单笔数

    if not df.empty:
        # 计算主力净流入
        buy_col  = '主动买入特大单金额' if '主动买入特大单金额' in df.columns else None
        sell_col = '主动卖出特大单金额' if '主动卖出特大单金额' in df.columns else None
        if buy_col and sell_col:
            df['主力净流入'] = df[buy_col] - df[sell_col]
            df['方向'] = df['主力净流入'].apply(lambda x: '🔴流入' if x > 0 else '🟢流出')

    print("=== 大单流向 ===")
    print(df.to_string(index=False))

    # A-2. 实时分时（今日）
    intraday_resp = ths.intraday_data(TARGET)
    intraday_df = intraday_resp.df
    # 字段：时间(datetime), 价格, 成交量, 均价 等
    print(f"\n=== 今日分时（最近5条） ===")
    print(intraday_df.tail(5).to_string(index=False))

    # A-3. 盘口深度（五档）
    depth_resp = ths.depth(TARGET)
    depth_df = depth_resp.df
    print("\n=== 当前盘口 ===")
    print(depth_df.to_string(index=False))
    # 字段：买1~5价/量，卖1~5价/量

    # A-4. Tick 数据（3秒级）
    tick_resp = ths.tick_level1(TARGET)
    tick_df = tick_resp.df
    print(f"\n=== Tick数据（最近5条）===")
    print(tick_df.tail(5).to_string(index=False))


# ═══════════════════════════════════════════════════════════
# 场景B：全市场竞价异动扫描（9:15~9:25 使用）
# ═══════════════════════════════════════════════════════════

with THS() as ths:

    # 扫描沪市 + 深市
    sh_anomaly = ths.call_auction_anomaly("USHA")
    sz_anomaly = ths.call_auction_anomaly("USZA")

    sh_df = sh_anomaly.df if sh_anomaly else pd.DataFrame()
    sz_df = sz_anomaly.df if sz_anomaly else pd.DataFrame()
    anomaly_df = pd.concat([sh_df, sz_df], ignore_index=True)

    # 异动类型1 已自动映射为中文，例如：
    # 涨停试盘 / 跌停试盘 / 涨停撤单 / 竞价抢筹 / 竞价砸盘
    # 大幅高开 / 大幅低开 / 急速上涨 / 急速下跌
    # 买一剩余大 / 卖一剩余大 / 大买单试盘 / 大卖单试盘

    print("\n=== 竞价异动（全部） ===")
    if not anomaly_df.empty:
        print(anomaly_df.to_string(index=False))

        # 只看强势异动
        strong_types = ['涨停试盘', '竞价抢筹', '大幅高开', '急速上涨', '大买单试盘']
        strong_df = anomaly_df[anomaly_df.get('异动类型1', pd.Series(dtype=str)).isin(strong_types)]
        print(f"\n=== 强势异动（{len(strong_df)}只） ===")
        print(strong_df.to_string(index=False))

    # 早盘集合竞价快照（单股）
    auction_resp = ths.call_auction(TARGET)
    print(f"\n=== {TARGET} 竞价快照 ===")
    print(auction_resp.df.to_string(index=False))


# ═══════════════════════════════════════════════════════════
# 场景C：历史某日分时回溯（复盘用）
# ═══════════════════════════════════════════════════════════

with THS() as ths:
    # 查历史某日分时（近一年内任意交易日）
    hist_resp = ths.min_snapshot(TARGET, date="20250301")
    hist_df = hist_resp.df
    # 字段：时间(timestamp), 价格, 成交量, 均价 等
    # 注意：已过滤掉成交量=4294967295的无效数据

    print(f"\n=== 历史分时（2025-03-01，共{len(hist_df)}条）===")
    print(hist_df.head(10).to_string(index=False))

    # 超级盘口历史（含十档委托，近一年）
    super_resp = ths.tick_super_level1(TARGET, date="20250301")
    print(f"\n=== 超级盘口历史（共{len(super_resp.df)}条）===")
    print(super_resp.df.head(5).to_string(index=False))
