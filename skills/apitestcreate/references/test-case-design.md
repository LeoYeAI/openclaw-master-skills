# 接口测试用例设计详细指南

## 一、参数校验测试用例设计

### 1. 字符串参数测试矩阵

| 测试维度 | 测试值 | 说明 |
|----------|--------|------|
| 空值 | `""`, `null`, `"   "` | 空字符串、null、纯空格 |
| 长度边界 | `min-1`, `min`, `max`, `max+1` | 边界值测试 |
| 字符类型 | 纯字母、纯数字、纯中文、混合 | 字符组成测试 |
| 特殊字符 | `<script>`, `' OR '1'='1`, `&lt;` | XSS、SQL注入测试 |
| Unicode | emoji、生僻字、日文韩文 | 多语言支持 |
| 格式 | 邮箱、手机号、身份证、URL | 正则格式校验 |

### 2. 数字参数测试矩阵

| 测试维度 | 测试值 | 说明 |
|----------|--------|------|
| 零值 | `0`, `-0`, `0.0` | 零的各种表示 |
| 正数边界 | `min-1`, `min`, `max`, `max+1` | 取值范围边界 |
| 负数边界 | 如果允许负数 | 负数边界值 |
| 精度 | `1.23456789`, `1.1e10` | 小数精度、科学计数法 |
| 类型转换 | `"123"`, `"abc"`, `true` | 类型转换测试 |
| 溢出 | `MAX_INT+1`, `-MAX_INT-1` | 整数溢出 |

### 3. 枚举参数测试矩阵

```python
def test_enum_parameter(api_path, param_name, valid_values):
    """
    枚举参数测试用例生成器
    
    Args:
        api_path: 接口路径
        param_name: 参数名
        valid_values: 有效枚举值列表
    
    Returns:
        测试用例列表
    """
    test_cases = []
    
    # 测试每个有效枚举值
    for value in valid_values:
        test_cases.append({
            "name": f"有效枚举值-{value}",
            "param": {param_name: value},
            "expected": "success"
        })
    
    # 测试无效枚举值
    invalid_values = [
        "INVALID_ENUM",
        "",
        None,
        999,
        "valid_enum_lower_case",  # 大小写测试
    ]
    
    for value in invalid_values:
        test_cases.append({
            "name": f"无效枚举值-{value}",
            "param": {param_name: value},
            "expected": "error"
        })
    
    return test_cases
```

---

## 二、业务逻辑测试用例设计

### 1. 状态机测试

```
状态转换图示例：

[待支付] --支付成功--> [已支付] --发货--> [已发货] --签收--> [已完成]
    |                     |
    --取消--> [已取消]   --退款--> [已退款]
```

**状态转换测试用例：**

| 当前状态 | 操作 | 目标状态 | 是否合法 |
|----------|------|----------|----------|
| 待支付 | 支付 | 已支付 | ✓ |
| 待支付 | 取消 | 已取消 | ✓ |
| 已支付 | 发货 | 已发货 | ✓ |
| 已支付 | 取消 | 已取消 | ✗ |
| 已支付 | 退款 | 已退款 | ✓ |
| 已发货 | 签收 | 已完成 | ✓ |

### 2. 并发场景测试

```python
import threading
import time

class ConcurrencyTest:
    """并发测试工具类"""
    
    def __init__(self, api_client, num_threads=10):
        self.client = api_client
        self.num_threads = num_threads
        self.results = []
        self.lock = threading.Lock()
    
    def concurrent_request(self, func, *args):
        """并发执行请求"""
        def worker():
            try:
                result = func(*args)
                with self.lock:
                    self.results.append({"success": True, "data": result})
            except Exception as e:
                with self.lock:
                    self.results.append({"success": False, "error": str(e)})
        
        threads = [threading.Thread(target=worker) for _ in range(self.num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        return self.results
    
    def test_concurrent_update(self, resource_id):
        """测试并发更新"""
        return self.concurrent_request(
            self.client.update_resource,
            resource_id,
            {"value": time.time()}
        )
```

### 3. 数据一致性测试

```python
def test_data_consistency_after_create(api_client, db_client):
    """创建后数据一致性测试"""
    
    # 1. 调用API创建数据
    create_data = {
        "name": "测试产品",
        "price": 99.99,
        "stock": 100
    }
    response = api_client.create_product(create_data)
    product_id = response["data"]["id"]
    
    # 2. 直接查询数据库验证
    db_record = db_client.query(
        "SELECT * FROM products WHERE id = ?", 
        (product_id,)
    )
    
    # 3. 比对API返回与数据库记录
    assert db_record["name"] == create_data["name"]
    assert float(db_record["price"]) == create_data["price"]
    assert db_record["stock"] == create_data["stock"]
    
    # 4. 通过API查询验证
    api_record = api_client.get_product(product_id)
    assert api_record["data"]["name"] == create_data["name"]
    assert api_record["data"]["price"] == create_data["price"]
    assert api_record["data"]["stock"] == create_data["stock"]
```

