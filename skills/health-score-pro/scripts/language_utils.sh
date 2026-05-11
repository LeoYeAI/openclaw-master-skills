#!/bin/bash

# 语言工具函数库
# 用途：提供统一的语言获取和多语言支持功能

# 获取用户语言
# 优先级：profile.md > 环境变量 > 默认值(zh-CN)
get_user_language() {
    local username="${1:-}"
    local profile_file
    
    # 如果提供了用户名，读取用户的 profile.md
    if [ -n "$username" ]; then
        profile_file="$HOME/.openclaw/workspace/memory/health-users/$username/profile.md"
    else
        # 尝试从全局配置读取
        profile_file="$HOME/.openclaw/workspace/memory/health-users/.default_language"
    fi
    
    # 从 profile.md 读取语言
    if [ -f "$profile_file" ]; then
        local language=$(grep -E "^\s*-\s*\*\*Language\*\*:" "$profile_file" | sed 's/.*\*\*Language\*\*:\s*//' | tr -d ' ')
        if [ -n "$language" ]; then
            echo "$language"
            return 0
        fi
    fi
    
    # 从环境变量读取
    if [ -n "$HEALTH_LANGUAGE" ]; then
        echo "$HEALTH_LANGUAGE"
        return 0
    fi
    
    # 默认值：zh-CN（中文）
    echo "zh-CN"
}

# 获取本地化文本
# 用法：get_localized_text "key" "language"
get_localized_text() {
    local key="$1"
    local language="${2:-$(get_user_language)}"
    
    case "$language" in
        zh-CN|zh)
            # 中文
            case "$key" in
                "backup.success") echo "✅ 数据已安全备份到 GitHub！" ;;
                "backup.failed") echo "❌ 备份未完成，请检查网络或 Git 配置" ;;
                "backup.no_changes") echo "ℹ️  没有需要备份的更改" ;;
                "backup.paused") echo "⚠️  自动备份已暂停" ;;
                "backup.configured") echo "✅ 备份功能已配置" ;;
                "time.now") date '+%Y年%m月%d日 %H:%M:%S %Z' ;;
                "time.timezone") echo "用户时区" ;;
                *) echo "$key" ;;
            esac
            ;;
        en)
            # English
            case "$key" in
                "backup.success") echo "✅ Data successfully backed up to GitHub!" ;;
                "backup.failed") echo "❌ Backup failed. Please check network or Git configuration" ;;
                "backup.no_changes") echo "ℹ️  No changes to backup" ;;
                "backup.paused") echo "⚠️  Auto backup is paused" ;;
                "backup.configured") echo "✅ Backup feature configured" ;;
                "time.now") date '+%Y-%m-%d %H:%M:%S %Z' ;;
                "time.timezone") echo "User timezone" ;;
                *) echo "$key" ;;
            esac
            ;;
        ja)
            # 日本語
            case "$key" in
                "backup.success") echo "✅ データがGitHubに正常にバックアップされました！" ;;
                "backup.failed") echo "❌ バックアップに失敗しました。ネットワークまたはGit設定を確認してください" ;;
                "backup.no_changes") echo "ℹ️  バックアップする変更はありません" ;;
                "backup.paused") echo "⚠️  自動バックアップは一時停止中です" ;;
                "backup.configured") echo "✅ バックアップ機能が設定されました" ;;
                "time.now") date '+%Y年%m月%d日 %H:%M:%S %Z' ;;
                "time.timezone") echo "ユーザータイムゾーン" ;;
                *) echo "$key" ;;
            esac
            ;;
        ko)
            # 한국어
            case "$key" in
                "backup.success") echo "✅ 데이터가 GitHub에 안전하게 백업되었습니다!" ;;
                "backup.failed") echo "❌ 백업 실패. 네트워크 또는 Git 설정을 확인하세요" ;;
                "backup.no_changes") echo "ℹ️  백업할 변경 사항이 없습니다" ;;
                "backup.paused") echo "⚠️  자동 백업이 일시 중지됨" ;;
                "backup.configured") echo "✅ 백업 기능이 구성됨" ;;
                "time.now") date '+%Y년%m월%d일 %H:%M:%S %Z' ;;
                "time.timezone") echo "사용자 시간대" ;;
                *) echo "$key" ;;
            esac
            ;;
        fr)
            # Français
            case "$key" in
                "backup.success") echo "✅ Données sauvegardées avec succès sur GitHub !" ;;
                "backup.failed") echo "❌ Échec de la sauvegarde. Vérifiez le réseau ou la configuration Git" ;;
                "backup.no_changes") echo "ℹ️  Aucun changement à sauvegarder" ;;
                "backup.paused") echo "⚠️  Sauvegarde automatique en pause" ;;
                "backup.configured") echo "✅ Fonction de sauvegarde configurée" ;;
                "time.now") date '+%Y-%m-%d %H:%M:%S %Z' ;;
                "time.timezone") echo "Fuseau horaire utilisateur" ;;
                *) echo "$key" ;;
            esac
            ;;
        de)
            # Deutsch
            case "$key" in
                "backup.success") echo "✅ Daten erfolgreich auf GitHub gesichert!" ;;
                "backup.failed") echo "❌ Backup fehlgeschlagen. Bitte Netzwerk oder Git-Konfiguration prüfen" ;;
                "backup.no_changes") echo "ℹ️  Keine Änderungen zum Sichern" ;;
                "backup.paused") echo "⚠️  Automatisches Backup pausiert" ;;
                "backup.configured") echo "✅ Backup-Funktion konfiguriert" ;;
                "time.now") date '+%Y-%m-%d %H:%M:%S %Z' ;;
                "time.timezone") echo "Benutzerzeitzone" ;;
                *) echo "$key" ;;
            esac
            ;;
        es)
            # Español
            case "$key" in
                "backup.success") echo "✅ ¡Datos respaldados exitosamente en GitHub!" ;;
                "backup.failed") echo "❌ Error de respaldo. Verifica la red o configuración de Git" ;;
                "backup.no_changes") echo "ℹ️  No hay cambios para respaldar" ;;
                "backup.paused") echo "⚠️  Respaldo automático pausado" ;;
                "backup.configured") echo "✅ Función de respaldo configurada" ;;
                "time.now") date '+%Y-%m-%d %H:%M:%S %Z' ;;
                "time.timezone") echo "Zona horaria del usuario" ;;
                *) echo "$key" ;;
            esac
            ;;
        *)
            # 默认：中文
            get_localized_text "$key" "zh-CN"
            ;;
    esac
}

# 验证语言代码是否有效
# 用法：validate_language "zh-CN"
validate_language() {
    local language="$1"
    
    case "$language" in
        zh-CN|zh|en|ja|ko|fr|de|es)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# 列出支持的语言
list_supported_languages() {
    cat <<EOF
🌐 支持的语言列表

🇨🇳 中文（简体）
  zh-CN (默认)

🇺🇸 English
  en

🇯🇵 日本語
  ja

🇰🇷 한국어
  ko

🇫🇷 Français
  fr

🇩🇪 Deutsch
  de

🇪🇸 Español
  es
EOF
}

# 如果直接执行此脚本，显示帮助信息
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo "语言工具函数库"
    echo ""
    echo "用法："
    echo "  source language_utils.sh"
    echo "  language=\$(get_user_language [username])"
    echo "  text=\$(get_localized_text \"key\" [language])"
    echo ""
    echo "测试："
    echo "  当前语言：$(get_user_language)"
    echo "  备份成功（中文）：$(get_localized_text 'backup.success' 'zh-CN')"
    echo "  备份成功（英文）：$(get_localized_text 'backup.success' 'en')"
fi
