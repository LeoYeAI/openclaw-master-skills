const fs = require('fs');
const path = require('path');

const API_BASE_URL = 'https://saas.api.yoo-ai.com';

/**
 * 创建 PPT 生成任务
 * @param {Object} params - PPT 生成参数 (text 或 custom_data, font_name, language, color, user_name)
 * @param {string} apiKey - API Key
 * @returns {Promise<string>} - 任务 ID
 */
async function createPptTask(params, apiKey) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(params)
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`创建任务失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data.id;
}

/**
 * 获取 PPT 生成结果/状态
 * @param {string} id - 任务 ID
 * @param {string} apiKey - API Key
 * @returns {Promise<Object>} - 状态数据
 */
async function getPptResult(id, apiKey) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-result?id=${id}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${apiKey}`
        }
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`获取状态失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data;
}

/**
 * 获取 PPT 下载链接（GET）
 * @param {string} id - 任务 ID
 * @param {string} apiKey - API Key
 * @returns {Promise<string>} - 下载 URL
 */
async function getDownloadUrl(id, apiKey) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-download?id=${id}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${apiKey}`
        }
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`获取下载链接失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data.download_url;
}

/**
 * 获取 PPT 在线编辑链接
 * @param {string} id - 任务 ID
 * @param {string} apiKey - API Key
 * @param {boolean} report - 是否开启在线编辑报告模式 (默认为 true)
 * @returns {Promise<string>} - 编辑器 URL
 */
async function getEditorUrl(id, apiKey, report = true) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-editor`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            id,
            expire: 86400,
            report: report
        })
    });

    const result = await response.json();
    if (result.code === 204) {
        return null; // 正在生成中
    }
    if (!response.ok || result.code !== 200) {
        throw new Error(`获取编辑链接失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data.url;
}

/**
 * 重新生成 PPT（更换风格等）
 * @param {string} id - 任务 ID
 * @param {Object} styleParams - 新的风格参数 (cover_id, transition, font_name, color)
 * @param {string} apiKey - API Key
 */
async function regeneratePpt(id, styleParams, apiKey) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-create-task`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            id,
            ...styleParams
        })
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`重新生成失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data.id;
}

/**
 * 为 PPT 生成演讲稿
 * @param {string} id - 任务 ID
 * @param {string} apiKey - API Key
 */
async function addSpeakerNotes(id, apiKey) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-create-task`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            id,
            note: '1' // '1' 表示生成演讲稿备注
        })
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`生成演讲稿失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data.id;
}

/**
 * 获取 PPT 模板封面预览
 * @param {Object} params - 封面参数 (title, count, user_name, color, style, size)
 * @param {string} apiKey - API Key
 */
async function getPptCovers(params, apiKey) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-cover`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(params)
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`获取封面失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data;
}

/**
 * 插入新页面
 * @param {string} id - 任务 ID
 * @param {Object} pageParams - 页面参数 (slide_number, slide_type, text)
 * @param {string} apiKey - API Key
 */
async function insertPage(id, pageParams, apiKey) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-page`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            id,
            page_index: pageParams.slide_number,
            type: pageParams.slide_type,
            text: pageParams.text
        })
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`插入页面失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data.id;
}

/**
 * 获取 Banana PPT 风格/模板列表
 * @param {string} type - 类型 ('style' 或 'template')
 * @param {string} apiKey - API Key
 */
async function getBananaStyles(type, apiKey) {
    const formData = new FormData();
    formData.append('type', type);

    const response = await fetch(`${API_BASE_URL}/apps/ppt-banana-style`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`
        },
        body: formData
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`获取风格失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data;
}

/**
 * 创建 Banana PPT 生成任务 (绘图PPT)
 * @param {Object} params - 参数 (text, complex, style, import_image, doc_type)
 * @param {string} apiKey - API Key
 */
async function createBananaPptTask(params, apiKey) {
    const response = await fetch(`${API_BASE_URL}/apps/ppt-banana`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(params)
    });

    const result = await response.json();
    if (!response.ok || result.code !== 200) {
        throw new Error(`创建任务失败 (HTTP ${response.status}): ${result.msg || response.statusText}`);
    }
    return result.data.id;
}

/**
 * 下载文件并保存到本地
 * @param {string} url - 下载链接
 * @param {string} outputPath - 保存路径
 */
async function downloadFile(url, outputPath) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`下载文件失败: ${response.statusText}`);
    }
    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    fs.writeFileSync(outputPath, buffer);
}

module.exports = {
    createPptTask,
    getPptResult,
    getDownloadUrl,
    getEditorUrl,
    regeneratePpt,
    addSpeakerNotes,
    insertPage,
    getPptCovers,
    getBananaStyles,
    createBananaPptTask,
    downloadFile
};