---

## 三、接口响应校验模板

### 1. 列表接口响应校验

```python
def validate_list_api_response(response, config):
    """
    列表接口响应校验器
    
    config = {
        "required_fields": ["id", "name", "status"],
        "field_types": {
            "id": int,
            "name": str,
            "status": int,
            "created_at": str
        },
        "pagination": True,
        "max_items": 100
    }
    """
    errors = []
    
    # 校验响应结构
    if "code" not in response:
        errors.append("缺少code字段")
    if "data" not in response:
        errors.append("缺少data字段")
        return errors
    
    data = response["data"]
    
    # 校验分页信息
    if config.get("pagination"):
        pagination_fields = ["total", "page", "page_size"]
        for field in pagination_fields:
            if field not in response:
                errors.append(f"缺少分页字段: {field}")
    
    # 校验列表项
    if not isinstance(data, list):
        errors.append("data字段应为数组")
        return errors
    
    if config.get("max_items") and len(data) > config["max_items"]:
        errors.append(f"返回数据超过最大限制: {len(data)} > {config['max_items']}")
    
    # 校验每条记录
    for i, item in enumerate(data):
        # 必填字段
        for field in config.get("required_fields", []):
            if field not in item:
                errors.append(f"第{i+1}条记录缺少字段: {field}")
        
        # 字段类型
        for field, expected_type in config.get("field_types", {}).items():
            if field in item and item[field] is not None:
                if not isinstance(item[field], expected_type):
                    errors.append(
                        f"第{i+1}条记录字段{field}类型错误: "
                        f"期望{expected_type}, 实际{type(item[field])}"
                    )
    
    return errors
```

### 2. 错误响应校验

```python
def validate_error_response(response, expected_error):
    """
    错误响应校验
    
    expected_error = {
        "code": 10001,
        "message_contains": "参数",
        "http_status": 400
    }
    """
    errors = []
    
    # 校验HTTP状态码
    if response.status_code != expected_error.get("http_status", 400):
        errors.append(
            f"HTTP状态码错误: 期望{expected_error.get('http_status')}, "
            f"实际{response.status_code}"
        )
    
    data = response.json()
    
    # 校验错误码
    if "code" in expected_error:
        if data.get("code") != expected_error["code"]:
            errors.append(
                f"错误码错误: 期望{expected_error['code']}, "
                f"实际{data.get('code')}"
            )
    
    # 校验错误信息
    if "message_contains" in expected_error:
        if expected_error["message_contains"] not in data.get("message", ""):
            errors.append(
                f"错误信息不包含: {expected_error['message_contains']}, "
                f"实际{data.get('message')}"
            )
    
    return errors
```

---

## 四、性能测试场景

### 1. 响应时间基准

| 接口类型 | P50 | P95 | P99 | 最大值 |
|----------|-----|-----|-----|--------|
| 简单查询 | <50ms | <100ms | <200ms | <500ms |
| 复杂查询 | <200ms | <500ms | <1000ms | <2000ms |
| 写入操作 | <100ms | <300ms | <500ms | <1000ms |
| 批量操作 | <500ms | <2000ms | <5000ms | <10000ms |

### 2. 性能测试脚本

```python
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

def performance_test(api_func, num_requests=100, concurrency=10):
    """
    性能测试工具
    
    Args:
        api_func: 要测试的API函数
        num_requests: 总请求数
        concurrency: 并发数
    """
    response_times = []
    errors = []
    
    def make_request():
        start = time.time()
        try:
            api_func()
            return time.time() - start, None
        except Exception as e:
            return time.time() - start, str(e)
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        results = list(executor.map(lambda _: make_request(), range(num_requests)))
    
    for elapsed, error in results:
        response_times.append(elapsed * 1000)  # 转换为毫秒
        if error:
            errors.append(error)
    
    response_times.sort()
    
    return {
        "total_requests": num_requests,
        "success_count": num_requests - len(errors),
        "error_count": len(errors),
        "error_rate": len(errors) / num_requests * 100,
        "avg_ms": statistics.mean(response_times),
        "min_ms": min(response_times),
        "max_ms": max(response_times),
        "p50_ms": response_times[int(num_requests * 0.5)],
        "p95_ms": response_times[int(num_requests * 0.95)],
        "p99_ms": response_times[int(num_requests * 0.99)],
    }
```

---

## 五、补充测试场景设计

### 1. 通用信息校验测试设计

