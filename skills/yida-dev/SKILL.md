---
name: yida-dev
description: 钉钉宜搭低代码开发助手。用于创建表单和自定义页面、编写 JS 动作面板、使用 JS-API、配置数据源、设计流程自动化。适用于宜搭表单开发、JS 代码调试、API 集成等场景。
trigger_phrases:
  - 宜搭
  - yida
  - 钉钉表单
  - 低代码开发
  - 宜搭JS
  - 宜搭开发
---

## ⚠️ 重要：宜搭开发模式

**与传统前端不同，宜搭有独特的开发模式：**

1. **页面不是代码写的** - 页面通过宜搭可视化拖拽创建，不是 JSX/HTML 声明
2. **不要写组件声明代码** - ❌ 禁止 `import Button`、❌ 禁止 `const Page = () => {...}`
3. **只有 JS 动作面板** - 宜搭的 JS 代码是"动作面板"，只能写函数，不能写组件
4. **组件通过 fieldId 引用** - 使用 `this.$('textField_xxx')` 操作已存在的组件

## 组件 fieldId 命名规范

宜搭组件的 fieldId 格式为：`组件类型_随机后缀`

| 组件类型 | fieldId 示例 |
|---------|-------------|
| 单行文本 | `textField_m2iqeyip` |
| 多行文本/文本域 | `textareaField_lu7rqky5` |
| 单选 | `radioField_m2l8tqxr` |
| 流水号 | `serialNumberField_lr76bpi4` |
| 数字 | `numberField_mbhl6h58` |
| 下拉选择 | `selectField_mbhjt4zb` |
| 日期 | `dateField_ll0bcdf1` |
| 附件 | `attachmentField_mbhjt4zd` |
| 图片 | `imageField_mbhjt4zl` |
| 人员选择 | `employeeField_mbhjt4zr` |
| 人员多选 | `employeeField_xxx` + `multiple: true` |
| 部门选择 | `departmentSelectField_lu7qx4i5` |
| 子表单/明细表 | `tableField_mbhjt4zy` |
| 地址 | `addressField_mbhjt508` |
| 关联表单 | `associationFormField_mbhjt50s` |
| 区块 | `pageSection_m2vthls5` |
| 按钮 | `button_invoiceAdd` |
| 发票组件 | `ccInvoiceFieldComponentView_m2vv4aux` |
| 多列布局 | `columnsLayout_m2k6t8hx` |
| 标签页 | `tabsLayout_lkcfmpjv` |

## 常见开发模式

### 条件显示
- 组件属性 → 高级 → 是否渲染 → 绑定变量 `state.sta`
- 或 JS 设置：`this.$('fieldId').setBehavior('HIDDEN')`

### 事件函数命名
- `export function onChange({ value }) { }` - 值变化事件
- `export function didMount() { }` - 页面加载完成

### setTimeout 延迟
宜搭组件 onChange 事件中修改状态需要延迟：
```js
export function onChange({ value }) {
  setTimeout(() => {
    this.setState({ sta: value === '价款合同' })
  }, 200)
}
```

### 隐藏字段
组件属性中设置 `behavior: "HIDDEN"` 可隐藏字段（可用于数据传递）

### 只读字段
组件属性中设置 `behavior: "READONLY"` 可设为只读

### 公式字段
在组件属性中设置 `valueType: "formula"` + `formula: "#{textField_xxx}"`
```json
{
  "valueType": "formula",
  "formula": "CONCATENATE(\"XMBH\",TEXT(TODAY(),\"yyMMdd\"),MID(TEXT(TIMESTAMP(NOW())),9,5))"
}
```

### TableField 事件
新增行时获取行数：
```js
export function onAddClick(newGroupId) {
  const count = this.$('tableField_xxx').getValue().length
  this.$('textField_count').setValue(count + '条')
}
```

### TableField onChange 计算不重复值
遍历子表单行，计算某列的不重复值数量：
```js
export function onChange({ value, extra }) {
  const subFormInst = this.$('tableField_xxx')
  const items = subFormInst.getItems()
  let distinctNum = []
  items.forEach(item => {
    const rowData = subFormInst.getItemValue(item)
    if (rowData['textField_col'] && !distinctNum.includes(rowData['textField_col'])) {
      distinctNum.push(rowData['textField_col'])
    }
  })
  this.$('numberField_count').setValue(distinctNum.length)
}
```

