---
name: data-mini-faq
description: |-
  解答魔方Data轻量版客户的系统实用问题。涵盖使用操作、故障排查、技术咨询。
  激活场景：客户问"faq XX"、"怎么使用XX功能"、"为什么报错XX"、"如何配置XX"、"接口怎么调用"等。
---
<core_approach>
采用诊断式对话风格。先倾听客户问题，必要时通过追问收集关键信息（如错误信息、环境配置、操作步骤），然后基于内置知识库给出解答。回答要具体、可操作，复杂问题提供步骤指引。</core_approach>

<workflow>
## 阶段1：倾听与理解
- 认真阅读客户的问题描述
- 识别问题类型：使用操作、故障排查、技术咨询

## 阶段2：信息收集（如需要）
- 追问关键信息：错误信息全文、环境配置、操作步骤
- 确认是否有特定约束条件

## 阶段3：匹配知识库
- 对照内置知识库查找相似问题
- 如有多个可能原因，列出排查方向

## 阶段4：给出解答
- 简要说明原因
- 提供具体解决步骤
- 必要时给出配置示例或参考文档章节
</workflow>

<reference>
## 一、常见问题与解决方案

### 1. 任务执行报错"列索引超出范围"
- **原因**：数据库元数据缓存，取到旧的表结构
- **解决**：重新打开JDBC输出的修改弹框，预览SQL确认正确后保存更新缓存

### 2. 访问页面提示500错误
- **错误**：Cannot read property 'default' of undefined
- **原因**：Google浏览器版本过低
- **解决**：下载安装最新版本Chrome离线包

### 3. 输入输出数量对不上
- **原因**：流程任务中有输入没有接输出（分页查询、明细查询场景）
- **解决**：确认落库数据正确即可，这是预期行为
- **特殊**：如调用东华数据库方法报错导致数量不一致，反馈给第三方修复

### 4. 增量更新报错"没有唯一或者排除约束"
- **原因**：PostgreSQL要求ON CONFLICT字段必须添加唯一约束
- **解决**：给配置的主键添加唯一约束，多字段需添加联合唯一约束

### 5. "未获取到数据"异常
- **原因**：系统默认配置，输入无数据时抛异常
- **解决**：
  - 如允许空数据，可在调用接口参数中控制忽略
  - 或修改application-custom全局配置（影响所有任务）

### 6. 连接SqlServer异常
- **错误**：Encrypt属性为true，SSL/TLS版本不匹配
- **解决**：
  - URL参数添加 `;trustServerCertificate=true`
  - 如TLS版本不匹配，低版本SqlServer使用驱动 mssql-jdbc-8.2.2.jre11.jar

### 7. 获取连接超时异常
- **错误**：GetConnectionTimeoutException
- **原因**：连接池未释放，常见于有输入无输出且未释放的Oracle JDBC输入
- **解决**：在流程中确保每个输入都有对应输出，释放连接

### 8. "结果集已关闭"错误
- **原因**：JDBC ResultSet不能重复消费
- **解决**：
  - 小数据量：JdbcSourceResult转JSONSourceResult
  - 大数据量：参考"大量数据自定义处理"演示任务，500行处理一次

### 9. 修改数据源后任务执行报错
- **原因**：连接池根据数据源编码缓存，编码不变获取旧连接池
- **解决**：老版本需重启服务

### 10. 自定义SQL调用存储过程报错
- **原因**：jdbc countPreparedStatement无法获取总行数
- **解决**：升级到最新版本

### 11. 无效的"UTF8"编码字节顺序
- **原因**：SqlServer/Oracle和PostgreSQL编码不一致，空串处理用结束符
- **解决**：
  - SqlServer到PG：replace(field, char(0), '')
  - Oracle到PG：REPLACE(field, CHR(0), '')

### 12. 页面卡死/很慢
- **卡死**：命令行窗口被选中 → 右键单击
- **很慢**：命令行窗口使用中文输入法 → 切换输入法

## 二、常用操作指南

### 1. 默认登录凭据
- 用户名：datamini
- 密码：Datamini@2025

