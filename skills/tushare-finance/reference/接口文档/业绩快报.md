# 业绩快报

**文档ID**: 46
**原始链接**: https://tushare.pro/document/2?doc_id=46

---

## 业绩快报

接口：express描述：获取上市公司业绩快报权限：用户需要至少2000积分才可以调取，具体请参阅积分获取办法提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用express_vip接口（参数一致），需积攒5000积分。

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
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>股票代码</td>
</tr>
<tr>
<td>ann_date</td>
<td>str</td>
<td>N</td>
<td>公告日期</td>
</tr>
<tr>
<td>start_date</td>
<td>str</td>
<td>N</td>
<td>公告开始日期</td>
</tr>
<tr>
<td>end_date</td>
<td>str</td>
<td>N</td>
<td>公告结束日期</td>
</tr>
<tr>
<td>period</td>
<td>str</td>
<td>N</td>
<td>报告期(每个季度最后一天的日期,比如20171231表示年报，20170630半年报，20170930三季报)</td>
</tr>
</tbody></table>
输出参数

<table>
<thead>
<tr>
<th>名称</th>
<th>类型</th>
<th>描述</th>
</tr>
</thead>
<tbody><tr>
<td>ts_code</td>
<td>str</td>
<td>TS股票代码</td>
</tr>
<tr>
<td>ann_date</td>
<td>str</td>
<td>公告日期</td>
</tr>
<tr>
<td>end_date</td>
<td>str</td>
<td>报告期</td>
</tr>
<tr>
<td>revenue</td>
<td>float</td>
<td>营业收入(元)</td>
</tr>
<tr>
<td>operate_profit</td>
<td>float</td>
<td>营业利润(元)</td>
</tr>
<tr>
<td>total_profit</td>
<td>float</td>
<td>利润总额(元)</td>
</tr>
<tr>
<td>n_income</td>
<td>float</td>
<td>净利润(元)</td>
</tr>
<tr>
<td>total_assets</td>
<td>float</td>
<td>总资产(元)</td>
</tr>
<tr>
<td>total_hldr_eqy_exc_min_int</td>
<td>float</td>
<td>股东权益合计(不含少数股东权益)(元)</td>
</tr>
<tr>
<td>diluted_eps</td>
<td>float</td>
<td>每股收益(摊薄)(元)</td>
</tr>
<tr>
<td>diluted_roe</td>
<td>float</td>
<td>净资产收益率(摊薄)(%)</td>
</tr>
<tr>
<td>yoy_net_profit</td>
<td>float</td>
<td>去年同期修正后净利润</td>
</tr>
<tr>
<td>bps</td>
<td>float</td>
<td>每股净资产</td>
</tr>
<tr>
<td>yoy_sales</td>
<td>float</td>
<td>同比增长率:营业收入</td>
</tr>
<tr>
<td>yoy_op</td>
<td>float</td>
<td>同比增长率:营业利润</td>
</tr>
<tr>
<td>yoy_tp</td>
<td>float</td>
<td>同比增长率:利润总额</td>
</tr>
<tr>
<td>yoy_dedu_np</td>
<td>float</td>
<td>同比增长率:归属母公司股东的净利润</td>
</tr>
<tr>
<td>yoy_eps</td>
<td>float</td>
<td>同比增长率:基本每股收益</td>
</tr>
<tr>
<td>yoy_roe</td>
<td>float</td>
<td>同比增减:加权平均净资产收益率</td>
</tr>
<tr>
<td>growth_assets</td>
<td>float</td>
<td>比年初增长率:总资产</td>
</tr>
<tr>
<td>yoy_equity</td>
<td>float</td>
<td>比年初增长率:归属母公司的股东权益</td>
</tr>
<tr>
<td>growth_bps</td>
<td>float</td>
<td>比年初增长率:归属于母公司股东的每股净资产</td>
</tr>
<tr>
<td>or_last_year</td>
<td>float</td>
<td>去年同期营业收入</td>
</tr>
<tr>
<td>op_last_year</td>
<td>float</td>
<td>去年同期营业利润</td>
</tr>
<tr>
<td>tp_last_year</td>
<td>float</td>
<td>去年同期利润总额</td>
</tr>
<tr>
<td>np_last_year</td>
<td>float</td>
<td>去年同期净利润</td>
</tr>
<tr>
<td>eps_last_year</td>
<td>float</td>
<td>去年同期每股收益</td>
</tr>
<tr>
<td>open_net_assets</td>
<td>float</td>
<td>期初净资产</td>
</tr>
<tr>
<td>open_bps</td>
<td>float</td>
<td>期初每股净资产</td>
</tr>
<tr>
<td>perf_summary</td>
<td>str</td>
<td>业绩简要说明</td>
</tr>
<tr>
<td>is_audit</td>
<td>int</td>
<td>是否审计： 1是 0否</td>
</tr>
<tr>
<td>remark</td>
<td>str</td>
<td>备注</td>
</tr>
</tbody></table>
接口用法

```

pro = ts.pro_api()

pro.express(ts_code='600000.SH', start_date='20180101', end_date='20180701', fields='ts_code,ann_date,end_date,revenue,operate_profit,total_profit,n_income,total_assets')

```

获取某一季度全部股票数据

```

df = pro.express_vip(period='20181231',fields='ts_code,ann_date,end_date,revenue,operate_profit,total_profit,n_income,total_assets')

```

数据样例

```
     ts_code  ann_date  end_date       revenue  operate_profit  total_profit      n_income  total_assets  \
0  603535.SH  20180411  20180331  2.064659e+08    3.345047e+07  3.340047e+07  2.672643e+07  1.682111e+09   
1  603535.SH  20180208  20171231  1.034262e+09    1.323373e+08  1.440493e+08  1.188325e+08  1.710466e+09   
2  603535.SH  20171016  20170930  7.064117e+08    9.509520e+07  9.931530e+07  8.202480e+07  1.672986e+09

```
