# Widget 可复用模式

生成 widget 时，按需引入以下模式。每个模式自包含，直接内联到 widget 文件中。

---

## 1. 可拖拽定位

让 widget 可被鼠标拖拽移动，位置自动存入 localStorage。

**使用场景**：用户希望自由调整 widget 位置

**要点**：
- 使用 `useRef` 获取 DOM 元素
- 纯 DOM 事件实现拖拽（mousedown/mousemove/mouseup）
- `className` 中不要设 `bottom/top/left/right`，由组件内 state 控制
- 必须移除 `pointer-events: none`

```jsx
import { React } from 'uebersicht'

export const refreshFrequency = false

export const className = `
  position: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
`

const WIDGET_ID = 'my-widget'

const DraggableWidget = () => {
  const { useState, useEffect, useRef, useCallback } = React
  const storageKey = `oc-pos-${WIDGET_ID}`
  const saved = JSON.parse(localStorage.getItem(storageKey) || 'null')
  const [pos, setPos] = useState(saved || { x: 200, y: 200 })
  const dragging = useRef(false)
  const offset = useRef({ x: 0, y: 0 })

  const onMouseDown = useCallback((e) => {
    dragging.current = true
    offset.current = { x: e.clientX - pos.x, y: e.clientY - pos.y }
    e.preventDefault()
  }, [pos])

  useEffect(() => {
    const onMove = (e) => {
      if (!dragging.current) return
      const next = { x: e.clientX - offset.current.x, y: e.clientY - offset.current.y }
      setPos(next)
      localStorage.setItem(storageKey, JSON.stringify(next))
    }
    const onUp = () => { dragging.current = false }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }, [])

  return (
    <div
      onMouseDown={onMouseDown}
      style={{
        position: 'fixed',
        left: pos.x,
        top: pos.y,
        cursor: 'grab',
        userSelect: 'none',
      }}
    >
      {/* widget 内容 */}
    </div>
  )
}

export const render = () => <DraggableWidget />
```

---

## 2. 状态持久化（localStorage）

widget 被 Übersicht 重新 mount 时恢复之前的状态，防止状态丢失。

**使用场景**：计时器、计数器、待办列表等需要持久状态的 widget

```jsx
// 封装 hook：用法和 useState 一致，自动读写 localStorage
const usePersistedState = (key, initial) => {
  const { useState, useEffect } = React
  const storageKey = `oc-${key}`
  const [value, setValue] = useState(() => {
    const saved = localStorage.getItem(storageKey)
    return saved !== null ? JSON.parse(saved) : initial
  })

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(value))
  }, [value])

  return [value, setValue]
}

// 用法示例
const Widget = () => {
  const [count, setCount] = usePersistedState('counter', 0)
  return <div onClick={() => setCount(c => c + 1)}>{count}</div>
}
```

---

## 3. Shell 输出安全解析

command 的 stdout 可能包含换行、空值、特殊字符。统一用分隔符 + 安全解析。

**使用场景**：所有使用 `command` 获取数据的 widget

```jsx
// command 中用 ||| 作分隔符
export const command = `
  echo "field1:$(some_command)"
  echo "field2:$(other_command)"
`

// 安全解析函数
const parseOutput = (raw, fields) => {
  const result = {}
  fields.forEach(f => { result[f] = '?' })
  if (!raw) return result
  raw.trim().split('\n').forEach(line => {
    const idx = line.indexOf(':')
    if (idx > -1) {
      const key = line.slice(0, idx).trim()
      const val = line.slice(idx + 1).trim()
      if (fields.includes(key)) result[key] = val
    }
  })
  return result
}

// 用法
export const render = ({ output }) => {
  const data = parseOutput(output, ['field1', 'field2'])
  return <div>{data.field1}</div>
}
```

---

## 4. 条件渲染 + 占位符

command 首次执行前 output 为空，避免闪烁或显示错误。

**使用场景**：所有 command-based widget

```jsx
export const render = ({ output, error }) => {
  if (error) return <div style={{ color: 'rgba(255,80,80,0.8)' }}>Error</div>
  if (!output) return <div style={{ opacity: 0.3 }}>Loading...</div>

  // 正常渲染
  return <div>{output.trim()}</div>
}
```

---
