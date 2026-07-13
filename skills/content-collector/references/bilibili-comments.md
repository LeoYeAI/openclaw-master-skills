# B站评论区浏览器提取方法

B站评论区使用 Web Components + Shadow DOM，需要逐层穿透才能读取。

## DOM 层级结构

```
document
└── bili-comments (shadowRoot)
    └── #feed
        └── bili-comment-thread-renderer × N (shadowRoot)
            ├── #comment → bili-comment-renderer (shadowRoot)
            │   ├── bili-comment-user-info (shadowRoot) → #user-name a → 用户名
            │   ├── #content → bili-rich-text (shadowRoot) → #contents span → 评论文本
            │   └── bili-comment-action-buttons-renderer (shadowRoot) → #like button span → 点赞数
            └── #replies → bili-comment-replies-renderer (shadowRoot)
                └── bili-comment-renderer × N → 子评论（结构同上）
```

## 提取 JS（在 browser evaluate 中运行）

```javascript
(() => {
  function getCommentText(rendererEl) {
    const sr = rendererEl?.shadowRoot;
    if (!sr) return { user: '', content: '', likes: '0' };
    const richText = sr.querySelector('bili-rich-text');
    const rtSr = richText?.shadowRoot;
    const contentP = rtSr?.querySelector('#contents');
    const spans = contentP?.querySelectorAll('span') || [];
    let text = '';
    spans.forEach(s => text += s.textContent);
    const userInfo = sr.querySelector('bili-comment-user-info');
    const uSr = userInfo?.shadowRoot;
    const userName = uSr?.querySelector('#user-name a')?.textContent?.trim() || '';
    const actionBtns = sr.querySelector('bili-comment-action-buttons-renderer');
    const aSr = actionBtns?.shadowRoot;
    const likes = aSr?.querySelector('#like button span')?.textContent?.trim() || '0';
    return { user: userName, content: text.trim(), likes };
  }

  const biliComments = document.querySelector('bili-comments');
  const sr1 = biliComments?.shadowRoot;
  if (!sr1) return JSON.stringify({ error: 'no comments component' });

  const threads = sr1.querySelectorAll('bili-comment-thread-renderer');
  const results = [];
  threads.forEach(thread => {
    const sr2 = thread.shadowRoot;
    if (!sr2) return;
    const mainComment = getCommentText(sr2.querySelector('#comment'));
    if (!mainComment.content) return;
    const repliesRenderer = sr2.querySelector('bili-comment-replies-renderer');
    const rSr = repliesRenderer?.shadowRoot;
    const replyRenderers = rSr?.querySelectorAll('bili-comment-renderer') || [];
    const subReplies = [];
    replyRenderers.forEach(rr => {
      const sub = getCommentText(rr);
      if (sub.content) subReplies.push(sub);
    });
    results.push({ ...mainComment, sub_replies: subReplies });
  });
  return JSON.stringify({ count: results.length, items: results });
})()
```

## 使用步骤

1. 用 `browser` 工具启动浏览器（需已登录B站）
2. 导航到视频页面
3. 滚动到评论区（`window.scrollTo(0, 3000)`），等待3秒
4. 运行上述 JS 提取评论
5. 可多次滚动 + 提取获得更多评论

## 注意事项

- 未登录状态评论区可能不加载
- 默认加载约20条，滚动可触发更多
- B站的 shadow DOM 结构可能随版本更新变化
