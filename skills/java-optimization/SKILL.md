---
name: "java-optimization"
description: "执行 Java 代码性能优化，包括 JVM 调优、并发编程、内存管理、缓存策略、数据库优化、集合框架优化等。Invoke when user needs to optimize Java code performance."
version: "1.0.0"
last_updated: "2026-03-11"
author: "赵辉亮"
---

# Java 性能优化技能

高级 Java 性能优化技术，专注于 JVM 应用性能提升、内存管理、并发处理和系统调优。

## 性能优化策略

### 1. 缓存策略 (Caching)

使用 Spring Cache 或 Caffeine 实现高效缓存：

```java
// ✅ 使用 Caffeine 本地缓存
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import java.time.Duration;

public class MaterialService {
    private final Cache<String, Material> cache = Caffeine.newBuilder()
        .maximumSize(10_000)
        .expireAfterWrite(Duration.ofMinutes(10))
        .recordStats()
        .build();
    
    public Material getMaterial(String code) {
        return cache.get(code, key -> repository.findByCode(code));
    }
}
```

```java
// ✅ 使用 Spring Cache + Redis
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class FormulaService {
    
    @Cacheable(value = "formulas", key = "#id", 
               condition = "#id != null",
               unless = "#result == null")
    public Formula getFormula(Long id) {
        return formulaRepository.findById(id).orElse(null);
    }
}
```

**何时使用缓存：**
- 频繁访问的数据库查询结果
- 计算成本高的数据
- 不经常变化的配置数据
- 第三方 API 调用结果

### 2. 并行处理 (Parallel Processing)

使用 Stream API 和 Fork/Join 框架：

```java
import java.util.stream.Collectors;

// ✅ 并行流处理 CPU 密集型任务
public List<NutritionResult> calculateBatch(List<Material> materials) {
    return materials.parallelStream()
        .map(this::calculateNutrition)
        .collect(Collectors.toList());
}
```

```java
// ✅ 使用 CompletableFuture 异步处理
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class AsyncCalculator {
    private final ExecutorService executor = Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors()
    );
    
    public CompletableFuture<Double> calculateAsync(Material material) {
        return CompletableFuture.supplyAsync(() -> {
            return calculateNutrition(material);
        }, executor);
    }
    
    // ✅ 批量异步处理
    public CompletableFuture<List<Result>> batchCalculate(List<Material> materials) {
        List<CompletableFuture<Result>> futures = materials.stream()
            .map(m -> calculateAsync(m))
            .collect(Collectors.toList());
        
        return CompletableFuture.allOf(
                futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> futures.stream()
                .map(CompletableFuture::join)
                .collect(Collectors.toList()));
    }
}
```

**最佳实践：**
- 并行流适合大数据量和 CPU 密集型操作
- 小数据集使用顺序流（避免线程切换开销）
- 使用 `@Async` 进行异步方法调用
- 合理设置线程池大小

### 3. 内存优化 (Memory Optimization)

#### 避免不必要的对象创建
```java
// ❌ 错误 - 循环内创建对象
for (int i = 0; i < items.size(); i++) {
    StringBuilder sb = new StringBuilder();
    sb.append(items.get(i));
}

// ✅ 正确 - 循环外创建
StringBuilder sb = new StringBuilder(items.size() * 10);
for (String item : items) {
    sb.append(item);
}
```

#### 使用基本类型而非包装类
```java
// ❌ 错误 - 使用包装类
List<Integer> values = new ArrayList<>();
int sum = 0;
for (Integer value : values) {
    sum += value; // 自动拆箱
}

// ✅ 正确 - 使用基本类型
int[] values = new int[size];
int sum = 0;
for (int value : values) {
    sum += value;
}
```

#### 使用 String.join 替代字符串拼接
```java
// ❌ 错误 - 低效的字符串拼接
String result = "";
for (String item : items) {
    result += item + ",";
}

// ✅ 正确 - 使用 String.join
String result = String.join(",", items);

// ✅ 或使用 StringBuilder
StringBuilder sb = new StringBuilder();
for (String item : items) {
    sb.append(item).append(",");
}
```

#### 集合初始化时指定容量
```java
// ❌ 错误 - 默认容量可能导致多次扩容
List<String> list = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    list.add(String.valueOf(i));
}

// ✅ 正确 - 预分配容量
List<String> list = new ArrayList<>(1000);
for (int i = 0; i < 1000; i++) {
    list.add(String.valueOf(i));
}
```

### 4. 数据库查询优化

