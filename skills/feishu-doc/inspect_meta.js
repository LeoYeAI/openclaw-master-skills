const { getTenantAccessToken } = require('./lib/auth');

async function inspect(appToken, label) {
    const token = await getTenantAccessToken();
    console.log(`\n=== Inspecting ${label} (${appToken}) ===`);
    
    // 1. Get Tables
    const tablesRes = await fetch(`https://open.feishu.cn/open-apis/bitable/v1/apps/${appToken}/tables`, {
        headers: { Authorization: `Bearer ${token}` }
    });
    const tablesData = await tablesRes.json();
    
    if (tablesData.code !== 0) {
        console.error("Error getting tables:", tablesData.msg);
        return;
    }
    
    for (const table of tablesData.data.items) {
        console.log(`Table: ${table.name} (ID: ${table.table_id})`);
        
        // 2. Get Fields
        const fieldsRes = await fetch(`https://open.feishu.cn/open-apis/bitable/v1/apps/${appToken}/tables/${table.table_id}/fields`, {
             headers: { Authorization: `Bearer ${token}` }
        });
        const fieldsData = await fieldsRes.json();
        
        if (fieldsData.code !== 0) {
            console.error("Error getting fields:", fieldsData.msg);
            continue;
        }
        
        // Filter for relevant fields to reduce noise
        const interestingFields = ['需求', '需求详述', '优先级', '模块', '备注', '文本']; 
        
        fieldsData.data.items.forEach(f => {
            // Log interesting fields OR Select fields (Type 3) to see options
            if (interestingFields.includes(f.field_name) || f.type === 3) { 
                console.log(`  - Field: ${f.field_name} (ID: ${f.field_id}, Type: ${f.type})`);
                if (f.property && f.property.options) {
                    console.log(`    Options: ${f.property.options.map(o => o.name).join(', ')}`);
                }
            }
        });
    }
}

(async () => {
    // Template (Iter 10)
    await inspect('X8QPbUQdValKN7sFIwfcsy8fnEh', 'Template (Iter 10)');
    // Target (Iter 11)
    await inspect('LvlAbvfzMaxUP8sGOEWcLrX7nHb', 'Target (Iter 11)');
})();
