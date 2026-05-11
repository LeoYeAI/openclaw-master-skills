# 同花顺App热榜数

**文档ID**: 320
**原始链接**: https://tushare.pro/document/2?doc_id=320

---

## 同花顺热榜

接口：ths_hot描述：获取同花顺App热榜数据，包括热股、概念板块、ETF、可转债、港美股等等，每日盘中提取4次，收盘后4次，最晚22点提取一次。限量：单次最大2000条，可根据日期等参数循环获取全部数据积分：用户积5000积分可调取使用，积分获取办法请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系同花顺解决数据采购问题。

输入参数

<table>
<thead>
<tr>
<th>名称</th>
<th>类型</th>
<th>必选</th>
<th>描述</th>
</tr>
</thead>
<tbody><tr>
<td>trade_date</td>
<td>str</td>
<td>N</td>
<td>交易日期</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>N</td>
<td>TS代码</td>
</tr>
<tr>
<td>market</td>
<td>str</td>
<td>N</td>
<td>热榜类型(热股、ETF、可转债、行业板块、概念板块、期货、港股、热基、美股)</td>
</tr>
<tr>
<td>is_new</td>
<td>str</td>
<td>N</td>
<td>是否最新（默认Y，如果为N则为盘中和盘后阶段采集，具体时间可参考rank_time字段，状态N每小时更新一次，状态Y更新时间为22：30）</td>
</tr>
</tbody></table>
输出参数

<table>
<thead>
<tr>
<th>名称</th>
<th>类型</th>
<th>默认显示</th>
<th>描述</th>
</tr>
</thead>
<tbody><tr>
<td>trade_date</td>
<td>str</td>
<td>Y</td>
<td>交易日期</td>
</tr>
<tr>
<td>data_type</td>
<td>str</td>
<td>Y</td>
<td>数据类型</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>股票代码</td>
</tr>
<tr>
<td>ts_name</td>
<td>str</td>
<td>Y</td>
<td>股票名称</td>
</tr>
<tr>
<td>rank</td>
<td>int</td>
<td>Y</td>
<td>排行</td>
</tr>
<tr>
<td>pct_change</td>
<td>float</td>
<td>Y</td>
<td>涨跌幅%</td>
</tr>
<tr>
<td>current_price</td>
<td>float</td>
<td>Y</td>
<td>当前价格</td>
</tr>
<tr>
<td>concept</td>
<td>str</td>
<td>Y</td>
<td>标签</td>
</tr>
<tr>
<td>rank_reason</td>
<td>str</td>
<td>Y</td>
<td>上榜解读</td>
</tr>
<tr>
<td>hot</td>
<td>float</td>
<td>Y</td>
<td>热度值</td>
</tr>
<tr>
<td>rank_time</td>
<td>str</td>
<td>Y</td>
<td>排行榜获取时间</td>
</tr>
</tbody></table>
接口示例

```

#获取查询月份券商金股
df = pro.ths_hot(trade_date='20240315', market='热股', fields='ts_code,ts_name,hot,concept')

```

数据示例

```
        ts_code ts_name       hot                  concept
0   300750.SZ    宁德时代  214462.0    ["钠离子电池", "同花顺漂亮100"]
1   603580.SH    艾艾精工  185431.0     ["人民币贬值受益", "台湾概念股"]
2   002085.SZ    万丰奥威  180332.0  ["飞行汽车(eVTOL)", "低空经济"]
3   600733.SH    北汽蓝谷  156000.0        ["一体化压铸", "华为汽车"]
4   603259.SH    药明康德  154360.0         ["CRO概念", "创新药"]
..        ...     ...       ...                      ...
95  300735.SZ    光弘科技   28528.0        ["智能穿戴", "EDR概念"]
96  002632.SZ    道明光学   28101.0       ["AI手机", "消费电子概念"]
97  601086.SH    国芳集团   28006.0          ["新零售", "网络直播"]
98  002406.SZ    远东传动   28003.0        ["工业互联网", "智能制造"]
99  600160.SH    巨化股份   27979.0      ["PVDF概念", "氟化工概念"]

```

数据来源