#### 避免 N+1 查询问题
```java
// ❌ 错误 - N+1 查询
List<Formula> formulas = formulaRepository.findAll();
for (Formula formula : formulas) {
    List<Material> materials = materialRepository.findByFormulaId(formula.getId());
}

// ✅ 正确 - 使用 JOIN FETCH
@Query("SELECT f FROM Formula f LEFT JOIN FETCH f.materials WHERE f.deleted = 0")
List<Formula> findAllWithMaterials();
```

#### 使用批量操作
```java
// ✅ 批量插入/更新
@Transactional
public void batchInsert(List<Item> items) {
    int batchSize = 50;
    for (int i = 0; i < items.size(); i++) {
        entityManager.persist(items.get(i));
        
        if (i % batchSize == 0 && i > 0) {
            entityManager.flush();
            entityManager.clear();
        }
    }
}
```

#### 使用投影查询减少数据传输
```java
// ✅ 只查询需要的字段
@Query("SELECT new com.example.dto.FormulaSummary(f.id, f.name, f.totalCost) " +
       "FROM Formula f WHERE f.deleted = 0")
List<FormulaSummary> findSummaries();
```

### 5. 并发编程优化

#### 使用线程池
```java
// ✅ 自定义线程池配置
@Configuration
public class ThreadPoolConfig {
    
    @Bean
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-executor-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

#### 使用并发容器
```java
// ✅ 线程安全的 Map
ConcurrentHashMap<String, Object> cache = new ConcurrentHashMap<>();

// ✅ 原子操作
AtomicLong counter = new AtomicLong(0);
counter.incrementAndGet();

// ✅ 读写锁
ReadWriteLock lock = new ReentrantReadWriteLock();
lock.readLock().lock();
try {
    return cache.get(key);
} finally {
    lock.readLock().unlock();
}
```

### 6. JVM 调优参数

#### 堆内存配置
```bash
# 生产环境推荐配置
-Xms4g                    # 初始堆大小
-Xmx4g                    # 最大堆大小
-XX:NewRatio=2            # 新生代与老年代比例
-XX:SurvivorRatio=8       # Eden 与 Survivor 比例
-XX:+UseG1GC              # 使用 G1 垃圾收集器
-XX:MaxGCPauseMillis=200  # 最大 GC 停顿时间
-XX:+ParallelRefProcEnabled
```

#### GC 日志配置
```bash
# GC 日志记录
-Xloggc:/var/log/gc.log
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-XX:+UseGCLogFileRotation
-XX:NumberOfGCLogFiles=10
-XX:GCLogFileSize=100M
```

### 7. Stream API 优化

#### 避免在 Stream 中执行副作用操作
```java
// ❌ 错误 - forEach 有副作用
List<String> result = new ArrayList<>();
list.stream()
    .forEach(item -> result.add(transform(item)));

// ✅ 正确 - 使用 map 和 collect
List<String> result = list.stream()
    .map(this::transform)
    .collect(Collectors.toList());
```

#### 合理使用并行流
```java
// ❌ 错误 - 小数据集使用并行流
List<Integer> smallList = Arrays.asList(1, 2, 3, 4, 5);
smallList.parallelStream().map(...); // 线程切换开销大于收益

// ✅ 正确 - 大数据集或 CPU 密集型任务
if (list.size() > 10000) {
    return list.parallelStream().map(...).collect(...);
}
```

### 8. 锁优化

#### 缩小同步范围
```java
// ❌ 错误 - 方法级别同步
public synchronized void process() {
    // 非临界区代码
    prepare();
    
    // 临界区代码
    synchronized(this) {
        updateSharedState();
    }
}

// ✅ 正确 - 代码块级别同步
public void process() {
    prepare(); // 非同步
    
    synchronized(this) {
        updateSharedState(); // 仅同步必要部分
    }
}
```

#### 使用读写锁优化读多写少场景
```java
// ✅ 使用 ReentrantReadWriteLock
private final ReadWriteLock lock = new ReentrantReadWriteLock();

public Data get(String key) {
    lock.readLock().lock();
    try {
        return cache.get(key);
    } finally {
        lock.readLock().unlock();
    }
}

