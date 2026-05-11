# 新闻快讯（短讯）

**文档ID**: 143
**原始链接**: https://tushare.pro/document/2?doc_id=143

---

## 新闻快讯

接口：news描述：获取主流新闻网站的快讯新闻数据,提供超过6年以上历史新闻。限量：单次最大1500条新闻，可根据时间参数循环提取历史积分：本接口需单独开权限（跟积分没关系），具体请参阅权限说明

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
<td>start_date</td>
<td>datetime</td>
<td>Y</td>
<td>开始日期(格式：2018-11-20 09:00:00）</td>
</tr>
<tr>
<td>end_date</td>
<td>datetime</td>
<td>Y</td>
<td>结束日期</td>
</tr>
<tr>
<td>src</td>
<td>str</td>
<td>Y</td>
<td>新闻来源 见下表</td>
</tr>
</tbody></table>
数据源

<table>
<thead>
<tr>
<th>来源名称</th>
<th>src标识</th>
<th>描述</th>
</tr>
</thead>
<tbody><tr>
<td>新浪财经</td>
<td>sina</td>
<td>获取新浪财经实时资讯</td>
</tr>
<tr>
<td>华尔街见闻</td>
<td>wallstreetcn</td>
<td>华尔街见闻快讯</td>
</tr>
<tr>
<td>同花顺</td>
<td>10jqka</td>
<td>同花顺财经新闻</td>
</tr>
<tr>
<td>东方财富</td>
<td>eastmoney</td>
<td>东方财富财经新闻</td>
</tr>
<tr>
<td>云财经</td>
<td>yuncaijing</td>
<td>云财经新闻</td>
</tr>
<tr>
<td>凤凰新闻</td>
<td>fenghuang</td>
<td>凤凰新闻</td>
</tr>
<tr>
<td>金融界</td>
<td>jinrongjie</td>
<td>金融界新闻</td>
</tr>
<tr>
<td>财联社</td>
<td>cls</td>
<td>财联社快讯</td>
</tr>
<tr>
<td>第一财经</td>
<td>yicai</td>
<td>第一财经快讯</td>
</tr>
</tbody></table>
- 时间参数格式例子：start_date='2018-11-20 09:00:00', end_date='2018-11-20 22:05:03'


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
<td>datetime</td>
<td>str</td>
<td>Y</td>
<td>新闻时间</td>
</tr>
<tr>
<td>content</td>
<td>str</td>
<td>Y</td>
<td>内容</td>
</tr>
<tr>
<td>title</td>
<td>str</td>
<td>Y</td>
<td>标题</td>
</tr>
<tr>
<td>channels</td>
<td>str</td>
<td>N</td>
<td>分类</td>
</tr>
</tbody></table>
接口调用

```

pro = ts.pro_api()

df = pro.news(src='sina', start_date='2018-11-21 09:00:00', end_date='2018-11-22 10:10:00')

```

数据样例

更多数据预览，请点击网站头部菜单的资讯数据。
