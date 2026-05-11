const fs = require('fs');
const path = require('path');
const { 
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
} = require('./ppt_api');
const { 
    parseMarkdownToCustomData, 
    summarizeCatalogs, 
    validateCustomData 
} = require('./outline_parser');
const { analyzeProject } = require('./project_analyzer');

const DEFAULT_CONFIG = {
    font_name: '黑体',
    color: '蓝色',
    language: 'zh-CN',
    complex: 1,
    ai_picture: false,
    output_dir: 'outputs'
};

const TASKS_FILE = path.join(process.cwd(), '.tasks.json');

// 获取配置（支持 output_dir）
function getConfig() {
    const configPath = path.join(__dirname, '..', 'config.json');
    let fileConfig = {};
    if (fs.existsSync(configPath)) {
        try {
            fileConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        } catch (e) {}
    }
    return { ...DEFAULT_CONFIG, ...fileConfig };
}

// 任务持久化
function saveTask(taskId, title, status = 'processing') {
    let tasks = {};
    try {
        if (fs.existsSync(TASKS_FILE)) {
            tasks = JSON.parse(fs.readFileSync(TASKS_FILE, 'utf8'));
        }
    } catch (e) {}
    tasks[taskId] = { title, status, updated_at: new Date().toISOString() };
    fs.writeFileSync(TASKS_FILE, JSON.stringify(tasks, null, 2));
}

// 获取 Prompt 模板
function getPrompt(type, variables) {
    const promptPath = path.join(__dirname, '..', 'references', 'prompts.md');
    if (!fs.existsSync(promptPath)) {
        throw new Error('未找到 references/prompts.md 提示词库。');
    }
    const content = fs.readFileSync(promptPath, 'utf8');
    const sections = content.split('---');
    let template = '';
    if (type === 'file_review') {
        template = sections[0].split('## 1. 通用文件分析大纲生成 (create_from_file_with_review)')[1];
    } else if (type === 'project_analysis') {
        template = sections[1].split('## 2. AI 编码项目分析汇报 (create_from_project_analysis)')[1];
    }

    if (!template) throw new Error(`未找到类型为 ${type} 的 Prompt 模板。`);

    let result = template.trim();
    for (const [key, val] of Object.entries(variables)) {
        result = result.replace(new RegExp(`{{${key}}}`, 'g'), val);
    }
    return result;
}

// 获取 API Key
function getApiKey() {
    // 优先从环境变量获取，方便开源部署
    if (process.env.YOO_AI_API_KEY) {
        return process.env.YOO_AI_API_KEY;
    }

    const configPath = path.join(__dirname, '..', 'config.json');
    if (fs.existsSync(configPath)) {
        try {
            const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
            if (config.API_KEY && config.API_KEY !== 'YOUR_API_KEY_HERE') {
                return config.API_KEY;
            }
        } catch (e) {
            // 忽略 JSON 解析错误，继续尝试其他方式
        }
    }

    throw new Error('未找到 API Key。请设置环境变量 YOO_AI_API_KEY 或在 config.json 中配置。');
}

