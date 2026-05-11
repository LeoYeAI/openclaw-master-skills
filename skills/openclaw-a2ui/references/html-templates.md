# A2UI HTML 卡片模板库

所有模板均使用**内联样式**，兼容 webchat DOMPurify 白名单（`ui-config.json` 已扩展）。
输出时包在 ` ```html ``` ` 代码块中，webchat 会自动渲染。

---

## 设计规范

```
卡片背景: #ffffff
边框圆角: 12px
阴影: 0 2px 12px rgba(0,0,0,0.08)
主色: #5865f2（蓝紫）
成功色: #22c55e
警告色: #f59e0b
错误色: #ef4444
信息色: #3b82f6
字体: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
标题颜色: #1a1a2e
正文颜色: #374151
说明颜色: #6b7280
分割线: #f0f0f0
最大宽度: 600px
```

---

## text-card（文字摘要卡片）

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5865f2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
    <strong style="font-size:16px;color:#1a1a2e">标题文字</strong>
  </div>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 14px">
  <p style="color:#374151;line-height:1.7;margin:0;font-size:14px">正文内容，支持多行。可以是摘要、结论、说明等任何文字性内容。</p>
</div>
```

---

## list-card（列表卡片）

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">要点列表</strong>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 14px">
  <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px">
    <li style="display:flex;align-items:flex-start;gap:10px">
      <svg style="flex-shrink:0;margin-top:2px" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      <span style="color:#374151;font-size:14px;line-height:1.5">第一个要点内容</span>
    </li>
    <li style="display:flex;align-items:flex-start;gap:10px">
      <svg style="flex-shrink:0;margin-top:2px" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      <span style="color:#374151;font-size:14px;line-height:1.5">第二个要点内容</span>
    </li>
    <li style="display:flex;align-items:flex-start;gap:10px">
      <svg style="flex-shrink:0;margin-top:2px" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      <span style="color:#374151;font-size:14px;line-height:1.5">第三个要点内容</span>
    </li>
  </ul>
</div>
```

**带 emoji 图标版：**
```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">✨ 列表标题</strong>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 14px">
  <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px">
    <li style="display:flex;align-items:flex-start;gap:8px;padding:8px;background:#f8fafc;border-radius:8px">
      <span style="font-size:16px">🚀</span>
      <span style="color:#374151;font-size:14px;line-height:1.5">要点一</span>
    </li>
    <li style="display:flex;align-items:flex-start;gap:8px;padding:8px;background:#f8fafc;border-radius:8px">
      <span style="font-size:16px">⚡</span>
      <span style="color:#374151;font-size:14px;line-height:1.5">要点二</span>
    </li>
  </ul>
</div>
```

---

## data-card（键值对数据卡片）

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">数据信息</strong>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 4px">
  <div style="display:flex;flex-direction:column">
    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f9fafb">
      <span style="color:#6b7280;font-size:13px">状态</span>
      <span style="background:#dcfce7;color:#16a34a;font-size:12px;padding:2px 8px;border-radius:12px;font-weight:500">正常</span>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f9fafb">
      <span style="color:#6b7280;font-size:13px">版本</span>
      <span style="color:#1a1a2e;font-weight:500;font-size:14px">v1.2.3</span>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f9fafb">
      <span style="color:#6b7280;font-size:13px">更新时间</span>
      <span style="color:#1a1a2e;font-size:14px">2026-03-09</span>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0">
      <span style="color:#6b7280;font-size:13px">负责人</span>
      <span style="color:#1a1a2e;font-size:14px">张三</span>
    </div>
  </div>
</div>
```

**带 badge 状态版：**
- `#dcfce7` / `#16a34a` → 成功/正常
- `#fef3c7` / `#d97706` → 警告
- `#fee2e2` / `#dc2626` → 错误
- `#dbeafe` / `#2563eb` → 信息

---

## code-card（代码卡片）

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
    <div style="display:flex;align-items:center;gap:8px">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
      <span style="color:#374151;font-size:14px;font-weight:500">示例代码</span>
    </div>
    <span style="background:#f3f4f6;color:#6b7280;font-size:12px;padding:2px 8px;border-radius:6px;font-family:monospace">python</span>
  </div>
  <pre style="background:#1e1e2e;border-radius:8px;padding:16px;margin:0;overflow-x:auto"><code style="color:#cdd6f4;font-family:'Fira Code','Cascadia Code',Consolas,monospace;font-size:13px;line-height:1.6">def hello_a2ui():
    print("Hello, A2UI! 🎉")
    return True

