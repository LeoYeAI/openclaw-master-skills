# Frontend 领域专业知识库

> 创建日期: 2025-01-17
> 知识来源: 深度研究 + 行业最佳实践
> 适用场景: 优化/创建前端开发相关 Skills

---

## 目录

1. [核心概念](#1-核心概念)
2. [现代化开发模式](#2-现代化开发模式)
3. [组件设计原则](#3-组件设计原则)
4. [状态管理](#4-状态管理)
5. [性能优化](#5-性能优化)
6. [常见陷阱](#6-常见陷阱)
7. [可访问性](#7-可访问性a11y)
8. [工具与技术](#8-工具与技术)

---

## 1. 核心概念

### 1.1 前端三要素

来源: [MDN Web Docs](https://developer.mozilla.org/)

**前端 = HTML (结构) + CSS (表现) + JavaScript (行为)**

| 要素 | 职责 | 关键技术 |
|------|------|----------|
| **HTML** | 内容结构化 | 语义化标签、可访问性、SEO |
| **CSS** | 视觉表现 | 布局、动画、响应式设计 |
| **JavaScript** | 交互行为 | DOM 操作、事件处理、数据通信 |

### 1.2 现代前端架构

```
┌─────────────────────────────────────────┐
│  现代前端架构                      │
├─────────────────────────────────────────┤
│  展示层 → 逻辑层 → 数据层          │
│  (UI)     (State)   (API)        │
│                                     │
│  特点: 组件化、声明式、响应式      │
└─────────────────────────────────────────┘
```

---

## 2. 现代化开发模式

### 2.1 框架选择原则

| 框架 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| **React** | 复杂 SPA、大型团队 | 生态丰富、灵活 | 学习曲线陡 |
| **Vue** | 快速开发、中小型项目 | 易学、模板语法清晰 | 生态相对较小 |
| **Svelte** | 性能敏感、轻量级 | 无虚拟 DOM、编译优化 | 生态较新 |
| **Angular** | 企业级应用、大团队 | 完整框架、TypeScript 支持 | 过重、学习曲线陡 |

### 2.2 CSR vs SSR

| 方案 | 特点 | 适用场景 | 工具 |
|------|------|----------|------|
| **CSR (Client-Side Rendering)** | 浏览器渲染 | SPA、后台管理 | React Router, Vue Router |
| **SSR (Server-Side Rendering)** | 服务端渲染 | SEO 要求高 | Next.js, Nuxt.js |
| **SSG (Static Site Generation)** | 构建时生成 | 博客、文档站 | Next.js, Hugo |

### 2.3 Build Tools

| 工具 | 生态 | 特点 |
|------|------|------|
| **Vite** | 多框架 | 极快、热更新、简单配置 |
| **Webpack** | 多框架 | 配置强大、生态成熟 |
| **esbuild** | 多框架 | 极速、Go 编写 |
| **Turbopack** | 多框架 (Next.js 15+) | Rust 编写、增量构建 |

---

## 3. 组件设计原则

### 3.1 组件设计最佳实践

来源: [React Docs: Thinking in React](https://react.dev/learn/thinking-in-react)

**核心原则**：
1. **单一职责** - 一个组件只做一件事
2. **可复用性** - 通过 props 自定义
3. **组合优于继承** - 使用组合模式
4. **受控 vs 非受控** - 明确数据流

### 3.2 组件模式

#### 3.2.1 容器组件 vs 展示组件

```javascript
// ❌ 错误：混合逻辑和视图
function UserList({ users, onFetch }) {
  useEffect(() => onFetch(), []);
  return <ul>{users.map(u => <li>{u.name}</li>)}</ul>;
}

// ✅ 正确：分离容器和展示
// 展示组件
function UserListView({ users }) {
  return <ul>{users.map(u => <li>{u.name}</li>)}</ul>;
}

// 容器组件
function UserListContainer() {
  const [users, setUsers] = useState([]);
  const fetchUsers = () => api.getUsers().then(setUsers);
  
  useEffect(() => fetchUsers(), []);
  
  return <UserListView users={users} />;
}
```

#### 3.2.2 高阶组件 (HOC) vs Hooks

来源: [React Hooks vs HOC](https://react.dev/reference/react/hooks)

| 模式 | 用途 | 现状 |
|------|------|------|
| HOC | 复用组件逻辑 | 已被 Hooks 替代 |
| Hooks | 复用状态逻辑 | ✅ 推荐 |
| Render Props | 复用渲染逻辑 | 特定场景使用 |

### 3.3 Props 设计

**良好 Props 设计原则**：
- 明确类型定义
- 提供默认值
- 避免 props drilling
- 使用 TypeScript/PropTypes

```typescript
// ✅ 好的 Props 设计
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
  children: ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  onClick,
  children
}) => {
  // 实现逻辑
};
```

---

## 4. 状态管理

### 4.1 状态层级

```
┌─────────────────────────────────────────┐
│  状态管理决策树                      │
├─────────────────────────────────────────┤
│  本地组件状态 → useState/useReducer │
│  跨组件状态 → Context API / Zustand  │
│  全局复杂状态 → Redux / XState    │
│  服务器状态 → React Query / SWR   │
└─────────────────────────────────────────┘
```

### 4.2 状态管理方案对比

| 方案 | 复杂度 | 适用场景 | 学习成本 |
|------|--------|----------|----------|
| **useState** | 低 | 单个组件状态 | 低 |
| **useReducer** | 中 | 复杂组件状态逻辑 | 中 |
| **Context API** | 中-高 | 跨组件数据 | 中 |
| **Zustand** | 中 | 轻量级全局状态 | 低 |
| **Redux Toolkit** | 高 | 大型应用全局状态 | 高 |
| **Jotai** | 中 | 细粒度状态更新 | 中 |

### 4.3 服务器状态管理

来源: [React Query Documentation](https://tanstack.com/query/latest)

**问题**：手动管理服务器状态容易出错。

**解决方案**：使用数据获取库

| 库 | 特点 |
|------|------|
| **React Query** | 缓存、自动重试、乐观更新 |
| **SWR** | 轻量、实时数据同步 |
| **Apollo Client** | GraphQL 专用、状态管理 |

---

## 5. 性能优化

### 5.1 渲染性能

来源: [React Performance Optimization](https://react.dev/learn/render-and-commit)

**核心问题**：避免不必要的重渲染。

| 优化技术 | 原理 | 适用场景 |
|----------|------|----------|
| **memo** | 浅比较 props | 纯展示组件 |
| **useMemo** | 缓存计算结果 | 昂贵计算 |
| **useCallback** | 稳定函数引用 | 传递给子组件的回调 |
| **虚拟列表** | 只渲染可见项 | 长列表 |

```javascript
// ❌ 错误：每次渲染都重新创建函数
function Parent() {
  return <Child onClick={() => doSomething()} />;
}

// ✅ 正确：使用 useCallback 稳定函数
function Parent() {
  const handleClick = useCallback(() => doSomething(), [/* deps */]);
  return <Child onClick={handleClick} />;
}
```

### 5.2 加载性能

| 优化项 | 技术 | 效果 |
|--------|------|------|
| **代码分割** | React.lazy, Suspense | 减少初始包体积 |
| **懒加载** | 动态 import | 按需加载 |
| **预加载** | `<link rel="preload">` | 提前加载关键资源 |
| **图片优化** | WebP, 响应式图片, 懒加载 | 减少图片体积 |

### 5.3 运行时性能

```javascript
// ❌ 错误：N+1 查询
async function fetchPosts() {
  const posts = await api.getPosts();
  for (const post of posts) {
    post.author = await api.getUser(post.authorId); // N+1 查询
  }
  return posts;
}

// ✅ 正确：批量查询
async function fetchPosts() {
  const posts = await api.getPosts();
  const authorIds = [...new Set(posts.map(p => p.authorId))];
  const authors = await api.getUsers(authorIds); // 批量查询
  return posts.map(post => ({
    ...post,
    author: authors.find(a => a.id === post.authorId)
  }));
}
```

---

## 6. 常见陷阱

### 6.1 React 特定陷阱

| 陷阱 | 表现 | 解决 |
|------|------|------|
| useEffect 依赖缺失 | 闭包捕获旧值 | 正确列出依赖或移除依赖 |
| setState 异步 | setState 后立即读取旧值 | 使用函数式 setState |
| Props Drilling | props 层层传递 | 使用 Context 或状态管理库 |
| Key 属性错误 | 列表更新异常 | 使用稳定的唯一 key |

```javascript
// ❌ 错误：setState 异步问题
function Counter() {
  const [count, setCount] = useState(0);
  
  const handleClick = () => {
    setCount(count + 1);
    console.log(count); // 还是旧值
  };
}

// ✅ 正确：使用函数式更新
function Counter() {
  const [count, setCount] = useState(0);
  
  const handleClick = () => {
    setCount(c => c + 1);
    console.log(count); // 注意：这里还是旧值
  };
}
```

### 6.2 CSS 陷阱

| 陷阱 | 表现 | 解决 |
|------|------|------|
| **z-index 层级混乱** | 元素不按预期显示 | 建立层叠上下文 |
| **Flexbox 不居中** | 对齐问题 | 理解 align-items/justify-content |
| **响应式断点混乱** | 布局错乱 | 统一断点系统 |
| **过度使用 !important** | 样式难以覆盖 | 优化选择器优先级 |

### 6.3 通用陷阱

| 陷阱 | 表现 | 解决 |
|------|------|------|
| **不处理错误边界** | 整个应用崩溃 | 使用 Error Boundary |
| **内存泄漏** | 性能下降 | 清理订阅、定时器、事件监听器 |
| **XSS 风险** | 注入攻击 | 避免直接插入 HTML，使用 React/DOM API |
| **硬编码环境变量** | 部署困难 | 使用 .env 文件 |

---

## 7. 可访问性 (a11y)

### 7.1 WCAG 标准

来源: [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

**四大原则**：
- **Perceivable (可感知)** - 信息可感知
- **Operable (可操作)** - 可用键盘操作
- **Understandable (可理解)** - 内容清晰易懂
- **Robust (健壮性)** - 兼容辅助技术

### 7.2 可访问性检查清单

```markdown
## A11y Checklist

### 语义 HTML
- [ ] 使用正确的 HTML 标签 (nav, main, article, section)
- [ ] 图片有 alt 文本
- [ ] 表单有 label 关联
- [ ] 链接有描述性文本

### 键盘导航
- [ ] 所有交互元素可通过键盘访问
- [ ] 有焦点指示器
- [ ] Tab 顺序合理
- [ ] 没有键盘陷阱

### 颜色对比
- [ ] 文本和背景对比度 ≥ 4.5:1
- [ ] 大文本对比度 ≥ 3:1
- [ ] 不仅用颜色传达信息

### 屏幕阅读器
- [ ] 使用 ARIA 属性 (aria-label, aria-live)
- [ ] 动态内容有 aria-live
- [ ] 表单错误有 aria-describedby
```

---

## 8. 工具与技术

### 8.1 开发工具

| 类别 | 工具 | 用途 |
|------|------|------|
| **浏览器 DevTools** | Chrome/Firefox DevTools | 调试、性能分析 |
| **React DevTools** | Chrome 扩展 | 组件树、状态检查 |
| **Vue DevTools** | Chrome 扩展 | 组件检查、Vuex 调试 |
| **Storybook** | 独立开发环境 | 组件文档、可视化测试 |

### 8.2 性能工具

| 工具 | 用途 |
|------|------|
| **Lighthouse** | 性能审计、可访问性检查 |
| **WebPageTest** | 多地性能测试 |
| **Bundle Analyzer** | 打包体积分析 |
| **React Profiler** | 渲染性能分析 |

### 8.3 类型安全

| 工具 | 特点 |
|------|------|
| **TypeScript** | 静态类型、IDE 支持 |
| **Zod** | 运行时类型验证 |
| **PropTypes** | React 运行时类型检查 |

### 8.4 测试工具

| 类别 | 工具 | 框架 |
|------|------|------|
| **单元测试** | Jest, Vitest | React, Vue |
| **组件测试** | Testing Library | React, Vue |
| **E2E 测试** | Cypress, Playwright | 通用 |

---

## 参考资料

- [React Documentation](https://react.dev/) - React 官方文档
- [Vue Documentation](https://vuejs.org/) - Vue 官方文档
- [MDN Web Docs](https://developer.mozilla.org/) - Web 标准
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) - 可访问性标准
- [React Query](https://tanstack.com/query/latest) - 服务器状态管理
- [Zustand](https://zustand-demo.pmnd.rs/) - 轻量级状态管理
- [Storybook](https://storybook.js.org/) - 组件文档
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先 CSS 框架
- [Web Performance](https://web.dev/performance/) - 性能优化指南
