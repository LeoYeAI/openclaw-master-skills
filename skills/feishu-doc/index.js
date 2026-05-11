const { fetchWithAuth, getToken } = require('../feishu-common/index.js');
const fs = require('fs');
const path = require('path');
const { sanitizeMarkdown, validateBlocks } = require('./input_guard.js');

const { resolveWiki } = require('./lib/wiki');
const { fetchBitableContent } = require('./lib/bitable');
const { fetchSheetContent } = require('./lib/sheet');


// Block Types Mapping
const BLOCK_TYPE_NAMES = {
  1: "Page",
  2: "Text",
  3: "Heading1",
  4: "Heading2",
  5: "Heading3",
  12: "Bullet",
  13: "Ordered",
  14: "Code",
  15: "Quote",
  17: "Todo",
  18: "Bitable",
  21: "Diagram",
  22: "Divider",
  23: "File",
  27: "Image",
  30: "Sheet",
  31: "Table",
  32: "TableCell",
};

// --- Helpers ---

function extractToken(input) {
    if (!input) return input;
    // Handle full URLs: https://.../docx/TOKEN or /wiki/TOKEN
    const match = input.match(/\/(?:docx|wiki|doc|sheet|file|base)\/([a-zA-Z0-9]+)/);
    if (match) return match[1];
    return input;
}

async function resolveToken(docToken) {
    // Ensure we have a clean token first
    const cleanToken = extractToken(docToken);
    const accessToken = await getToken();
    try {
        const wikiNode = await resolveWiki(cleanToken, accessToken);
        if (wikiNode) {
            const { obj_token, obj_type } = wikiNode;
            if (obj_type === 'docx' || obj_type === 'doc') {
                return obj_token;
            } else if (obj_type === 'bitable' || obj_type === 'sheet') {
                 return { token: obj_token, type: obj_type };
            }
        }
    } catch (e) {
        // Ignore resolution errors
    }
    return cleanToken; // Default fallback
}

async function batchInsertBlocks(targetToken, blocks) {
    const BATCH_SIZE = 20; 
    let blocksAdded = 0;
    
    for (let i = 0; i < blocks.length; i += BATCH_SIZE) {
        const chunk = blocks.slice(i, i + BATCH_SIZE);
        const payload = { children: chunk };

        let retries = 3;
        while (retries > 0) {
            try {
                let createData;
                let batchError = null;

                try {
                    if (i > 0) await new Promise(r => setTimeout(r, 200));

                    const createRes = await fetchWithAuth(`https://open.feishu.cn/open-apis/docx/v1/documents/${targetToken}/blocks/${targetToken}/children`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    createData = await createRes.json();
                } catch (err) {
                    // Handle HTTP 400 (Bad Request) or 422 (Unprocessable Entity) by catching fetch error
                    if (err.message && (err.message.includes('HTTP 400') || err.message.includes('HTTP 422'))) {
                        batchError = err;
                    } else {
                        throw err;
                    }
                }
                
                if (batchError || (createData && createData.code !== 0)) {
                     const errorMsg = batchError ? batchError.message : `Code ${createData.code}: ${createData.msg}`;
                     console.error(`[feishu-doc] Batch failed (${errorMsg}). Retrying item-by-item.`);
                     
                     for (const block of chunk) {
                        try {
                            const singleRes = await fetchWithAuth(`https://open.feishu.cn/open-apis/docx/v1/documents/${targetToken}/blocks/${targetToken}/children`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ children: [block] })
                            });
                            const singleData = await singleRes.json();
                            if (singleData.code !== 0) {
                                console.error(`[feishu-doc] Skipping bad block: ${singleData.msg} (Type: ${block.block_type})`);
                            } else {
                                blocksAdded++;
                            }
                        } catch (err) {
                             console.error(`[feishu-doc] Skipping bad block (exception): ${err.message} (Type: ${block.block_type})`);
                        }
                     }
                     // Consider the chunk processed (partially successful) to avoid failing the whole operation
                     // But we break the retry loop because we handled this chunk manually
                     break; 
                }

                blocksAdded += chunk.length;
                break; 
            } catch (e) {
                retries--;
                if (retries === 0) throw e;
                await new Promise(r => setTimeout(r, (3 - retries) * 1000));
            }
        }
    }
    return blocksAdded;
}

