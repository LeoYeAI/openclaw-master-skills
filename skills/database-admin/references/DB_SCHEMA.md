# 数据库设计规范 Database Schema Guidelines 📜

## 一、表结构设计 Principles

### 🔹 命名规范
- **表名**: 全小写，下划线分隔（如 `user_profiles`）
- **列名**: snake_case（如 `created_at`, `full_name`）
- **索引名**: `{table}_{column}_idx`

### 🔹 数据类型选择
| 用途 | 推荐类型 | 说明 |
|------|----------|------|
| 主键/自增 | SERIAL / BIGSERIAL | PostgreSQL 特有，自动增长 |
| 短文本 | VARCHAR(n) | 长度根据实际需求设定 |
| 长文本 | TEXT | 文章、描述等 |
| 数值 | NUMERIC(p,s) | 金额用定点数（如 NUMERIC(10,2)） |
| 大整数 | BIGINT | 计数器等可能超过 INT32 的字段 |
| 日期时间 | TIMESTAMP WITH TIME ZONE | 建议使用带时区的时间戳 |
| JSON 数据 | JSONB | 嵌套文档存储 |

### 🔹 索引策略
- **主键**: 自动创建唯一索引
- **查询字段**: 常用 WHERE/SORT/DISTINCT 字段创建索引
- **多列索引**: 遵循 WHERE 条件的列顺序（如 `WHERE status='active' AND created_at>`）
- **避免**: 在低基数列上创建索引

## 二、常见表结构 Examples

### 1. 用户表 users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
);

COMMENT ON TABLE users IS '用户账户表';
```

### 2. 订单表 orders
```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL,
    total_amount NUMERIC(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    status VARCHAR(30) DEFAULT 'pending',
    payment_method VARCHAR(50),
    shipping_address TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_orders_user (user_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_created (created_at)
);

-- 检查约束
ALTER TABLE orders ADD CONSTRAINT chk_quantity CHECK (quantity > 0);
```

### 3. 商品表 products
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    price NUMERIC(10,2) NOT NULL DEFAULT 0,
    cost NUMERIC(10,2) NOT NULL DEFAULT 0,
    stock_quantity INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    image_urls JSONB, -- 多图存储
    
    INDEX idx_products_category (category),
    INDEX idx_products_price_range ((price)) -- 复合索引用于价格范围查询
);
```

## 三、查询优化 Tips

### 🔹 常用模式
- **分页查询**: `LIMIT offset, count`
- **聚合统计**: `GROUP BY ... HAVING ...`
- **子查询**: CTE (WITH) 优于多层嵌套子查询
- **外连接**: 使用 `LEFT JOIN` 保留左表所有记录

### 🔹 避免的陷阱
1. 不要在 WHERE 中直接比较 JSONB 字段（除非创建 GIN/GIST 索引）
2. 避免选择不必要的列（SELECT *）
3. 不要在大表上使用 ORDER BY 随机列

## 四、事务安全 Transaction Safety

```sql
-- BEGIN/COMMIT 包裹批量操作
BEGIN;
UPDATE orders SET status = 'paid' WHERE id IN (1,2,3);
INSERT INTO order_items (order_id, product_id, quantity) VALUES ...;
COMMIT;

-- 捕获约束违规
DO $$
BEGIN
    INSERT INTO orders (...) VALUES ...
    EXCEPTION WHEN unique_violation THEN
        RAISE EXCEPTION '用户已存在';
END $$;
```

---

*杜子美诗曰："读书破万卷，下笔如有神" —— 数据结构清晰，查询自然流畅*
