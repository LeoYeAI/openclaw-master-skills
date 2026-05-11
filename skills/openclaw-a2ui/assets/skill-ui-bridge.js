(function () {
  'use strict';

  var DONE_ATTR   = 'data-sui-done';
  var DEBOUNCE_MS = 320;

  var allowedTags  = new Set();
  var allowedAttrs = new Set();
  var ready = false;

  // ── 白名单净化 ────────────────────────────────────────────────────────────

  function sanitize(html) {
    var doc = new DOMParser().parseFromString('<body>' + html + '</body>', 'text/html');
    cleanNode(doc.body);
    return doc.body.innerHTML;
  }

  function cleanNode(node) {
    var i = node.childNodes.length;
    while (i--) {
      var child = node.childNodes[i];
      if (child.nodeType === 3) continue;
      if (child.nodeType !== 1) { node.removeChild(child); continue; }
      var tag = child.tagName.toLowerCase();
      if (!allowedTags.has(tag)) {
        var frag = document.createDocumentFragment();
        while (child.firstChild) frag.appendChild(child.firstChild);
        node.replaceChild(frag, child);
        continue;
      }
      var attrs = Array.from(child.attributes);
      for (var a = 0; a < attrs.length; a++) {
        if (!allowedAttrs.has(attrs[a].name)) child.removeAttribute(attrs[a].name);
      }
      cleanNode(child);
    }
  }

  // ── 骨架屏 ────────────────────────────────────────────────────────────────

  var SKELETON_STYLE = [
    '@keyframes sui-shimmer {',
    '  0%   { background-position: -400px 0 }',
    '  100% { background-position:  400px 0 }',
    '}',
    '.sui-skeleton {',
    '  display: block;',
    '  background: #fff;',
    '  border-radius: 10px;',
    '  padding: 12px 14px;',
    '  box-shadow: 0 2px 12px rgba(0,0,0,0.07);',
    '  width: 320px;',
    '  box-sizing: border-box;',
    '  overflow: hidden;',
    '}',
    '.sui-skeleton .sui-line {',
    '  border-radius: 5px;',
    '  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);',
    '  background-size: 800px 100%;',
    '  animation: sui-shimmer 1.4s infinite linear;',
    '}',
  ].join('\n');

  var styleInjected = false;
  function injectStyle() {
    if (styleInjected) return;
    styleInjected = true;
    var s = document.createElement('style');
    s.textContent = SKELETON_STYLE;
    document.head.appendChild(s);
  }

  function createSkeleton() {
    injectStyle();
    var el = document.createElement('div');
    el.className = 'sui-skeleton';
    el.innerHTML = [
      '<div class="sui-line" style="height:12px;width:45%;margin-bottom:12px"></div>',
      '<div class="sui-line" style="height:8px;width:92%;margin-bottom:7px"></div>',
      '<div class="sui-line" style="height:8px;width:78%;margin-bottom:7px"></div>',
      '<div class="sui-line" style="height:8px;width:60%;margin-bottom:14px"></div>',
      '<div style="display:flex;gap:8px">',
      '  <div class="sui-line" style="height:8px;flex:2;border-radius:5px"></div>',
      '  <div class="sui-line" style="height:8px;flex:1;border-radius:5px"></div>',
      '</div>',
    ].join('');
    return el;
  }

  // ── 找消息气泡容器 ────────────────────────────────────────────────────────

  function findBubble(chatText) {
    var el = chatText.parentElement;
    var steps = 0;
    while (el && steps < 6) {
      var display = window.getComputedStyle(el).display;
      if (display !== 'inline' && display !== 'inline-block' &&
          el.tagName !== 'HTML' && el.tagName !== 'BODY') {
        return el;
      }
      el = el.parentElement;
      steps++;
    }
    return chatText;
  }

  // ── 检测 & 渲染 ───────────────────────────────────────────────────────────

  var MARKER_RE = /<div\s[^>]*class=["']a2ui["']/;
  var timers        = typeof WeakMap !== 'undefined' ? new WeakMap() : null;
  var skeletons     = typeof WeakMap !== 'undefined' ? new WeakMap() : null; // chatText → skeletonEl

  function renderChatText(el) {
    if (el.getAttribute(DONE_ATTR)) return;

    // 移除骨架屏
    function removeSkeleton() {
      if (!skeletons) return;
      var sk = skeletons.get(el);
      if (sk && sk.parentNode) {
        sk.parentNode.style.display = '';
        sk.parentNode.style.minWidth = '';
        sk.parentNode.removeChild(sk);
      }
      skeletons.delete(el);
    }

    var text = (el.textContent || '').trim();
    if (!MARKER_RE.test(text)) {
      removeSkeleton();
      el.style.display = '';
      return;
    }

    // 完整性检查
    var openCount  = (text.match(/<div[\s>]/g) || []).length;
    var closeCount = (text.match(/<\/div>/g)   || []).length;
    if (closeCount < openCount) {
      scheduleRender(el);
      return;
    }

    el.setAttribute(DONE_ATTR, '1');
    removeSkeleton();

    var aIdx = text.search(MARKER_RE);
    if (aIdx < 0) { el.style.display = ''; return; }

    var wrapper = document.createElement('div');
    wrapper.setAttribute(DONE_ATTR, '1');
    wrapper.style.cssText = 'display:block;margin:4px 0;opacity:0;transition:opacity 0.18s ease';
    wrapper.innerHTML = sanitize(text.slice(aIdx));

    el.style.display = '';
    el.innerHTML = '';
    el.appendChild(wrapper);

    requestAnimationFrame(function () {
      requestAnimationFrame(function () { wrapper.style.opacity = '1'; });
    });
  }

  function scheduleRender(el) {
    if (!timers) { renderChatText(el); return; }

    // 第一次：隐藏 chat-text，在其直接父节点里插入骨架屏
    if (skeletons && !skeletons.get(el)) {
      el.style.display = 'none';

      var parent = el.parentNode;
      var sk = createSkeleton();
      // 插到直接父节点，撑开气泡
      if (parent) {
        parent.style.display = 'inline-block';
        parent.style.minWidth = '320px';
        parent.appendChild(sk);
      }
      skeletons.set(el, sk);
    }

    var old = timers.get(el);
    if (old) clearTimeout(old);

    var tid = setTimeout(function () {
      timers.delete(el);
      renderChatText(el);
    }, DEBOUNCE_MS);
    timers.set(el, tid);
  }

  function processChatText(el) {
    if (!ready) return;
    if (el.getAttribute(DONE_ATTR)) return;
    var text = (el.textContent || '').trim();
    if (!MARKER_RE.test(text)) return;
    scheduleRender(el);
  }

  function walkAdded(node) {
    if (node.nodeType !== 1) return;
    if (node.classList && node.classList.contains('chat-text')) {
      processChatText(node);
      return;
    }
    var els = node.querySelectorAll ? node.querySelectorAll('.chat-text') : [];
    for (var i = 0; i < els.length; i++) processChatText(els[i]);
  }

  function walkMutation(mut) {
    if (mut.type === 'childList') {
      for (var i = 0; i < mut.addedNodes.length; i++) walkAdded(mut.addedNodes[i]);
    }
    var el = mut.target;
    while (el && el.nodeType === 3) el = el.parentNode;
    while (el) {
      if (el.classList && el.classList.contains('chat-text')) {
        processChatText(el);
        break;
      }
      el = el.parentElement;
    }
  }

  // ── 启动 ─────────────────────────────────────────────────────────────────

  function getAuthHeader() {
    try {
      var hash = location.hash.replace(/^#/, '');
      var hp = new URLSearchParams(hash);
      var t = hp.get('token');
      if (t) return 'Bearer ' + t;
      var raw = localStorage.getItem('openclaw.device.auth.v1');
      if (raw) { var d = JSON.parse(raw); if (d && d.token) return 'Bearer ' + d.token; }
      raw = localStorage.getItem('openclaw.control.settings.v1');
      if (raw) { var s = JSON.parse(raw); if (s && s.token) return 'Bearer ' + s.token; }
    } catch (e) {}
    return null;
  }

  async function boot() {
    try {
      var m;
      if (window.__skillUiManifest) {
        m = window.__skillUiManifest;
      } else {
        var authHeader = getAuthHeader();
        var fetchOpts = authHeader ? { headers: { 'Authorization': authHeader } } : {};
        var r = await fetch('/plugins/skill-ui/manifest', fetchOpts);
        if (!r.ok) { console.warn('[skill-ui-bridge] manifest', r.status); return; }
        m = await r.json();
      }

      (m.skills || []).forEach(function (s) {
        var c = s.config || {};
        ((c.dompurify && c.dompurify.allowedTags)  || []).forEach(function (t) { allowedTags.add(t);  });
        ((c.dompurify && c.dompurify.allowedAttrs) || []).forEach(function (a) { allowedAttrs.add(a); });
      });

      ready = true;
      walkAdded(document.body || document.documentElement);

      new MutationObserver(function (mutations) {
        for (var i = 0; i < mutations.length; i++) walkMutation(mutations[i]);
      }).observe(document.body || document.documentElement, {
        childList: true,
        subtree: true,
        characterData: true,
      });

      console.log('[skill-ui-bridge] boot ok, tags:', allowedTags.size, 'attrs:', allowedAttrs.size);
    } catch (e) {
      console.warn('[skill-ui-bridge] boot failed', e);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