```python
def test_url_validation(api_client):
    """URL校验测试"""
    # 正确的URL
    response = api_client.request("GET", "/api/users/123")
    assert response.status_code in [200, 404]  # 资源存在或不存在但URL正确
    
    # 错误的URL
    response = api_client.request("GET", "/api/invalid/url/path")
    assert response.status_code == 404

def test_http_method_validation(api_client):
    """请求方法校验测试"""
    # 正确的请求方法
    response = api_client.post("/api/users", {"name": "test"})
    assert response.status_code in [200, 201]
    
    # 错误的请求方法
    response = api_client.get("/api/users", {"name": "test"})  # POST接口用GET
    assert response.status_code == 405

def test_request_header_validation(api_client):
    """请求头校验测试"""
    # 正确的Content-Type
    headers = {"Content-Type": "application/json"}
    response = api_client.post("/api/users", {"name": "test"}, headers=headers)
    assert response.status_code in [200, 201]
    
    # 错误的Content-Type
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = api_client.post("/api/users", "name=test", headers=headers)
    assert response.status_code == 400

def test_authentication_validation(api_client):
    """接口鉴权校验测试"""
    # 正确的token
    headers = {"Authorization": "Bearer valid_token"}
    response = api_client.get("/api/profile", headers=headers)
    assert response.status_code == 200
    
    # 不传认证信息
    response = api_client.get("/api/profile")
    assert response.status_code == 401
    
    # 错误的认证信息
    headers = {"Authorization": "Bearer invalid_token"}
    response = api_client.get("/api/profile", headers=headers)
    assert response.status_code == 401
    
    # 失效的认证信息
    headers = {"Authorization": "Bearer expired_token"}
    response = api_client.get("/api/profile", headers=headers)
    assert response.status_code == 401
```

### 2. 参数详细校验测试设计

```python
def test_required_parameter_validation(api_client):
    """必填项校验测试"""
    # 所有必填项完整
    data = {
        "username": "testuser",
        "password": "test123456",
        "email": "test@example.com"
    }
    response = api_client.post("/api/register", data)
    assert response.status_code == 201
    
    # 必填项不传
    data = {
        "username": "testuser",
        "password": "test123456"
        # email缺失
    }
    response = api_client.post("/api/register", data)
    assert response.status_code == 400
    assert "email" in response.json()["message"]
    
    # 必填项传空值
    data = {
        "username": "testuser",
        "password": "test123456",
        "email": None
    }
    response = api_client.post("/api/register", data)
    assert response.status_code == 400
    
    # 必填项传空字符串
    data = {
        "username": "testuser",
        "password": "test123456",
        "email": ""
    }
    response = api_client.post("/api/register", data)
    assert response.status_code == 400

def test_optional_parameter_validation(api_client):
    """选填项校验测试"""
    # 选填项都不填
    required_data = {
        "username": "testuser",
        "password": "test123456",
        "email": "test@example.com"
    }
    response = api_client.post("/api/register", required_data)
    assert response.status_code == 201
    
    # 传递部分选填项
    data = {
        "username": "testuser",
        "password": "test123456",
        "email": "test@example.com",
        "phone": "13800138000",  # 选填项
        "age": 25  # 选填项
    }
    response = api_client.post("/api/register", data)
    assert response.status_code == 201

def test_parameter_length_validation(api_client):
    """参数长度校验测试"""
    # 超过最大长度
    data = {"username": "a" * 21}  # maxLength=20
    response = api_client.post("/api/register", data)
    assert response.status_code == 400
    
    # 低于最小长度
    data = {"username": "ab"}  # minLength=3
    response = api_client.post("/api/register", data)
    assert response.status_code == 400
    
    # 等于最大长度
    data = {"username": "a" * 20}
    response = api_client.post("/api/register", data)
    assert response.status_code == 201

def test_parameter_type_validation(api_client):
    """参数类型校验测试"""
    # 正确的数据类型
    data = {"age": 25}  # integer
    response = api_client.post("/api/register", data)
    assert response.status_code == 201
    
    # 错误的数据类型
    data = {"age": "25"}  # string instead of integer
    response = api_client.post("/api/register", data)
    assert response.status_code == 400

def test_parameter_uniqueness_validation(api_client, db_client):
    """参数唯一性校验测试"""
    # 唯一字段传不同值
    data1 = {"username": "user1", "email": "user1@example.com"}
    response1 = api_client.post("/api/register", data1)
    assert response1.status_code == 201
    
    data2 = {"username": "user2", "email": "user2@example.com"}
    response2 = api_client.post("/api/register", data2)
    assert response2.status_code == 201
    
    # 唯一字段传重复值
    data3 = {"username": "user3", "email": "user1@example.com"}  # 重复的email
    response3 = api_client.post("/api/register", data3)
    assert response3.status_code == 409  # Conflict
    assert "email" in response3.json()["message"]
```

