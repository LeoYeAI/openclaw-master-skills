# 地图展示房源方案参考

向客户推荐房源时，可以通过地图直观展示房源位置和周边配套。

**推荐方案**：方案二（Vue Webapp），启动 server.py 后浏览器访问即可。如果已在 `.env` 中配置 `AMAP_JS_API_KEY` 和 `AMAP_JS_API_SECURITY_CODE`，页面会展示完整地图；未配置时自动降级为卡片列表模式，点击卡片跳转高德网页查看。

**备选方案**：方案一（高德网页直链），适用于无法启动 webapp 的场景，直接在对话中给客户发送链接。

---

## 方案一：高德网页版直链（默认）

直接生成高德地图网页 URL，用浏览器打开即可查看。

### 优点
- **零配置**：不需要任何 API Key，开箱即用
- **功能完整**：高德网页版自带周边搜索、路线规划、街景等全部功能
- **信息实时**：展示的 POI、路线等信息始终是高德最新数据

### 缺点
- **无法多点标注**：每次只能搜索/定位一个地点，无法在同一地图上同时展示多个房源
- **无法自定义信息**：不能在地图上叠加房价、匹配度等自定义数据
- **需要多次操作**：对比多个房源需要依次打开多个链接

### URL 格式

```
# 按关键词搜索（推荐，适合搜小区名）
https://www.amap.com/search?query={关键词}&city={城市编码}

# 按坐标定位（精确位置）
https://www.amap.com/search?query={经度},{纬度}

# 查看周边（搜索周边配套）
https://www.amap.com/around?query={配套类型}&center={经度},{纬度}
```

### 常用城市编码
- 深圳：440300
- 广州：440100
- 北京：110000
- 上海：310000
- 杭州：440300

### 使用示例

向客户展示房源时，为每个房源生成链接：

```markdown
**绿城桂语兰庭**
- 📍 地图查看：[高德地图](https://www.amap.com/search?query=绿城桂语兰庭&city=440300)

**拾悦城楠园**
- 📍 地图查看：[高德地图](https://www.amap.com/search?query=拾悦城楠园&city=440300)
```

如果需要查看周边配套，引导客户在高德地图页面中使用"周边"功能，或生成周边搜索链接：

```markdown
- 🏫 周边学校：[查看](https://www.amap.com/around?query=学校&center=113.88,22.72)
- 🚇 周边地铁：[查看](https://www.amap.com/around?query=地铁站&center=113.88,22.72)
```

---

## 方案二：Vue Webapp + 高德 JS API（推荐）

通过 Vue webapp 提供完整的地图 + 房源卡片交互界面，前端从后端 API 读取 `properties.json` 和 `.env` 配置，在浏览器中直接渲染地图。

### 架构

```
webapp/                              ← Vue 前端源码
├── src/views/MapView.vue            ← 地图页面组件
├── src/components/PropertyCard.vue  ← 房源卡片组件
└── src/api.ts                       ← 后端 API 调用

skills/zhongjie/
├── scripts/server.py                ← FastAPI 后端（提供配置和数据 API）
└── assets/dist/                     ← 前端构建产物

.skills-data/zhongjie/
├── .env                             ← API Key 配置
└── data/
    └── properties.json              ← 房源数据（由技能维护）
```

### 优点
- **多房源同屏对比**：所有推荐房源同时标注在一张地图上
- **自定义信息弹窗**：点击标注可显示房价、户型、匹配度、中介点评等
- **周边配套下拉跳转**：每个房源卡片自带周边配套下拉选择器，点击后跳转高德网页版查看（零 API 消耗）
- **卫星图切换**：标准地图/卫星图切换，方便看实际环境
- **API 用量极低**：仅在初始化时为每个房源调用一次地名搜索（N 个房源 = N 次调用），搜索失败会自动重试
- **无需手动生成**：启动 server.py 后浏览器访问即可，数据更新后刷新页面自动生效
- **未配置 API Key 也可用**：自动降级为纯卡片列表，点击跳转高德网页

