# Admin 管理后台模块参考文档

> **版本：** v2.2 · **Phase：** Layer 1（管理栈）
> **职责：** RBAC 权限体系、商品/订单/用户 CRUD、运营统计、审计日志

---

## 一、RBAC 权限体系

### 角色定义

```javascript
// sharing/constants.js
export const UserRole = {
  USER:   'user',     // 普通用户：下单、查看自己的订单
  ADMIN:  'admin',    // 管理员：全站 CRUD
  MANAGER:'manager',  // 运营：订单管理、商品上下架
};
```

### 权限矩阵

| 操作 | user（本人） | manager | admin |
|------|------------|---------|-------|
| 查看自己的订单 | ✅ | ✅ | ✅ |
| 管理任意订单 | ❌ | ✅ | ✅ |
| 商品上架/下架 | ❌ | ✅ | ✅ |
| 修改商品价格 | ❌ | ❌ | ✅ |
| 用户管理 | ❌ | ❌ | ✅ |
| 查看运营统计 | ❌ | ✅ | ✅ |
| 审计日志 | ❌ | ❌ | ✅ |
| 系统设置 | ❌ | ❌ | ✅ |

---

## 二、Admin Guard 中间件

```javascript
// cloud-functions/utils/admin-guard.js

/**
 * 验证管理员权限
 * @param {Request} request
 * @param {Object} env
 * @param {string[]} allowedRoles - 允许的角色，如 ['admin', 'manager']
 * @returns {{ userId, role } | Response} 成功返回用户信息，失败返回 Response
 */
export async function adminGuard(request, env, allowedRoles = ['admin']) {
  const authHeader = request.headers.get('Authorization') || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;

  if (!token) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
  }

  const payload = await verifyJWT(token, env);
  if (!payload) {
    return new Response(JSON.stringify({ error: 'Invalid token' }), { status: 401 });
  }

  if (!allowedRoles.includes(payload.role)) {
    return new Response(JSON.stringify({ error: 'Forbidden: insufficient permissions' }), { status: 403 });
  }

  return { userId: payload.sub, role: payload.role };
}
```

---

## 三、商品管理 CRUD

### 3.1 列表查询（支持分页 + 筛选）

```javascript
// cloud-functions/api/admin/products.js

export async function onRequest(request, env) {
  // Admin Guard
  const auth = await adminGuard(request, env);
  if (auth instanceof Response) return auth;

  const url = new URL(request.url);
  const page = Math.max(1, parseInt(url.searchParams.get('page') || '1'));
  const pageSize = Math.min(100, parseInt(url.searchParams.get('pageSize') || '20'));
  const offset = (page - 1) * pageSize;
  const category = url.searchParams.get('category');
  const status = url.searchParams.get('status'); // active / inactive
  const keyword = url.searchParams.get('keyword');

  const pool = new Pool({ connectionString: env.DATABASE_URL });

  // WHERE 条件构建
  const conditions = [];
  const params = [];
  if (category) { conditions.push('category_id = ?'); params.push(category); }
  if (status) { conditions.push('status = ?'); params.push(status); }
  if (keyword) { conditions.push('name LIKE ?'); params.push(`%${keyword}%`); }
  const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

  const whereClause = where || 'WHERE 1=1';

  const [rows] = await pool.query(
    `SELECT id, name, category_id, price, stock, status, version, created_at
     FROM products ${whereClause}
     ORDER BY id DESC
     LIMIT ? OFFSET ?`,
    [...params, pageSize, offset]
  );

  const [[{ total }]] = await pool.query(
    `SELECT COUNT(*) as total FROM products ${whereClause}`, params
  );

  await pool.end();

  return new Response(JSON.stringify({
    data: rows,
    pagination: { page, pageSize, total, pages: Math.ceil(total / pageSize) }
  }), { headers: { 'Content-Type': 'application/json' } });
}
```

### 3.2 创建商品（乐观锁）

