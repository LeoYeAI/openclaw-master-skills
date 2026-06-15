# MindsDB SQL查询示例

## 基础查询

### SELECT基础

```sql
-- 查询所有列
SELECT * FROM employees

-- 查询指定列
SELECT employee_id, name, department FROM employees

-- 查询并重命名列
SELECT 
  employee_id AS ID,
  name AS employee_name,
  department AS dept
FROM employees
```

### WHERE条件

```sql
-- 等于条件
SELECT * FROM employees WHERE department = 'Sales'

-- 多条件AND
SELECT * FROM employees 
WHERE department = 'Sales' AND salary > 50000

-- 多条件OR
SELECT * FROM employees 
WHERE department = 'Sales' OR department = 'Marketing'

-- IN条件
SELECT * FROM employees 
WHERE department IN ('Sales', 'Marketing', 'IT')

-- BETWEEN条件
SELECT * FROM employees 
WHERE salary BETWEEN 40000 AND 60000

-- LIKE模糊查询
SELECT * FROM employees 
WHERE name LIKE 'John%'

-- NULL值查询
SELECT * FROM employees 
WHERE manager_id IS NULL

-- NOT条件
SELECT * FROM employees 
WHERE department NOT IN ('HR', 'Finance')
```

### 排序和限制

```sql
-- 升序排序
SELECT * FROM employees ORDER BY salary ASC

-- 降序排序
SELECT * FROM employees ORDER BY salary DESC

-- 多列排序
SELECT * FROM employees 
ORDER BY department ASC, salary DESC

-- 限制结果数量
SELECT * FROM employees LIMIT 10

-- 分页查询
SELECT * FROM employees 
LIMIT 10 OFFSET 20
```

## 聚合查询

### 基础聚合

```sql
-- 计数
SELECT COUNT(*) FROM employees

-- 去重计数
SELECT COUNT(DISTINCT department) FROM employees

-- 求和
SELECT SUM(salary) FROM employees

-- 平均值
SELECT AVG(salary) FROM employees

-- 最大值
SELECT MAX(salary) FROM employees

-- 最小值
SELECT MIN(salary) FROM employees
```

### GROUP BY分组

```sql
-- 按部门分组统计
SELECT 
  department,
  COUNT(*) as employee_count,
  AVG(salary) as avg_salary,
  SUM(salary) as total_salary
FROM employees
GROUP BY department

-- 多列分组
SELECT 
  department,
  job_title,
  COUNT(*) as count,
  AVG(salary) as avg_salary
FROM employees
GROUP BY department, job_title
```

### HAVING过滤

```sql
-- 过滤分组结果
SELECT 
  department,
  COUNT(*) as employee_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 5

-- 复杂条件
SELECT 
  department,
  AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000
```

## 连接查询

### INNER JOIN

```sql
-- 内连接
SELECT 
  e.employee_id,
  e.name,
  d.department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
```

### LEFT JOIN

```sql
-- 左连接
SELECT 
  e.employee_id,
  e.name,
  d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
```

### RIGHT JOIN

```sql
-- 右连接
SELECT 
  e.employee_id,
  e.name,
  d.department_name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.department_id
```

### FULL OUTER JOIN

```sql
-- 全外连接
SELECT 
  e.employee_id,
  e.name,
  d.department_name
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.department_id
```

### 多表连接

```sql
-- 三表连接
SELECT 
  o.order_id,
  c.customer_name,
  p.product_name,
  oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
```

### 自连接

```sql
-- 查找员工及其经理
SELECT 
  e.name AS employee,
  m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
```

## 子查询

### 标量子查询

```sql
-- 查找工资高于平均工资的员工
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
```

### IN子查询

```sql
-- 查找有订单的客户
SELECT customer_id, customer_name
FROM customers
WHERE customer_id IN (SELECT DISTINCT customer_id FROM orders)
```

### EXISTS子查询

```sql
-- 查找有订单的客户
SELECT customer_id, customer_name
FROM customers c
WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
)
```

### FROM子查询

```sql
-- 使用子查询作为表
SELECT department, avg_salary
FROM (
  SELECT 
    department,
    AVG(salary) as avg_salary
  FROM employees
  GROUP BY department
) AS dept_avg
WHERE avg_salary > 50000
```

## 窗口函数

### ROW_NUMBER

