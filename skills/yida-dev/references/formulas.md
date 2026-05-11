# 公式函数大全

本文档列出宜搭表单中常用的公式函数。

## 日期时间函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `NOW()` | 当前时间 | `NOW()` |
| `TODAY()` | 当前日期 | `TODAY()` |
| `DATE(year, month, day)` | 构建日期 | `DATE(2024, 1, 1)` |
| `YEAR(date)` | 获取年份 | `YEAR(NOW())` |
| `MONTH(date)` | 获取月份 | `MONTH(NOW())` |
| `DAY(date)` | 获取日 | `DAY(NOW())` |
| `DATEDIF(start, end, unit)` | 日期间隔 | `DATEDIF(TODAY(), 截止日期, 'D')` |
| `DATEADD(date, days)` | 日期加减 | `DATEADD(NOW(), 7)` |
| `EOMONTH(date)` | 月末日期 | `EOMONTH(NOW(), 0)` |

## 文本函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `CONCATENATE(text1, text2, ...)` | 文本连接 | `CONCATENATE(姓名, "的年龄", 年龄)` |
| `LEFT(text, num)` | 左侧取字符 | `LEFT("hello", 2)` → "he" |
| `RIGHT(text, num)` | 右侧取字符 | `RIGHT("hello", 2)` → "lo" |
| `MID(text, start, num)` | 截取文本 | `MID("hello", 2, 2)` → "el" |
| `LEN(text)` | 文本长度 | `LEN("hello")` → 5 |
| `TRIM(text)` | 去除空格 | `TRIM(" hello ")` |
| `UPPER(text)` | 转大写 | `UPPER("abc")` |
| `LOWER(text)` | 转小写 | `LOWER("ABC")` |
| `SUBSTITUTE(text, old, new)` | 替换文本 | `SUBSTITUTE("a-b", "-", ":")` |
| `FIND(find_text, text)` | 查找位置 | `FIND("b", "abc")` → 2 |
| `REPT(text, times)` | 重复文本 | `REPT("a", 3)` → "aaa" |

## 数学函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `SUM(num1, num2, ...)` | 求和 | `SUM(数量, 价格)` |
| `AVERAGE(num1, num2, ...)` | 平均值 | `AVERAGE(成绩1, 成绩2, 成绩3)` |
| `MAX(num1, num2, ...)` | 最大值 | `MAX(数值1, 数值2)` |
| `MIN(num1, num2, ...)` | 最小值 | `MIN(数值1, 数值2)` |
| `ABS(num)` | 绝对值 | `ABS(-5)` → 5 |
| `ROUND(num, digits)` | 四舍五入 | `ROUND(3.14159, 2)` → 3.14 |
| `FLOOR(num)` | 向下取整 | `FLOOR(3.9)` → 3 |
| `CEIL(num)` | 向上取整 | `CEIL(3.1)` → 4 |
| `MOD(num, divisor)` | 取余 | `MOD(10, 3)` → 1 |
| `POWER(base, exp)` | 幂运算 | `POWER(2, 3)` → 8 |
| `SQRT(num)` | 平方根 | `SQRT(4)` → 2 |

## 逻辑函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `IF(condition, true_val, false_val)` | 条件判断 | `IF(成绩>=60, "及格", "不及格")` |
| `AND(cond1, cond2, ...)` | 且 | `IF(AND(语文>90, 数学>90), "优秀", "")` |
| `OR(cond1, cond2, ...)` | 或 | `IF(OR(语文<60, 数学<60), "有挂科", "")` |
| `NOT(cond)` | 非 | `NOT(已完成)` |
| `IFERROR(val, error_val)` | 错误处理 | `IFERROR(计算结果, 0)` |

## 数组函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `ARRAY(value1, value2, ...)` | 构建数组 | `ARRAY(1, 2, 3)` |
| `INCLUDES(array, value)` | 包含判断 | `INCLUDES(ARRAY(1,2,3), 2)` |
| `INDEX(array, position)` | 获取元素 | `INDEX(ARRAY("a","b"), 2)` → "b" |
| `JOIN(array, separator)` | 数组合并 | `JOIN(ARRAY("a","b"), ",")` → "a,b" |

## 用户函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `USERFIELD(user_type)` | 当前用户信息 | `USERFIELD("userId")` |
| `USERDEPT()` | 当前用户部门 | `USERDEPT()` |
| `DEPTFIELD(deptId, field)` | 部门字段 | `DEPTFIELD(部门, "deptName")` |

## 数据查询函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `QUERY(formUuid, conditions)` | 查询数据 | `QUERY("FORM_xxx", "状态='已完成'")` |
| `LOOKUP(formUuid, matchField, returnField, matchValue)` | 查找 | `LOOKUP("商品表", "商品编码", "单价", "A001")` |
| `COUNTIF(formUuid, condition)` | 条件计数 | `COUNTIF("报名表", "状态='已报名'")` |
| `SUMIF(formUuid, sumField, condition)` | 条件求和 | `SUMIF("订单表", "金额", "客户='A公司'")` |

## 其他函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `UUID()` | 生成唯一ID | `UUID()` |
| `RAND()` | 随机数 | `RAND()` |
| `RECORDID()` | 当前记录ID | `RECORDID()` |
| `CREATEDTIME()` | 创建时间 | `CREATEDTIME()` |
| `MODIFIEDTIME()` | 修改时间 | `MODIFIEDTIME()` |

## 常见公式示例

### 计算年龄
```
DATEDIF(出生日期, TODAY(), 'Y')
```

### 判断是否逾期
```
IF(截止日期 < TODAY(), "已逾期", "未逾期")
```

### 计算折扣
```
IF(数量>=10, 0.9, IF(数量>=5, 0.95, 1))
```

### 提取部门
```
LEFT(部门路径, FIND("/", 部门路径 & "/") - 1)
```

### 序号生成
```
"NO." & TEXT(RECORDID(), "0000")
```

### 多级联动
```
IFS(省="浙江省", ARRAY("杭州市","宁波市","温州市"), 省="江苏省", ARRAY("南京市","苏州市"))
```
