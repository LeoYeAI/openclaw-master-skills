# ETF基本信息

**文档ID**: 385
**原始链接**: https://tushare.pro/document/2?doc_id=385

---

## ETF基础信息

接口：etf_basic描述：获取国内ETF基础信息，包括了QDII。数据来源与沪深交易所公开披露信息。限量：单次请求最大放回5000条数据（当前ETF总数未超过2000）权限：用户积8000积分可调取，具体请参阅积分获取办法

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
<td>ETF代码（带.SZ/.SH后缀的6位数字，如：159526.SZ）</td>
</tr>
<tr>
<td>index_code</td>
<td>str</td>
<td>N</td>
<td>跟踪指数代码</td>
</tr>
<tr>
<td>list_date</td>
<td>str</td>
<td>N</td>
<td>上市日期（格式：YYYYMMDD）</td>
</tr>
<tr>
<td>list_status</td>
<td>str</td>
<td>N</td>
<td>上市状态（L上市 D退市 P待上市）</td>
</tr>
<tr>
<td>exchange</td>
<td>str</td>
<td>N</td>
<td>交易所（SH上交所 SZ深交所）</td>
</tr>
<tr>
<td>mgr</td>
<td>str</td>
<td>N</td>
<td>管理人（简称，e.g.华夏基金)</td>
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
<td>基金交易代码</td>
</tr>
<tr>
<td>csname</td>
<td>str</td>
<td>Y</td>
<td>ETF中文简称</td>
</tr>
<tr>
<td>extname</td>
<td>str</td>
<td>Y</td>
<td>ETF扩位简称(对应交易所简称)</td>
</tr>
<tr>
<td>cname</td>
<td>str</td>
<td>Y</td>
<td>基金中文全称</td>
</tr>
<tr>
<td>index_code</td>
<td>str</td>
<td>Y</td>
<td>ETF基准指数代码</td>
</tr>
<tr>
<td>index_name</td>
<td>str</td>
<td>Y</td>
<td>ETF基准指数中文全称</td>
</tr>
<tr>
<td>setup_date</td>
<td>str</td>
<td>Y</td>
<td>设立日期（格式：YYYYMMDD）</td>
</tr>
<tr>
<td>list_date</td>
<td>str</td>
<td>Y</td>
<td>上市日期（格式：YYYYMMDD）</td>
</tr>
<tr>
<td>list_status</td>
<td>str</td>
<td>Y</td>
<td>存续状态（L上市 D退市 P待上市）</td>
</tr>
<tr>
<td>exchange</td>
<td>str</td>
<td>Y</td>
<td>交易所（上交所SH 深交所SZ）</td>
</tr>
<tr>
<td>mgr_name</td>
<td>str</td>
<td>Y</td>
<td>基金管理人简称</td>
</tr>
<tr>
<td>custod_name</td>
<td>str</td>
<td>Y</td>
<td>基金托管人名称</td>
</tr>
<tr>
<td>mgt_fee</td>
<td>float</td>
<td>Y</td>
<td>基金管理人收取的费用</td>
</tr>
<tr>
<td>etf_type</td>
<td>str</td>
<td>Y</td>
<td>基金投资通道类型（境内、QDII）</td>
</tr>
</tbody></table>
接口示例

```

#获取当前所有上市的ETF列表
df = pro.etf_basic(list_status='L', fields='ts_code,extname,index_code,index_name,exchange,mgr_name')


#获取“嘉实基金”所有上市的ETF列表
df = pro.etf_basic(mgr='嘉实基金'， list_status='L', fields='ts_code,extname,index_code,index_name,exchange,etf_type')


#获取“嘉实基金”在深交所上市的所有ETF列表
df = pro.etf_basic(mgr='嘉实基金'， list_status='L', exchange='SZ', fields='ts_code,extname,index_code,index_name,exchange,etf_type')


#获取以沪深300指数为跟踪指数的所有上市的ETF列表
df = pro.etf_basic(index_code='000300.SH', fields='ts_code,extname,index_code,index_name,exchange,mgr_name')

```

数据示例

```
      ts_code       extname    index_code    index_name exchange   mgr_name
0   159238.SZ      300ETF增强  000300.SH    沪深300指数       SZ   景顺长城基金
1   159300.SZ        300ETF  000300.SH    沪深300指数       SZ     富国基金
2   159330.SZ    沪深300ETF基金  000300.SH    沪深300指数       SZ   西藏东财基金
3   159393.SZ    沪深300指数ETF  000300.SH    沪深300指数       SZ     万家基金
4   159673.SZ    沪深300ETF鹏华  000300.SH    沪深300指数       SZ     鹏华基金
5   159919.SZ      沪深300ETF  000300.SH    沪深300指数       SZ     嘉实基金
6   159925.SZ    沪深300ETF南方  000300.SH    沪深300指数       SZ     南方基金
7   159927.SZ     鹏华沪深300指数  000300.SH    沪深300指数       SZ     鹏华基金
8   510300.SH      沪深300ETF  000300.SH    沪深300指数       SH   华泰柏瑞基金
9   510310.SH   沪深300ETF易方达  000300.SH    沪深300指数       SH    易方达基金
10  510320.SH    沪深300ETF中金  000300.SH    沪深300指数       SH     中金基金
11  510330.SH    沪深300ETF华夏  000300.SH    沪深300指数       SH     华夏基金
12  510350.SH    沪深300ETF工银  000300.SH    沪深300指数       SH   工银瑞信基金
13  510360.SH    沪深300ETF基金  000300.SH    沪深300指数       SH     广发基金
14  510370.SH      300指数ETF  000300.SH    沪深300指数       SH     兴业基金
15  510380.SH      国寿300ETF  000300.SH    沪深300指数       SH   国寿安保基金
16  510390.SH    沪深300ETF平安  000300.SH    沪深300指数       SH     平安基金
17  515130.SH    沪深300ETF博时  000300.SH    沪深300指数       SH     博时基金
18  515310.SH    沪深300指数ETF  000300.SH    沪深300指数       SH    汇添富基金
19  515330.SH    沪深300ETF天弘  000300.SH    沪深300指数       SH     天弘基金
20  515350.SH    民生加银300ETF  000300.SH    沪深300指数       SH   民生加银基金
21  515360.SH    方正沪深300ETF  000300.SH    沪深300指数       SH   方正富邦基金
22  515380.SH    沪深300ETF泰康  000300.SH    沪深300指数       SH     泰康基金
23  515390.SH  沪深300ETF指数基金  000300.SH    沪深300指数       SH     华安基金
24  515660.SH   沪深300ETF国联安  000300.SH    沪深300指数       SH    国联安基金
25  515930.SH    永赢沪深300ETF  000300.SH    沪深300指数       SH     永赢基金
26  561000.SH  沪深300ETF增强基金  000300.SH    沪深300指数       SH     华安基金
27  561300.SH      300增强ETF  000300.SH    沪深300指数       SH     国泰基金
28  561930.SH    沪深300ETF招商  000300.SH    沪深300指数       SH     招商基金
29  561990.SH    沪深300增强ETF  000300.SH    沪深300指数       SH     招商基金
30  563520.SH    沪深300ETF永赢  000300.SH    沪深300指数       SH     永赢基金

```
