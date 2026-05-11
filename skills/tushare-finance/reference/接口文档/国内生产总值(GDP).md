# 国内生产总值（GDP）

**文档ID**: 227
**原始链接**: https://tushare.pro/document/2?doc_id=227

---

## GDP数据

接口：cn_gdp描述：获取国民经济之GDP数据限量：单次最大10000，一次可以提取全部数据权限：用户积累600积分可以使用，具体请参阅积分获取办法

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
<td>q</td>
<td>str</td>
<td>N</td>
<td>季度（2019Q1表示，2019年第一季度）</td>
</tr>
<tr>
<td>start_q</td>
<td>str</td>
<td>N</td>
<td>开始季度</td>
</tr>
<tr>
<td>end_q</td>
<td>str</td>
<td>N</td>
<td>结束季度</td>
</tr>
<tr>
<td>fields</td>
<td>str</td>
<td>N</td>
<td>指定输出字段（e.g. fields='quarter,gdp,gdp_yoy'）</td>
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
<td>quarter</td>
<td>str</td>
<td>Y</td>
<td>季度</td>
</tr>
<tr>
<td>gdp</td>
<td>float</td>
<td>Y</td>
<td>GDP累计值（亿元）</td>
</tr>
<tr>
<td>gdp_yoy</td>
<td>float</td>
<td>Y</td>
<td>当季同比增速（%）</td>
</tr>
<tr>
<td>pi</td>
<td>float</td>
<td>Y</td>
<td>第一产业累计值（亿元）</td>
</tr>
<tr>
<td>pi_yoy</td>
<td>float</td>
<td>Y</td>
<td>第一产业同比增速（%）</td>
</tr>
<tr>
<td>si</td>
<td>float</td>
<td>Y</td>
<td>第二产业累计值（亿元）</td>
</tr>
<tr>
<td>si_yoy</td>
<td>float</td>
<td>Y</td>
<td>第二产业同比增速（%）</td>
</tr>
<tr>
<td>ti</td>
<td>float</td>
<td>Y</td>
<td>第三产业累计值（亿元）</td>
</tr>
<tr>
<td>ti_yoy</td>
<td>float</td>
<td>Y</td>
<td>第三产业同比增速（%）</td>
</tr>
</tbody></table>
接口调用

```

pro = ts.pro_api()

df = pro.cn_gdp(start_q='2018Q1', end_q='2019Q3')


#获取指定字段
df = pro.cn_gdp(start_q='2018Q1', end_q='2019Q3', fields='quarter,gdp,gdp_yoy')

```

数据样例

```
    quarter          gdp gdp_yoy          pi pi_yoy           si si_yoy           ti ti_yoy
0    2019Q4  990865.1000    6.10  70466.7000   3.10  386165.3000   5.70  534233.1000   6.90
1    2019Q3  712845.4000    6.20  43005.0000   2.90  276912.5000   5.60  392927.9000   7.00
2    2019Q2  460636.7000    6.30  23207.0000   3.00  179122.1000   5.80  258307.5000   7.00
3    2019Q1  218062.8000    6.40   8769.4000   2.70   81806.5000   6.10  127486.9000   7.00
4    2018Q4  900309.5000    6.60  64734.0000   3.50  366000.9000   5.80  469574.6000   7.60
..      ...          ...     ...         ...    ...          ...    ...          ...    ...
147  1956Q4    1028.0000   15.00    443.9000   4.70     280.7000  34.50     303.4000  14.10
148  1955Q4     910.0000    6.80    421.0000   7.90     222.2000   7.60     266.8000   4.60
149  1954Q4     859.0000    4.20    392.0000   1.70     211.7000  15.70     255.3000  -0.60
150  1953Q4     824.0000   15.60    378.0000   1.90     192.5000  35.80     253.5000  27.30
151  1952Q4     679.0000    None    342.9000   None     141.8000   None     194.3000   None

```