### EmployeeField onChange
人员选择变化时获取人员信息：
```js
export function onChange({ value }) {
  // value 是人员对象 { name, userId, ... }
  this.$('textField_name').setValue(value.name)
}
```

### PageSection 区块
用于分组显示，有标题头：
```json
{
  "componentName": "PageSection",
  "props": {
    "title": { "zh_CN": "基本信息" },
    "behavior": "NORMAL",  // 或 "HIDDEN" 隐藏整个区块
    "showHeader": true
  }
}
```

### 关联表单数据填充
选择关联表单时自动填充其他字段：
```json
{
  "dataFillingRules": [
    { "sourceType": "SelectField", "targetType": "TextField", "source": "selectField_src", "target": "textField_target" }
  ]
}
```

### 联动字段
设置 `valueType: "linkage"` + `linkage` 属性从其他表单获取数据

### SUM 汇总公式
汇总子表单某列：
```json
{
  "valueType": "formula",
  "formula": "SUM(#{numberField_column})"
}
```

### RadioField 联动
单选切换时显示/隐藏字段（配置选项的联动规则）

### onBlur 事件
失焦时执行校验（如手机号验证）：
```js
export function onBlur() {
  let phone = this.$('textField_xxx').getValue()
  if (!phone) return
  if (!this.isPhoneNumber(phone)) {
    this.utils.toast({ title: '请输入正确的手机号', type: 'warning' })
    this.$('textField_xxx').setValue('')
  }
}

export function isPhoneNumber(input) {
  return /^1\d{10}$/.test(input.replace(/\D/g, ''))
}
```

### NumberField 校验
设置 minValue 最小值：
```json
{ "validation": [{ "type": "minValue", "param": "0" }] }
```

## 组件属性参考

### SelectField 下拉选择
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| dataSource | 选项数据 | DataSource[] | [] |
| onChange | 值变化事件 | (value: string) => void | - |
| showSearch | 展开后能搜索 | boolean | true |
| filterLocal | 本地过滤 | boolean | - |
| mode | single/multi | string | single |
| hasClear | 清除按钮 | boolean | true |
| autoWidth | 菜单对齐 | boolean | true |

### TableField 明细表
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| onChange | 值变化事件 | ({value, extra}) => void | - |
| onAddClick | 新增行事件 | (newGroupId) => void | - |
| onDelClick | 删除行事件 | (groupId, item) => void | - |
| maxItems | 最大条数 | number | 50 |
| addButtonPosition | 新增位置 | 'top' \| 'bottom' | bottom |
| layoutSetting.layout | 排列方式 | 'TILED' \| 'TABLE' | TABLE |
| layoutSetting.theme | 主题 | 'zebra' \| 'split' \| 'border' | split |
| showIndex | 显示序号 | boolean | true |

### TableField JS 操作
```js
const table = this.$('tableField_xxx')
table.getValue()           // 获取所有行数据
table.getItems()           // 获取行实例数组
table.getItemValue(item)   // 获取某行数据
table.addItem()            // 新增一行
table.removeItem(item)    // 删除一行
```

### NumberField
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| precision | 小数位数 (0-20) | number | 0 |
| thousandsSeparators | 千分位 | boolean | false |
| innerAfter | 单位 | string | - |
| innerBefore | 前缀 | string | - |

### RadioField
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| dataSource | 选项 | DataSource[] | [] |
| onChange | 值变化 | (value) => void | - |
| shape | 形状 | 'default' \| 'button' | default |
| itemDirection | 排列 | 'hoz' \| 'ver' | hoz |
| supportInverse | 反选 | boolean | false |

### ColumnsLayout 多列布局
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| layout | 分栏配置 | string | '6:6' |
| columnGap | 列间距 | number | 0 |
| rowGap | 行间距 | number | 0 |
| display | 手机排列 | 'VERTICAL' \| 'HORIZONTAL' | VERTICAL |

 布局格式: `2:2:2:2:4` (总和=12), 多行: `4:4:4\|6:6`