// --- Actions ---

async function resolveDoc(docToken) {
    const resolved = await resolveToken(docToken);
    if (!resolved) throw new Error('Could not resolve token');
    // Normalize return
    if (typeof resolved === 'string') return { token: resolved, type: 'docx' };
    return resolved;
}

async function readDoc(docToken) {
    const accessToken = await getToken();
    const cleanToken = extractToken(docToken);

    try {
        return await readDocxDirect(cleanToken);
    } catch (e) {
        // Code 1770002 = Not Found (often means it's a wiki token not a doc token)
        // Code 1061001 = Permission denied (sometimes happens with wiki wrappers)
        // "Request failed with status code 404" = Generic Axios/HTTP error
        const isNotFound = e.message.includes('not found') || 
                           e.message.includes('1770002') || 
                           e.message.includes('status code 404') ||
                           e.message.includes('HTTP 404');
        
        if (isNotFound) {
            try {
                const wikiNode = await resolveWiki(cleanToken, accessToken);
                if (wikiNode) {
                    const { obj_token, obj_type } = wikiNode;
                    
                    if (obj_type === 'docx' || obj_type === 'doc') {
                        return await readDocxDirect(obj_token);
                    } else if (obj_type === 'bitable') {
                        return await fetchBitableContent(obj_token, accessToken);
                    } else if (obj_type === 'sheet') {
                        return await fetchSheetContent(obj_token, accessToken);
                    } else {
                        throw new Error(`Unsupported Wiki Object Type: ${obj_type}`);
                    }
                }
            } catch (wikiError) {
                // If wiki resolution also fails, throw the original error
            }
        }
        throw e;
    }
}

async function readDocxDirect(docToken) {
    const rawContent = await fetchWithAuth(`https://open.feishu.cn/open-apis/docx/v1/documents/${docToken}/raw_content`);
    const rawData = await rawContent.json();
    if (rawData.code !== 0) throw new Error(`RawContent Error: ${rawData.msg} (${rawData.code})`);

    const docInfo = await fetchWithAuth(`https://open.feishu.cn/open-apis/docx/v1/documents/${docToken}`);
    const infoData = await docInfo.json();
    if (infoData.code !== 0) throw new Error(`DocInfo Error: ${infoData.msg} (${infoData.code})`);

    const blocks = await fetchWithAuth(`https://open.feishu.cn/open-apis/docx/v1/documents/${docToken}/blocks`);
    const blockData = await blocks.json();
    if (blockData.code !== 0) throw new Error(`Blocks Error: ${blockData.msg} (${blockData.code})`);

    const items = blockData.data?.items ?? [];
    const blockCounts = {};
    
    for (const b of items) {
        const type = b.block_type ?? 0;
        const name = BLOCK_TYPE_NAMES[type] || `type_${type}`;
        blockCounts[name] = (blockCounts[name] || 0) + 1;
    }

    return {
        title: infoData.data?.document?.title,
        content: rawData.data?.content,
        revision_id: infoData.data?.document?.revision_id,
        block_count: items.length,
        block_types: blockCounts
    };
}

