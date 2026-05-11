# TodoMVC 完整教程

本文档是宜搭官方 TodoMVC 教程的完整代码实现。

## 教程地址

- 示例页面：https://www.aliwork.com/o/demo/todoMVC-3
- 在线试玩：https://www.aliwork.com/o/coc?tplUuid=TPL_PMFQNW628OML366HTNJO

## 掌握技能

通过本教程你将学会：
- 宜搭基本组件使用
- 用户行为事件处理
- 全局变量使用
- 条件渲染 & 循环渲染
- 自定义样式
- 远程 API 使用
- 宜搭 OpenAPI 使用

## 全局变量定义

在页面设置中添加以下全局变量：

```js
{
  todoList: [           // 任务列表
    { id: 1, content: '任务内容', done: false }
  ],
  editRowId: 0,         // 当前编辑的任务ID
  mode: 'All',           // 筛选模式：All/Active/Completed
  newId: 1              // 新任务ID生成器
}
```

## 页面结构

```
┌─────────────────────────────────────┐
│           大 Logo                    │  ← 文本组件
├─────────────────────────────────────┤
│  [输入框]                        [+] │  ← 输入框 + 按钮
├─────────────────────────────────────┤
│  ☐ 任务内容...              [E] [X] │  ← 循环渲染
│  ☑ 已完成任务...            [E] [X] │
├─────────────────────────────────────┤
│  3 items left  [All][Active][Clear] │  ← 统计 + 筛选
└─────────────────────────────────────┘
```

## 核心功能代码

### 1. 创建任务

给输入框绑定 onKeyDown 事件：

```js
export function onRowAdd(e) {
  // 只处理回车键
  if (e.keyCode !== 13) return;
  
  const { todoList, newId } = this.state;
  
  this.setState({
    todoList: [
      {
        id: newId,
        done: false,
        content: this.$('input').getValue()  // 获取输入框内容
      },
      ...todoList
    ],
    newId: newId + 1
  });
  
  // 清空输入框
  this.$('input').setValue('');
}
```

### 2. 循环渲染任务列表

1. 选中任务列表容器组件
2. 在高级属性中设置"循环数据"为 `state.todoList`
3. 循环内组件使用 `this.item` 获取当前行数据

### 3. 条件渲染 - 任务状态

设置三个组件的条件渲染：

```js
// 编辑态 - 当 editRowId === 当前任务ID 时显示
state.editRowId === this.item.id

// 待完成态 - 不在编辑态且未完成
state.editRowId !== this.item.id && !this.item.done

// 已完成态 - 不在编辑态且已完成
state.editRowId !== this.item.id && this.item.done
```

### 4. 任务状态切换

给单选组件绑定 onChange 事件：

```js
export function onTodoCheck({ value }) {
  this.setState({
    todoList: this.state.todoList.map(item => {
      if (item.id === this.item.id) {
        return {
          ...item,
          done: value === 'done'  // 'done' 表示已完成
        };
      }
      return item;
    }),
    editRowId: 0  // 重置编辑态
  });
}
```

### 5. 编辑任务内容

**点击 Edit 按钮：**

```js
export function onEdit() {
  this.setState({
    editRowId: this.item.id  // 设置当前任务为编辑态
  });
}
```

**输入框 onKeyDown 事件：**

```js
export function onRowEdit(e) {
  // 只处理回车键
  if (e.keyCode !== 13) return;
  
  this.setState({
    todoList: this.state.todoList.map(item => {
      if (item.id === this.item.id) {
        return {
          ...item,
          content: this.$('rowInput').getValue()  // 获取编辑内容
        };
      }
      return item;
    }),
    editRowId: 0  // 退出编辑态
  });
}
```

### 6. 删除任务

```js
export function onDelete() {
  this.setState({
    todoList: this.state.todoList.filter(item => {
      return item.id !== this.item.id;  // 过滤掉当前任务
    })
  });
}
```

### 7. 任务筛选

**筛选器 onChange 事件：**

```js
export function onModeChange({ value }) {
  this.setState({ mode: value });
}
```

**获取显示列表（绑定到循环数据）：**

```js
export function getShowList() {
  const { mode, todoList = [] } = this.state;
  
  if (mode === 'Active') {
    // 返回未完成的任务
    return todoList.filter(item => !item.done);
  } else if (mode === 'Completed') {
    // 返回已完成的任务
    return todoList.filter(item => item.done);
  }
  
  // 默认返回全部
  return todoList;
}
```