### Button 按钮
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| type | 按钮类型 | 'primary'\|'normal'\|'secondary' | primary |
| content | 按钮文案 | string | 按钮 |
| size | 尺寸 | 'small'\|'medium'\|'large' | medium |
| behavior | 显示状态 | 'NORMAL'\|'DISABLED'\|'HIDDEN' | NORMAL |
| loading | 加载状态 | boolean | false |

### Icon 图标
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| baseType | 基础图标 | string | smile |
| size | 尺寸 | 'xxs'\|'xs'\|'small'\|'medium'\|'large' | medium |
| useType | 使用自定义 | boolean | false |

### EmployeeField 人员选择
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| multiple | 多选 | boolean | false |
| showEmplId | 显示工号 | boolean | false |
| showAvater | 显示头像 | boolean | true |
| closeOnSelect | 选中后关闭 | boolean | false |
| onChange | 值变化 | ({value}) => void | - |

### DateField 日期选择
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| format | 日期格式 | string | YYYY-MM-DD |
| type | 限制范围 | 'none'\|'beforeToday'\|'afterToday' | none |
| hasClear | 清除按钮 | boolean | true |
| returnType | 返回类型 | 'timestamp'\|'string'\|'moment' | timestamp |
| onChange | 值变化 | ({value}) => void | - |

### TextField 单行输入
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| validationType | 格式 | 'text'\|'mobile'\|'email'\|'chineseID' | text |
| maxLength | 字数上限 | number | 200 |
| hasClear | 清除按钮 | boolean | true |
| hasLimitHint | 计数器 | boolean | false |
| trim | 去空格 | boolean | false |
| onChange | 值变化 | ({value}) => void | - |

### TextareaField 多行输入
| 属性 | 说明 | 类型 | 默认值 |
|-----|------|-----|-------|
| rows | 行数 | number | 4 |
| autoHeight | 自动高度 | boolean | false |
| maxLength | 字数上限 | number | - |

### USER() 公式
人员字段自动填充当前登录人：
```json
{ "valueType": "formula", "formula": "USER()" }
```

### 关联表单数据过滤
设置 dataFilterRules 过滤可选数据

### 页面级校验器
在页面属性 → 数据校验 中配置，检测重复数据：
```json
{
  "displayRule": "EXIST(角色名称)",
  "rule": "EXIST(#{formUuid}, \"textField_lenz6y7q\", #{textField_lenz6y7q})",
  "message": "角色名称不能重复"
}

## 核心概念

### 全局变量 (State)
类似 React state，用于页面全局状态管理：
- 创建：在数据源面板 → 添加变量
- 读取：`this.state.name` 或 `state.name`（变量绑定时）
- 更改：`this.setState({ name: 'Jack' })`
- 特殊变量：`urlParams` - 获取 URL 参数

⚠️ 注意：setState 后可立即获取新值（不同于 React），但无回调函数

### 远程数据源
配置远程 API 进行异步请求：
```js
// 手动加载
this.dataSourceMap.apiName.load({ params }).then(res => {})