hello_a2ui()</code></pre>
</div>
```

---

## steps-card（步骤流程卡片）

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:16px">操作步骤</strong>
  <div style="display:flex;flex-direction:column;gap:0">
    <div style="display:flex;gap:16px">
      <div style="display:flex;flex-direction:column;align-items:center">
        <div style="width:28px;height:28px;border-radius:50%;background:#5865f2;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;flex-shrink:0">1</div>
        <div style="width:2px;background:#e5e7eb;flex:1;margin:4px 0;min-height:20px"></div>
      </div>
      <div style="padding-bottom:16px">
        <div style="font-weight:500;color:#1a1a2e;font-size:14px;margin-bottom:4px">第一步标题</div>
        <div style="color:#6b7280;font-size:13px;line-height:1.5">第一步详细说明文字</div>
      </div>
    </div>
    <div style="display:flex;gap:16px">
      <div style="display:flex;flex-direction:column;align-items:center">
        <div style="width:28px;height:28px;border-radius:50%;background:#5865f2;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;flex-shrink:0">2</div>
        <div style="width:2px;background:#e5e7eb;flex:1;margin:4px 0;min-height:20px"></div>
      </div>
      <div style="padding-bottom:16px">
        <div style="font-weight:500;color:#1a1a2e;font-size:14px;margin-bottom:4px">第二步标题</div>
        <div style="color:#6b7280;font-size:13px;line-height:1.5">第二步详细说明文字</div>
      </div>
    </div>
    <div style="display:flex;gap:16px">
      <div style="display:flex;flex-direction:column;align-items:center">
        <div style="width:28px;height:28px;border-radius:50%;background:#22c55e;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;flex-shrink:0">✓</div>
      </div>
      <div>
        <div style="font-weight:500;color:#1a1a2e;font-size:14px;margin-bottom:4px">完成</div>
        <div style="color:#6b7280;font-size:13px;line-height:1.5">所有步骤完成！</div>
      </div>
    </div>
  </div>
</div>
```

---

## table-card（表格卡片）

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">数据表格</strong>
  <div style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead>
        <tr style="background:#f8fafc">
          <th style="text-align:left;padding:10px 12px;color:#6b7280;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;border-bottom:2px solid #e5e7eb">名称</th>
          <th style="text-align:left;padding:10px 12px;color:#6b7280;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;border-bottom:2px solid #e5e7eb">状态</th>
          <th style="text-align:right;padding:10px 12px;color:#6b7280;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.05em;border-bottom:2px solid #e5e7eb">数量</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:10px 12px;color:#374151;border-bottom:1px solid #f3f4f6">项目 A</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6"><span style="background:#dcfce7;color:#16a34a;font-size:12px;padding:2px 8px;border-radius:12px">正常</span></td>
          <td style="padding:10px 12px;color:#374151;text-align:right;border-bottom:1px solid #f3f4f6">42</td>
        </tr>
        <tr>
          <td style="padding:10px 12px;color:#374151;border-bottom:1px solid #f3f4f6">项目 B</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6"><span style="background:#fef3c7;color:#d97706;font-size:12px;padding:2px 8px;border-radius:12px">警告</span></td>
          <td style="padding:10px 12px;color:#374151;text-align:right;border-bottom:1px solid #f3f4f6">7</td>
        </tr>
        <tr>
          <td style="padding:10px 12px;color:#374151">项目 C</td>
          <td style="padding:10px 12px"><span style="background:#fee2e2;color:#dc2626;font-size:12px;padding:2px 8px;border-radius:12px">错误</span></td>
          <td style="padding:10px 12px;color:#374151;text-align:right">0</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

---

## image-card（图片卡片）

```html
<div style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <img src="https://example.com/photo.jpg" alt="图片描述" style="width:100%;display:block;max-height:300px;object-fit:cover">
  <div style="padding:14px 16px">
    <p style="color:#374151;font-size:13px;margin:0;line-height:1.5">图片说明文字放在这里</p>
  </div>
</div>
```