public void put(String key, Data value) {
    lock.writeLock().lock();
    try {
        cache.put(key, value);
    } finally {
        lock.writeLock().unlock();
    }
}
```

### 9. 集合框架选择

| 场景 | 推荐集合 | 性能特点 |
|------|----------|----------|
| 频繁随机访问 | `ArrayList` | O(1) 访问 |
| 频繁头尾插入删除 | `LinkedList` | O(1) 插入删除 |
| 高频并发读写 | `ConcurrentHashMap` | 分段锁 |
| 有序 Map | `TreeMap` | O(log n) |
| 去重 | `HashSet` | O(1) |
| 固定大小缓存 | `LinkedHashMap` | LRU 支持 |

```java
// ✅ 根据场景选择合适的集合
// 需要快速查找 - 使用 HashMap
Map<Long, RefundOrder> orderMap = new HashMap<>(size);

// 需要保持插入顺序 - 使用 LinkedHashMap
Map<String, Object> orderedCache = new LinkedHashMap<>(16, 0.75f, true);

// 高并发场景 - 使用 ConcurrentHashMap
ConcurrentHashMap<String, Object> concurrentCache = new ConcurrentHashMap<>();
```

## 性能分析工具

### VisualVM 监控
```bash
# 启动 VisualVM
jvisualvm

# 连接到运行中的应用
# 监控：CPU、内存、线程、类加载
# 分析：CPU 热点、内存泄漏
```

### JProfiler 性能分析
```bash
# CPU 分析：识别方法执行热点
# 内存分析：检测内存泄漏
# SQL 分析：优化数据库查询
# 线程分析：检测死锁
```

### Arthas 在线诊断
```bash
# 安装 Arthas
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar

# 常用命令
dashboard          # 查看系统仪表盘
thread             # 查看线程信息
heapdump           # 导出堆转储
profiler           # CPU 性能分析
trace              # 方法调用追踪
watch              # 观察方法参数和返回值
```

## 基准测试

### JMH 基准测试
```java
import org.openjdk.jmh.annotations.*;
import java.util.concurrent.TimeUnit;

@State(Scope.Thread)
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
public class BenchmarkTest {
    
    @Param({"100", "1000", "10000"})
    public int size;
    
    private List<String> dataList;
    
    @Setup
    public void setup() {
        dataList = IntStream.range(0, size)
            .mapToObj(String::valueOf)
            .collect(Collectors.toList());
    }
    
    @Benchmark
    public String testStringBuilder() {
        StringBuilder sb = new StringBuilder();
        for (String s : dataList) {
            sb.append(s);
        }
        return sb.toString();
    }
    
    @Benchmark
    public String testStringJoiner() {
        StringJoiner joiner = new StringJoiner("");
        for (String s : dataList) {
            joiner.add(s);
        }
        return joiner.toString();
    }
}
```

## 常见性能反模式

### ❌ 在循环中执行数据库查询
```java
// 错误示例
for (Order order : orders) {
    User user = userRepository.findById(order.getUserId());
}

// 正确做法
List<Long> userIds = orders.stream()
    .map(Order::getUserId)
    .collect(Collectors.toList());
List<User> users = userRepository.findAllById(userIds);
```

### ❌ 滥用同步
```java
// 错误示例 - 过度同步
public synchronized void method() {
    // 只有部分代码需要同步
}

// 正确做法 - 缩小同步范围
public void method() {
    // 非同步代码
    synchronized(lock) {
        // 仅同步必要部分
    }
    // 非同步代码
}
```

### ❌ 大对象频繁创建
```java
// 错误示例
public void process() {
    byte[] buffer = new byte[1024 * 1024]; // 1MB
    // 使用...
} // GC 时会回收

// 正确做法 - 使用对象池或复用
private static final ThreadLocal<byte[]> BUFFER_POOL = 
    ThreadLocal.withInitial(() -> new byte[1024 * 1024]);
