"""
案例2：板块行业排名 + 概念板块
场景1：今天哪些行业在涨？排名前5/后5
场景2：查某个概念板块的成分股行情
"""

from thsdk import THS
import pandas as pd

with THS() as ths:

    # ══════════════════════════════════════════════
    # 场景1：行业涨跌排名
    # ══════════════════════════════════════════════

    # 1-A. 获取同花顺行业板块列表
    resp = ths.ths_industry()
    industry_df = resp.df
    # 含字段：名称, 代码(link_code=URFIXXXXXX), 价格, 涨幅, 成交量,
    #         上涨家数, 下跌家数, 板块总市值, 板块流通市值, 领涨股

    # 1-B. 排序：涨幅最高/最低5个行业
    industry_df_sorted = industry_df.sort_values('涨幅', ascending=False)
    top5    = industry_df_sorted.head(5)[['名称', '涨幅', '上涨家数', '下跌家数', '领涨股']]
    bottom5 = industry_df_sorted.tail(5)[['名称', '涨幅', '上涨家数', '下跌家数', '领涨股']]

    print("=== 今日涨幅前5行业 ===")
    print(top5.to_string(index=False))
    print("\n=== 今日跌幅前5行业 ===")
    print(bottom5.to_string(index=False))

    # 1-C. 获取某行业板块的实时行情（更多字段）
    target_industry = industry_df_sorted.iloc[0]  # 涨幅第一的行业
    link_code = str(target_industry.get('代码') or target_industry.get('link_code', ''))
    if link_code:
        block_resp = ths.market_data_block(link_code, "基础数据")
        print(f"\n{target_industry['名称']} 板块行情：")
        print(block_resp.df)

    # ══════════════════════════════════════════════
    # 场景2：概念板块列表 + 成分股
    # ══════════════════════════════════════════════

    # 2-A. 获取概念板块列表
    concept_resp = ths.ths_concept()
    concept_df = concept_resp.df
    # 含：名称, 代码(link_code), 涨幅, 领涨股 等

    # 2-B. 找 AI / 人工智能 相关概念
    ai_concepts = concept_df[
        concept_df['名称'].str.contains('人工智能|AI|大模型', na=False, case=False)
    ]
    print("\n=== AI相关概念板块 ===")
    print(ai_concepts[['名称', '涨幅', '领涨股']].to_string(index=False))

    # 2-C. 查某概念的成分股
    if not ai_concepts.empty:
        ai_link_code = str(ai_concepts.iloc[0].get('代码') or ai_concepts.iloc[0].get('link_code', ''))
        if ai_link_code:
            members_resp = ths.block_constituents(ai_link_code)
            members_df = members_resp.df
            print(f"\n{ai_concepts.iloc[0]['名称']} 成分股（共{len(members_df)}只）：")
            print(members_df.head(10).to_string(index=False))

    # ══════════════════════════════════════════════
    # 场景3：主要指数行情
    # ══════════════════════════════════════════════

    index_codes = {
        "上证指数": "USHI000001",
        "深证成指": "USZI399001",
        "创业板指": "USZI399006",
        "沪深300":  "USHI000300",
        "科创50":   "USHI000688",
    }

    # 同市场批量查（沪市指数一批，深市指数一批）
    sh_codes = [v for k, v in index_codes.items() if v.startswith("USHI")]
    sz_codes = [v for k, v in index_codes.items() if v.startswith("USZI")]

    sh_resp = ths.market_data_index(sh_codes)
    sz_resp = ths.market_data_index(sz_codes)

    idx_df = pd.concat([sh_resp.df, sz_resp.df], ignore_index=True)
    print("\n=== 主要指数行情 ===")
    print(idx_df[['名称', '价格', '涨幅', '涨跌', '成交量', '总金额']].to_string(index=False))

    # 指数K线（日线，近60个交易日）
    sh_kline = ths.klines("USHI000001", interval="day", count=60)
    sh_df = sh_kline.df
    print(f"\n上证指数近60日，区间涨幅：{(sh_df['收盘价'].iloc[-1]/sh_df['收盘价'].iloc[0]-1)*100:.2f}%")