**多图画廊版：**
```html
<div style="background:#fff;border-radius:12px;padding:16px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">图片集</strong>
  <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px">
    <img src="https://example.com/1.jpg" alt="图1" style="width:100%;border-radius:8px;aspect-ratio:4/3;object-fit:cover">
    <img src="https://example.com/2.jpg" alt="图2" style="width:100%;border-radius:8px;aspect-ratio:4/3;object-fit:cover">
    <img src="https://example.com/3.jpg" alt="图3" style="width:100%;border-radius:8px;aspect-ratio:4/3;object-fit:cover">
    <img src="https://example.com/4.jpg" alt="图4" style="width:100%;border-radius:8px;aspect-ratio:4/3;object-fit:cover">
  </div>
</div>
```

---

## video-card（视频卡片）

> `<video>` 和 `<iframe>` 在 webchat 中被过滤，用封面图+链接方式呈现。

```html
<div style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <div style="position:relative">
    <img src="https://example.com/thumbnail.jpg" alt="视频封面" style="width:100%;display:block;max-height:280px;object-fit:cover">
    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.6);border-radius:50%;width:56px;height:56px;display:flex;align-items:center;justify-content:center">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="#fff"><polygon points="5 3 19 12 5 21 5 3"/></svg>
    </div>
  </div>
  <div style="padding:14px 16px">
    <strong style="color:#1a1a2e;font-size:15px;display:block;margin-bottom:6px">视频标题</strong>
    <p style="color:#6b7280;font-size:13px;margin:0 0 10px;line-height:1.5">视频简介描述文字</p>
    <a href="https://example.com/video" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;background:#5865f2;color:#fff;text-decoration:none;padding:7px 14px;border-radius:8px;font-size:13px;font-weight:500">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="#fff"><polygon points="5 3 19 12 5 21 5 3"/></svg>
      点击播放
    </a>
  </div>
</div>
```

---

## composite-card（组合卡片）

```html
<div style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <img src="https://example.com/hero.jpg" alt="封面图" style="width:100%;display:block;max-height:200px;object-fit:cover">
  <div style="padding:20px">
    <h3 style="margin:0 0 8px;color:#1a1a2e;font-size:18px">主标题</h3>
    <p style="color:#6b7280;font-size:14px;line-height:1.6;margin:0 0 16px">这是一段描述性文字，介绍内容的核心价值和特点。支持多行显示。</p>
    <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 14px">
    <ul style="list-style:none;padding:0;margin:0 0 16px;display:flex;flex-direction:column;gap:8px">
      <li style="display:flex;align-items:center;gap:8px">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        <span style="color:#374151;font-size:14px">特性一：高性能</span>
      </li>
      <li style="display:flex;align-items:center;gap:8px">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        <span style="color:#374151;font-size:14px">特性二：易使用</span>
      </li>
      <li style="display:flex;align-items:center;gap:8px">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        <span style="color:#374151;font-size:14px">特性三：可扩展</span>
      </li>
    </ul>
    <div style="display:flex;justify-content:flex-end">
      <a href="#" style="background:#5865f2;color:#fff;text-decoration:none;padding:8px 16px;border-radius:8px;font-size:13px;font-weight:500">了解更多 →</a>
    </div>
  </div>
</div>
```

---

## progress-card（进度卡片）

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:16px">进度概览</strong>
  <div style="display:flex;flex-direction:column;gap:14px">
    <div>
      <div style="display:flex;justify-content:space-between;margin-bottom:6px">
        <span style="color:#374151;font-size:13px">任务 A</span>
        <span style="color:#6b7280;font-size:13px">75%</span>
      </div>
      <div style="background:#f3f4f6;border-radius:999px;height:8px;overflow:hidden">
        <div style="background:#5865f2;height:100%;width:75%;border-radius:999px"></div>
      </div>
    </div>
    <div>
      <div style="display:flex;justify-content:space-between;margin-bottom:6px">
        <span style="color:#374151;font-size:13px">任务 B</span>
        <span style="color:#6b7280;font-size:13px">40%</span>
      </div>
      <div style="background:#f3f4f6;border-radius:999px;height:8px;overflow:hidden">
        <div style="background:#22c55e;height:100%;width:40%;border-radius:999px"></div>
      </div>
    </div>
    <div>
      <div style="display:flex;justify-content:space-between;margin-bottom:6px">
        <span style="color:#374151;font-size:13px">任务 C</span>
        <span style="color:#6b7280;font-size:13px">92%</span>
      </div>
      <div style="background:#f3f4f6;border-radius:999px;height:8px;overflow:hidden">
        <div style="background:#f59e0b;height:100%;width:92%;border-radius:999px"></div>
      </div>
    </div>
  </div>
