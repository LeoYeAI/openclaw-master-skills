# 基金管理人

**文档ID**: 118
**原始链接**: https://tushare.pro/document/2?doc_id=118

---

## 公募基金公司

接口：fund_company描述：获取公募基金管理人列表积分：用户需要1500积分才可以调取，一次可以提取全部数据。具体请参阅积分获取办法

输入参数

无，可提取全部

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
<td>name</td>
<td>str</td>
<td>Y</td>
<td>基金公司名称</td>
</tr>
<tr>
<td>shortname</td>
<td>str</td>
<td>Y</td>
<td>简称</td>
</tr>
<tr>
<td>short_enname</td>
<td>str</td>
<td>N</td>
<td>英文缩写</td>
</tr>
<tr>
<td>province</td>
<td>str</td>
<td>Y</td>
<td>省份</td>
</tr>
<tr>
<td>city</td>
<td>str</td>
<td>Y</td>
<td>城市</td>
</tr>
<tr>
<td>address</td>
<td>str</td>
<td>Y</td>
<td>注册地址</td>
</tr>
<tr>
<td>phone</td>
<td>str</td>
<td>Y</td>
<td>电话</td>
</tr>
<tr>
<td>office</td>
<td>str</td>
<td>Y</td>
<td>办公地址</td>
</tr>
<tr>
<td>website</td>
<td>str</td>
<td>Y</td>
<td>公司网址</td>
</tr>
<tr>
<td>chairman</td>
<td>str</td>
<td>Y</td>
<td>法人代表</td>
</tr>
<tr>
<td>manager</td>
<td>str</td>
<td>Y</td>
<td>总经理</td>
</tr>
<tr>
<td>reg_capital</td>
<td>float</td>
<td>Y</td>
<td>注册资本</td>
</tr>
<tr>
<td>setup_date</td>
<td>str</td>
<td>Y</td>
<td>成立日期</td>
</tr>
<tr>
<td>end_date</td>
<td>str</td>
<td>Y</td>
<td>公司终止日期</td>
</tr>
<tr>
<td>employees</td>
<td>float</td>
<td>Y</td>
<td>员工总数</td>
</tr>
<tr>
<td>main_business</td>
<td>str</td>
<td>Y</td>
<td>主要产品及业务</td>
</tr>
<tr>
<td>org_code</td>
<td>str</td>
<td>Y</td>
<td>组织机构代码</td>
</tr>
<tr>
<td>credit_code</td>
<td>str</td>
<td>Y</td>
<td>统一社会信用代码</td>
</tr>
</tbody></table>
接口示例

```

pro = ts.pro_api()

df = pro.fund_company()

```

数据示例

```
                  name                   shortname          province   city  \
0           北京广能投资基金管理有限公司        广能基金       北京    北京市   
1               平安银行股份有限公司        平安银行       广东    深圳市   
2               宏源证券股份有限公司        宏源证券       新疆  乌鲁木齐市   
3            陕西省国际信托股份有限公司         陕国投       陕西    西安市   
4               东北证券股份有限公司        东北证券       吉林    长春市   
5               国元证券股份有限公司        国元证券       安徽    合肥市   
6               国海证券股份有限公司        国海证券       广西    桂林市   
7               广发证券股份有限公司        广发证券       广东    广州市   
8               长江证券股份有限公司        长江证券       湖北    武汉市   
9           上海浦东发展银行股份有限公司        浦发银行       上海    上海市   
10              东方金钰股份有限公司        东方金钰       湖北    鄂州市   
11              国金证券股份有限公司        国金证券       四川    成都市   
```