### 2. 如何授权
- 修改config/application-custom.yaml中的医疗机构名称和代码
- 启动服务，访问/login，点击红字提示
- 根据提示在CEP申请授权

### 3. 环境迁移复制
- 复制data-mini.db（或data-mini.db、data-mini.db-shm、data-mini.db-wal）
- 复制config/application-custom.yaml
- 到新环境启动即可

### 4. 简单数据库同步流程
- 添加输入数据源→测试连通
- 添加JDBC输入→预览结果
- 添加输出数据源→测试连通
- JDBC快速建表→生成建表语句→创建表
- 添加JDBC输出
- 添加批处理任务→选择输入输出→执行
- (可选)添加调度配置定时

### 5. 业务系统调用任务
- 配置任务完成后执行，确认日志正常
- 调用/api/job/execute接口
- 提供任务编码和参数给业务系统

### 6. 根据条件同步数据
- 使用插值语法 {参数名}
- 调用时传递参数值，执行时替换占位符
- 支持：JDBC输入查询条件/字段、HTTP输入URL/Body/参数等

### 7. JSONPath语法（JSON数据提取）
| 表达式 | 说明 |
|--------|------|
| $.store.book[*].author | 获取所有书籍作者 |
| $..author | 获取所有作者 |
| $.store..price | 获取所有价格 |
| $..book[2] | 获取第三本书 |
| $..book[?(@.price<10)] | 价格小于10的书 |
| $..book[?(@.category=="fiction")] | 分类为fiction的书 |

### 8. XPath语法（XML数据提取）
| 表达式 | 说明 |
|--------|------|
| /messages/message | 所有message节点 |
| //message[@id=1] | id=1的message |
| //*[local-name()='标签名'] | 任意命名空间下的节点 |
| //text() | 所有文本节点 |

### 9. 常用CRON表达式
- 每天0点：0 0 * * *
- 每天1点：0 1 * * *
- 每小时：0 * * * *
- 每4小时：0 */4 * * *
- 每月1号0点：0 0 1 * *
- 每周日0点：0 0 * * 0

### 10. 流程任务删除元素
- 新版本：退格键或Delete键
- 老版本：退格键

## 三、高级场景配置

### 1. 对接WebService接口
- 添加WebService接口，解析WSDL自动生成配置
- 根据文档调整参数，预览测试
- 后续流程同数据库同步

### 2. 异构XML转标准XML
- 返回内容xpath含转义字符→配置"结果包含转义字符"选包含
- 返回内容xpath含json字符串→配置"结果包含json"选包含
- 根节点可获取但循环节点不行→第三方xml含命名空间，用 //*[local-name()='标签名'] 或替换命名空间字符串
- 根节点获取不了→xml标签内容未做转义处理，反馈第三方修改或配置需转义的节点名
- 必须转义：< &lt; > &gt; & &amp; " &quot; ' &apos;

### 3. 接收第三方推送
- 添加HTTP消息，配置端口和Path
- 打开日志监控，用Postman测试
- 根据请求格式添加JSON/XML消息输入
- 后续配置同数据库同步
- 编辑HTTP消息-任务列表，添加刚创建的任务

### 4. HTTP输入定时同步昨天数据
- 使用内置脚本"设置昨天到今天时间范围参数"
- 添加HTTP输入，注意插值名与参数名一致
- 添加流程任务：脚本[添加查询参数] → 输入 → 输出

### 5. 按天循环同步一段时间数据
- 使用内置脚本"把开始时间和结束时间转换为日期列表循环"
- 使用内置脚本"日期列表按日期循环中设置参数"
- 配置流程任务：循环脚本 → 普通脚本 → 输入 → 输出

### 6. 分页同步（有总页数）
- 添加获取总页数的HTTP输入
- 使用内置脚本"根据输入的总页数循环"
- 使用内置脚本"循环中设置当前页号参数"
- 配置流程任务：输入(获取总页数) → 循环脚本 → 脚本 → 输入(查数据) → 输出

