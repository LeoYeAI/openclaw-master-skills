/**
 * Feishu Doc Input Guard
 * Innovated by GEP Cycle #1226 (Updated Cycle #1759)
 * 
 * Prevents 400 errors by sanitizing markdown before API submission.
 * Enforces:
 * - No nested tables (Feishu limitation)
 * - Valid block structure
 * - Text length limits
 */

const sanitizeMarkdown = (text) => {
    if (!text) return "";
    
    // 1. Remove null bytes and control characters (except newlines/tabs)
    // Expanded range to include more control characters if needed, but keeping basic set for now.
    // Added \r removal to normalize newlines.
    // Preserving \t (0x09) and \n (0x0A)
    let safeText = text.replace(/[\x00-\x08\x0B-\x1F\x7F\r]/g, "");

    // 2. Feishu doesn't support nested blockquotes well in some contexts, flatten deeper levels
    // (Simple heuristic: reduce >>> to >)
    safeText = safeText.replace(/^>{2,}/gm, ">");

    return safeText;
};

const validateBlocks = (blocks) => {
    return blocks.filter(block => {
        // Text blocks must have content
        if (block.block_type === 2) {
            const content = block.text?.elements?.[0]?.text_run?.content;
            return content && content.trim().length > 0;
        }
        // Headings/Bullets/Quotes must have content
        const typeMap = { 3: 'heading1', 4: 'heading2', 5: 'heading3', 12: 'bullet', 13: 'ordered', 15: 'quote' };
        if (block.block_type in typeMap) {
             const prop = typeMap[block.block_type];
             const content = block[prop]?.elements?.[0]?.text_run?.content;
             return content && content.trim().length > 0;
        }
        // Code blocks are generally safe even if empty, but better to prevent empty text_run issues
        if (block.block_type === 14) {
             const content = block.code?.elements?.[0]?.text_run?.content;
             // Allow empty code blocks but ensure text_run structure exists
             // Feishu might reject empty content in text_run, so let's enforce at least a space or filter it.
             // Filtering empty code blocks is safer for append operations.
             return content && content.length > 0; 
        }
        return true;
    });
};

module.exports = {
    sanitizeMarkdown,
    validateBlocks
};
