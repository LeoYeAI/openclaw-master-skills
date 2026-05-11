# HTML 卡片模板参考

在 `markdown.allowRawHTML: true` 且 DOMPurify 白名单已扩展的环境下，可直接在回复中使用以下模板。

## TextCard — 文字摘要

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:560px;font-family:-apple-system,sans-serif">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">标题</strong>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 12px">
  <p style="color:#374151;line-height:1.6;margin:0">正文内容。</p>
</div>
```

## ListCard — 列表要点

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:560px;font-family:-apple-system,sans-serif">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">列表标题</strong>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 12px">
  <div style="display:flex;flex-direction:column;gap:8px">
    <div style="display:flex;align-items:center;gap:8px">
      <span style="color:#22c55e;font-weight:bold">✓</span>
      <span style="color:#374151;font-size:14px">条目一</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px">
      <span style="color:#22c55e;font-weight:bold">✓</span>
      <span style="color:#374151;font-size:14px">条目二</span>
    </div>
  </div>
</div>
```

## DataCard — 键值对数据

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:560px;font-family:-apple-system,sans-serif">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">数据标题</strong>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 12px">
  <div style="display:flex;flex-direction:column">
    <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f9fafb;font-size:14px">
      <span style="color:#6b7280">键名</span>
      <span style="color:#1a1a2e;font-weight:500">值</span>
    </div>
    <div style="display:flex;justify-content:space-between;padding:8px 0;font-size:14px">
      <span style="color:#6b7280">键名2</span>
      <span style="color:#1a1a2e;font-weight:500">值2</span>
    </div>
  </div>
</div>
```

## StepsCard — 步骤流程

```html
<div style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:560px;font-family:-apple-system,sans-serif">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">步骤标题</strong>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 12px">
  <div style="display:flex;flex-direction:column;gap:14px">
    <div style="display:flex;gap:12px;align-items:flex-start">
      <div style="width:26px;height:26px;background:#5865f2;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0">1</div>
      <div>
        <div style="font-size:14px;font-weight:600;color:#1a1a2e">步骤标题</div>
        <div style="font-size:13px;color:#6b7280;margin-top:2px">步骤说明</div>
      </div>
    </div>
  </div>
</div>
```

## Badge 样式

```html
<span style="display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:500;background:#dcfce7;color:#16a34a">成功</span>
<span style="display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:500;background:#dbeafe;color:#2563eb">信息</span>
<span style="display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:500;background:#ffedd5;color:#ea580c">警告</span>
<span style="display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:500;background:#fee2e2;color:#dc2626">错误</span>
```
