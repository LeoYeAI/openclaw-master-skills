# JSX 组件

JSX 组件允许通过 ES6+ JSX 代码渲染完全自定义的内容，用于纯展示场景。

## 基本用法

在组件属性中设置 `render` 函数：

```js
function render(me, state, data) {
  return <div>Hello World</div>;
}
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `me` | 组件实例，可用 `me.props` 获取属性 |
| `state` | 页面全局状态 |
| `data` | 数据源数据 |

## 示例：渲染表格

```js
function render(me, state, data) {
  var columnsMap = data.fields.map(item => item.domainCode + '-' + item.name);
  
  var header = data.fields.map(item => { 
    return <td>{`${item.domainName}-${item.displayName}`}</td> 
  });
  
  var body = data.datas.map((item, index) => { 
    return (
      <tr className={index % 2 === 1 ? "even" : ""}>
        {columnsMap.map(key => <td>{item[key]}</td>)}
      </tr>
    );
  });

  return (
    <table className="vc-jsx-table">
      <thead><tr>{header}</tr></thead>
      <tbody>{body}</tbody>
    </table>
  );
}
```

## 支持的 JSX 特性

- 数组映射 `map`
- 条件渲染 `if/else`
- 模板字符串
- 箭头函数
- 解构赋值
- CSS 类名动态绑定

## 样式

```js
function render(me, state, data) {
  return (
    <div style={{ padding: '16px', background: '#fff' }}>
      <h2 style={{ color: '#333', fontSize: '16px' }}>标题</h2>
    </div>
  );
}
```

## 版本要求

专业版及以上可用。
