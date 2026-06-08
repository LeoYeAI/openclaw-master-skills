# 公文字体清单

根据GB/T 9704-2012《党政机关公文格式》标准，公文生成需要以下字体：

| 字体名称 | 用途 | 文件名 | 是否必需 |
|---------|------|--------|---------|
| 方正小标宋_GBK | 用于发文机关标志、标题 | FZXBSJW.TTF, FZXBSJW_GB.TTF, 方正小标宋GBK.TTF, 方正小标宋_GBK.TTF | 是 |
| 仿宋_GB2312 | 用于正文、发文字号 | SIMFANG.TTF, FANGSONG.TTF | 是 |
| 黑体 | 用于一级标题、密级 | SIMHEI.TTF, HEITI.TTF | 是 |
| 楷体_GB2312 | 用于二级标题、签发人姓名 | SIMKAI.TTF, KAITI.TTF | 是 |
| 宋体 | 用于页码 | SIMSUN.TTF, SONGTI.TTF, SIMSUN.TTC, simsun.ttc | 是 |

## 字体下载说明

### 方式1：从系统字体目录复制

Windows系统字体目录：`C:\Windows\Fonts`

### 方式2：从官方渠道下载

1. **方正小标宋_GBK**
   - 官方网站：http://www.foundertype.com/
   - 说明：方正字库官方提供，需要授权使用

2. **仿宋_GB2312、黑体、楷体_GB2312、宋体**
   - Windows系统自带，可直接从系统字体目录复制
   - 或从微软官网下载

## 安装方法

### Windows系统
```powershell
# 以管理员身份运行PowerShell
python scripts/install_fonts.py
```

### macOS系统
```bash
python scripts/install_fonts.py
```

### Linux系统
```bash
python scripts/install_fonts.py
```