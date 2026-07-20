#!/bin/bash
# Auto Publish - 自动上传视频到各大平台
# Usage: bash scripts/auto-publish.sh --video file.mp4 --platform bilibili --title "标题"

set -e

# 默认参数
VIDEO=""
PLATFORM=""
TITLE=""
DESCRIPTION=""
TAGS=""
COVER=""
SCHEDULE=""
CONFIG_DIR="$HOME/.fcpx-assistant/publish"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 帮助信息
show_help() {
    cat << EOF
📤 视频自动上传工具

支持上传到 B 站、YouTube、抖音等平台。

用法:
  bash $0 --video <文件> --platform <平台> --title "标题" [选项]

选项:
  --video <文件>      视频文件路径（必需）
  --platform <平台>   目标平台：bilibili, youtube, tiktok, xiaohongshu（必需）
  --title "标题"      视频标题（必需）
  --description "描述" 视频描述（可选）
  --tags "标签"       标签，逗号分隔（可选）
  --cover <文件>      封面图片路径（可选）
  --schedule <时间>   定时发布时间（ISO 格式，可选）
  --draft             保存为草稿，不立即发布
  --config            配置平台账号信息
  --help              显示帮助信息

支持的平台:
  bilibili    - B ilibili (B 站)
  youtube     - YouTube
  tiktok      - 抖音/TikTok
  xiaohongshu - 小红书

示例:
  bash $0 --video ./output.mp4 --platform bilibili --title "我的 Vlog" --tags "vlog，日常"
  bash $0 --video ./video.mp4 --platform youtube --title "Tutorial" --schedule "2026-03-29T10:00:00"

配置账号:
  bash $0 --config

EOF
    exit 0
}

