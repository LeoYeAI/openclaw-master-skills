const fs = require('fs');
const path = require('path');

/**
 * 分析项目的核心逻辑
 */
function analyzeProject(projectPath) {
    if (!fs.existsSync(projectPath)) {
        throw new Error(`项目路径不存在: ${projectPath}`);
    }

    const summary = {
        type: '未知',
        techStack: [],
        dependencies: [],
        architecture: [],
        entryPoints: []
    };

    // 1. 依赖分析
    const depFiles = {
        'package.json': 'Node.js/Frontend',
        'requirements.txt': 'Python',
        'pyproject.toml': 'Python',
        'go.mod': 'Go',
        'pom.xml': 'Java/Maven',
        'build.gradle': 'Java/Gradle',
        'composer.json': 'PHP'
    };

    const frameworkMap = {
        'react': 'React',
        'vue': 'Vue',
        '@angular/core': 'Angular',
        'next': 'Next.js',
        'nuxt': 'Nuxt.js',
        'express': 'Express',
        'koa': 'Koa',
        '@nestjs/core': 'NestJS',
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'FastAPI',
        'spring-boot': 'Spring Boot',
        'gin-gonic/gin': 'Gin (Go)',
        'laravel/framework': 'Laravel'
    };

    for (const [file, type] of Object.entries(depFiles)) {
        const filePath = path.join(projectPath, file);
        if (fs.existsSync(filePath)) {
            summary.type = type;
            const content = fs.readFileSync(filePath, 'utf8');
            if (file === 'package.json') {
                try {
                    const pkg = JSON.parse(content);
                    const allDeps = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };
                    summary.dependencies = Object.keys(allDeps).slice(0, 20);
                    
                    // 识别框架
                    Object.entries(frameworkMap).forEach(([pkgName, frameName]) => {
                        if (allDeps[pkgName]) summary.techStack.push(frameName);
                    });
                } catch (e) {}
            } else if (file === 'requirements.txt') {
                const deps = content.split('\n')
                    .map(l => l.trim())
                    .filter(l => l && !l.startsWith('#'))
                    .map(l => l.split('==')[0].split('>=')[0].trim());
                summary.dependencies = deps.slice(0, 15);
                if (deps.some(d => d.toLowerCase().includes('django'))) summary.techStack.push('Django');
                if (deps.some(d => d.toLowerCase().includes('flask'))) summary.techStack.push('Flask');
                if (deps.some(d => d.toLowerCase().includes('fastapi'))) summary.techStack.push('FastAPI');
            } else {
                summary.dependencies = content.split('\n').filter(l => l.trim() && !l.startsWith('#')).slice(0, 10);
            }
        }
    }

    // 2. 架构分析 (识别常见目录模式)
    const architecturePatterns = {
        'components': '组件化开发 (Components)',
        'pages': '页面路由 (Pages)',
        'views': '视图层 (Views)',
        'api': '接口定义 (API)',
        'services': '业务逻辑层 (Services)',
        'controllers': '控制器层 (Controllers)',
        'models': '数据模型层 (Models)',
        'utils': '工具库 (Utils)',
        'hooks': 'React Hooks',
        'store': '状态管理 (Store/Redux/Vuex)',
        'middleware': '中间件 (Middleware)',
        'routes': '路由配置 (Routes)',
        'assets': '静态资源 (Assets)'
    };

    const identifiedPatterns = new Set();
    const scanDirs = (dir, depth = 0) => {
        if (depth > 2) return;
        try {
            const files = fs.readdirSync(dir, { withFileTypes: true });
            files.forEach(file => {
                if (file.isDirectory() && !['node_modules', '.git', 'dist', 'build', '.next', '.nuxt'].includes(file.name)) {
                    summary.architecture.push(`${'  '.repeat(depth)}/${file.name}`);
                    if (architecturePatterns[file.name.toLowerCase()]) {
                        identifiedPatterns.add(architecturePatterns[file.name.toLowerCase()]);
                    }
                    scanDirs(path.join(dir, file.name), depth + 1);
                }
            });
        } catch (e) {}
    };
    scanDirs(projectPath);
    summary.patterns = Array.from(identifiedPatterns);

    // 3. 入口点分析
    const commonEntries = [
        'src/index.js', 'src/main.js', 'src/index.tsx', 'src/App.tsx',
        'index.js', 'app.js', 'server.js', 'main.py', 'app.py', 'main.go'
    ];
    commonEntries.forEach(entry => {
        if (fs.existsSync(path.join(projectPath, entry))) {
            summary.entryPoints.push(entry);
        }
    });

    return formatSummary(summary);
}

function formatSummary(s) {
    const archSummary = s.patterns.length > 0 
        ? `该项目采用了 ${s.patterns.join('、')} 等典型架构模式，目录结构清晰，职责分明。`
        : `该项目采用通用的目录组织方式。`;

    return [
        `项目分析摘要:`,
        `- 项目类型: ${s.type}`,
        `- 核心技术栈: ${s.techStack.join(', ') || '根据依赖推断中'}`,
        `- 主要依赖: ${s.dependencies.join(', ')}`,
        `- 项目架构: ${archSummary}`,
        `- 详细目录结构:`,
        ...s.architecture.map(line => `  ${line}`),
        `- 启动入口: ${s.entryPoints.join(', ') || '未识别'}`
    ].join('\n');
}

module.exports = { analyzeProject };
