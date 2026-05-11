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
        loggerLevel: 1 // Explicit 1 (ERROR)
    });
}

program
  .requiredOption('--title <title>', 'Document Title')
  .option('--folder_token <token>', 'Folder Token (Optional)')
  .option('--grant <user_id>', 'Grant edit permission to user (open_id or user_id)')
  .parse(process.argv);

const options = program.opts();

async function grantPermission(client, docToken, userId) {
    try {
        // Try as open_id first, then user_id if needed, or just rely on API flexibility
        // Member type: "openid" or "userid"
        // We'll guess "openid" if it starts with 'ou_', else 'userid' if 'eu_'? No, let's try 'openid' default.
        const memberType = userId.startsWith('ou_') ? 'openid' : 'userid';

        await client.drive.permissionMember.create({
            token: docToken,
            type: 'docx',
            data: {
                members: [{
                    member_type: memberType,
                    member_id: userId,
                    perm: 'edit'
                }]
            }
        });
        console.error(`[Permission] Granted edit access to ${userId}`);
    } catch (e) {
        console.error(`[Permission] Failed to grant access: ${e.message}`);
    }
}

async function create() {
    const client = getClient();
    try {
        const res = await client.docx.document.create({
            data: {
                title: options.title,
                folder_token: options.folder_token || undefined
            }
        });

        if (res.code === 0) {
            const doc = res.data.document;
            const docToken = doc.document_id;
            const url = `https://feishu.cn/docx/${docToken}`;

            if (options.grant) {
                await grantPermission(client, docToken, options.grant);
            }

            console.log(JSON.stringify({
                title: doc.title,
                doc_token: docToken,
                url: url,
                granted_to: options.grant || null
            }, null, 2));
        } else {
            console.error('Failed to create document:', res.msg);
            process.exit(1);
        }
    } catch (e) {
        console.error('Error:', e.message);
        process.exit(1);
    }
}

create();