</div>
```

---

## tabs-card（标签页卡片）

> webchat 不支持 JS 事件，用折叠 `<details>` 模拟标签页效果。

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">标签页内容</strong>
  <details open style="border:1px solid #e5e7eb;border-radius:8px;margin-bottom:6px;overflow:hidden">
    <summary style="padding:10px 14px;cursor:pointer;background:#f8fafc;color:#374151;font-size:14px;font-weight:500;list-style:none;display:flex;align-items:center;gap:6px">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
      标签一：概览
    </summary>
    <div style="padding:14px;color:#374151;font-size:14px;line-height:1.6">
      标签一的内容，展开显示。
    </div>
  </details>
  <details style="border:1px solid #e5e7eb;border-radius:8px;margin-bottom:6px;overflow:hidden">
    <summary style="padding:10px 14px;cursor:pointer;background:#f8fafc;color:#374151;font-size:14px;font-weight:500;list-style:none;display:flex;align-items:center;gap:6px">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
      标签二：详情
    </summary>
    <div style="padding:14px;color:#374151;font-size:14px;line-height:1.6">
      标签二的内容，点击展开显示。
    </div>
  </details>
</div>
```

---

## stats-card（统计数字卡片）

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:16px">统计概览</strong>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
    <div style="background:#f0f4ff;border-radius:10px;padding:14px;text-align:center">
      <div style="font-size:24px;font-weight:700;color:#5865f2;margin-bottom:4px">128</div>
      <div style="font-size:12px;color:#6b7280">总请求数</div>
    </div>
    <div style="background:#f0fdf4;border-radius:10px;padding:14px;text-align:center">
      <div style="font-size:24px;font-weight:700;color:#22c55e;margin-bottom:4px">99.2%</div>
      <div style="font-size:12px;color:#6b7280">成功率</div>
    </div>
    <div style="background:#fffbeb;border-radius:10px;padding:14px;text-align:center">
      <div style="font-size:24px;font-weight:700;color:#f59e0b;margin-bottom:4px">42ms</div>
      <div style="font-size:12px;color:#6b7280">平均延迟</div>
    </div>
  </div>
</div>
```

---

## alert-card（提示/警告卡片）

```html
<!-- 成功 -->
<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:12px;padding:16px;max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0;display:flex;gap:12px;align-items:flex-start">
  <svg style="flex-shrink:0;margin-top:1px" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>
  <div>
    <strong style="color:#15803d;font-size:14px;display:block;margin-bottom:4px">操作成功</strong>
    <span style="color:#166534;font-size:13px;line-height:1.5">详细说明文字</span>
  </div>
</div>

<!-- 警告 -->
<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:12px;padding:16px;max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0;display:flex;gap:12px;align-items:flex-start">
  <svg style="flex-shrink:0;margin-top:1px" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
  <div>
    <strong style="color:#92400e;font-size:14px;display:block;margin-bottom:4px">注意事项</strong>
    <span style="color:#78350f;font-size:13px;line-height:1.5">警告详细内容</span>
  </div>
</div>

<!-- 错误 -->
<div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:12px;padding:16px;max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0;display:flex;gap:12px;align-items:flex-start">
  <svg style="flex-shrink:0;margin-top:1px" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
  <div>
    <strong style="color:#991b1b;font-size:14px;display:block;margin-bottom:4px">发生错误</strong>
    <span style="color:#7f1d1d;font-size:13px;line-height:1.5">错误详细信息</span>
  </div>
</div>

<!-- 信息 -->
<div style="background:#eff6ff;border:1px solid #93c5fd;border-radius:12px;padding:16px;max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0;display:flex;gap:12px;align-items:flex-start">
  <svg style="flex-shrink:0;margin-top:1px" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
  <div>
    <strong style="color:#1e40af;font-size:14px;display:block;margin-bottom:4px">提示信息</strong>
    <span style="color:#1e3a8a;font-size:13px;line-height:1.5">信息详细内容</span>
  </div>
</div>
```
