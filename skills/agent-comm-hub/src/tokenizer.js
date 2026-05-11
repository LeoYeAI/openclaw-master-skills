/**
 * tokenizer.ts — 中文 N-gram 分词器 (Phase 2 Day 3)
 *
 * 解决 FTS5 默认 tokenizer 不支持中文分词的问题。
 * 方案：在写入时对中文内容预分词（bigram + trigram），
 *       搜索时对查询词也做相同处理，配合精确短语匹配。
 *
 * 无外部依赖，纯算法实现。
 */
/**
 * 生成 N-gram 分词结果
 * @param text 输入文本（中文/英文混合）
 * @param n gram 长度（2=bigram, 3=trigram）
 * @returns N-gram tokens 数组
 */
export function ngram(text, n) {
    const tokens = [];
    for (let i = 0; i <= text.length - n; i++) {
        tokens.push(text.slice(i, i + n));
    }
    return tokens;
}
/**
 * 对混合文本分词：英文按单词拆分并小写化，中文按 bigram+trigram 拆分
 * @param text 输入文本
 * @returns 去重后的 tokens 数组
 */
function segment(text) {
    const parts = [];
    // 按英文/数字块和中文块分割
    const segments = text.split(/([a-zA-Z0-9_]+)/);
    for (const seg of segments) {
        if (/^[a-zA-Z0-9_]+$/.test(seg)) {
            // 英文/数字：整词 + 小写化
            parts.push(seg.toLowerCase());
        }
        else if (seg.trim()) {
            // 中文：bigram + trigram
            for (let n = 2; n <= 3; n++) {
                parts.push(...ngram(seg, n));
            }
        }
    }
    return [...new Set(parts)];
}
/**
 * 为记忆内容构建 FTS tokens（写入时调用）
 * 将 title + content 分词后的 tokens 拼接为空格分隔的字符串，
 * 存入 memories.fts_tokens 列供 FTS5 索引。
 *
 * @param title 记忆标题
 * @param content 记忆内容
 * @returns 空格分隔的 tokens 字符串
 */
export function buildFtsTokens(title, content) {
    const text = (title || "") + " " + content;
    return segment(text).join(" ");
}
/**
 * 将搜索 query 转换为 FTS5 MATCH 表达式（搜索时调用）
 *
 * 策略：精确短语匹配 + bigram OR 搜索
 * 例如 "机器学习" → '"机器学习" OR 机机 OR 机器 OR 器学 OR 学习'
 *
 * @param query 用户搜索关键词
 * @returns FTS5 MATCH 表达式
 */
export function buildSearchQuery(query) {
    if (!query.trim())
        return "";
    // 清理 FTS5 特殊字符（保留双引号、字母数字、中文、空格）
    const cleaned = query.replace(/[!*()&|:{}^~\\]/g, " ").trim();
    const segments = cleaned.split(/([a-zA-Z0-9_]+)/);
    const parts = [];
    for (const seg of segments) {
        if (/^[a-zA-Z0-9_]+$/.test(seg)) {
            // 英文/数字：精确匹配 + 前缀通配
            parts.push(seg.toLowerCase());
            parts.push(seg.toLowerCase() + "*");
        }
        else if (seg.trim()) {
            // 中文：精确短语（带引号）+ bigram OR
            // 过滤掉纯符号 token
            const stripped = seg.replace(/[\s#]+/g, "").trim();
            if (stripped.length >= 2) {
                parts.push('"' + stripped.replace(/"/g, '""') + '"');
            }
            // 仅对包含中文的 segment 生成 bigram
            if (/[\u4e00-\u9fff]/.test(seg)) {
                const chineseOnly = seg.replace(/[^\u4e00-\u9fff]/g, "");
                if (chineseOnly.length >= 2) {
                    parts.push(...ngram(chineseOnly, 2));
                }
            }
        }
    }
    const result = [...new Set(parts)].join(" OR ");
    return result;
}
//# sourceMappingURL=tokenizer.js.map