// 重新加载所有自动加载的数据源
this.reloadDataSource()
```

数据处理函数：
- `willFetch` - 请求发送前修改参数
- `fit` - 响应数据适配
- `didFetch` - 请求成功后的数据处理
- `onError` - 错误处理

### 生命周期
```js
export function didMount() { }    // 页面加载完成
export function willUnmount() { } // 页面卸载前
```

### 事件处理
给组件绑定动作事件，在动作面板实现处理逻辑：
```js
export function onClick() {
  const { name, age } = this.params  // 获取绑定时设置的参数
}
```

### 表单校验
内置规则 + 自定义校验函数：
```js
function validateRule(value) {
  if (/^杭州/.test(value)) return true
  return false
}
```

手动触发校验：
```js
this.$('textField_xxx').validate((errors, values) => {})
```

常用校验示例：
- 银行卡号（Luhn算法）：16或19位数字
- 身份证号：18位，末尾校验码

### 循环渲染
循环数据要求是数组，绑定变量获取循环数据：
- `this.item` - 获取当前行数据
- `this.index` - 获取当前行索引

容器组件绑定循环数据后可遍历渲染，内部组件通过变量绑定访问数据。

### 条件渲染
组件高级属性 → 是否渲染 → 绑定变量控制显隐
```js
// 绑定 state.xxx 控制显示
state.urlParams.showName  // 根据URL参数控制
```

### 自定义样式
两种方式：
1. 基础样式配置 - 可视化配置布局、文字、背景等
2. 手工编码模式 - CSS 选择器、伪类等

## 名词解释

| 术语 | 说明 |
|------|------|
| 全局变量 | 类似 React state，页面状态管理 |
| 远程 API | HTTP 接口配置，包含请求地址、参数、数据处理函数 |
| Schema | 低代码协议，描述页面/组件结构，类似 HTML |
| 组件唯一标识 | 组件的 fieldId，宜搭全局唯一标识 |
| 页面 | 独立展示界面（表单、报表、自定义页面） |
| 物料 | 可沉淀的前端能力（组件、区块、模板） |
| 业务组件 | 基于基础组件的业务领域组件 |
| 低代码业务组件 | 通过低代码编辑器搭建的业务组件 |
| 区块 | 组合多个组件/布局，可复制复用 |
| 模板 | 垂直业务领域的页面模板 |

## 集成自动化（连接器）

触发类型：
- 表单事件触发 - 提交/流程状态更新
- 定时触发 - 周期循环
- 应用事件触发 - 钉钉生态事件
- Webhook 触发

节点类型：
- 触发器
- 一方连接器（钉钉消息、待办等）
- 自定义连接器
- 数据节点（新增/更新/获取/删除）
- 分支节点（条件分支/并行分支）
- 发起审批
- 消息节点
- 开发者节点（Groovy 脚本）

## 自定义组件

⚠️ 仅限专属版

### 概念
- 普通组件 - 展示型，无数据存储
- 表单组件 - 可提交数据（暂未开放）

### 开发流程
1. 创建组件 - 应用设置 → 组件管理 → 新增组件
2. 开发调试 - 定义属性 + 搭建视图 + 编写逻辑
3. 发布版本 - 开发版(0.1.0) / 正式版(1.x.x)
4. 安装使用 - 选择页面类型安装

### 组件属性 (propTypes)
- 属性类型：文本、布尔、数字、对象、数组、函数、元素
- 设置器：TextSetter、BoolSetter、NumberSetter、JsonSetter、OptionsSetter、ActionSetter、SlotSetter 等

### 组件生命周期
```js
export function componentDidMount() { }   // 渲染完成
export function componentDidUpdate() { }  // 更新完成
export function componentDidCatch() { }   // 错误捕获
export function componentWillUnmount() { } // 销毁前
```

### 组件内获取属性
```js
this.props.xxx  // 获取传入的属性
```

### 页面中操作自定义组件
```js
this.$('fieldId').get('propName')  // 获取属性
this.$('fieldId').set('propName', value)  // 设置属性
```

### 组件联动
添加 function 类型属性作为事件回调，在组件内通过 `this.props.xxx()` 触发

### 注意事项
- fieldId 不能随意修改，会影响公式和存储
- 线上应用请安装正式版本 (1.x.x)
- 不支持删除/卸载组件

## 调试方法

- `debugger` 断点调试
- 浏览器控制台 `cmd/ctrl + p` → `page.js` 添加断点
- URL 加 `?__showDevtools` 打开调试面板
- URL 加 `?__debug` 查看/编辑 Schema
- 移动端调试：引入 vConsole
```js
const vConsole = 'https://g.alicdn.com/code/lib/vConsole/3.11.2/vconsole.min.js';
const js = document.createElement('script');
js.src = vConsole;
document.body.append(js);
js.onload = function() { window.vConsole = new window.VConsole(); };
```

## API 体系

### 宜搭 JS-API
前端页面调用，包括：
- 全局变量：`this.state.xxx` / `this.setState()`
- 远程数据：`this.dataSourceMap.xxx.load()` / `this.reloadDataSource()`
- 组件操作：`this.$(fieldId).getValue()` / `this.$(fieldId).setValue()`
- 工具类：`this.utils.toast()` / `this.utils.dialog()` / `this.utils.router.push()`
- 校验：`this.$(fieldId).validate()` / `this.$(fieldId).setValidation()`

### 跨应用数据源 API (OpenAPI)
远程数据源配置中调用，用于表单数据操作：
- 新建：`POST /v1/form/saveFormData.json`
- 更新：`POST /v1/form/updateFormData.json`
- 删除：`POST /v1/form/deleteFormData.json`
- 查询：`GET /v1/form/searchFormDatas.json`
- 流程发起：`POST /v1/process/startInstance.json`

### 钉钉 JS-API
需手动加载：`https://g.alicdn.com/dingding/dingtalk-jsapi/2.10.3/dingtalk.open.js`
- 弹框：device.notification.alert/confirm/prompt
- 扫码：biz.util.scan
- 地图：biz.map.locate/view
- 通讯录：biz.contact.choose/complexPicker

