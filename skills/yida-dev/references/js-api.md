# 完整 JS-API 参考

> **推荐**：使用组件别名代替系统生成的 fieldId，代码更易读。
> 
> - 别名：`this.$('userName').getValue()` 
> - fieldId：`this.$('textField_xxx').getValue()`（不推荐）
> 
> ⚠️ 组件别名功能仅支持**专业版/专属版**，免费版仍需使用 fieldId。

本文档提供宜搭自定义页面中可用的完整 JS-API。

## 目录

- [组件操作 API](#组件操作-api)
- [弹窗选择器](#弹窗选择器)
- [路由 API](#路由-api)
- [工具函数](#工具函数)
- [数据源 API](#数据源-api)
- [表单 API](#表单-api)

## 组件操作 API

### 获取组件值

```js
// 获取文本值
this.$('field').getValue();   // field 为组件别名

// 获取组件显示文本
this.$('field').getText();

// 获取多项选择值（多选、下拉多选）
this.$('field').getValues();
```

### 设置组件值

```js
// 设置值
this.$('field').setValue('hello');

// 设置多项选择值
this.$('field').setValues(['选项1', '选项2']);
```

### 组件属性操作

```js
// 获取属性
this.$('field').get('content');       // 文本内容
this.$('field').get('placeholder');  // 占位符
this.$('field').get('maxLength');     // 最大长度

// 设置属性
this.$('field').set('placeholder', '请输入');
this.$('field').set('maxLength', 100);
```

### 组件状态

```js
// 设置状态
this.$('field').setBehavior('READONLY');  // 只读
this.$('field').setBehavior('DISABLED');   // 禁用
this.$('field').setBehavior('HIDDEN');      // 隐藏
this.$('field').setBehavior('NORMAL');      // 正常

// 获取状态
this.$('field').getBehavior();
```

### 组件校验

```js
// 校验
const isValid = this.$('field').validate();

// 设置校验规则
this.$('field').setValidation([
  { type: 'required', message: '必填' },
  { type: 'maxLength', param: '10' },
  { type: 'minLength', param: '3' },
  { type: 'mobile', message: '手机号格式错误' },
  { type: 'email', message: '邮箱格式错误' },
  { type: 'url', message: 'URL格式错误' },
  { type: 'customValidate', param: (value) => {
    return /^\d*$/.test(value) || '只能输入数字';
  }}
]);

// 启用/禁用校验
this.$('field').disableValid();
this.$('field').enableValid();

// 获取校验错误信息
this.$('field').getErrors();
```

### 组件焦点与选中

```js
// 获取焦点
this.$('field').focus();

// 选中内容
this.$('field').select();

// 清除内容
this.$('field').clear();
```

### 重置组件

```js
// 重置为默认值
this.$('field').reset();

// 重置为指定值
this.$('field').reset('default value');
```

## 表单 API

### 整表校验

```js
// 校验所有组件
this.validateForm((errors) => {
  if (errors) {
    console.log('校验失败', errors);
  }
});

// 获取所有错误
const allErrors = this.getErrors();
```

### 表单数据

```js
// 获取表单数据
const formData = this.getFormData();

// 设置表单数据
this.setFormData({ field1: 'value1', field2: 'value2' });
```

## 工具函数 API

### 消息提示

```js
// 轻提示
this.utils.toast({ title: '成功', type: 'success' });
this.utils.toast({ title: '失败', type: 'error' });
this.utils.toast({ title: '警告', type: 'warning' });
this.utils.toast({ title: '信息', type: 'info' });

// 对话框
this.utils.dialog({
  type: 'alert',
  title: '提示',
  content: '内容'
});

this.utils.dialog({
  type: 'confirm',
  title: '确认',
  content: '确认操作吗？',
  onOk: () => { /* 确定 */ },
  onCancel: () => { /* 取消 */ }
});
```

### 路由跳转

```js
// 跳转页面
this.utils.router.push('/pageId');
this.utils.router.push('/pageId', { id: 1, name: 'test' });

// 替换当前页
this.utils.router.replace('/pageId');

// 返回
this.utils.router.back();

// 获取参数
const id = this.utils.router.getQuery('id');
const params = this.utils.router.getQueries();

// 获取路径
const path = this.utils.router.getPath();

// 获取页面 ID
const pageId = this.utils.router.getPageId();
```

### 用户信息

```js
// 获取用户 ID
const userId = this.utils.getLoginUserId();

// 获取用户名
const userName = this.utils.getLoginUserName();

// 获取用户信息
const userInfo = this.utils.getLoginUserInfo();
```

### 环境判断

```js
// 是否移动端
this.utils.isMobile();

// 是否 PC 端
this.utils.isPC();

// 是否钉钉端内
this.utils.isDingTalk();

// 是否提交页
this.utils.isSubmissionPage();

// 是否查看页
this.utils.isViewPage();

// 是否编辑页
this.utils.isEditPage();
```

### 格式化

```js
// 日期格式化
this.utils.formatter('date', new Date(), 'YYYY-MM-DD');
this.utils.formatter('date', new Date(), 'YYYY-MM-DD HH:mm:ss');

// 数字格式化
this.utils.formatter('money', 10000.99);
this.utils.formatter('number', 1234567, ',');

// 手机号格式化
this.utils.formatter('cnmobile', '15652988282');

// 脱敏处理
this.utils.formatter('mask', '15652988282', { type: 'mobile' });
this.utils.formatter('mask', '310101199001011234', { type: 'idCard' });
```

### 日期区间

```js
// 获取当天区间
const [dayStart, dayEnd] = this.utils.getDateTimeRange();

// 获取本月区间
const [monthStart, monthEnd] = this.utils.getDateTimeRange(new Date(), 'month');

// 获取本年区间
const [yearStart, yearEnd] = this.utils.getDateTimeRange(new Date(), 'year');
```

### 外部脚本

```js
// 动态加载 JS
this.utils.loadScript('https://example.com/script.js', () => {
  console.log('加载完成');
});

// 动态加载 CSS
this.utils.loadStyle('https://example.com/style.css');
```

### 图片与文件

```js
// 图片预览
this.utils.previewImage({
  current: 'https://example.com/image.jpg',
  images: ['https://example.com/1.jpg', 'https://example.com/2.jpg']
});

// 文件下载
this.utils.downloadFile('https://example.com/file.pdf', 'filename.pdf');

// 获取上传文件信息
this.$('uploadField').getFiles();
```

### 页面操作

```js
// 新开页面
this.utils.openPage('/pageId');
this.utils.openPage('/pageId', { id: 1 });

// 关闭当前页（iframe 场景）
this.utils.closePage();

// 刷新当前页
this.utils.refreshPage();

// 打印
this.utils.print();
```

### 本地存储

```js
// 存储
this.utils.setStorage('key', 'value');
this.utils.setStorage('key', { obj: 'value' });

// 读取
const value = this.utils.getStorage('key');

// 删除
this.utils.removeStorage('key');

// 清空
this.utils.clearStorage();
```

### 其他工具

```js// 防抖
this.utils.debounce(fn, 300);

// 节流
this.utils.throttle(fn, 300);

// 深拷贝
this.utils.cloneDeep(obj);

// 生成 UUID
this.utils.uuid();

// 获取语言
this.utils.getLocale();
```

## 数据源 API

### 调用数据源

```js
// 手动调用
this.dataSourceMap.apiName.load({ param: 'value' }).then(res => {
  console.log(res);
});

// 带错误处理
this.dataSourceMap.apiName.load({ param: 'value' })
  .then(res => { /* 成功 */ })
  .catch(err => { /* 失败 */ });

// 取消请求
const request = this.dataSourceMap.apiName.load({ param: 'value' });
request.cancel();
```

### 刷新数据源

```js
// 刷新所有自动加载的数据源
this.reloadDataSource();

// 刷新指定数据源
this.dataSourceMap.apiName.reload();
```

### 获取数据源状态

```js
const status = this.dataSourceMap.apiName.status;
// 'init' | 'loading' | 'success' | 'error'

const data = this.dataSourceMap.apiName.data;
const error = this.dataSourceMap.apiName.error;
```

## 生命周期

```js
// 页面加载完成
export function didMount() {
  // 初始化操作
}

// 页面卸载前
export function willUnmount() {
  // 清理操作
}

// 页面参数变化（路由参数变化时）
export function onRouteChange(query) {
  console.log('新参数:', query);
}
```

## 国际化

```js
// 获取翻译
this.utils.i18n('key');

// 获取当前语言
const locale = this.utils.getLocale();

// 切换语言
this.utils.setLocale('en-US');
```