### 8. 待办数量统计

```js
export function getleftCount() {
  const { todoList } = this.state;
  return todoList.filter(item => !item.done).length;
}
```

### 9. 清除已完成

```js
export function onClearCompleted() {
  this.setState({
    todoList: this.state.todoList.filter(item => !item.done)
  });
}
```

### 10. 本地存储

**保存数据：**

```js
export function saveTodoData() {
  const { todoList, newId } = this.state;
  
  if (window.localStorage) {
    window.localStorage.setItem(
      'todoMVC', 
      JSON.stringify({ todoList, newId })
    );
  }
}
```

**加载数据：**

```js
export function getTodoData() {
  if (window.localStorage) {
    const data = window.localStorage.getItem('todoMVC');
    if (data) {
      return JSON.parse(data);
    }
  }
  return {};
}
```

**在 didMount 中加载：**

```js
export function didMount() {
  const data = this.getTodoData();
  if (data.todoList) {
    this.setState(data);
  }
}
```

**在每个修改 todoList 的地方调用 saveTodoData()**

## 样式 CSS

```css
/* 整体容器 */
.todo-app {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

/* Logo 样式 */
.todo-header h1 {
  font-size: 80px;
  font-weight: 200;
  color: #b83f45;
  text-align: center;
}

/* 输入框 */
.todo-input {
  width: 100%;
  padding: 16px 16px 16px 60px;
  font-size: 24px;
  border: none;
  box-shadow: inset 0 -2px 1px rgba(0,0,0,0.1);
}

/* 任务项 */
.todo-item {
  position: relative;
  font-size: 24px;
}

.todo-item.completed label {
  color: #d9d9d9;
  text-decoration: line-through;
}

/* 任务项按钮 */
.todo-item button {
  float: right;
  margin: 5px;
  font-size: 18px;
  color: #cc9a9a;
  cursor: pointer;
}

/* 底部栏 */
.todo-footer {
  color: #777;
  padding: 10px 15px;
  height: 20px;
  border-top: 1px solid #e6e6e6;
}
```

## 远程 API 对接（进阶）

当本地存储升级为远程存储时：

### 1. 创建普通表单

创建表单包含：
- 任务内容（单行文本）
- 任务状态（单选：已完成/未完成）

### 2. 配置远程 API

**获取列表：**

```js
// 名称：todoList
// URL: /dingtalk/web/APP_xxx/v1/form/listInstData.json

// 自动加载：开启

// didFetch 转换数据：
function didFetch(content) {
  return (content.data || []).map(item => {
    return {
      id: item.formInstId,
      content: item.formData.textField_xxx,
      done: item.formData.radioField_xxx === '已完成'
    };
  });
}
```

**新增任务：**

```js
// 名称：add
// URL: /dingtalk/web/APP_xxx/v1/form/createInst.json

// willFetch 转换参数：
function willFetch(vars, config) {
  vars.data.formDataJson = JSON.stringify({
    textField_xxx: vars.data.content,
    radioField_xxx: '未完成'
  });
}

// didFetch：
function didFetch(content) {
  this.utils.toast({ title: '添加成功' });
  this.reloadDataSource();
  return content;
}
```

**更新任务：**

```js
// 名称：update
// URL: /dingtalk/web/APP_xxx/v1/form/updateInst.json

// willFetch：
function willFetch(vars, config) {
  const { id, content, done } = vars.data;
  vars.data.formInstId = id;
  
  const data = {};
  if (content) {
    data.textField_xxx = content;
  }
  if (typeof done === 'boolean') {
    data.radioField_xxx = done ? '已完成' : '未完成';
  }
  vars.data.updateFormDataJson = JSON.stringify(data);
}
```

**删除任务：**

```js
// 名称：del
// URL: /dingtalk/web/APP_xxx/v1/form/deleteInst.json
```

### 3. 替换本地逻辑

将 `this.setState` 替换为 `this.dataSourceMap.xxx.load()`：

```js
// 修改前
export function onRowAdd(e) {
  if (e.keyCode !== 13) return;
  this.setState({ /* ... */ });
}

// 修改后
export function onRowAdd(e) {
  if (e.keyCode !== 13) return;
  this.dataSourceMap.add.load({
    content: this.$('input').getValue()
  });
}
```
