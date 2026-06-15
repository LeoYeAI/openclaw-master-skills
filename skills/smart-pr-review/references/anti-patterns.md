# 常见反模式库

帮助 reviewer 快速识别代码中的问题模式。每个反模式包含：问题描述、识别方法、正确做法。

---

## 1. 错误处理反模式

### 1.1 吞掉错误（Silent Catch）
```typescript
// ❌ 反模式：catch 后什么都不做
try {
  await saveUser(data);
} catch (e) {
  // ignore
}

// ✅ 正确：至少记录日志，或向上抛出
try {
  await saveUser(data);
} catch (e) {
  logger.error("保存用户失败", { error: e, data });
  throw e;
}
```
**识别**: catch 块为空或只有注释

### 1.2 Pokemon 异常处理（Catch 'Em All）
```python
# ❌ 反模式：捕获所有异常
try:
    result = do_something()
except:
    pass

# ✅ 正确：捕获具体异常
try:
    result = do_something()
except ValueError as e:
    logger.warning(f"输入值无效: {e}")
    result = default_value
```
**识别**: 裸 `except:` 或 `catch (Exception e)` 且处理逻辑不区分异常类型

### 1.3 错误信息无用
```go
// ❌ 反模式：错误信息没有上下文
if err != nil {
    return fmt.Errorf("failed")
}

// ✅ 正确：包含操作、对象、原因
if err != nil {
    return fmt.Errorf("saving user %s to database: %w", userID, err)
}
```
**识别**: 错误信息中缺少变量值、操作名称、资源标识

---

## 2. 并发反模式

### 2.1 竞态条件（Check-Then-Act）
```typescript
// ❌ 反模式：检查和操作不是原子的
if (!cache.has(key)) {
  const value = await expensiveComputation(key);
  cache.set(key, value); // 另一个请求可能已经设置了
}

// ✅ 正确：使用原子操作或锁
const value = await cache.getOrSet(key, () => expensiveComputation(key));
```
**识别**: 先检查状态再修改，且中间没有锁/原子操作

### 2.2 Goroutine 泄漏
```go
// ❌ 反模式：goroutine 无退出机制
func startWorker() {
    go func() {
        for {
            task := <-taskChan // 如果 channel 永远没有数据，goroutine 永远阻塞
            process(task)
        }
    }()
}

// ✅ 正确：使用 context 控制生命周期
func startWorker(ctx context.Context) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return
            case task := <-taskChan:
                process(task)
            }
        }
    }()
}
```
**识别**: goroutine 中无 `select` + `ctx.Done()` 或 done channel

### 2.3 共享可变状态无保护
```python
# ❌ 反模式：多线程访问共享字典
results = {}

def worker(item):
    result = process(item)
    results[item.id] = result  # 竞态条件

# ✅ 正确：使用线程安全的数据结构
from threading import Lock
results = {}
lock = Lock()

def worker(item):
    result = process(item)
    with lock:
        results[item.id] = result
```

---

## 3. 性能反模式

### 3.1 N+1 查询
```typescript
// ❌ 反模式：循环中查询数据库
const users = await db.query("SELECT * FROM users");
for (const user of users) {
  const orders = await db.query(
    "SELECT * FROM orders WHERE user_id = ?", [user.id]
  ); // N 次额外查询！
}

// ✅ 正确：批量查询 + 内存关联
const users = await db.query("SELECT * FROM users");
const userIds = users.map(u => u.id);
const orders = await db.query(
  "SELECT * FROM orders WHERE user_id IN (?)", [userIds]
);
const ordersByUser = groupBy(orders, "user_id");
```
**识别**: 循环体内有数据库查询、API 调用、文件读取

### 3.2 内存泄漏（事件监听器）
```typescript
// ❌ 反模式：useEffect 中注册事件但不清理
useEffect(() => {
  window.addEventListener("resize", handleResize);
}, []);

// ✅ 正确：返回清理函数
useEffect(() => {
  window.addEventListener("resize", handleResize);
  return () => window.removeEventListener("resize", handleResize);
}, []);
```
**识别**: `addEventListener` / `setInterval` / `subscribe` 没有对应的清理

### 3.3 不必要的全量拷贝
```python
# ❌ 反模式：处理大列表时创建多个中间拷贝
result = list(filter(lambda x: x > 0, map(lambda x: x * 2, large_list)))

# ✅ 正确：使用生成器延迟求值
result = (x * 2 for x in large_list if x * 2 > 0)
```
**识别**: 大集合上的链式 map/filter 创建中间数组

---

## 4. 安全反模式