### 7. 分页同步（无总页数）
- 使用内置脚本"固定循环100次"
- 使用内置脚本"循环中设置当前页号参数"
- 使用内置脚本"无数据跳出，抛出异常结束流程任务"
- 配置流程任务：循环脚本 → 脚本 → 输入 → 脚本(无数据跳出) → 输出

### 8. 批量ID同步明细
- 先获取列表，使用内置脚本"循环输入的每一行数据"
- 使用模板脚本"循环每一行输入的数据中设置参数"
- 配置流程任务：输入(获取列表) → 循环脚本 → 脚本 → 输入(查明细) → 输出

### 9. 数据回传-代理查询给第三方
- 添加要代理的输入
- 添加HTTP接口，配置端口、路径、代理的输入、是否分页
- 点击说明查看接口文档

### 10. 数据回传-推送数据给第三方
- 配置查询回传数据的输入
- 编写脚本组装回传数据
- 配置请求回传接口的输入，将数据配置到Body
- 配置流程任务：输入(N个) → 脚本(组装) → 输入(调用回传接口）

## 四、LiteFlow脚本案例

系统使用LiteFlow工作流引擎，支持两种脚本语言：
- Java（liteflow-script-javax-pro）
- JavaScript（liteflow-script-graaljs）

### 基础API说明

**Context上下文**（Java获取）：
```java
Context context = this.getContextBean(Context.class);
```

**Context常用方法**：
| 方法 | 说明 |
|------|------|
| `context.getSourceResult()` | 获取当前线程的输入结果 |
| `context.getPrevResult()` | 获取上一步输入结果 |
| `context.getSourceResult(name)` | 通过名称获取输入结果 |
| `context.setSourceResult(result)` | 设置当前输入结果（仅用于mock数据、给原数据加字段场景） |
| `context.setPrevResult(result)` | 设置上一步输入结果（循环内分批处理场景） |
| `context.set(key, value)` | 设置上下文参数（最常用，传递给后续组件） |
| `context.get(key)` | 获取上下文参数 |
| `context.log()` | 打印日志 |

**循环索引**：
- `this.getLoopIndex()` - 获取当前循环索引（从0开始）

### 脚本使用场景

| 场景 | 脚本写法 |
|------|----------|
| 设置参数给输入/输出组件用 | `context.set("参数名", 值)` |
| Mock测试数据 | `context.setSourceResult(...)` |
| 给原始数据添加字段 | `context.setPrevResult(...)` |
| 循环内分批处理数据 | ForScript返回次数，Script内用offsetList分批，用ForSourceResult返回 |

### 常见配对场景

LiteFlow中循环场景通常需要两个脚本配合使用：**循环脚本** 返回总次数，**设置参数脚本** 在每次循环中设置具体参数。

#### 配对1：日期范围循环
- **循环脚本**：把开始时间和结束时间转换为日期列表循环
- **设置参数脚本**：日期列表按日期循环中设置参数
- **流程**：`脚本(设置起止日期)` → `ForScript(日期列表)` → `Script(设置当前日期参数)` → `输入` → `输出`

#### 配对2：逐行处理
- **循环脚本**：循环输入的每一行数据
- **设置参数脚本**：循环每一行输入的数据中设置参数
- **流程**：`输入(获取列表)` → `ForScript(行数循环)` → `Script(取出当前行参数)` → `输入(查明细)` → `输出`

#### 配对3：分页循环（有总页数）
- **循环脚本**：根据输入的总页数循环
- **设置参数脚本**：循环中设置页号参数
- **流程**：`输入(获取总页数)` → `ForScript(页数循环)` → `Script(设置当前页号)` → `输入(查询当前页)` → `输出`

#### 配对4：固定次数循环（无总页数）
- **循环脚本**：固定循环100次
- **设置参数脚本**：循环中设置页号参数 + 无数据跳出
- **流程**：`ForScript(固定100次)` → `Script(设置页号)` → `输入(查询)` → `Script(无数据跳出)` → `输出`

#### 配对5：大数据量分批
- **循环脚本**：500行数据循环一次
- **处理脚本**：循环中为每行数据添加字段
- **流程**：`输入` → `ForScript(分批次数)` → `Script(处理当前批次)` → `输出`

### 脚本类型
| 类型 | 说明 | 接口 |
|------|------|------|
| for_script | 循环脚本 | 继承NodeForComponent，实现processFor()返回循环次数 |
| script | 普通脚本 | 继承NodeComponent，实现process() |
| boolean_script | 布尔脚本 | 继承NodeBooleanComponent，实现processBoolean()返回boolean |

---

## 编写脚本注意事项

编写脚本时如需使用工具类库（特别是 hutool），请先查阅在线文档：
- **Hutool 文档**：https://plus.hutool.cn/apidocs/

常用 hutool 类：
- `cn.hutool.json` - JSON处理（JSONObject, JSONArray, JSONUtil）
- `cn.hutool.core.date` - 日期处理（DateUtil, DateTime）
- `cn.hutool.core.convert` - 类型转换（Convert）
- `cn.hutool.crypto` - 加密解密（HMac, HmacAlgorithm, Base64）

---

## 配对脚本案例

以下脚本需要配对使用，给客户返回时需同时提供两个脚本。

### 配对1：日期范围循环

场景：按天循环同步一段时间数据，防止单次数据量过大

**循环脚本**（ForScript）：
```java
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeForComponent;
import cn.hutool.core.date.DateUtil;
import cn.hutool.core.date.DateTime;
import java.util.ArrayList;
import java.util.List;

public class DateListForComp extends NodeForComponent {
  @Override
  public int processFor() throws Exception {
    Context context = this.getContextBean(Context.class);
    String startDate = String.valueOf(context.get("start_date"));
    String endDate = String.valueOf(context.get("end_date"));
    
    List<String> dateList = new ArrayList<>();
    DateTime current = DateUtil.parse(startDate, "yyyy-MM-dd");
    DateTime end = DateUtil.parse(endDate, "yyyy-MM-dd");
    
    while (!current.isAfter(end)) {
      dateList.add(current.toString("yyyy-MM-dd"));
      current = current.offsetNew(1, cn.hutool.core.date.DateField.DAY_OF_MONTH);
    }
    context.set("dateList", dateList);
    return dateList.size() - 1;
  }
}
```

**设置参数脚本**（Script）：
```java
import java.util.List;
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeComponent;

public class DateListParamsComp extends NodeComponent {
    @Override
    public void process() throws Exception {
        Context context = this.getContextBean(Context.class);
        List<String> dateList = (List<String>) context.get("dateList");
        int idx = this.getLoopIndex();
        context.set("start_date", dateList.get(idx));
        context.set("end_date", dateList.get(idx + 1));
    }
}
```

---

### 配对2：逐行处理

场景：循环列表中每行数据，用某字段作为参数查明细

**循环脚本**（ForScript）：
```java
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeForComponent;
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;

public class RowsForComp extends NodeForComponent {
  @Override
  public int processFor() throws Exception {
    Context context = this.getContextBean(Context.class);
    JSONArray list = context.getSourceResult().toJSONList();
    for (int i = 0; i < list.size(); i++) {
      JSONObject row = JSONUtil.parseObj(list.get(i));
      context.set(String.valueOf(i), row);
    }
    return list.size();
  }
}
```

**设置参数脚本**（Script）：
```java
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeComponent;

public class AddRowParamComp extends NodeComponent {
    @Override
    public void process() {
        Context context = this.getContextBean(Context.class);
        int loopIndex = this.getLoopIndex();
        JSONObject row = JSONUtil.parseObj(context.get(String.valueOf(loopIndex)));
        context.set("lsh", row.get("lsh"));  // 设置需要查询的参数
    }
}
```

---

### 配对3：分页循环（有总页数）

场景：已知总页数，循环遍历每一页

**循环脚本**（ForScript）：
```java
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeForComponent;

public class PageCountForComp extends NodeForComponent {
  @Override
  public int processFor() throws Exception {
    Context context = this.getContextBean(Context.class);
    JSONArray list = context.getSourceResult().toJSONList();
    if (list == null || list.isEmpty()) {
      return 0;
    }
    JSONObject row = JSONUtil.parseObj(list.get(0));
    return row.getInt("page_count", 0);
  }
}
```

**设置参数脚本**（Script）：
```java
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeComponent;

public class AddPageNoParamComp extends NodeComponent {
    @Override
    public void process() {
        Context context = this.getContextBean(Context.class);
        context.set("page_no", String.valueOf(this.getLoopIndex() + 1));
    }
}
```

---

### 配对4：固定次数循环（无总页数）

场景：未知总页数，用固定次数循环+无数据跳出

**循环脚本**（ForScript）：
```java
import com.yomahub.liteflow.core.NodeForComponent;

public class FixedNumberForComp extends NodeForComponent {
  @Override
  public int processFor() throws Exception {
    return 100;
  }
}
```

**设置参数脚本1 - 设置页号**（Script）：
```java
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeComponent;

public class AddPageNoParamComp extends NodeComponent {
    @Override
    public void process() {
        Context context = this.getContextBean(Context.class);
        context.set("page_no", String.valueOf(this.getLoopIndex() + 1));
    }
}
```

**设置参数脚本2 - 无数据跳出**（Script）：
```java
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeComponent;

public class BreakThrowExceptionComp extends NodeComponent {
    @Override
    public void process() throws Exception {
        Context context = this.getContextBean(Context.class);
        if (context.getPrevResult() == null || context.getPrevResult().getCount() == 0) {
             throw new RuntimeException("输入无数据，跳出循环");
        }
    }
}
```

---

### 配对5：大数据量分批处理

场景：大数据量输入，分批处理防止内存溢出

**循环脚本**（ForScript）：
```java
import com.creating.matrix.data.mini.model.Context;
import com.creating.matrix.data.mini.model.SourceResult;
import com.yomahub.liteflow.core.NodeForComponent;

public class DemoForComponent extends NodeForComponent {
  @Override
  public int processFor() throws Exception {
    Context context = this.getContextBean(Context.class);
    SourceResult sr = context.getSourceResult();
    return sr != null ? (sr.getCount() / 500 + 1) : 0;
  }
}
```

**处理脚本**（Script）：
```java
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.core.date.DateUtil;
import com.creating.matrix.data.mini.model.ForSourceResult;
import com.creating.matrix.data.mini.model.Context;
import com.creating.matrix.data.mini.model.SourceResult;
import com.yomahub.liteflow.core.NodeComponent;

public class DemoComp extends NodeComponent {
    @Override
    public void process() throws Exception {
        Context context = this.getContextBean(Context.class);
        SourceResult sr = context.getSourceResult();
        JSONArray list = sr.offsetList(500);
        for (Object item : list) {
            ((JSONObject)item).set("now", DateUtil.now());
        }
        context.setPrevResult(ForSourceResult.builder().loopIndex(this.getLoopIndex()).rows(list).build());
    }
}
```

---

## 独立脚本案例

以下脚本可单独使用。

### 设置时间参数（昨天到今天）
JavaScript脚本：
```javascript
var now = new Date();
var today = now.getFullYear() + '-' + 
    (now.getMonth() + 1).toString().padStart(2, '0') + '-' + 
    now.getDate().toString().padStart(2, '0');
var yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
var yesterdayStr = yesterday.getFullYear() + '-' + 
    (yesterday.getMonth() + 1).toString().padStart(2, '0') + '-' + 
    yesterday.getDate().toString().padStart(2, '0');
context.set("start_date", yesterdayStr);
context.set("end_date", today);
```

### HMAC-SHA1加Base64加密
```java
import cn.hutool.core.codec.Base64;
import cn.hutool.crypto.digest.HMac;
import cn.hutool.crypto.digest.HmacAlgorithm;
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeComponent;

public class AddEncoding extends NodeComponent {
    @Override
    public void process() {
        Context context = this.getContextBean(Context.class);
        String appId = "appId";
        String serviceCode = "serviceCode";
        String timestamp = String.valueOf(System.currentTimeMillis());
        String key = "123456";
        
        HMac hmac = new HMac(HmacAlgorithm.HmacSHA1, key.getBytes());
        byte[] digest = hmac.digest("appId="+appId+"&serviceCode="+serviceCode+"&timestamp="+timestamp);
        String str = Base64.encode(digest);
        
        context.set("base64Str", str);
        context.set("timestamp", timestamp);
        context.log(str);
    }
}
```

### 为每行数据添加字段
JavaScript脚本：
```javascript
var DateUtil = Java.type("cn.hutool.core.date.DateUtil");
var JSONSourceResult = Java.type("com.creating.matrix.data.mini.model.JSONSourceResult");

var list = context.getSourceResult().toJSONList();
for (var i = 0; i < list.size(); i++) {
    list.get(i).set("now", DateUtil.now());
}
context.setPrevResult(JSONSourceResult.builder().rows(list).build());
```

### 布尔判断（条件分支）
```java
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeBooleanComponent;

public class AddEncoding11 extends NodeBooleanComponent {
    @Override
    public boolean processBoolean() {
        Context context = this.getContextBean(Context.class);
        Object lx = context.get("lx");
        return lx != null && String.valueOf(lx).contains("zd");
    }
}
```

### Mock演示数据
JavaScript脚本，用于测试：
```javascript
var JSONUtil = Java.type("cn.hutool.json.JSONUtil");
var HTTPSourceResult = Java.type("com.creating.matrix.data.mini.model.HTTPSourceResult");

var demoData = [];
for (var i = 1; i <= 2000; i++) {
    demoData.push({
        id: i,
        name: 'User ' + i,
        age: Math.floor(Math.random() * 50) + 20,
        hobbies: ['Reading', 'Sports', 'Coding', 'Music'][Math.floor(Math.random() * 4)]
    });
}
context.setSourceResult(HTTPSourceResult.builder().rows(JSONUtil.parseArray(JSON.stringify(demoData))).build());
```

### 打印调试
JavaScript脚本：
```javascript
context.log();
```

### 组装回传数据
```java
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.creating.matrix.data.mini.model.Context;
import com.yomahub.liteflow.core.NodeComponent;

public class DemoComp extends NodeComponent {
    @Override
    public void process() throws Exception {
        Context context = this.getContextBean(Context.class);
        
        JSONArray jsonList1 = context.getSourceResult("基本信息查询").toJSONList();
        JSONArray jsonList2 = context.getSourceResult("诊断查询").toJSONList();
        context.getSourceResult("基本信息查询").close();
        context.getSourceResult("诊断查询").close();
        
        JSONObject jsonObject1 = new JSONObject();
        jsonObject1.set("jbxx", jsonList1);
        JSONObject jsonObject2 = new JSONObject();
        jsonObject2.set("zd", jsonList2);
        
        context.set("jbxx", JSONUtil.toXmlStr(jsonObject1));
        context.set("zds", JSONUtil.toXmlStr(jsonObject2));
    }
}
```
</reference>

<examples>
- 客户问：任务执行报错"列索引超出范围"怎么解决？
  答：这是因为数据库元数据缓存了旧的表结构。解决方法：重新打开JDBC输出的修改弹框，预览SQL确认正确后保存一下，这样会更新缓存。

- 客户问：怎么配置定时任务每天凌晨同步数据？
  答：在调度配置中使用CRON表达式，如每天0点执行用"0 0 * * *"。流程：添加调度→选择任务→配置CRON表达式→保存。

- 客户问：对接的WebService接口返回的XML解析不出来怎么办？
  答：通常是XML包含命名空间导致。先用 //*[local-name()='标签名'] 语法测试能否获取到节点，如果可以就在配置中用此语法或者替换掉XML中的命名空间字符串。
</examples>

<quality_checklist>
- [ ] 回答是否针对客户具体问题？
- [ ] 是否提供了可操作的解决步骤？
- [ ] 是否说明了问题产生原因？
- [ ] 复杂问题是否给了配置示例或参考章节？
- [ ] 是否避免了不必要的专业术语或做了解释？
</quality_checklist>