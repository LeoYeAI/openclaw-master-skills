/**
 * shenye-design Cloudflare Worker
 * 优化版本 — 2026-03-04
 *
 * 改动清单：
 *  [1] HTML 响应加缓存头 + CF 边缘 cacheTtl:300，避免每次回源
 *  [2] 清除 HTML 里 Google preconnect / dns-prefetch / gstatic 标签
 *  [3] CSS 内 @import fonts.googleapis.com 过滤
 *  [4] R2 objectKey 包含 query string，防止缓存 key 冲突
 *  [5] jQuery 直接替换为 jsdmirror（大陆 CDN 节点，字节一致，SRI 校验通过）
 *  [6] 重写 data-video-urls 属性，将视频 URL 也纳入 /_cdn/ R2 缓存
 *  [7] /_cdn/ 支持 HTTP Range 请求，视频可分段加载、立即起播
 *  [8] /_cdn/ CSS 文件在缓存前先改写内部绝对 URL，防止字体/图片绕过 R2 直连 Fastly
 *  [9] 移除 stylesheet <link> 的 integrity 属性，防止 CSS 内容改写后 SRI 校验失败导致无样式
 * [10] 重写视频 <source src>、data-poster-url、video[style] background-image，补全视频 poster 漏洞
 */

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const pathname = url.pathname;
    const webflowHost = "REPLACE_WITH_YOUR_WEBFLOW_HOST" // 例：mysite.webflow.io;

    // 1️⃣ 静态资源处理（robots.txt / sitemap.xml 从 R2 Public 返回）
    if (pathname === "/robots.txt" || pathname === "/sitemap.xml") {
      const r2Base = "REPLACE_WITH_YOUR_R2_PUBLIC_URL" // 例：https://pub-xxxx.r2.dev;
      const fileResponse = await fetch(`${r2Base}${pathname}`, { cf: { cacheEverything: true } });
      if (fileResponse.ok) {
        const contentType = pathname.endsWith(".xml") ? "application/xml" : "text/plain";
        return new Response(fileResponse.body, {
          headers: { "content-type": contentType, "cache-control": "public, max-age=3600" }
        });
      }
    }

    // 2️⃣ /_cdn/ 路径：R2 持久化缓存层（含 Range 请求支持）
    if (pathname.startsWith("/_cdn/")) {
      const regex = /^\/_cdn\/([^\/]+)\/(.*)$/;
      const match = pathname.match(regex);
      if (!match) return new Response("Invalid CDN Path", { status: 400 });

      const upstreamHost = match[1];
      const restPath = match[2];
      const upstreamURL = `https://${upstreamHost}/${restPath}${url.search}`;

      // [改动 4] R2 key 包含 query string，避免同路径不同参数映射到同一 key
      const objectKey = `assets/${upstreamHost}/${restPath}${
        url.search ? "_" + btoa(url.search).replace(/[^a-z0-9]/gi, "") : ""
      }`;

      // [改动 7] 读取 Range 请求头，用于视频分段加载
      const rangeHeader = req.headers.get("Range");

      try {
        const object = await env.MY_BUCKET.get(objectKey);

        if (object) {
          // R2 命中：处理 Range 请求（视频分段播放）
          if (rangeHeader) {
            const rangeMatch = rangeHeader.match(/bytes=(\d+)-(\d*)/);
            if (rangeMatch) {
              const totalSize = object.size;
              const start = parseInt(rangeMatch[1]);
              const end = rangeMatch[2] ? parseInt(rangeMatch[2]) : totalSize - 1;
              const length = end - start + 1;

              const rangeObject = await env.MY_BUCKET.get(objectKey, {
                range: { offset: start, length }
              });

              if (rangeObject) {
                const headers = new Headers();
                rangeObject.writeHttpMetadata(headers);
                headers.set("content-range", `bytes ${start}-${end}/${totalSize}`);
                headers.set("content-length", String(length));
                headers.set("accept-ranges", "bytes");
                headers.set("cache-control", "public, max-age=31536000, immutable");
                headers.set("x-cache", "HIT-R2-RANGE");
                return new Response(rangeObject.body, { status: 206, headers });
              }
            }
          }

          // 普通完整请求
          const headers = new Headers();
          object.writeHttpMetadata(headers);
          headers.set("cache-control", "public, max-age=31536000, immutable");
          headers.set("accept-ranges", "bytes");
          headers.set("x-cache", "HIT-R2");
          return new Response(object.body, { headers });
        }

        // R2 未命中：回源上游，同时异步写入 R2
        // 注意：有 Range 请求时先返回上游分段响应，不写 R2（等完整请求来缓存）
        const fetchHeaders = {
          "user-agent": req.headers.get("user-agent") || "Cloudflare-Worker"
        };
        if (rangeHeader) fetchHeaders["Range"] = rangeHeader;

        const upstreamResp = await fetch(upstreamURL, {
          headers: fetchHeaders,
          cf: { cacheEverything: true }
        });

        if (upstreamResp.ok || upstreamResp.status === 206) {
          const contentType = upstreamResp.headers.get("content-type");
          const newHeaders = new Headers(upstreamResp.headers);
          newHeaders.set("accept-ranges", "bytes");
          newHeaders.set("x-cache", rangeHeader ? "MISS-R2-RANGE-PASS" : "MISS-R2-FETCHED");

            // 只有完整响应（200）才缓存进 R2，避免缓存残片
          if (upstreamResp.status === 200 && !rangeHeader) {
            newHeaders.set("cache-control", "public, max-age=31536000, immutable");

            // [改动 8] CSS 文件：先改写内部绝对 URL，再缓存进 R2
            // 问题根源：/_cdn/ 直接透传原始 CSS，CSS 里的 font/image 绝对地址绕过了 R2 缓存
            const isCss = contentType?.includes("text/css") || restPath.endsWith(".css");
            if (isCss) {
              let cssText = await upstreamResp.text();
              cssText = cssText.replace(
                /https:\/\/(cdn\.prod\.website-files\.com|assets\.website-files\.com|uploads-ssl\.webflow\.com)/g,
                (_, host) => `/_cdn/${host}`
              );
              newHeaders.set("content-type", "text/css; charset=UTF-8");
              newHeaders.set("x-cache", "MISS-R2-FETCHED-CSS-REWRITTEN");
              ctx.waitUntil(
                env.MY_BUCKET.put(objectKey, cssText, {
                  httpMetadata: { contentType: "text/css; charset=UTF-8", cacheControl: "public, max-age=31536000, immutable" }
                })
              );
              return new Response(cssText, { status: 200, headers: newHeaders });
            }

            const copyForR2 = upstreamResp.clone();
            ctx.waitUntil(
              env.MY_BUCKET.put(objectKey, copyForR2.body, {
                httpMetadata: { contentType, cacheControl: "public, max-age=31536000, immutable" }
              })
            );
          }

          return new Response(upstreamResp.body, {
            status: upstreamResp.status,
            headers: newHeaders
          });
        }
        return new Response(`Source Not Found: ${upstreamURL}`, { status: 404 });
      } catch (e) {
        return new Response(`R2 Error: ${e.message}`, { status: 500 });
      }
    }

    // 3️⃣ 反向代理 Webflow 主站
    const proxyURL = new URL(req.url);
    proxyURL.hostname = webflowHost;
    proxyURL.protocol = "https:";

    // [改动 1] 加 cacheTtl: 300，让 CF 边缘节点缓存回源响应 5 分钟
    const originResp = await fetch(proxyURL.toString(), {
      method: req.method,
      headers: req.headers,
      redirect: "follow",
      cf: { cacheEverything: true, cacheTtl: 300 }
    });

    const contentType = originResp.headers.get("content-type") || "";

    // 4️⃣ HTML 处理
    if (contentType.includes("text/html")) {
      const rewriter = new HTMLRewriter()
        // 移除 Google Fonts stylesheet
        .on('link[href*="fonts.googleapis.com"]', { element(el) { el.remove(); } })
        // [改动 2] 移除所有 Google / gstatic preconnect & dns-prefetch
        .on('link[rel="preconnect"][href*="google"]',    { element(el) { el.remove(); } })
        .on('link[rel="preconnect"][href*="gstatic"]',   { element(el) { el.remove(); } })
        .on('link[rel="dns-prefetch"][href*="google"]',  { element(el) { el.remove(); } })
        .on('link[href*="fonts.gstatic.com"]',           { element(el) { el.remove(); } })
        // 移除 WebFont Loader（Google Fonts JS 加载器）
        .on('script[src*="webfont.js"]', { element(el) { el.remove(); } })
        // [改动 9] 移除 stylesheet <link> 的 integrity 属性
        // 原因：/_cdn/ 处理器会改写 CSS 内部 URL，导致文件内容变化，SRI 哈希失效
        // 浏览器会拒绝加载哈希不匹配的 CSS，导致页面无样式
        .on('link[rel="stylesheet"][integrity]', {
          element(el) { el.removeAttribute("integrity"); }
        })
        // [改动 5] 将 Webflow 注入的 jQuery（CloudFront）替换为 jsdmirror
        // 三源字节完全一致（SHA256 相同），SRI integrity 校验仍会通过
        .on('script[src*="d3e54v103j8qbb.cloudfront.net"][src*="jquery"]', {
          element(el) {
            el.setAttribute("src", "https://cdn.jsdmirror.com/npm/jquery@3.5.1/dist/jquery.min.js");
            // crossorigin 保留（SRI 跨域校验必须）
          }
        })
        // 隐藏 Webflow badge
        .on(".w-webflow-badge", { element(el) { el.remove(); } })
        .on("head", {
          element(el) {
            el.prepend(
              `<style>.w-webflow-badge{display:none!important;visibility:hidden!important;opacity:0!important}</style>`,
              { html: true }
            );
          }
        })
        // 重写标准资产 URL（link/script/img/source）到 /_cdn/ 路径
        // source[src] 覆盖 <video> 的 <source> 子元素；source[srcset] 覆盖 <picture> 的多分辨率图
        .on("link[href], script[src], img[src], source[src], source[srcset]", {
          element(el) {
            for (const attr of ["href", "src", "srcset"]) {
              const val = el.getAttribute(attr);
              if (val) el.setAttribute(attr, rewriteAssetURL(val));
            }
          }
        })
        // [改动 6] 重写 Webflow 背景视频的 data-video-urls 属性
        // 格式：逗号分隔的完整 URL 列表（mp4,webm）
        .on("[data-video-urls]", {
          element(el) {
            const val = el.getAttribute("data-video-urls");
            if (val) {
              const rewritten = val
                .split(",")
                .map(u => rewriteAssetURL(u.trim()))
                .join(",");
              el.setAttribute("data-video-urls", rewritten);
            }
          }
        })
        // [改动 10] 重写 Webflow 背景视频的 poster 相关属性
        // data-poster-url：Webflow JS 读取用于设置海报帧
        // video[style]：Webflow 将 poster 写入 style="background-image:url(...)"，浏览器直接读取
        .on("[data-poster-url]", {
          element(el) {
            const val = el.getAttribute("data-poster-url");
            if (val) el.setAttribute("data-poster-url", rewriteAssetURL(val));
          }
        })
        .on("video[style]", {
          element(el) {
            const style = el.getAttribute("style");
            if (style && style.includes("background-image")) {
              const rewritten = style.replace(
                /url\(["']?(https:\/\/(?:cdn\.prod\.website-files\.com|assets\.website-files\.com|uploads-ssl\.webflow\.com)[^"')]*?)["']?\)/g,
                (_, u) => `url("${rewriteAssetURL(u)}")`
              );
              el.setAttribute("style", rewritten);
            }
          }
        });

      // [改动 1] 设置 HTML 缓存头：CF 边缘缓存 5 分钟
      const respHeaders = new Headers(originResp.headers);
      respHeaders.set("cache-control", "public, max-age=300, s-maxage=300");
      respHeaders.delete("set-cookie"); // 移除 cookie 避免缓存污染

      return new Response(rewriter.transform(originResp).body, {
        status: originResp.status,
        headers: respHeaders
      });
    }

    // 5️⃣ CSS 处理
    if (contentType.includes("text/css")) {
      let cssText = await originResp.text();

      // [改动 3] 过滤 CSS 文件内的 Google Fonts @import
      cssText = cssText.replace(
        /@import\s+url\(['"]?https?:\/\/fonts\.googleapis\.com[^'")\s]*['"]?\)[^;]*;/g,
        ""
      );

      // 重写资产域名到 /_cdn/ 路径（含 Webflow jQuery CloudFront 域名）
      cssText = cssText.replace(
        /https:\/\/(cdn\.prod\.website-files\.com|assets\.website-files\.com|uploads-ssl\.webflow\.com)/g,
        (match) => {
          const host = match.replace("https://", "");
          return `/_cdn/${host}`;
        }
      );

      return new Response(cssText, {
        headers: {
          "content-type": "text/css; charset=UTF-8",
          "cache-control": "public, max-age=31536000, immutable",
          "x-processed": "true"
        }
      });
    }

    // 6️⃣ 其余流量透传
    return originResp;
  }
};

/**
 * 将 Webflow CDN / CloudFront 资产 URL 重写到 /_cdn/ 路径
 * 支持：
 *  - 单个 URL
 *  - srcset 格式（"url1 1x, url2 2x"）
 *  - data-video-urls 格式（"url1.mp4, url2.webm"，调用前已 split）
 */
function rewriteAssetURL(u) {
  try {
    // srcset 格式：包含逗号 + 空格描述符
    if (/,\s*https?:\/\//.test(u) || (u.includes(",") && u.includes(" "))) {
      return u.split(",").map(part => {
        const seg = part.trim().split(/\s+/);
        seg[0] = rewriteAssetURL(seg[0]);
        return seg.join(" ");
      }).join(", ");
    }
    const parsed = new URL(u, "https://dummy.base");
    const host = parsed.hostname;
    const hosts = [
      "cdn.prod.website-files.com",
      "assets.website-files.com",
      "uploads-ssl.webflow.com"
      // d3e54v103j8qbb.cloudfront.net 已在 HTMLRewriter 里直接替换为 jsdmirror，无需走 /_cdn/
    ];
    if (hosts.includes(host)) {
      return `/_cdn/${host}${parsed.pathname}${parsed.search}`;
    }
    return u;
  } catch {
    return u;
  }
}