```sql
-- 为每行分配唯一编号
SELECT 
  name,
  department,
  salary,
  ROW_NUMBER() OVER (ORDER BY salary DESC) as rank
FROM employees
```

### RANK

```sql
-- 排名（相同值相同排名）
SELECT 
  name,
  department,
  salary,
  RANK() OVER (ORDER BY salary DESC) as rank
FROM employees
```

### DENSE_RANK

```sql
-- 密集排名（相同值相同排名，排名连续）
SELECT 
  name,
  department,
  salary,
  DENSE_RANK() OVER (ORDER BY salary DESC) as rank
FROM employees
```

### LAG和LEAD

```sql
-- 查看前一行和后一行数据
SELECT 
  order_date,
  amount,
  LAG(amount) OVER (ORDER BY order_date) as prev_amount,
  LEAD(amount) OVER (ORDER BY order_date) as next_amount
FROM orders
```

### 聚合窗口函数

```sql
-- 计算累计总和
SELECT 
  order_date,
  amount,
  SUM(amount) OVER (ORDER BY order_date) as running_total
FROM orders

-- 计算移动平均
SELECT 
  order_date,
  amount,
  AVG(amount) OVER (
    ORDER BY order_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) as moving_avg
FROM orders
```

## CASE表达式

### 简单CASE

```sql
SELECT 
  name,
  department,
  CASE department
    WHEN 'Sales' THEN '销售部'
    WHEN 'Marketing' THEN '市场部'
    WHEN 'IT' THEN '技术部'
    ELSE '其他部门'
  END AS department_cn
FROM employees
```

### 搜索CASE

```sql
SELECT 
  name,
  salary,
  CASE 
    WHEN salary >= 80000 THEN '高级'
    WHEN salary >= 60000 THEN '中级'
    WHEN salary >= 40000 THEN '初级'
    ELSE '实习'
  END AS level
FROM employees
```

## 数据操作

### INSERT

```sql
-- 插入单行
INSERT INTO employees (name, department, salary)
VALUES ('John Doe', 'Sales', 50000)

-- 插入多行
INSERT INTO employees (name, department, salary)
VALUES 
  ('Jane Smith', 'Marketing', 55000),
  ('Bob Johnson', 'IT', 60000)
```

### UPDATE

```sql
-- 更新单列
UPDATE employees
SET salary = salary * 1.1
WHERE department = 'Sales'

-- 更新多列
UPDATE employees
SET salary = 55000,
    department = 'Marketing'
WHERE employee_id = 1
```

### DELETE

```sql
-- 删除指定行
DELETE FROM employees
WHERE employee_id = 1

-- 条件删除
DELETE FROM employees
WHERE department = 'Sales' AND salary < 40000
```

## 数据定义

### CREATE TABLE

```sql
CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  department VARCHAR(50),
  salary DECIMAL(10, 2),
  hire_date DATE,
  manager_id INT,
  FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
)
```

### ALTER TABLE

```sql
-- 添加列
ALTER TABLE employees ADD COLUMN email VARCHAR(100)

-- 修改列
ALTER TABLE employees MODIFY COLUMN salary DECIMAL(12, 2)

-- 删除列
ALTER TABLE employees DROP COLUMN email
```

### DROP TABLE

```sql
DROP TABLE IF EXISTS employees
```

### CREATE INDEX

```sql
-- 创建索引
CREATE INDEX idx_department ON employees(department)

-- 创建复合索引
CREATE INDEX idx_dept_salary ON employees(department, salary)

-- 创建唯一索引
CREATE UNIQUE INDEX idx_email ON employees(email)
```

## 高级查询

### UNION

```sql
-- 合并查询结果
SELECT name, email FROM customers
UNION
SELECT name, email FROM employees

-- 保留重复
SELECT name, email FROM customers
UNION ALL
SELECT name, email FROM employees
```

### INTERSECT

```sql
-- 查找交集
SELECT customer_id FROM orders_2023
INTERSECT
SELECT customer_id FROM orders_2024
```

### EXCEPT

```sql
-- 查找差集
SELECT customer_id FROM orders_2023
EXCEPT
SELECT customer_id FROM orders_2024
```

### 递归查询

```sql
-- 查询组织结构
WITH RECURSIVE org_tree AS (
  -- 基础查询
  SELECT employee_id, name, manager_id, 1 as level
  FROM employees
  WHERE manager_id IS NULL
  
  UNION ALL
  
  -- 递归查询
  SELECT e.employee_id, e.name, e.manager_id, ot.level + 1
  FROM employees e
  JOIN org_tree ot ON e.manager_id = ot.employee_id
)
SELECT * FROM org_tree ORDER BY level, employee_id
```

