# ST股票列表

**文档ID**: 397
**原始链接**: https://tushare.pro/document/2?doc_id=397

---

## ST股票列表

接口：stock_st，可以通过数据工具调试和查看数据。描述：获取ST股票列表，可根据交易日期获取历史上每天的ST列表权限：3000积分起提示：每天上午9:20更新，单次请求最大返回1000行数据，可循环提取,本接口数据从20160101开始,太早历史无法补齐

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
<td>N</td>
<td>股票代码</td>
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
<td>开始时间</td>
</tr>
<tr>
<td>end_date</td>
<td>str</td>
<td>N</td>
<td>结束时间</td>
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
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>股票代码</td>
</tr>
<tr>
<td>name</td>
<td>str</td>
<td>Y</td>
<td>股票名称</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>Y</td>
<td>交易日期</td>
</tr>
<tr>
<td>type</td>
<td>str</td>
<td>Y</td>
<td>类型</td>
</tr>
<tr>
<td>type_name</td>
<td>str</td>
<td>Y</td>
<td>类型名称</td>
</tr>
</tbody></table>
接口用法

```

pro = ts.pro_api()

#获取20250813日所有的ST股票
df = pro.stock_st(trade_date='20250813')


```

数据样例

```
             ts_code   name trade_date type type_name
0    300313.SZ  *ST天山   20250813   ST     风险警示板
1    605081.SH  *ST太和   20250813   ST     风险警示板
2    300391.SZ  *ST长药   20250813   ST     风险警示板
3    300343.SZ   ST联创   20250813   ST     风险警示板
4    300044.SZ   ST赛为   20250813   ST     风险警示板
..         ...    ...        ...  ...       ...
170  300175.SZ   ST朗源   20250813   ST     风险警示板
171  603721.SH  *ST天择   20250813   ST     风险警示板
172  600289.SH   ST信通   20250813   ST     风险警示板
173  000929.SZ  *ST兰黄   20250813   ST     风险警示板
174  000638.SZ  *ST万方   20250813   ST     风险警示板

```