// 通用轮询与下载逻辑
async function pollAndDownload(taskId, apiKey, title, report = true) {
    let status = 0;
    const startTime = Date.now();
    const timeout = 10 * 60 * 1000; // 延长超时时间至 10 分钟

    const config = getConfig();
    const outputDir = path.isAbsolute(config.output_dir) 
        ? config.output_dir 
        : path.join(process.cwd(), config.output_dir);
    
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log(`🔍 任务已启动，ID: ${taskId}`);
    saveTask(taskId, title, 'processing');
    
    // 立即获取编辑器链接作为“实时渲染工作台”
    let editorUrl = null;
    try {
        editorUrl = await getEditorUrl(taskId, apiKey, report);
        if (editorUrl) {
            console.log(`\n📺 [EDITOR_URL_START]${editorUrl}[EDITOR_URL_END]`);
            console.log('您的 PPT 正在实时渲染中，您可以点击上方链接进入“在线工作台”观看生成过程，并在完成后直接编辑。\n');
        }
    } catch (e) {
        console.log('ℹ️ 实时工作台链接准备中...');
    }

    while (status !== 2) {
        if (Date.now() - startTime > timeout) {
            saveTask(taskId, title, 'timeout');
            throw new Error('任务超时，请稍后使用 check_status 命令检查进度。');
        }
        const result = await getPptResult(taskId, apiKey);
        status = result.status;
        console.log(`⏳ 进度: ${result.progress}% - ${result.state_description || '处理中'}`);
        
        if (status === 2) break;
        if (status === -1 || status === 3) {
            saveTask(taskId, title, 'failed');
            const errorMsg = `生成失败 (状态码: ${status}): ${result.state_description || '未知错误'}`;
            console.error(`\n❌ ${errorMsg}`);
            console.log('💡 建议：请调用 validate_outline 命令诊断 JSON 数据是否存在格式或内容长度问题。');
            throw new Error(errorMsg);
        }
        await new Promise(r => setTimeout(r, 5000));
    }

    console.log('✨ 生成完成，正在同步至本地...');
    const downloadUrl = await getDownloadUrl(taskId, apiKey);
    const fileName = `${title.replace(/[\\\/\:\*\?\"\<\>\|]/g, '_')}_${taskId}.pptx`;
    const outputPath = path.join(outputDir, fileName);
    await downloadFile(downloadUrl, outputPath);
    
    // 如果之前没拿到编辑器链接（极少见情况），最后再尝试拿一次
    if (!editorUrl) {
        editorUrl = await getEditorUrl(taskId, apiKey, report);
    }
    
    console.log(`\n✅ PPT 已成功下载至: ${outputPath}`);
    saveTask(taskId, title, 'completed');
    
    if (editorUrl) {
        console.log(`\n📝 [EDITOR_URL_START]${editorUrl}[EDITOR_URL_END]`);
    }
    
    // 打印用于 Agent 识别的标记
    console.log(`\n[TASK_COMPLETED]${taskId}`);
}

// 绘图PPT专用轮询与下载逻辑
async function pollAndDownloadBanana(taskId, apiKey, title) {
    let status = 0;
    const startTime = Date.now();
    const timeout = 10 * 60 * 1000;

    const config = getConfig();
    const outputDir = path.isAbsolute(config.output_dir) 
        ? config.output_dir 
        : path.join(process.cwd(), config.output_dir);
    
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log(`🔍 [绘图PPT] 任务已启动，ID: ${taskId}`);
    console.log('⚠️  注意：此模式生成的 PPT 为图片型幻灯片，不支持编辑文本，但拥有极佳的视觉效果。');
    
    saveTask(taskId, title, 'processing');

    while (status !== 2) {
        if (Date.now() - startTime > timeout) {
            saveTask(taskId, title, 'timeout');
            throw new Error('任务超时，请稍后使用 check_status 命令检查进度。');
        }
        const result = await getPptResult(taskId, apiKey);
        status = result.status;
        console.log(`⏳ 进度: ${result.progress}% - ${result.state_description || '处理中'}`);
        
        if (status === 2) break;
        if (status === -1 || status === 3) {
            saveTask(taskId, title, 'failed');
            const errorMsg = `生成失败 (状态码: ${status}): ${result.state_description || '未知错误'}`;
            console.error(`\n❌ ${errorMsg}`);
            throw new Error(errorMsg);
        }
        await new Promise(r => setTimeout(r, 5000));
    }

    console.log('✨ 生成完成，正在同步至本地...');
    const downloadUrl = await getDownloadUrl(taskId, apiKey);
    const fileName = `${title.replace(/[\\\/\:\*\?\"\<\>\|]/g, '_')}_Banana_${taskId}.pptx`;
    const outputPath = path.join(outputDir, fileName);
    await downloadFile(downloadUrl, outputPath);
    
    console.log(`\n✅ PPT 已成功下载至: ${outputPath}`);
    saveTask(taskId, title, 'completed');
    
    console.log(`\n[TASK_COMPLETED]${taskId}`);
}

