# AH股比价

**文档ID**: 399
**原始链接**: https://tushare.pro/document/2?doc_id=399

---

## AH股比价

接口：stk_ah_comparison，可以通过数据工具调试和查看数据。描述：AH股比价数据，可根据交易日期获取历史权限：5000积分起提示：每天盘后17:00更新，单次请求最大返回1000行数据，可循环提取,本接口数据从20250812开始，由于历史不好补充，只能累积

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
<td>hk_code</td>
<td>str</td>
<td>N</td>
<td>港股股票代码（xxxxx.HK)</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>N</td>
<td>A股票代码(xxxxxx.SH/SZ/BJ)</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>N</td>
<td>交易日期（格式：YYYYMMDD下同）</td>
</tr>
<tr>
<td>start_date</td>
<td>str</td>
<td>N</td>
<td>开始日期</td>
</tr>
<tr>
<td>end_date</td>
<td>str</td>
<td>N</td>
<td>结束日期</td>
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
<td>hk_code</td>
<td>str</td>
<td>Y</td>
<td>港股股票代码</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>A股股票代码</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>Y</td>
<td>交易日期</td>
</tr>
<tr>
<td>hk_name</td>
<td>str</td>
<td>Y</td>
<td>港股股票名称</td>
</tr>
<tr>
<td>hk_pct_chg</td>
<td>float</td>
<td>Y</td>
<td>港股股票涨跌幅</td>
</tr>
<tr>
<td>hk_close</td>
<td>float</td>
<td>Y</td>
<td>港股股票收盘价</td>
</tr>
<tr>
<td>name</td>
<td>str</td>
<td>Y</td>
<td>A股股票名称</td>
</tr>
<tr>
<td>close</td>
<td>float</td>
<td>Y</td>
<td>A股股票收盘价</td>
</tr>
<tr>
<td>pct_chg</td>
<td>float</td>
<td>Y</td>
<td>A股股票涨跌幅</td>
</tr>
<tr>
<td>ah_comparison</td>
<td>float</td>
<td>Y</td>
<td>比价(A/H)</td>
</tr>
<tr>
<td>ah_premium</td>
<td>float</td>
<td>Y</td>
<td>溢价(A/H)%</td>
</tr>
</tbody></table>
接口用法

```

pro = ts.pro_api()

#获取20250812日所有的AH股比价数据
df = pro.stk_ah_comparison(trade_date='20250812')


```

数据样例

```
            hk_code    ts_code trade_date   hk_name  hk_pct_chg  hk_close  name  close  pct_chg  ah_comparison  ah_premium
0    02068.HK  601068.SH   20250812      中铝国际        0.78      2.60  中铝国际   5.14     0.00           2.16      115.84
1    03993.HK  603993.SH   20250812      洛阳钼业        0.60     10.07  洛阳钼业   9.85     0.31           1.07        6.80
2    06066.HK  601066.SH   20250812    中信建投证券        1.77     13.25  中信建投  26.09     0.66           2.15      114.99
3    06680.HK  300748.SZ   20250812      金力永磁       -5.67     18.30  金力永磁  27.30    -3.05           1.63       62.88
4    02333.HK  601633.SH   20250812      长城汽车        3.55     14.60  长城汽车  22.93     1.82           1.71       71.48
..        ...        ...        ...       ...         ...       ...   ...    ...      ...            ...         ...
155  06196.HK  002936.SZ   20250812      郑州银行        1.41      1.44  郑州银行   2.10     0.48           1.59       59.22
156  06818.HK  601818.SH   20250812    中国光大银行        1.61      3.78  光大银行   4.10     0.99           1.18       18.43
157  06693.HK  600988.SH   20250812      赤峰黄金        1.76     25.44  赤峰黄金  24.58     0.24           1.05        5.49
158  02196.HK  600196.SH   20250812      复星医药        2.22     19.77  复星医药  27.70     3.36           1.53       52.98
159  01065.HK  600874.SH   20250812  天津创业环保股份        2.24      4.10  创业环保   6.01     0.00           1.60       60.05

```