### 服务端 OpenAPI
需通过钉钉开放平台调用，需要鉴权：
- 创建钉钉应用 → 添加权限 → 获取 access_token
- 调用服务端接口

## 2026 年新功能

### 2026.02.03 集成自动化升级
- 异常日志支持批量重试
- 日志实例ID交互优化
- 数据节点过滤条件增加"父级条件"
- 新增 AI 节点

### 2026.01.20 新功能
- 宜搭表单新增「钉钉文档」选择组件
- 富文本支持钉钉文档链接自动识别
- 附件/图片支持批量下载
- 关联表单/关联列表支持自定义显示字段

### 2026.01.05 新功能
- 贴一贴：附件上传快捷黏贴（Ctrl+V）
- 实例标题支持变量动态更新
- 数据管理文本筛选动态匹配
- 关联表单数据搜索升级（大小写自动匹配）

## 快速参考

### 组件操作
```js
// ✅ 正确：操作已存在的组件（通过 fieldId）
this.$('textField_m2iqeyip').getValue()
this.$('textField_m2iqeyip').setValue('hello')

// ❌ 错误：不要声明/导入组件
// const MyButton = () => {...}  // 禁止！
```

### 状态管理
```js
this.setState({ key: 'value' })
const value = this.state.key

// URL 参数（默认全局变量）
const param = this.state.urlParams.xxx
```

### 生命周期
```js
export function didMount() { }   // 页面加载完成
export function willUnmount() { } // 页面卸载前
```

### 远程数据源
```js
this.dataSourceMap.api.load(params).then(res => { })
this.reloadDataSource()
```

### 常用工具
```js
this.utils.toast({ title: '成功', type: 'success' })
this.utils.router.push('/pageId')
this.utils.getLoginUserId()
```

## 详细文档

- [JS-API 完整参考](references/js-api.md) - 组件操作、校验、弹窗、路由等
- [故障排查指南](references/troubleshooting.md) - 调试方法、常见问题
- [TodoMVC 入门教程](references/todomvc.md) - 新人入门完整示例

## 调试方法

- URL 加 `?__showDevtools` 打开调试面板
- URL 加 `?__debug` 查看 Schema
- 代码加 `debugger` 断点
- 使用 `console.log` 输出调试信息

## 参考资源

| 资源 | 地址 |
|------|------|
| 帮助中心 | https://docs.aliwork.com/ |
| 开发者中心(前端) | https://developers.aliwork.com/ |
| 开放平台(服务端) | https://open.dingtalk.com/ |
| 示例中心 | https://www.aliwork.com/o/coc |
| 更新日志 | https://docs.aliwork.com/docs/yida_updates |
| OpenAPI | https://developers.aliwork.com/docs/api/openAPI |

## 服务端 OpenAPI (open.dingtalk.com)

需通过钉钉开放平台调用，需要创建应用并获取授权。

### 流程 API
| 接口 | 路径 | 说明 |
|------|------|------|
| 发起审批 | `POST /yida/v1/process/startInstance.json` | processCode, formUuid, formDataJson |
| 删除流程 | `POST /yida/v1/process/delete.json` | processInstanceId |
| 终止流程 | `POST /yida/v1/process/terminate.json` | processInstanceId |
| 查询实例 | `GET /yida/v1/process/getById.json` | processInstanceId |
| 查询实例列表 | `GET /yida/v1/process/getInstanceIds.json` | formUuid, instanceStatus |