async function main() {
    const subcommand = process.argv[2];
    const args = {};
    for (let i = 3; i < process.argv.length; i++) {
        if (process.argv[i].startsWith('--')) {
            const key = process.argv[i].slice(2);
            args[key] = process.argv[i+1];
            i++;
        }
    }

    try {
        const apiKey = getApiKey();
        const config = getConfig();
        const report = args.report !== 'false'; // 默认为 true，除非显式指定为 'false'

        // 字体清洗逻辑 (Input Sanitization)
        // 拦截不支持的“微软雅黑”并替换为默认值，或者处理空值
        if (args.font_name === '微软雅黑') {
            args.font_name = config.font_name;
        }

        switch (subcommand) {
            case 'create_from_text': {
                const taskIdText = await createPptTask({
                    text: args.text,
                    font_name: args.font_name || config.font_name,
                    color: args.color || config.color,
                    language: args.language || config.language,
                    report: report,
                    complex: parseInt(args.complex) || config.complex,
                    ai_picture: args.ai_picture === 'true' || args.ai_picture === true
                }, apiKey);
                await pollAndDownload(taskIdText, apiKey, args.text, report);
                break;
            }

            case 'create_from_custom_outline': {
                let customData;
                if (args.file) {
                    customData = JSON.parse(fs.readFileSync(args.file, 'utf8'));
                } else {
                    customData = JSON.parse(args.custom_data);
                }

                // 增加校验逻辑，防止发送非法数据导致后端报错
                const validationErrors = validateCustomData(customData.custom_data || customData);
                if (validationErrors.length > 0) {
                    console.log('\n❌ 大纲数据校验失败：');
                    validationErrors.forEach(err => console.log(`  - ${err}`));
                    console.log('\n请参考最新的大纲样式修改数据。');
                    process.exit(1);
                }

                const taskIdOutline = await createPptTask({
                    custom_data: customData.custom_data || customData,
                    font_name: args.font_name || config.font_name,
                    color: args.color || config.color,
                    language: args.language || config.language,
                    report: report
                }, apiKey);
                await pollAndDownload(taskIdOutline, apiKey, (customData.custom_data || customData).title || 'Custom_PPT', report);
                break;
            }

            case 'add_notes': {
                const taskIdNotes = await addSpeakerNotes(args.task_id, apiKey);
                await pollAndDownload(taskIdNotes, apiKey, `Notes_${args.task_id}`, report);
                break;
            }

            case 'insert_page': {
                const taskIdPage = await insertPage(args.task_id, {
                    slide_number: args.slide_number,
                    slide_type: args.slide_type,
                    text: args.text
                }, apiKey);
                await pollAndDownload(taskIdPage, apiKey, `Insert_${args.task_id}`, report);
                break;
            }

            case 'regenerate': {
                const regenerateParams = {};
                if (args.font_name) regenerateParams.font_name = args.font_name;
                if (args.color) regenerateParams.color = args.color;
                if (args.cover_id) regenerateParams.cover_id = args.cover_id;
                if (args.transition) regenerateParams.transition = args.transition;
                
                const taskIdRegen = await regeneratePpt(args.task_id, regenerateParams, apiKey);
                await pollAndDownload(taskIdRegen, apiKey, `Regen_${args.task_id}`, report);
                break;
            }

            case 'create_from_file_with_review': {
                if (!args.file_path || !args.user_prompt) {
                    console.log('参数错误：需要提供 --file_path 与 --user_prompt');
                    process.exit(1);
                }
                // 读取文件内容
                if (!fs.existsSync(args.file_path)) {
                    throw new Error(`文件不存在: ${args.file_path}`);
                }
                const fileText = fs.readFileSync(args.file_path, 'utf8');
                const count_1 = (args.count_1 && Number(args.count_1)) || 6;
                const count_2 = (args.count_2 && Number(args.count_2)) || 4;
                const language = args.language || config.language;
                // 构建专家 Prompt
                const prompt = getPrompt('file_review', {
                    user_prompt: args.user_prompt,
                    file_text: fileText,
                    count_1,
                    count_2,
                    language
                });
                // 如果没有提供 markdown_path，则输出 Prompt 供 Agent 调用 LLM
                if (!args.markdown_path) {
                    console.log('[PROMPT_START]');
                    console.log(prompt);
                    console.log('[PROMPT_END]');
                    console.log('请使用上述 Prompt 生成 Markdown 大纲，并保存到文件后，重新运行本命令：');
                    console.log(`node scripts/chatppt_creator.js create_from_file_with_review --file_path "${args.file_path}" --user_prompt "${args.user_prompt}" --count_1 ${count_1} --count_2 ${count_2} --language ${language} --markdown_path "<markdown文件路径>"`);
                    break;
                }
                // 解析 Markdown 为 custom_data
                if (!fs.existsSync(args.markdown_path)) {
                    throw new Error(`找不到 Markdown 文件: ${args.markdown_path}`);
                }
                const markdown = fs.readFileSync(args.markdown_path, 'utf8');
                const customData = parseMarkdownToCustomData(markdown);
                const ts = Date.now();
                const jsonPath = path.join(process.cwd(), `ppt_outline_${ts}.json`);
                fs.writeFileSync(jsonPath, JSON.stringify({ custom_data: customData }, null, 2), 'utf8');
                // 输出简化大纲供审阅
                const summary = summarizeCatalogs(customData);
                console.log('\n[OUTLINE_REVIEW_START]');
                console.log(summary);
                console.log('[OUTLINE_REVIEW_END]\n');
                console.log(`[OUTLINE_JSON_PATH]${jsonPath}`);
                console.log('\n⚠️  请将上述大纲展示给用户确认。');
                console.log('确认无误后运行：');
                console.log(`node scripts/chatppt_creator.js generate_from_outline --json_path "${jsonPath}" --font_name "${config.font_name}" --color "${config.color}" --language "${language}"`);
                console.log('\n如需修改，请提供补丁 JSON 文件并运行：');
                console.log('node scripts/chatppt_creator.js apply_outline_patch --json_path "<outline.json>" --patch_path "<patch.json>"');
                break;
            }

            case 'apply_outline_patch': {
                if (!args.json_path || !args.patch_path) {
                    console.log('参数错误：需要提供 --json_path 与 --patch_path');
                    process.exit(1);
                }
                const outline = JSON.parse(fs.readFileSync(args.json_path, 'utf8'));
                const patch = JSON.parse(fs.readFileSync(args.patch_path, 'utf8'));
                const data = outline.custom_data;
                // 支持的补丁操作：remove_catalog, rename_catalog, remove_sub_catalog, rename_sub_catalog
                if (patch.remove_catalog && Array.isArray(patch.remove_catalog)) {
                    // 按降序删除以避免索引错乱
                    patch.remove_catalog.sort((a, b) => b - a).forEach(idx => {
                        if (idx >= 0 && idx < data.catalogs.length) {
                            data.catalogs.splice(idx, 1)
                            // 同步删除 contents 中对应 catalog_index 的项
                            data.contents = data.contents
                                .filter(c => c.catalog_index !== idx)
                                .map(c => {
                                    if (c.catalog_index > idx) c.catalog_index -= 1
                                    return c
                                })
                        }
                    })
                }
                if (patch.rename_catalog && Array.isArray(patch.rename_catalog)) {
                    patch.rename_catalog.forEach(({ index, title }) => {
                        if (index >= 0 && index < data.catalogs.length && typeof title === 'string') {
                            data.catalogs[index].catalog = title
                        }
                    })
                }
                if (patch.remove_sub_catalog && Array.isArray(patch.remove_sub_catalog)) {
                    patch.remove_sub_catalog.forEach(({ catalog_index, sub_index }) => {
                        const cat = data.catalogs[catalog_index]
                        if (cat && sub_index >= 0 && sub_index < cat.sub_catalog.length) {
                            cat.sub_catalog.splice(sub_index, 1)
                            data.contents = data.contents
                                .filter(c => !(c.catalog_index === catalog_index && c.sub_catalog_index === sub_index))
                                .map(c => {
                                    if (c.catalog_index === catalog_index && c.sub_catalog_index > sub_index) {
                                        c.sub_catalog_index -= 1
                                    }
                                    return c
                                })
                        }
                    })
                }
                if (patch.rename_sub_catalog && Array.isArray(patch.rename_sub_catalog)) {
                    patch.rename_sub_catalog.forEach(({ catalog_index, sub_index, title }) => {
                        const cat = data.catalogs[catalog_index]
                        if (cat && sub_index >= 0 && sub_index < cat.sub_catalog.length && typeof title === 'string') {
                            cat.sub_catalog[sub_index] = title
                        }
                    })
                }
                fs.writeFileSync(args.json_path, JSON.stringify({ custom_data: data }, null, 2), 'utf8')
                console.log('\n[OUTLINE_PATCH_APPLIED]SUCCESS')
                console.log('[OUTLINE_REVIEW_START]')
                console.log(summarizeCatalogs(data))
                console.log('[OUTLINE_REVIEW_END]\n')
                break;
            }

            case 'generate_from_outline': {
                if (!args.json_path) {
                    console.log('参数错误：需要提供 --json_path')
                    process.exit(1);
                }
                const finalOutline = JSON.parse(fs.readFileSync(args.json_path, 'utf8'));
                
                // 预校验
                const validationErrors = validateCustomData(finalOutline.custom_data);
                if (validationErrors.length > 0) {
                    console.log('\n❌ JSON 校验失败，请修正后重试：');
                    validationErrors.forEach(err => console.log(`  - ${err}`));
                    console.log(`\n请检查文件: ${args.json_path}`);
                    process.exit(1);
                }

                const genTaskId = await createPptTask({
                    custom_data: finalOutline.custom_data,
                    font_name: args.font_name || config.font_name,
                    color: args.color || config.color,
                    language: args.language || config.language,
                    report: report
                }, apiKey);
                await pollAndDownload(genTaskId, apiKey, finalOutline.custom_data.title || 'Final_PPT', report);
                break;
            }

            case 'validate_outline': {
                if (!args.json_path) {
                    console.log('参数错误：需要提供 --json_path')
                    process.exit(1);
                }
                const outline = JSON.parse(fs.readFileSync(args.json_path, 'utf8'));
                const errors = validateCustomData(outline.custom_data || outline);
                if (errors.length === 0) {
                    console.log('✅ JSON 格式正确，可以生成 PPT。');
                } else {
                    console.log('❌ 发现以下错误：');
                    errors.forEach(err => console.log(`  - ${err}`));
                }
                break;
            }

            case 'create_from_project_analysis': {
                if (!args.project_path || !args.user_prompt) {
                    console.log('参数错误：需要提供 --project_path 与 --user_prompt');
                    process.exit(1);
                }
                
                // 1. 代码库分析
                console.log(`🔍 正在分析项目: ${args.project_path}...`);
                const projectSummary = analyzeProject(args.project_path);
                
                const count_1 = (args.count_1 && Number(args.count_1)) || 7;
                const count_2 = (args.count_2 && Number(args.count_2)) || 4;
                const language = args.language || config.language;

                // 2. 构建专家 Prompt
                const prompt = getPrompt('project_analysis', {
                    user_prompt: args.user_prompt,
                    project_summary: projectSummary,
                    count_1,
                    count_2,
                    language
                });

                if (!args.markdown_path) {
                    console.log('[PROMPT_START]');
                    console.log(prompt);
                    console.log('[PROMPT_END]');
                    console.log('\n--- 项目分析已完成 ---');
                    console.log(projectSummary);
                    console.log('\n请使用上述 Prompt 生成 Markdown 大纲，保存后运行：');
                    console.log(`node scripts/chatppt_creator.js create_from_project_analysis --project_path "${args.project_path}" --user_prompt "${args.user_prompt}" --markdown_path "<markdown路径>"`);
                    break;
                }

                // 3. 解析与审阅 (复用逻辑)
                const markdown = fs.readFileSync(args.markdown_path, 'utf8');
                const customData = parseMarkdownToCustomData(markdown);
                const ts = Date.now();
                const jsonPath = path.join(process.cwd(), `project_ppt_${ts}.json`);
                fs.writeFileSync(jsonPath, JSON.stringify({ custom_data: customData }, null, 2), 'utf8');
                
                console.log('\n[OUTLINE_REVIEW_START]');
                console.log(summarizeCatalogs(customData));
                console.log('[OUTLINE_REVIEW_END]\n');
                console.log(`[OUTLINE_JSON_PATH]${jsonPath}`);
                console.log('\n⚠️  请将上述大纲展示给用户确认。');
                console.log('确认无误后运行：');
                console.log(`node scripts/chatppt_creator.js generate_from_outline --json_path "${jsonPath}"`);
                break;
            }

            case 'check_status': {
                if (!fs.existsSync(TASKS_FILE)) {
                    console.log('ℹ️ 暂无历史任务记录。');
                    break;
                }
                const tasks = JSON.parse(fs.readFileSync(TASKS_FILE, 'utf8'));
                if (args.task_id) {
                    const task = tasks[args.task_id];
                    if (task) {
                        console.log(`\n任务 ID: ${args.task_id}`);
                        console.log(`标题: ${task.title}`);
                        console.log(`状态: ${task.status}`);
                        console.log(`更新时间: ${task.updated_at}`);
                        
                        const result = await getPptResult(args.task_id, apiKey);
                        console.log(`实时进度: ${result.progress}% - ${result.state_description || '处理中'}`);
                        if (result.preview_url) {
                            console.log(`预览链接: [PREVIEW_URL_START]${result.preview_url}[PREVIEW_URL_END]`);
                        }
                    } else {
                        console.log(`❌ 未找到任务: ${args.task_id}`);
                    }
                } else {
                    console.log('\n📋 历史任务列表 (最近 10 条):');
                    Object.entries(tasks).slice(-10).reverse().forEach(([id, t]) => {
                        console.log(`- [${t.status}] ${t.title} (ID: ${id})`);
                    });
                }
                break;
            }

            case 'preview_covers': {
                if (!args.title) {
                    console.log('参数错误：需要提供 --title');
                    process.exit(1);
                }
                const covers = await getPptCovers({
                    title: args.title,
                    count: parseInt(args.count) || 4,
                    user_name: args.user_name || '尤小优',
                    color: args.color,
                    style: args.style,
                    size: args.size || '3'
                }, apiKey);

                console.log('\n[COVER_PREVIEW_START]');
                covers.forEach((c, i) => {
                    console.log(`--- 模板 ${i + 1} ---`);
                    console.log(`ID: ${c.cover_id}`);
                    console.log(`颜色: ${c.color}`);
                    console.log(`预览图: [IMAGE_URL_START]${c.cover_image}[IMAGE_URL_END]`);
                });
                console.log('[COVER_PREVIEW_END]\n');
                console.log('您可以选择一个喜欢的模板 ID，并在创建或重新生成 PPT 时通过 --cover_id 参数使用它。');
                break;
            }

            case 'list_banana_styles': {
                const type = args.type || 'style'; // 'style' or 'template'
                const styles = await getBananaStyles(type, apiKey);
                console.log(`\n[BANANA_STYLES_START]`);
                styles.forEach((s, i) => {
                    const id = s.style_id;
                    const name = s.name || s.style_name;
                    const preview = s.images ? (s.images.cover_image || s.images.cover_url) : '无预览图';
                    console.log(`--- 样式 ${i + 1} ---`);
                    console.log(`ID: ${id}`);
                    console.log(`名称: ${name}`);
                    console.log(`预览: [IMAGE_URL_START]${preview}[IMAGE_URL_END]`);
                });
                console.log(`[BANANA_STYLES_END]\n`);
                console.log('请选择一个 ID，使用 create_banana_ppt --style "<ID>" 进行生成。');
                break;
            }

            case 'create_banana_ppt': {
                if (!args.text) {
                    console.log('参数错误：需要提供 --text');
                    process.exit(1);
                }
                const taskId = await createBananaPptTask({
                    text: args.text,
                    complex: parseInt(args.complex) || 1,
                    style: args.style,
                    import_image: args.import_image,
                    doc_type: args.doc_type
                }, apiKey);
                
                await pollAndDownloadBanana(taskId, apiKey, args.text);
                break;
            }

            default:
                console.log('未知子命令');
        }
    } catch (error) {
        console.error(`❌ 错误: ${error.message}`);
        process.exit(1);
    }
}

main();
