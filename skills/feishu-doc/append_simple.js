const fs = require('fs');
const path = require('path');
const { program } = require('commander');
const Lark = require('@larksuiteoapi/node-sdk');
const env = require('../common/env');

env.load(); // Load environment variables

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;

// Helper to get client
function getClient() {
    return new Lark.Client({
        appId: APP_ID,
        appSecret: APP_SECRET,
        disableTokenCache: false,
        loggerLevel: 1 // Suppress INFO logs to stdout (1=ERROR)
    });
}

program
  .requiredOption('--doc_token <token>', 'Document Token')
  .requiredOption('--file <path>', 'Path to markdown content file')
  .parse(process.argv);

const options = program.opts();

async function append() {
    const client = getClient();
    const docToken = options.doc_token;
    let content = '';

    try {
        content = fs.readFileSync(options.file, 'utf8');
    } catch (e) {
        console.error(`Failed to read file: ${e.message}`);
        process.exit(1);
    }

    // Convert markdown to blocks (simplified)
    // Feishu Doc Block structure
    const blocks = [];
    const lines = content.split('\n');

    for (const line of lines) {
        if (!line.trim()) continue;

        let blockType = 2; // Text
        let contentText = line;
        let propName = 'text';

        if (line.startsWith('### ')) {
            blockType = 5; // Heading 3
            contentText = line.substring(4);
            propName = 'heading3';
        } else if (line.startsWith('## ')) {
            blockType = 4; // Heading 2
            contentText = line.substring(3);
            propName = 'heading2';
        } else if (line.startsWith('# ')) {
            blockType = 3; // Heading 1
            contentText = line.substring(2);
            propName = 'heading1';
        } else if (line.startsWith('- ') || line.startsWith('* ')) {
            blockType = 12; // Bullet
            contentText = line.substring(2);
            propName = 'bullet';
        } else if (line.startsWith('```')) {
             continue;
        }

        blocks.push({
            block_type: blockType,
            [propName]: {
                elements: [{
                    text_run: {
                        content: contentText,
                        text_element_style: {}
                    }
                }]
            }
        });
    }

    if (blocks.length === 0) {
        console.log(JSON.stringify({ success: true, message: "No content to append" }));
        return;
    }

    // Append blocks
    try {
        const res = await client.docx.documentBlockChildren.create({
            path: {
                document_id: docToken,
                block_id: docToken,
            },
            data: {
                children: blocks
            }
        });

        if (res.code === 0) {
            console.log(JSON.stringify({ success: true, blocks_added: blocks.length }));
        } else {
            console.error(JSON.stringify({ success: false, error: res.msg, code: res.code }));
            process.exit(1);
        }
    } catch (e) {
        console.error(JSON.stringify({ success: false, error: e.message }));
        process.exit(1);
    }
}

append();