```javascript
// POST /api/admin/products（创建）
// PUT /api/admin/products/:id（更新）

export async function onRequest(request, env) {
  const auth = await adminGuard(request, env);
  if (auth instanceof Response) return auth;

  const body = await request.json();
  const { id, name, price, stock, category_id, status } = body;

  if (!name || !price) {
    return new Response(JSON.stringify({ error: 'name 和 price 为必填项' }), { status: 400 });
  }

  const pool = new Pool({ connectionString: env.DATABASE_URL });

  try {
    if (id) {
      // 更新（乐观锁）
      const [result] = await pool.query(
        `UPDATE products SET name=?, price=?, stock=?, category_id=?, status=?,
         version=version+1 WHERE id=? AND version=?`,
        [name, price, stock, category_id, status, id, body.version]
      );
      if (result.affectedRows === 0) {
        return new Response(JSON.stringify({ error: '并发冲突，请重试' }), { status: 409 });
      }
    } else {
      // 创建
      const [result] = await pool.query(
        `INSERT INTO products (name, price, stock, category_id, status) VALUES (?, ?, ?, ?, ?)`,
        [name, price, stock || 0, category_id, status || 'active']
      );
      await adminLog(pool, auth.userId, 'product:create', `ID=${result.insertId}`);
    }

    return new Response(JSON.stringify({ ok: true }), { headers: { 'Content-Type': 'application/json' } });
  } finally {
    await pool.end();
  }
}
```

---

## 四、运营统计

```javascript
// cloud-functions/api/admin/stats.js

export async function onRequest(request, env) {
  const auth = await adminGuard(request, env, ['admin', 'manager']);
  if (auth instanceof Response) return auth;

  const pool = new Pool({ connectionString: env.DATABASE_URL });

  const [[todayOrders]] = await pool.query(`
    SELECT COUNT(*) as count, COALESCE(SUM(total), 0) as revenue
    FROM orders WHERE DATE(created_at) = CURDATE() AND status != 'CANCELLED'
  `);

  const [[totalUsers]] = await pool.query(`SELECT COUNT(*) as count FROM users`);

  const [[totalProducts]] = await pool.query(`SELECT COUNT(*) as count FROM products WHERE status='active'`);

  const [ordersByStatus] = await pool.query(`
    SELECT status, COUNT(*) as count, SUM(total) as revenue
    FROM orders GROUP BY status
  `);

  const [recentOrders] = await pool.query(`
    SELECT o.id, o.order_no, o.total, o.status, o.created_at, u.email
    FROM orders o JOIN users u ON u.id = o.user_id
    ORDER BY o.created_at DESC LIMIT 10
  `);

  await pool.end();

  return new Response(JSON.stringify({
    today: { orders: todayOrders.count, revenue: todayOrders.revenue },
    total: { users: totalUsers.count, products: totalProducts.count },
    byStatus: ordersByStatus,
    recentOrders
  }), { headers: { 'Content-Type': 'application/json' } });
}

async function adminLog(pool, adminId, action, target) {
  await pool.query(
    'INSERT INTO admin_logs (admin_id, action, target) VALUES (?, ?, ?)',
    [adminId, action, target]
  );
}
```

---

## 五、审计日志表

```sql
CREATE TABLE admin_logs (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  admin_id    BIGINT UNSIGNED NOT NULL,
  action      VARCHAR(64) NOT NULL,  -- product:create / product:update / order:cancel / ...
  target      VARCHAR(128),
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (admin_id) REFERENCES users(id)
);

CREATE INDEX idx_admin_logs_admin ON admin_logs(admin_id);
CREATE INDEX idx_admin_logs_action ON admin_logs(action);
CREATE INDEX idx_admin_logs_created ON admin_logs(created_at);
```

> **记录时机**：所有 Admin CRUD 操作写入 `admin_logs`，包括创建/更新/删除商品、修改订单状态、修改用户角色。