### 4.1 硬编码凭证
```typescript
// ❌ 反模式：密钥写死在代码中
const API_KEY = "sk-1234567890abcdef";
const DB_PASSWORD = "admin123";

// ✅ 正确：从环境变量或密钥管理服务获取
const API_KEY = process.env.API_KEY;
if (!API_KEY) throw new Error("API_KEY 环境变量未设置");
```
**识别**: 代码中包含 `key=`、`token=`、`password=`、`secret=` 等字面量

### 4.2 SQL 注入
```python
# ❌ 反模式：字符串拼接 SQL
query = f"SELECT * FROM users WHERE name = '{user_input}'"
cursor.execute(query)

# ✅ 正确：参数化查询
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```
**识别**: SQL 字符串中使用 f-string、`+`、`format()` 拼接用户输入

### 4.3 路径遍历
```typescript
// ❌ 反模式：直接使用用户输入作为文件路径
app.get("/files/:name", (req, res) => {
  const filePath = path.join("/uploads", req.params.name);
  res.sendFile(filePath); // 用户可以传 ../../etc/passwd
});

// ✅ 正确：验证路径不超出预期目录
app.get("/files/:name", (req, res) => {
  const safeName = path.basename(req.params.name); // 去除路径分隔符
  const filePath = path.join("/uploads", safeName);
  if (!filePath.startsWith("/uploads/")) {
    return res.status(403).send("Forbidden");
  }
  res.sendFile(filePath);
});
```
**识别**: 用户输入与 `path.join` / `os.path.join` / 文件操作结合使用

### 4.4 XSS（跨站脚本）
```typescript
// ❌ 反模式：直接渲染用户输入
return <div dangerouslySetInnerHTML={{ __html: userComment }} />;

// ✅ 正确：使用框架的自动转义，或使用 DOMPurify
import DOMPurify from "dompurify";
return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userComment) }} />;
```
**识别**: `dangerouslySetInnerHTML`、`innerHTML`、`v-html` 使用用户数据

---

## 5. 设计反模式

### 5.1 上帝对象（God Object）
```typescript
// ❌ 反模式：一个类做所有事
class UserService {
  createUser() { ... }
  sendEmail() { ... }
  generateReport() { ... }
  processPayment() { ... }
  uploadAvatar() { ... }
}
```
**识别**: 类/模块超过 500 行，方法涉及多个不相关的领域

### 5.2 过度工程化（Over-Engineering）
```typescript
// ❌ 反模式：一个简单操作搞出三层抽象
interface IUserRepositoryFactory {
  createRepository(): IUserRepository;
}
class UserRepositoryFactory implements IUserRepositoryFactory { ... }

// ✅ 正确：当前只需要一种实现时，直接用函数
async function getUser(id: string): Promise<User> {
  return db.users.findById(id);
}
```
**识别**: 单一实现的接口/抽象类、只调用一次的工厂、为假想需求预留的扩展点

### 5.3 欠工程化（Under-Engineering）
```typescript
// ❌ 反模式：2000 行函数，重复代码到处都是
function handleRequest(req) {
  if (req.type === "create") {
    // 200 行处理逻辑...
  } else if (req.type === "update") {
    // 200 行几乎相同的逻辑...
  } else if (req.type === "delete") {
    // 又是 200 行...
  }
}
```
**识别**: 大量重复代码、函数超过 200 行、深层嵌套（>4 层）

### 5.4 布尔参数陷阱
```typescript
// ❌ 反模式：布尔参数让调用方难以理解
createUser("John", true, false, true);

// ✅ 正确：使用 options 对象
createUser("John", {
  isAdmin: true,
  sendWelcomeEmail: false,
  requireMFA: true,
});
```
**识别**: 函数有 2 个以上布尔参数

---

## 6. API 设计反模式

### 6.1 不一致的错误响应
```typescript
// ❌ 反模式：不同端点返回不同格式的错误
// GET /users/999 → { error: "not found" }
// POST /orders  → { message: "Invalid input", code: 400 }
// PUT /items/1  → "Something went wrong"

// ✅ 正确：统一错误响应格式
// { error: { code: "NOT_FOUND", message: "User 999 not found", details: {} } }
```

### 6.2 破坏向后兼容性
```typescript
// ❌ 反模式：修改现有字段类型
// v1: { "count": 42 }
// v2: { "count": "42" }  // 数字变字符串，客户端会崩

// ✅ 正确：新增字段而非修改
// v2: { "count": 42, "count_str": "42" }
```
**识别**: 修改了现有 API 响应字段的类型或删除了字段

### 6.3 暴露内部实现
```typescript
// ❌ 反模式：API 响应暴露数据库字段名
{ "_id": "507f1f77bcf86cd799439011", "__v": 0, "password_hash": "..." }

// ✅ 正确：使用 DTO 转换
{ "id": "user_123", "name": "John" }
```
**识别**: 响应中包含 `_id`、`__v`、`password_hash`、内部 ID 格式
