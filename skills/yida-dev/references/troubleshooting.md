# 故障排查指南

本文档提供宜搭开发中常见问题的排查方法。

## 调试方法

### 1. debugger 断点调试

在代码中添加 `debugger` 关键字：

```js
export function onClick() {
  debugger; // 预览时在此处暂停
  const value = this.$('field').getValue();
}
```

### 2. 自助调试面板

URL 添加参数：
- `?__showDevtools` - 查看数据源变量、表单数据、错误请求
- `?__debug` - 查看/编辑页面 Schema

### 3. Chrome DevTools

- 预览页面按 `Cmd/Ctrl + P` 输入 `page.js` 快速定位源码
- 使用 Console 面板查看日志
- 使用 Network 面板查看请求

### 4. 移动端 vConsole

在动作面板最上方添加：

```js
const vConsole = 'https://g.alicdn.com/code/lib/vConsole/3.11.2/vconsole.min.js';
const js = document.createElement('script');
js.src = vConsole;
document.body.appendChild(js);
js.onload = function() { 
  window.vConsole = new window.VConsole(); 
};
```

## 常见问题

### this 指向问题

```js
// ❌ 错误 - 嵌套函数中 this 改变
export function wrong() {
  fetchData(function() {
    this.$('field').setValue('x'); // 报错：this is undefined
  });
}

// ✅ 正确 - 使用箭头函数
export function correct() {
  fetchData(() => {
    this.$('field').setValue('x'); // 正常
  });
}

// ✅ 正确 - 保存引用
export function alsoCorrect() {
  const that = this;
  fetchData(function() {
    that.$('field').setValue('x');
  });
}
```

### 状态更新问题

```js
// setState 是异步的，如需在更新后操作
this.setState({ value: 'new' }, () => {
  // 回调中获取最新值
  console.log(this.state.value);
});

// ❌ 错误 - 立即获取值
this.setState({ value: 'new' });
console.log(this.state.value); // 可能是旧值
```

### 组件值获取问题

```js
// ❌ 错误 - 组件未渲染时获取值
export function onClick() {
  const value = this.$('field').getValue(); // 可能报错
}

// ✅ 正确 - 先判断组件是否存在
export function onClick() {
  const field = this.$('field');
  if (field) {
    const value = field.getValue();
  }
}
```

### 循环中的事件绑定

```js
// 在循环渲染中，this.item 和 this.index 可用
// 事件处理函数中
export function onItemClick() {
  const currentItem = this.item;
  const currentIndex = this.index;
  console.log(currentItem.id, currentIndex);
}
```

### 远程数据源问题

```js
// 数据源请求失败
export function onError(err) {
  console.error('请求失败:', err);
  this.utils.toast({ title: '加载失败', type: 'error' });
}

// 在数据源配置中设置
function errorHandler(err) {
  console.error(err);
  return { success: false, message: err.message };
}
```

### 数组操作问题

```js
// ❌ 错误 - 直接修改 state 数组
this.state.list.push({ id: 1 });

// ✅ 正确 - 创建新数组
this.setState({
  list: [...this.state.list, { id: 1 }]
});

// ❌ 错误 - 直接删除
delete this.state.list[0];

// ✅ 正确 - 过滤创建新数组
this.setState({
  list: this.state.list.filter((_, i) => i !== 0)
});
```

### 表单提交问题

```js
// 提交前校验
export function onSubmit() {
  const nameField = this.$('name');
  const phoneField = this.$('phone');
  
  const nameValid = nameField.validate();
  const phoneValid = phoneField.validate();
  
  if (!nameValid || !phoneValid) {
    return;
  }
  
  // 继续提交逻辑
}
```

### 条件渲染问题

```js
// 组件未渲染时操作会报错
this.$('hiddenField').setValue('x'); // 隐藏组件可能不存在

// 使用前判断
const field = this.$('hiddenField');
if (field && field.getBehavior() !== 'HIDDEN') {
  field.setValue('x');
}
```

## 错误代码参考

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 500 | 服务器错误 | 检查后端服务或网络 |
| 401 | 未授权 | 登录状态失效，刷新页面 |
| 403 | 权限不足 | 检查应用权限设置 |
| 404 | 接口不存在 | 检查 API 路径 |
| 422 | 参数错误 | 检查请求参数格式 |

## 性能优化

### 减少 setState 调用

```js
// ❌ 多次调用
this.setState({ a: 1 });
this.setState({ b: 2 });
this.setState({ c: 3 });

// ✅ 合并调用
this.setState({ a: 1, b: 2, c: 3 });
```

### 使用数据源缓存

```js
// 启用数据源缓存
{
  "id": "userInfo",
  "options": {
    "cache": true,
    "cacheTimeout": 60000  // 缓存60秒
  }
}
```

### 避免频繁请求

```js
// 添加防抖
let timer;
export function onSearch(value) {
  clearTimeout(timer);
  timer = setTimeout(() => {
    this.dataSourceMap.search.load({ keyword: value });
  }, 300);
}
```