### 表单 API (V2)
| 接口 | 路径 | 说明 |
|------|------|------|
| 保存数据 | `POST /yida/v1/forms/saveData.json` | formUuid, formDataJson |
| 更新数据 | `POST /yida/v1/forms/updateData.json` | formInstId, formDataJson |
| 查询数据 | `GET /yida/v1/forms/listData.json` | formUuid, searchFieldJson |
| 获取子表数据 | `GET /yida/v1/forms/listSubTableData.json` | formUuid, formInstId, tableFieldId |

### 请求示例
```js
// 发起流程
const params = {
  processCode: "TPROC--CFYJ5HYUN89NJ1JW3IXBI7A95RXM3652O9MKK3",
  formUuid: "FORM-CFYJ5HYUN89NJ1JW3IXBI7A95RXM3552O9MKK2",
  formDataJson: JSON.stringify({ textField_kkm9o5cd: "123" })
};
this.dataSourceMap.myDatasource.load(params);
```

### 更多 API
- 批量操作、子表数据、审批记录等详见开放平台文档

## 场景案例专题

### 表单专题
常见表单开发场景：
- 数据权限：只允许查看自己的数据（表单权限设置）
- 子表单：获取子表单值赋值给主表、子表单序号生成、子表单批量导入
- 数据联动：数据源获取主表数据在子表展示、下拉框赋值、关联表单填充
- 校验：子表单重复校验、组件实时校验唯一性、自定义校验
- 高级：图片裁剪上传、扫码识别、地址组件动态类型、公历转农历

### 自定义页面专题
- 页面搭建、组件使用、事件处理

### 连接器专题
- 集成自动化、钉钉消息、待办通知

### 实用工具专题
- 常用工具组件使用

### 报表专题
- 数据可视化、图表配置

### 公式专题
- 公式函数使用、计算逻辑

### 方案专题
- 行业解决方案、业务场景案例

## Schema 生成

宜搭页面使用 JSON Schema 定义，可以直接粘贴到设计器中。

### 基础结构
```json
{
  "type": "nodeSchema",
  "componentsMap": {},
  "componentsTree": [
    {
      "componentName": "PageSection",
      "props": { ... },
      "children": [ ... ]
    }
  ]
}
```

### 常用组件 Schema

#### TextField (单行文本)
```json
{
  "componentName": "TextField",
  "props": {
    "fieldId": "textField_xxxxx",
    "label": { "type": "i18n", "zh_CN": "字段名称", "en_US": "字段名称" },
    "behavior": "NORMAL",
    "valueType": "custom",
    "validation": [{ "type": "required" }],
    "placeholder": { "type": "i18n", "zh_CN": "请输入", "en_US": "请输入" },
    "maxLength": 200,
    "visibility": ["PC", "MOBILE"]
  }
}
```

#### NumberField (数字)
```json
{
  "componentName": "NumberField",
  "props": {
    "fieldId": "numberField_xxxxx",
    "label": { "type": "i18n", "zh_CN": "金额", "en_US": "金额" },
    "precision": 2,
    "step": 1,
    "behavior": "NORMAL",
    "valueType": "custom",
    "validation": [
      { "type": "required" },
      { "type": "minValue", "param": 0 },
      { "type": "maxLength", "param": 25 }
    ]
  }
}
```

#### DateField (日期)
```json
{
  "componentName": "DateField",
  "props": {
    "fieldId": "dateField_xxxxx",
    "label": { "type": "i18n", "zh_CN": "日期", "en_US": "日期" },
    "format": "YYYY-MM-DD",
    "behavior": "NORMAL",
    "valueType": "custom",
    "validation": [{ "type": "required" }]
  }
}
```

#### SelectField (下拉选择)
```json
{
  "componentName": "SelectField",
  "props": {
    "fieldId": "selectField_xxxxx",
    "label": { "type": "i18n", "zh_CN": "选项", "en_US": "选项" },
    "mode": "single",
    "showSearch": true,
    "behavior": "NORMAL",
    "valueType": "custom",
    "defaultDataSource": {
      "customStashOptions": [
        { "text": { "zh_CN": "选项一", "en_US": "选项一" }, "value": "选项一", "sid": "serial_xxx" }
      ]
    }
  }
}
```