### 缺点
- **需要 API Key**：完整地图功能需要在高德开放平台注册并申请 JS API Key
- **需要安全密钥**：高德 JS API 2.0 要求配合安全密钥使用
- **有调用限额**：免费额度日均 5,000 次（按每次打开页面 N 次调用算，每天可用上千次）

### API Key 配置

客户需要在 [高德开放平台](https://lbs.amap.com/) 完成以下操作：

1. 注册并登录高德开放平台
2. 进入「应用管理」→「我的应用」→「创建新应用」
3. 在应用下「添加 Key」，服务平台选择 **Web端(JS API)**
4. 获取 **Key** 和 **安全密钥（jscode）**
5. 将 Key 和安全密钥告知中介哥，中介哥会保存到 `.skills-data/zhongjie/.env`

`.env` 配置格式：

```env
AMAP_JS_API_KEY=你的Key
AMAP_JS_API_SECURITY_CODE=你的安全密钥
```

### 使用方法

```bash
export PROJECT_ROOT="<项目根目录绝对路径>"

# 启动后端服务
python3 skills/zhongjie/scripts/server.py

# 浏览器访问
open http://localhost:8000
```

更新房源数据后，刷新浏览器页面即可看到最新内容，无需重启服务。

### properties.json 数据格式

房源数据文件为 JSON 数组，每个元素代表一个房源。支持以下字段：

```json
[
  {
    "name": "小区名称",
    "searchName": "高德地图搜索关键词（可选，默认用 name）",
    "area": "所在区域",
    "price": "参考均价",
    "priceDetail": "价格详情说明",
    "layout": "户型描述",
    "highlights": ["亮点1", "亮点2"],
    "concerns": ["短板1", "短板2"],
    "comment": "中介点评（一两句话）",
    "matchScore": 5,
    "isReference": false,
    "color": "#d4845a",
    "fallback": [113.935, 22.755],
    "sources": [
      {"label": "来源名称", "url": "https://..."}
    ]
  }
]
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 小区/楼盘名称 |
| `searchName` | string | | 高德地图搜索用名（不填则用 `name`），可加区域辅助定位 |
| `area` | string | | 所在区域（如"光明区"、"宝安沙井"） |
| `price` | string | | 参考均价 |
| `priceDetail` | string | | 价格补充说明（户型对应总价等） |
| `layout` | string | | 户型面积描述 |
| `highlights` | string[] | | 亮点标签（绿色） |
| `concerns` | string[] | | 短板标签（黄色） |
| `comment` | string | | 中介点评，一两句话 |
| `matchScore` | number | | 匹配度 1-5（显示为星星） |
| `isReference` | boolean | | 是否为参考标的（虚线卡片，绿色标记） |
| `color` | string | | 标注颜色（不填则自动分配） |
| `fallback` | [lng, lat] | | 备用坐标（高德搜索失败时使用） |
| `sources` | object[] | | 信息来源链接，每项含 `label`（来源名）和 `url`（链接地址） |

### 工作流程

```
推荐房源时：
    │
    ├─ 1. 确保 server.py 已启动
    │
    ├─ 2. 将房源数据写入 .skills-data/zhongjie/data/properties.json
    │
    └─ 3. 客户刷新浏览器页面即可查看所有房源位置和周边配套

后续更新：
    │
    ├─ 新增房源 → 在 properties.json 中追加 → 刷新浏览器
    └─ 修改信息 → 编辑 properties.json → 刷新浏览器
```

---

## 使用决策流程

```
客户想看房源位置
    │
    ├─ .env 中 AMAP_JS_API_KEY 已配置？
    │   ├─ 是 → 方案二：更新 properties.json → 刷新浏览器查看地图
    │   └─ 否 → webapp 自动降级为卡片列表（点击跳转高德），或用方案一直接发链接
    │
    └─ 客户首次使用且未配置？
        └─ 询问客户想用哪个方案，说明利弊
           ├─ 选方案一 → 直接使用，无需配置
           └─ 选方案二 → 引导注册高德开放平台，获取 Key 后配置
```