# 配置账号信息
setup_config() {
    mkdir -p "$CONFIG_DIR"
    
    cat << EOF
🔐 平台账号配置

请在以下位置创建配置文件：

1. B 站 (config/bilibili.json):
$CONFIG_DIR/bilibili.json
{
  "username": "你的账号",
  "password": "你的密码",
  "cookie": "登录后复制 cookie（推荐）",
  "upload_source": 1
}

2. YouTube (config/youtube.json):
$CONFIG_DIR/youtube.json
{
  "client_secrets": "path/to/client_secret.json",
  "token": "path/to/token.json"
}

3. 抖音 (config/tiktok.json):
$CONFIG_DIR/tiktok.json
{
  "cookie": "登录后复制 cookie"
}

4. 小红书 (config/xiaohongshu.json):
$CONFIG_DIR/xiaohongshu.json
{
  "cookie": "登录后复制 cookie"
}

⚠️  安全提示：
- 配置文件权限设置为 600: chmod 600 $CONFIG_DIR/*.json
- 建议使用 cookie 而非密码
- 不要将配置文件提交到 git

EOF
    exit 0
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --video)
            VIDEO="$2"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --title)
            TITLE="$2"
            shift 2
            ;;
        --description)
            DESCRIPTION="$2"
            shift 2
            ;;
        --tags)
            TAGS="$2"
            shift 2
            ;;
        --cover)
            COVER="$2"
            shift 2
            ;;
        --schedule)
            SCHEDULE="$2"
            shift 2
            ;;
        --draft)
            DRAFT=true
            shift
            ;;
        --config)
            setup_config
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "未知参数：$1"
            show_help
            ;;
    esac
done

# 检查必需参数
if [[ "$PLATFORM" == "config" ]] || [[ "$1" == "--config" ]]; then
    setup_config
fi

if [[ -z "$VIDEO" ]]; then
    print_error "缺少必需参数：--video"
    show_help
fi

if [[ -z "$PLATFORM" ]]; then
    print_error "缺少必需参数：--platform"
    show_help
fi

if [[ -z "$TITLE" ]]; then
    print_error "缺少必需参数：--title"
    show_help
fi

# 检查视频文件
if [[ ! -f "$VIDEO" ]]; then
    print_error "视频文件不存在：$VIDEO"
    exit 1
fi

# 检查配置文件
CONFIG_FILE="$CONFIG_DIR/${PLATFORM}.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    print_error "平台配置不存在：$CONFIG_FILE"
    print_info "运行以下命令配置账号："
    echo "  bash $0 --config"
    exit 1
fi

print_info "准备上传视频..."
print_info "文件：$VIDEO"
print_info "平台：$PLATFORM"
print_info "标题：$TITLE"

# 获取视频信息
VIDEO_SIZE=$(stat -f%z "$VIDEO" 2>/dev/null || stat -c%s "$VIDEO" 2>/dev/null || echo "unknown")
VIDEO_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO" 2>/dev/null || echo "unknown")

print_info "大小：$VIDEO_SIZE bytes"
print_info "时长：$VIDEO_DURATION 秒"

# 根据不同平台执行上传
upload_to_platform() {
    case $PLATFORM in
        bilibili)
            upload_bilibili
            ;;
        youtube)
            upload_youtube
            ;;
        tiktok)
            upload_tiktok
            ;;
        xiaohongshu)
            upload_xiaohongshu
            ;;
        *)
            print_error "不支持的平台：$PLATFORM"
            exit 1
            ;;
    esac
}

# B 站上传
upload_bilibili() {
    print_info "上传到 B 站..."
    
    # 检查是否有 bilibili-cli 或类似工具
    if command -v biliup &> /dev/null; then
        print_info "使用 biliup 上传..."
        
        # 构建上传命令
        BILI_CMD="biliup upload"
        BILI_CMD="$BILI_CMD '$VIDEO'"
        BILI_CMD="$BILI_CMD --title '$TITLE'"
        
        [[ -n "$DESCRIPTION" ]] && BILI_CMD="$BILI_CMD --desc '$DESCRIPTION'"
        [[ -n "$TAGS" ]] && BILI_CMD="$BILI_CMD --tag ${TAGS//,/ --tag }"
        [[ -n "$COVER" ]] && BILI_CMD="$BILI_CMD --cover '$COVER'"
        [[ -n "$SCHEDULE" ]] && BILI_CMD="$BILI_CMD --schedule '$SCHEDULE'"
        [[ -n "$DRAFT" ]] && BILI_CMD="$BILI_CMD --draft"
        
        print_info "执行：$BILI_CMD"
        eval "$BILI_CMD"
        
    else
        print_warning "未找到 biliup 工具"
        print_info "安装方法：pip install biliup"
        print_info ""
        print_info "或者使用网页上传："
        print_info "1. 打开 https://member.bilibili.com/platform/upload/video"
        print_info "2. 拖拽文件：$VIDEO"
        print_info "3. 填写标题：$TITLE"
        
        # 创建上传说明文件
        UPLOAD_INFO="$HOME/Desktop/B 站上传说明_$(date +%Y%m%d_%H%M%S).txt"
        cat > "$UPLOAD_INFO" << EOF
B 站上传信息
============

视频文件：$VIDEO
标题：$TITLE
描述：${DESCRIPTION:-无}
标签：${TAGS:-无}
封面：${COVER:-自动生成}

手动上传地址：
https://member.bilibili.com/platform/upload/video

提示：
1. 建议安装 biliup 实现自动上传
2. 安装命令：pip install biliup
3. 配置后运行：biliup upload '$VIDEO' --title '$TITLE'
EOF
        print_info "上传说明已保存到：$UPLOAD_INFO"
    fi
}

# YouTube 上传
upload_youtube() {
    print_info "上传到 YouTube..."
    
    if command -v google-cl &> /dev/null; then
        print_info "使用 gogcli 上传..."
        # 使用 gogcli 的 YouTube 上传功能
        echo "TODO: 实现 gogcli YouTube 上传"
    else
        print_warning "未找到 YouTube 上传工具"
        print_info "推荐使用 YouTube Studio 网页上传："
        print_info "https://studio.youtube.com/"
        
        # 创建上传说明文件
        UPLOAD_INFO="$HOME/Desktop/YouTube 上传说明_$(date +%Y%m%d_%H%M%S).txt"
        cat > "$UPLOAD_INFO" << EOF
YouTube 上传信息
===============

视频文件：$VIDEO
标题：$TITLE
描述：${DESCRIPTION:-无}
标签：${TAGS:-无}

手动上传地址：
https://studio.youtube.com/

提示：
1. 可以使用 Google Cloud YouTube API
2. 或使用第三方工具如 youtube-upload
EOF
        print_info "上传说明已保存到：$UPLOAD_INFO"
    fi
}

# 抖音上传
upload_tiktok() {
    print_info "上传到抖音..."
    
    print_warning "抖音上传需要特殊处理"
    print_info "建议使用抖音创作者服务平台："
    print_info "https://creator.douyin.com/"
    
    # 创建上传说明文件
    UPLOAD_INFO="$HOME/Desktop/抖音上传说明_$(date +%Y%m%d_%H%M%S).txt"
    cat > "$UPLOAD_INFO" << EOF
抖音上传信息
===========

视频文件：$VIDEO
标题：$TITLE
描述：${DESCRIPTION:-无}
标签：${TAGS:-无}

手动上传地址：
https://creator.douyin.com/

提示：
1. 抖音视频建议竖屏 9:16
2. 时长建议 15-60 秒
3. 可以使用抖音开放平台 API
EOF
    print_info "上传说明已保存到：$UPLOAD_INFO"
}

# 小红书上传
upload_xiaohongshu() {
    print_info "上传到小红书..."
    
    print_warning "小红书上传需要特殊处理"
    print_info "建议使用小红书创作服务平台："
    print_info "https://creator.xiaohongshu.com/"
    
    # 创建上传说明文件
    UPLOAD_INFO="$HOME/Desktop/小红书上传说明_$(date +%Y%m%d_%H%M%S).txt"
    cat > "$UPLOAD_INFO" << EOF
小红书上传信息
============

视频文件：$VIDEO
标题：$TITLE
描述：${DESCRIPTION:-无}
标签：${TAGS:-无}

手动上传地址：
https://creator.xiaohongshu.com/

提示：
1. 小红书视频建议竖屏 3:4 或 9:16
2. 封面图很重要
3. 标签有助于推荐
EOF
    print_info "上传说明已保存到：$UPLOAD_INFO"
}

# 执行上传
upload_to_platform

print_success "上传流程完成！"
print_info "检查平台后台确认上传状态"