#### RadioField (单选)
```json
{
  "componentName": "RadioField",
  "props": {
    "fieldId": "radioField_xxxxx",
    "label": { "type": "i18n", "zh_CN": "类型", "en_US": "类型" },
    "itemDirection": "hoz",
    "behavior": "NORMAL",
    "valueType": "custom",
    "dataSource": [
      { "text": { "zh_CN": "选项A", "en_US": "选项A" }, "value": "A", "sid": "serial_a" },
      { "text": { "zh_CN": "选项B", "en_US": "选项B" }, "value": "B", "sid": "serial_b" }
    ]
  }
}
```

#### EmployeeField (人员选择)
```json
{
  "componentName": "EmployeeField",
  "props": {
    "fieldId": "employeeField_xxxxx",
    "label": { "type": "i18n", "zh_CN": "申请人", "en_US": "申请人" },
    "multiple": false,
    "behavior": "NORMAL",
    "valueType": "custom",
    "userRangeType": "ALL",
    "validation": [{ "type": "required" }]
  }
}
```

#### AssociationFormField (关联表单)
```json
{
  "componentName": "AssociationFormField",
  "props": {
    "fieldId": "associationFormField_xxxxx",
    "label": { "type": "i18n", "zh_CN": "关联数据", "en_US": "关联数据" },
    "behavior": "NORMAL",
    "multiple": false,
    "associationForm": {
      "formUuid": "FORM-XXXXXXXX",
      "appType": "APP_XXXXXXXX"
    },
    "validation": [{ "type": "required" }]
  }
}
```

#### Image (图片)
```json
{
  "componentName": "Image",
  "props": {
    "fieldId": "image_xxxxx",
    "src": "https://example.com/image.jpg",
    "width": 100,
    "height": 100,
    "fit": "cover"
  }
}
```

#### Text (文本)
```json
{
  "componentName": "Text",
  "props": {
    "fieldId": "text_xxxxx",
    "content": { "type": "i18n", "zh_CN": "文本内容", "en_US": "文本内容" },
    "__style__": ":root { font-size: 16px; font-weight: 600; }"
  }
}
```

#### LinkBlock (链接块)
```json
{
  "componentName": "LinkBlock",
  "props": {
    "fieldId": "linkBlock_xxxxx",
    "link": { "type": "url", "url": "https://example.com", "isBlank": true },
    "__style__": ":root { margin: 10px; }"
  }
}
```

#### Div (容器)
```json
{
  "componentName": "Div",
  "props": {
    "fieldId": "div_xxxxx",
    "__style__": ":root { padding: 20px; background: #fff; }"
  }
}
```

### 布局组件

#### PageSection (区块)
```json
{
  "componentName": "PageSection",
  "props": {
    "fieldId": "pageSection_xxxxx",
    "title": { "type": "i18n", "zh_CN": "基本信息", "en_US": "基本信息" },
    "showHeader": true,
    "behavior": "NORMAL"
  }
}
```

#### ColumnsLayout + Column (多列布局)
```json
{
  "componentName": "ColumnsLayout",
  "props": {
    "fieldId": "columnsLayout_xxxxx",
    "layout": "4:4:4"
  },
  "children": [
    { "componentName": "Column", "props": { "fieldId": "column_1" } },
    { "componentName": "Column", "props": { "fieldId": "column_2" } },
    { "componentName": "Column", "props": { "fieldId": "column_3" } }
  ]
}
```

### 常用属性

| 属性 | 说明 | 值 |
|------|------|-----|
| behavior | 组件状态 | NORMAL, READONLY, HIDDEN, DISABLED |
| valueType | 值类型 | custom, formula, linkage |
| validation | 校验规则 | required, minValue, maxLength, customValidate |
| formula | 公式 | CONCATENATE, TODAY, TIMESTAMP, USER, SUM 等 |
| format | 日期格式 | YYYY-MM-DD, YYYY-MM-DD HH:mm:ss |

### 生成字段 ID
字段 ID 格式：`组件类型_随机后缀`，例如：
- `textField_abc123`
- `numberField_def456`
- `selectField_ghi789`

### 示例 App ID
当前应用：`APP_F22M8EK6I2HZTBIYV3U5`