## 实用函数

### 字符串函数

```sql
-- 大小写转换
SELECT UPPER(name), LOWER(name) FROM employees

-- 字符串长度
SELECT name, LENGTH(name) FROM employees

-- 字符串拼接
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM employees

-- 字符串截取
SELECT SUBSTRING(name, 1, 5) FROM employees

-- 去除空格
SELECT TRIM(name) FROM employees

-- 替换字符串
SELECT REPLACE(name, 'John', 'Jane') FROM employees
```

### 日期函数

```sql
-- 当前日期时间
SELECT NOW(), CURRENT_DATE, CURRENT_TIME

-- 日期加减
SELECT DATE_ADD(NOW(), INTERVAL 7 DAY)
SELECT DATE_SUB(NOW(), INTERVAL 1 MONTH)

-- 日期差
SELECT DATEDIFF('2024-12-31', '2024-01-01')

-- 日期格式化
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d')

-- 提取日期部分
SELECT YEAR(NOW()), MONTH(NOW()), DAY(NOW())
```

### 数值函数

```sql
-- 四舍五入
SELECT ROUND(3.14159, 2)

-- 向上取整
SELECT CEIL(3.14)

-- 向下取整
SELECT FLOOR(3.99)

-- 绝对值
SELECT ABS(-10)

-- 幂运算
SELECT POWER(2, 3)

-- 平方根
SELECT SQRT(16)
```

## 性能优化

### 使用索引

```sql
-- 创建索引
CREATE INDEX idx_name ON employees(name)

-- 使用索引的查询
SELECT * FROM employees WHERE name = 'John Doe'
```

### 限制结果

```sql
-- 使用LIMIT
SELECT * FROM employees LIMIT 100

-- 分页查询
SELECT * FROM employees LIMIT 10 OFFSET 0
SELECT * FROM employees LIMIT 10 OFFSET 10
```

### 避免SELECT *

```sql
-- 不推荐
SELECT * FROM employees

-- 推荐
SELECT employee_id, name, department FROM employees
```

### 使用EXISTS代替IN

```sql
-- 不推荐
SELECT * FROM employees
WHERE department_id IN (SELECT department_id FROM departments WHERE active = 1)

-- 推荐
SELECT * FROM employees e
WHERE EXISTS (
  SELECT 1 FROM departments d 
  WHERE d.department_id = e.department_id AND d.active = 1
)
```

## 常见模式

### 分页查询

```sql
-- 使用OFFSET和LIMIT
SELECT * FROM employees
ORDER BY employee_id
LIMIT 10 OFFSET 0

-- 使用WHERE子句（更高效）
SELECT * FROM employees
WHERE employee_id > 100
ORDER BY employee_id
LIMIT 10
```

### 查找重复记录

```sql
-- 查找重复的邮箱
SELECT email, COUNT(*) as count
FROM customers
GROUP BY email
HAVING COUNT(*) > 1

-- 查找并删除重复记录
DELETE FROM customers
WHERE customer_id NOT IN (
  SELECT MIN(customer_id)
  FROM customers
  GROUP BY email
)
```

### 计算百分比

```sql
SELECT 
  department,
  COUNT(*) as employee_count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM employees), 2) as percentage
FROM employees
GROUP BY department
```

### 年度对比

```sql
SELECT 
  YEAR(order_date) as year,
  SUM(amount) as total_sales
FROM orders
WHERE YEAR(order_date) IN (2023, 2024)
GROUP BY YEAR(order_date)
ORDER BY year
```

## 错误处理

### TRY-CATCH模式

```sql
-- 使用COALESCE处理NULL
SELECT 
  name,
  COALESCE(salary, 0) as salary
FROM employees

-- 使用NULLIF避免除零错误
SELECT 
  name,
  salary / NULLIF(hours_worked, 0) as hourly_rate
FROM employees
```

### 数据验证

```sql
-- 检查数据完整性
SELECT 
  COUNT(*) as total,
  COUNT(CASE WHEN name IS NULL THEN 1 END) as null_names,
  COUNT(CASE WHEN salary < 0 THEN 1 END) as negative_salaries
FROM employees
```
