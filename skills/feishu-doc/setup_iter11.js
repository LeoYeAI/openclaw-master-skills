const { getTenantAccessToken } = require('./lib/auth');

const APP_TOKEN = 'LvlAbvfzMaxUP8sGOEWcLrX7nHb';
const TABLE_ID = 'tblLy7koY2VGXGmR'; // From inspect_meta.js

async function setup() {
    const token = await getTenantAccessToken();
    console.log(`Setting up Iter 11 (App: ${APP_TOKEN}, Table: ${TABLE_ID})`);
    
    // 1. Create Fields
    // Field: 需求 (Text - Type 1)
    await createField(token, '需求', 1);
    
    // Field: 需求详述 (Text - Type 1)
    await createField(token, '需求详述', 1);
    
    // Field: 优先级 (Single Select - Type 3)
    const options = [
        { name: '上帝级重要', color: 0 }, // Red
        { name: '很重要', color: 1 },     // Orange
        { name: '重要', color: 2 },       // Yellow
        { name: '欠重要', color: 3 },     // Green
        { name: '待定', color: 4 }        // Blue
    ];
    await createField(token, '优先级', 3, { options: options });
    
    // 2. Insert Records
    const records = [
        {
            fields: {
                '需求': '获取行为和生活职业的结合',
                '需求详述': 'a. 当前获取行为不受生活职业的限制\nb. 炼药、烹饪行为因为和获取高度相关，还未完成开发\nc. 无法获取的道具走总控给其他NPC制作功能没做',
                '优先级': '上帝级重要'
            }
        },
        {
            fields: {
                '需求': 'NPC信息面板',
                '需求详述': '',
                '优先级': '很重要'
            }
        },
        {
            fields: {
                '需求': '心情系统',
                '需求详述': 'a. 完成了单独心情值的开发，心情值的变化和行为的结合没有处理',
                '优先级': '很重要'
            }
        },
        {
            fields: {
                '需求': '房间系统',
                '需求详述': 'a. 完成了item舒适度的计算，房间对NPC的影响和关系没有处理',
                '优先级': '重要'
            }
        },
        {
            fields: {
                '需求': '营地管理页面',
                '需求详述': 'a. 角色列表页\nb. 物品需求页',
                '优先级': '重要'
            }
        },
        {
            fields: {
                '需求': '路径COST计算规则',
                '需求详述': '',
                '优先级': '欠重要'
            }
        },
        {
            fields: {
                '需求': '营地功能旗帜的交互',
                '需求详述': '',
                '优先级': '欠重要'
            }
        }
    ];
    
    console.log(`Inserting ${records.length} records...`);
    const batchUrl = `https://open.feishu.cn/open-apis/bitable/v1/apps/${APP_TOKEN}/tables/${TABLE_ID}/records/batch_create`;
    
    const res = await fetch(batchUrl, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ records: records })
    });
    
    const data = await res.json();
    if (data.code !== 0) {
        console.error('Failed to create records:', JSON.stringify(data, null, 2));
    } else {
        console.log('Success! Created records.');
    }
}

async function createField(token, name, type, property) {
    console.log(`Creating field: ${name}`);
    const url = `https://open.feishu.cn/open-apis/bitable/v1/apps/${APP_TOKEN}/tables/${TABLE_ID}/fields`;
    
    const payload = {
        field_name: name,
        type: type
    };
    if (property) payload.property = property;
    
    const res = await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    if (data.code === 0) {
        console.log(`  -> Created field ID: ${data.data.field.field_id}`);
        return data.data.field.field_id;
    } else {
        console.warn(`  -> Failed to create field (might exist): ${data.msg}`);
        return null;
    }
}

setup().catch(console.error);