async function createDoc(title, folderToken) {
    const payload = { title };
    if (folderToken) payload.folder_token = folderToken;

    const res = await fetchWithAuth('https://open.feishu.cn/open-apis/docx/v1/documents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.code !== 0) throw new Error(data.msg);
    
    return {
        document_id: data.data?.document?.document_id,
        title: data.data?.document?.title,
        url: `https://feishu.cn/docx/${data.data?.document?.document_id}`
    };
}

async function writeDoc(docToken, content) {
    // 0. Auto-resolve Wiki token if needed
    let targetToken = docToken;
    try {
        const resolved = await resolveToken(docToken);
        if (typeof resolved === 'string') targetToken = resolved;
        else if (resolved.token) targetToken = resolved.token;
    } catch (e) {}

    // 1. Get existing blocks (validation step)
    let blocksRes;
    try {
        blocksRes = await fetchWithAuth(`https://open.feishu.cn/open-apis/docx/v1/documents/${targetToken}/blocks`);
    } catch (e) {
        throw e;
    }

    const blocksData = await blocksRes.json();
    
    // 2. Delete existing content (robustly)
    try {
        const childrenRes = await fetchWithAuth(`https://open.feishu.cn/open-apis/docx/v1/documents/${targetToken}/blocks/${targetToken}/children?page_size=500`);
        const childrenData = await childrenRes.json();
        
        if (childrenData.code === 0 && childrenData.data?.items?.length > 0) {
            const directChildrenCount = childrenData.data.items.length;
            await fetchWithAuth(`https://open.feishu.cn/open-apis/docx/v1/documents/${targetToken}/blocks/${targetToken}/children/batch_delete`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start_index: 0, end_index: directChildrenCount })
            });
        }
    } catch (delErr) {
        console.warn(`[feishu-doc] Warning: clear content failed. Appending instead.`);
    }

    // 3. Parse Content into Blocks
    const blocks = [];
    const lines = content.split('\n');
    let inCodeBlock = false;
    let codeContent = [];

    for (const line of lines) {
        if (line.trim().startsWith('```')) {
            if (inCodeBlock) {
                inCodeBlock = false;
                const codeText = sanitizeMarkdown(codeContent.join('\n'));
                blocks.push({
                    block_type: 14,
                    code: { elements: [{ text_run: { content: codeText, text_element_style: {} } }], language: 1 }
                });
                codeContent = [];
            } else {
                inCodeBlock = true;
            }
            continue;
        }
        if (inCodeBlock) {
            codeContent.push(line);
            continue;
        }

        if (!line.trim()) continue;

        let blockType = 2;
        let propName = 'text';
        let cleanText = sanitizeMarkdown(line);

        if (line.startsWith('# ')) { blockType = 3; propName = 'heading1'; cleanText = sanitizeMarkdown(line.substring(2)); }
        else if (line.startsWith('## ')) { blockType = 4; propName = 'heading2'; cleanText = sanitizeMarkdown(line.substring(3)); }
        else if (line.startsWith('### ')) { blockType = 5; propName = 'heading3'; cleanText = sanitizeMarkdown(line.substring(4)); }
        else if (line.startsWith('> ')) { blockType = 15; propName = 'quote'; cleanText = sanitizeMarkdown(line.substring(2)); } 
        else if (line.startsWith('- ') || line.startsWith('* ')) { blockType = 12; propName = 'bullet'; cleanText = sanitizeMarkdown(line.substring(2)); }
        else if (/^\d+\. /.test(line)) { blockType = 13; propName = 'ordered'; cleanText = sanitizeMarkdown(line.replace(/^\d+\. /, '')); }

        if (!cleanText.trim()) continue;

        blocks.push({
            block_type: blockType,
            [propName]: { elements: [{ text_run: { content: cleanText, text_element_style: {} } }] }
        });
    }

    const validBlocks = validateBlocks(blocks);
    const blocksAdded = await batchInsertBlocks(targetToken, validBlocks);

    return { success: true, message: 'Document overwritten', blocks_added: blocksAdded };
}

