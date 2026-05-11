# 校验规则说明

本文档详细说明了质效平台4.0中任务配置的校验规则逻辑。

## isTemplate 参数说明

`isTemplate` 是一个布尔值，用于区分当前操作是**创建模板**还是**创建流水线**：

| isTemplate 值 | 场景 | required 字段要求 |
|--------------|------|-----------------|
| `true` | 创建/编辑**模板任务** | **非必填** |
| `false` | 创建/编辑**流水线任务** | **必填** |

**校验公式**: `required = !isTemplate`

### 示例

```typescript
// isTemplate = false (创建流水线) → required = true (必填)
getCommonRule(false, '请输入任务名称', 'blur')
// 返回: [{ required: true, message: '请输入任务名称', trigger: 'blur' }]

// isTemplate = true (创建模板) → required = false (非必填)
getCommonRule(true, '请输入任务名称', 'blur')
// 返回: [{ required: false, message: '请输入任务名称', trigger: 'blur' }]
```

---

## 校验函数实现

### 1. getCommonRule - 通用校验函数

**位置**: `src/utils/validate.ts`

**函数签名**:
```typescript
export const getCommonRule = (isTemplate: boolean, message: string, trigger: string = 'blur') => {
  return [{ required: !isTemplate, message, trigger }]
}
```

**参数说明**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `isTemplate` | boolean | 是否为模板模式 |
| `message` | string | 校验失败时的错误提示信息 |
| `trigger` | string | 触发方式 (`blur`/`change`/`click`) |

**返回规则数组**:
```typescript
[
  {
    required: boolean,  // !isTemplate 的值
    message: string,      // 错误提示
    trigger: string     // 触发方式
  }
]
```

---

### 2. getWorkPathRule - 工作目录校验

**函数签名**:
```typescript
export const getWorkPathRule = (required: boolean, drawerData?: any) => {
  return [
    {
      required,
      message: drawerData?.data?.taskIsException ? '流水线源已变更，请修改' : '请输入工作目录',
      trigger: 'change'
    }
  ]
}
```

---

### 3. getArtifactPathRule - 制品路径校验

**函数签名**:
```typescript
export const getArtifactPathRule = (isTemplate: boolean) => {
  return [
    {
      required: !isTemplate,
      validator: validatePath(isTemplate),
      trigger: 'blur'
    }
  ]
}
```

**内部校验逻辑 (validatePath)**:
```typescript
const validatePath = (isTemplate: boolean) => {
  return (_rule: any, value: any, callback: any) => {
    const hasValue = value?.find((item: any) => item)
    // 1. 非模板模式下，制品路径不能为空
    if ((!value || !hasValue) && !isTemplate) {
      callback(new Error('请输入制品路径'))
      return
    }
    // 2. 制品路径不能以 "/" 开头
    const invalidPath = value?.find((item: any) => item && item.startsWith('/'))
    if (invalidPath) {
      callback(new Error('制品路径不能以"/"开头'))
      return
    }
    callback()
  }
}
```

---

### 4. getPackagedNameRule - 压缩包名称校验

**函数签名**:
```typescript
export const getPackagedNameRule = (isTemplate: boolean) => {
  return [
    {
      required: !isTemplate,
      validator: validatePackagedName(isTemplate),
      trigger: 'blur'
    }
  ]
}
```

**内部校验逻辑 (validatePackagedName)**:
```typescript
const validatePackagedName = (isTemplate: boolean) => {
  return (_: any, value: any, callback: any) => {
    // 1. 非模板模式下，压缩包名称不能为空
    if (!isTemplate && !value) {
      callback(new Error('请输入压缩包名称'))
      return
    }
    // 2. 格式校验：支持中文、大小写字母、数字、下划线"_"、横线"-"、括号"()"、大括号"{}"、半角点"."、"$"
    if (!/^[\u4e00-\u9fa5a-zA-Z0-9_().\-{}$]+$/.test(value) && value !== '') {
      callback(new Error('压缩包名称只允许输入中文，大小写字母、数字、下划线"_"、横线"-"、括号"()"、大括号"{}"、半角点"."、"$"'))
      return
    }
    callback()
  }
}
```

---

### 5. getBuildArgsRule - 构建参数校验

**函数签名**:
```typescript
export const getBuildArgsRule = (isTemplate: boolean, multiPlatform: string) => {
  const rules: any[] = []

  // 当开启多架构镜像时，需要校验
  if (multiPlatform === '1') {
    if (!isTemplate) {
      rules.push({
        required: true,
        message: '请输入更多构建参数',
        trigger: 'blur'
      })
    }

    rules.push({
      validator: validatePlatformArgs,
      trigger: 'blur'
    })
  }

  return rules
}
```

**多架构平台校验 (validatePlatformArgs)**:
```typescript
// 有效平台架构列表
const validPlatforms = [
  'linux/amd64', 'linux/arm64', 'linux/arm/v7', 'linux/arm/v6',
  'linux/386', 'linux/ppc64le', 'linux/s390x', 'linux/riscv64',
  'linux/mips64le', 'linux/mips64', 'windows/amd64', 'windows/arm64'
]

// 校验规则：
// 1. 必须包含 --platform 参数
// 2. 平台架构必须在有效列表中
// 3. 不允许重复的平台架构
```

---

### 6. getNodeCustomVersionRule - Node自定义版本校验

**函数签名**:
```typescript
export const getNodeCustomVersionRule = (isTemplate: boolean) => {
  return [
    {
      required: !isTemplate,
      validator: validateNpmCustomVersion(isTemplate),
      trigger: 'blur'
    }
  ]
}
```

**格式要求**: 只能输入数字和点号，如 `16.20.0`

---

## 触发方式说明

| trigger 值 | 说明 | 适用场景 |
|-----------|------|---------|
| `blur` | 失去焦点时触发 | 输入框、文本域 |
| `change` | 值变化时触发 | 下拉选择、开关 |
| `click` | 点击时触发 | 某些特殊控件 |

---

## 文档索引

各任务类型的具体校验规则请参考：

- [04-task-order-action.md](./04-task-order-action.md) - 执行命令
- [05-task-maven-build.md](./05-task-maven-build.md) - Maven构建
- [06-task-docker-build.md](./06-task-docker-build.md) - Docker构建
- [07-task-host-deploy.md](./07-task-host-deploy.md) - 主机部署
- [08-task-sae-image-update.md](./08-task-sae-image-update.md) - SAE镜像更新
- [09-task-sonar-qube.md](./09-task-sonar-qube.md) - SonarQube扫描
- [10-task-manual-review.md](./10-task-manual-review.md) - 人工审核
- [12-task-product-distribution.md](./12-task-product-distribution.md) - 制品分发
- [14-task-nodejs-build.md](./14-task-nodejs-build.md) - Node.js构建
- [15-task-python-build.md](./15-task-python-build.md) - Python构建
- [16-task-go-build.md](./16-task-go-build.md) - Go构建
- [17-task-cpp-build.md](./17-task-cpp-build.md) - C++构建
- [18-task-channel-build.md](./18-task-channel-build.md) - 渠道构建