```

## 实际优化案例

### 案例 1：退款订单查询优化

#### 优化前（耗时 2.5s）
```java
// ❌ N+1 查询问题
@GetMapping("/list")
public List<RefundOrderVO> list() {
    List<RefundOrder> orders = refundOrderMapper.selectAll();
    return orders.stream()
        .map(order -> {
            RefundOrderVO vo = convertToVO(order);
            // 每次循环都查询数据库
            User user = userMapper.selectById(order.getUserId());
            vo.setUserName(user.getName());
            return vo;
        })
        .collect(Collectors.toList());
}
```

#### 优化后（耗时 0.3s）
```java
// ✅ 批量查询 + 内存组装
@GetMapping("/list")
public List<RefundOrderVO> list() {
    // 一次性查询所有订单
    List<RefundOrder> orders = refundOrderMapper.selectAll();
    
    // 批量查询用户信息
    Set<Long> userIds = orders.stream()
        .map(RefundOrder::getUserId)
        .collect(Collectors.toSet());
    
    List<User> users = userMapper.selectBatchIds(userIds);
    Map<Long, User> userMap = users.stream()
        .collect(Collectors.toMap(User::getId, u -> u));
    
    // 内存组装，无数据库查询
    return orders.stream()
        .map(order -> {
            RefundOrderVO vo = convertToVO(order);
            User user = userMap.get(order.getUserId());
            vo.setUserName(user != null ? user.getName() : "未知用户");
            return vo;
        })
        .collect(Collectors.toList());
}
```

### 案例 2：退款状态统计优化

#### 优化前（单线程，耗时 5s）
```java
// ❌ 串行处理
public Map<Integer, Long> statisticsByStatus() {
    List<RefundOrder> orders = getAllOrders();
    return orders.stream()
        .collect(Collectors.groupingBy(
            RefundOrder::getRefundStatus,
            Collectors.counting()
        ));
}
```

#### 优化后（并行流，耗时 1.2s）
```java
// ✅ 并行流处理
public Map<Integer, Long> statisticsByStatus() {
    List<RefundOrder> orders = getAllOrders();
    return orders.parallelStream() // 并行处理
        .collect(Collectors.groupingByConcurrent(
            RefundOrder::getRefundStatus,
            Collectors.counting()
        ));
}
```

## Spring Boot 特定优化

### 1. Bean 作用域选择
```java
// ✅ 无状态 Service 使用 Singleton（默认）
@Service
public class RefundOrderService {
    // 不要定义可变状态字段
}

// ✅ 有状态 Bean 使用 Prototype
@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
public class OrderProcessor {
    private State state; // 每个请求新实例
}
```

### 2. 延迟初始化加速启动
```java
// application.yml
spring:
  main:
    lazy-initialization: true  # 全局延迟初始化

// 或针对特定 Bean
@Component
@Lazy
public class ExpensiveComponent {
    // 首次使用时才创建
}
```

### 3. AOP 性能考虑
```java
// ❌ 避免在高频调用方法上使用复杂切面
@Around("execution(* com.example.service.*.*(..))")
public Object logAll(ProceedingJoinPoint pjp) {
    // 会影响所有方法调用
}

// ✅ 精确匹配需要的类和方法
@Around("@annotation(com.example.annotation.NeedLog)")
public Object logNeeded(ProceedingJoinPoint pjp) {
    // 只拦截标注了@NeedLog 的方法
}
```

## IO 和网络优化

### 1. 使用 NIO 读取大文件
```java
// ❌ BIO 方式读取大文件
BufferedReader reader = new BufferedReader(new FileReader(file));
String line;
while ((line = reader.readLine()) != null) {
    // 逐行读取，效率低
}

// ✅ NIO 方式
try (FileChannel channel = FileChannel.open(path, StandardOpenOption.READ)) {
    MappedByteBuffer buffer = channel.map(MapMode.READ_ONLY, 0, channel.size());
    // 内存映射，适合大文件
}
```

### 2. 连接池配置
```java
// HikariCP 推荐配置
spring:
  datasource:
    hikaricp:
      maximum-pool-size: 20      # 最大连接数
      minimum-idle: 10           # 最小空闲连接
      connection-timeout: 30000  # 连接超时 30s
      idle-timeout: 600000       # 空闲超时 10min
      max-lifetime: 1800000      # 最大生命周期 30min
```

## 性能检查清单

### 代码层面
- [ ] 避免在循环中创建对象
- [ ] 使用 StringBuilder 进行字符串拼接
- [ ] 集合初始化时指定容量
- [ ] 优先使用基本类型
- [ ] 及时关闭资源（try-with-resources）
- [ ] 避免不必要的同步
- [ ] 使用懒加载

### 数据库层面
- [ ] 添加合适的索引
- [ ] 避免 SELECT *
- [ ] 使用分页查询
- [ ] 批量操作代替单条操作
- [ ] 使用连接池
- [ ] 慢查询监控

### 架构层面
- [ ] 合理使用缓存
- [ ] 异步处理耗时操作
- [ ] 消息队列削峰填谷
- [ ] CDN 加速静态资源
- [ ] 负载均衡分散压力

## 何时使用此技能

当用户提到以下关键词时激活此技能：
- "Java 性能优化"
- "提高响应速度"
- "减少内存占用"
- "JVM 调优"
- "并发优化"
- "数据库优化"
- "缓存策略"
- "性能分析"
- "CPU 占用高"
- "内存泄漏"
- "GC 频繁"
- "接口响应慢"