async function appendDoc(docToken, content) {
    let targetToken = docToken;
    try {
        const resolved = await resolveToken(docToken);
        if (typeof resolved === 'string') targetToken = resolved;
        else if (resolved.token) targetToken = resolved.token;
    } catch (e) {}

    // Use the same robust parsing and batching logic as writeDoc
    const blocks = [];
    const lines = content.split('\n');
    let inCodeBlock = false;
    let codeContent = [];

    for (const line of lines) {
        if (line.trim().startsWith('```')) {
            if (inCodeBlock) {
                inCodeBlock = false;
                const codeText = sanitizeMarkdown(codeContent.join('\n'));
                blocks.push({
                    block_type: 14,
                    code: { elements: [{ text_run: { content: codeText, text_element_style: {} } }], language: 1 }
                });
                codeContent = [];
            } else {
                inCodeBlock = true;
            }
            continue;
        }
        if (inCodeBlock) {
            codeContent.push(line);
            continue;
        }

        if (!line.trim()) continue;

        let blockType = 2;
        let propName = 'text';
        let cleanText = sanitizeMarkdown(line);

        if (line.startsWith('# ')) { blockType = 3; propName = 'heading1'; cleanText = sanitizeMarkdown(line.substring(2)); }
        else if (line.startsWith('## ')) { blockType = 4; propName = 'heading2'; cleanText = sanitizeMarkdown(line.substring(3)); }
        else if (line.startsWith('### ')) { blockType = 5; propName = 'heading3'; cleanText = sanitizeMarkdown(line.substring(4)); }
        else if (line.startsWith('> ')) { blockType = 15; propName = 'quote'; cleanText = sanitizeMarkdown(line.substring(2)); } 
        else if (line.startsWith('- ') || line.startsWith('* ')) { blockType = 12; propName = 'bullet'; cleanText = sanitizeMarkdown(line.substring(2)); }
        else if (/^\d+\. /.test(line)) { blockType = 13; propName = 'ordered'; cleanText = sanitizeMarkdown(line.replace(/^\d+\. /, '')); }

        if (!cleanText.trim()) continue;

        blocks.push({
            block_type: blockType,
            [propName]: { elements: [{ text_run: { content: cleanText, text_element_style: {} } }] }
        });
    }

    const validBlocks = validateBlocks(blocks);
    const blocksAdded = await batchInsertBlocks(targetToken, validBlocks);

    return { success: true, message: 'Document appended', blocks_added: blocksAdded };
}

// CLI Wrapper
if (require.main === module) {
    const { program } = require('commander');
    program
        .option('--action <action>', 'Action: read, write, create, append')
        .option('--token <token>', 'Doc Token')
        .option('--content <text>', 'Content')
        .option('--title <text>', 'Title')
        .parse(process.argv);
    
    const opts = program.opts();

    (async () => {
        try {
            const token = extractToken(opts.token);
            
            if (opts.action === 'read') {
                console.log(JSON.stringify(await readDoc(token), null, 2));
            } else if (opts.action === 'resolve') {
                console.log(JSON.stringify(await resolveDoc(token), null, 2));
            } else if (opts.action === 'create') {
                console.log(JSON.stringify(await createDoc(opts.title), null, 2));
            } else if (opts.action === 'write') {
                console.log(JSON.stringify(await writeDoc(token, opts.content), null, 2));
            } else if (opts.action === 'append') {
                console.log(JSON.stringify(await appendDoc(token, opts.content), null, 2));
            } else {
                console.error('Unknown action');
                process.exit(1);
            }
        } catch (e) {
            // Enhanced Error Reporting for JSON-expecting agents
            const errorObj = {
                code: 1,
                error: e.message,
                msg: e.message
            };
            
            if (e.message.includes('HTTP 400') || e.message.includes('400')) {
                errorObj.tip = "Check if the token is valid (docx/...) and not a URL or wiki link without resolution.";
            }
            
            console.error(JSON.stringify(errorObj, null, 2));
            process.exit(1);
        }
    })();
}

module.exports = { readDoc, createDoc, writeDoc, appendDoc, resolveDoc };