### 3. 补充项测试设计

```python
def test_idempotency(api_client):
    """幂等性测试"""
    # 准备数据
    data = {
        "order_id": "ORDER_123",
        "amount": 100.00,
        "product_id": "PROD_456"
    }
    
    # 第一次提交
    response1 = api_client.post("/api/payment", data)
    assert response1.status_code == 200
    result1 = response1.json()
    
    # 第二次提交（重复）
    response2 = api_client.post("/api/payment", data)
    assert response2.status_code == 200
    result2 = response2.json()
    
    # 结果应该相同（幂等）
    assert result1["data"]["transaction_id"] == result2["data"]["transaction_id"]
    
    # 抽奖场景（只能成功一次）
    lottery_data = {"user_id": "USER_789", "activity_id": "ACT_001"}
    response1 = api_client.post("/api/lottery/draw", lottery_data)
    assert response1.status_code == 200
    assert response1.json()["data"]["prize"] is not None
    
    response2 = api_client.post("/api/lottery/draw", lottery_data)
    assert response2.status_code == 400  # 已抽奖
    assert "already participated" in response2.json()["message"]

def test_weak_network_environment(api_client):
    """弱网环境测试"""
    # 使用网络代理工具模拟弱网（如Charles、Fiddler）
    # 设置网络延迟或丢包率
    
    # 支付场景网络中断
    # 在请求发送过程中中断网络
    try:
        response = api_client.post("/api/payment", {"order_id": "ORDER_123"}, timeout=0.1)
    except TimeoutError:
        # 查询支付状态
        status_response = api_client.get("/api/payment/ORDER_123/status")
        # 应该没有扣款或已自动退款
        assert status_response.json()["data"]["status"] in ["pending", "refunded"]

def test_distributed_system(api_client):
    """分布式系统测试"""
    # 使用nginx配置多个后端服务
    # 模拟负载均衡
    
    # 数据同步测试
    data = {"resource_id": "RES_001", "value": 100}
    
    # 在不同节点上操作
    for i in range(3):
        response = api_client.post("/api/resource/update", data)
        assert response.status_code == 200
    
    # 查询所有节点的数据
    responses = []
    for node in ["node1", "node2", "node3"]:
        response = api_client.get(f"/api/resource/RES_001?node={node}")
        responses.append(response.json()["data"]["value"])
    
    # 所有节点数据应该一致
    assert len(set(responses)) == 1

def test_restful_style(api_client):
    """RESTful接口风格测试"""
    # URL命名规范
    # 资源集合用复数
    response = api_client.get("/api/users")  # 正确
    assert response.status_code == 200
    
    # 避免动词
    response = api_client.get("/api/getUsers")  # 不推荐
    # 应该返回404或重定向
    
    # HTTP方法使用正确
    # GET - 查询
    response = api_client.get("/api/users/123")
    assert response.status_code == 200
    
    # POST - 创建
    response = api_client.post("/api/users", {"name": "test"})
    assert response.status_code == 201
    
    # PUT - 全量更新
    response = api_client.put("/api/users/123", {"name": "updated"})
    assert response.status_code == 200
    
    # PATCH - 部分更新
    response = api_client.patch("/api/users/123", {"name": "patched"})
    assert response.status_code == 200
    
    # DELETE - 删除
    response = api_client.delete("/api/users/123")
    assert response.status_code == 204
    
    # 状态码使用正确
    # 2xx - 成功
    # 4xx - 客户端错误
    # 5xx - 服务端错误

def test_sensitive_info_encryption(api_client):
    """敏感信息加密测试"""
    # 登录接口
    login_data = {
        "username": "testuser",
        "password": "test123456"
    }
    response = api_client.post("/api/login", login_data)
    assert response.status_code == 200
    
    # 抓包检查传输数据（需要网络抓包工具）
    # 密码应该加密传输
    
    # 检查日志输出
    # 日志中不应包含明文密码
    import logging
    log_records = []
    
    def log_handler(record):
        log_records.append(record.getMessage())
    
    logging.getLogger().addHandler(logging.Handler())
    
    # 模拟登录
    api_client.post("/api/login", login_data)
    
    # 检查日志
    for log in log_records:
        assert "test123456" not in log  # 密码不应出现在日志
        assert "testuser" not in log   # 用户名也可能需要脱敏
    
    # 检查数据库存储
    db_record = db_client.query("SELECT * FROM users WHERE username = %s", ("testuser",))
    assert db_record["password"] != "test123456"  # 密码应该加密存储
    assert db_record["password"].startswith("$2b$")  # bcrypt加密
```

---

## 六、测试数据管理
