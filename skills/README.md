# 🛡️ OpenClaw Guardian

<div align="center">

<a href="https://myclaw.ai">
  <img src="https://img.shields.io/badge/Powered%20by-MyClaw.ai-blue?style=for-the-badge" alt="Powered by MyClaw.ai" />
</a>

**[English](#english) · [中文](#中文) · [Français](#français) · [Deutsch](#deutsch) · [Русский](#русский) · [日本語](#日本語) · [Italiano](#italiano) · [Español](#español)**

</div>

---

## 🤖 Powered by [MyClaw.ai](https://myclaw.ai)

**[MyClaw.ai](https://myclaw.ai)** is an AI personal assistant platform that gives every user a fully-featured AI agent running on a dedicated server — with complete code control, internet access, and tool integrations. Think of it as your own private AI that can actually *do* things, not just answer questions.

OpenClaw Guardian is an open-source project born from MyClaw.ai's production infrastructure. We run thousands of AI agent instances 24/7, and Guardian is the hardening layer that keeps them alive. We're open-sourcing it so everyone can benefit.

> 🌐 **Try MyClaw.ai**: [https://myclaw.ai](https://myclaw.ai)

---

<a name="english"></a>
## 🇬🇧 English

> A standalone watchdog that keeps your [OpenClaw](https://openclaw.ai) Gateway alive 24/7 — with automatic repair, git-based rollback, and optional Discord alerts.

### Features

- **Auto-monitor** — checks Gateway health every 30 seconds
- **Auto-repair** — runs `openclaw doctor --fix` on failure (up to 3 attempts)
- **Auto-rollback** — resets workspace to last stable git commit if repair fails
- **Daily snapshots** — automatic daily `git commit` of your workspace
- **Discord alerts** — optional webhook notifications on failures and recovery

### How It Works

```
Gateway down detected
        │
        ▼
  doctor --fix  ──→ success? ──→ ✅ Done
  (up to 3x)
        │ all failed
        ▼
  git rollback  ──→ success? ──→ ✅ Done
        │ failed
        ▼
  cooldown 300s → resume monitoring
```

### Quick Start

```bash
# 1. Initialize git in workspace
cd ~/.openclaw/workspace
git init && git add -A && git commit -m "initial"

# 2. Install
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh

# 3. Start
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### Configuration

| Variable | Default | Description |
|---|---|---|
| `GUARDIAN_WORKSPACE` | `$HOME/.openclaw/workspace` | Workspace git repo path |
| `GUARDIAN_CHECK_INTERVAL` | `30` | Health check interval (seconds) |
| `GUARDIAN_MAX_REPAIR` | `3` | Max repair attempts before rollback |
| `GUARDIAN_COOLDOWN` | `300` | Cooldown after all repairs fail (seconds) |
| `DISCORD_WEBHOOK_URL` | _(unset)_ | Discord webhook for alerts (optional) |

### Install as OpenClaw Skill

```bash
clawhub install openclaw-guardian
```

---

<a name="中文"></a>
## 🇨🇳 中文

> 一个独立运行的守护进程，确保你的 [OpenClaw](https://openclaw.ai) Gateway 全天候稳定运行 —— 支持自动修复、基于 git 的回滚，以及可选的 Discord 告警通知。

### 功能特性

- **自动监控** — 每 30 秒检测 Gateway 状态
- **自动修复** — 异常时执行 `openclaw doctor --fix`（最多 3 次）
- **自动回滚** — 修复失败后自动回滚到上一个稳定的 git commit
- **每日快照** — 每天自动对 workspace 创建 git 备份
- **Discord 告警** — 可选的故障与恢复 Webhook 通知

### 工作流程

```
检测到 Gateway 停止运行
        │
        ▼
  doctor --fix  ──→ 成功? ──→ ✅ 完成
  (最多 3 次)
        │ 全部失败
        ▼
  git 回滚  ──→ 成功? ──→ ✅ 完成
        │ 失败
        ▼
  冷却 300s → 继续监控
```

### 快速开始

```bash
# 1. 初始化 workspace git 仓库
cd ~/.openclaw/workspace
git init && git add -A && git commit -m "initial"

# 2. 安装
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh

# 3. 启动
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### 配置项

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `GUARDIAN_WORKSPACE` | `$HOME/.openclaw/workspace` | workspace git 仓库路径 |
| `GUARDIAN_CHECK_INTERVAL` | `30` | 检测间隔（秒） |
| `GUARDIAN_MAX_REPAIR` | `3` | 最大修复次数 |
| `GUARDIAN_COOLDOWN` | `300` | 全部失败后冷却时长（秒） |
| `DISCORD_WEBHOOK_URL` | _(未设置)_ | Discord 告警 Webhook（可选） |

### 作为 OpenClaw Skill 安装

```bash
clawhub install openclaw-guardian
```

---

<a name="français"></a>
## 🇫🇷 Français

> Un processus de surveillance autonome qui maintient votre passerelle [OpenClaw](https://openclaw.ai) opérationnelle 24h/24 — avec réparation automatique, retour arrière Git et alertes Discord optionnelles.

### Fonctionnalités

- **Surveillance automatique** — vérifie l'état de la passerelle toutes les 30 secondes
- **Réparation automatique** — exécute `openclaw doctor --fix` en cas de panne (jusqu'à 3 tentatives)
- **Retour arrière automatique** — réinitialise le workspace au dernier commit Git stable si la réparation échoue
- **Instantanés quotidiens** — sauvegarde Git automatique quotidienne du workspace
- **Alertes Discord** — notifications webhook optionnelles en cas de panne ou de rétablissement

### Démarrage rapide

```bash
# 1. Initialiser le dépôt Git
cd ~/.openclaw/workspace
git init && git add -A && git commit -m "initial"

# 2. Installer
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh

# 3. Démarrer
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### Installer en tant que Skill OpenClaw

```bash
clawhub install openclaw-guardian
```

---

<a name="deutsch"></a>
## 🇩🇪 Deutsch

> Ein eigenständiger Watchdog-Prozess, der Ihr [OpenClaw](https://openclaw.ai) Gateway rund um die Uhr am Laufen hält — mit automatischer Reparatur, Git-basiertem Rollback und optionalen Discord-Benachrichtigungen.

### Funktionen

- **Automatische Überwachung** — prüft den Gateway-Status alle 30 Sekunden
- **Automatische Reparatur** — führt `openclaw doctor --fix` bei Ausfall aus (bis zu 3 Versuche)
- **Automatischer Rollback** — setzt den Workspace auf den letzten stabilen Git-Commit zurück, wenn die Reparatur fehlschlägt
- **Tägliche Snapshots** — automatisches tägliches Git-Backup des Workspaces
- **Discord-Benachrichtigungen** — optionale Webhook-Benachrichtigungen bei Ausfällen und Wiederherstellungen

### Schnellstart

```bash
# 1. Git-Repository initialisieren
cd ~/.openclaw/workspace
git init && git add -A && git commit -m "initial"

# 2. Installieren
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh

# 3. Starten
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### Als OpenClaw Skill installieren

```bash
clawhub install openclaw-guardian
```

---

<a name="русский"></a>
## 🇷🇺 Русский

> Автономный сторожевой процесс, обеспечивающий круглосуточную работу вашего шлюза [OpenClaw](https://openclaw.ai) — с автоматическим восстановлением, откатом на основе Git и опциональными уведомлениями в Discord.

### Возможности

- **Автоматический мониторинг** — проверяет состояние шлюза каждые 30 секунд
- **Автоматическое восстановление** — запускает `openclaw doctor --fix` при сбое (до 3 попыток)
- **Автоматический откат** — сбрасывает рабочую область до последнего стабильного коммита Git при неудаче восстановления
- **Ежедневные снимки** — автоматическое ежедневное резервное копирование рабочей области через Git
- **Уведомления Discord** — опциональные webhook-уведомления о сбоях и восстановлении

### Быстрый старт

```bash
# 1. Инициализация Git-репозитория
cd ~/.openclaw/workspace
git init && git add -A && git commit -m "initial"

# 2. Установка
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh

# 3. Запуск
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### Установить как OpenClaw Skill

```bash
clawhub install openclaw-guardian
```

---

<a name="日本語"></a>
## 🇯🇵 日本語

> [OpenClaw](https://openclaw.ai) ゲートウェイを24時間365日稼働させる自律型ウォッチドッグプロセス — 自動修復、Gitベースのロールバック、オプションのDiscordアラート機能付き。

### 機能

- **自動監視** — 30秒ごとにゲートウェイの状態を確認
- **自動修復** — 障害時に `openclaw doctor --fix` を実行（最大3回）
- **自動ロールバック** — 修復失敗時に最後の安定したGitコミットにリセット
- **日次スナップショット** — ワークスペースの自動日次Gitバックアップ
- **Discordアラート** — 障害・復旧時のオプションWebhook通知

### クイックスタート

```bash
# 1. Gitリポジトリの初期化
cd ~/.openclaw/workspace
git init && git add -A && git commit -m "initial"

# 2. インストール
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh

# 3. 起動
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### OpenClaw Skillとしてインストール

```bash
clawhub install openclaw-guardian
```

---

<a name="italiano"></a>
## 🇮🇹 Italiano

> Un processo watchdog autonomo che mantiene il tuo gateway [OpenClaw](https://openclaw.ai) operativo 24 ore su 24 — con riparazione automatica, rollback basato su Git e avvisi Discord opzionali.

### Funzionalità

- **Monitoraggio automatico** — controlla lo stato del gateway ogni 30 secondi
- **Riparazione automatica** — esegue `openclaw doctor --fix` in caso di guasto (fino a 3 tentativi)
- **Rollback automatico** — ripristina il workspace all'ultimo commit Git stabile se la riparazione fallisce
- **Snapshot giornalieri** — backup Git automatico giornaliero del workspace
- **Avvisi Discord** — notifiche webhook opzionali per guasti e ripristini

### Avvio rapido

```bash
# 1. Inizializza il repository Git
cd ~/.openclaw/workspace
git init && git add -A && git commit -m "initial"

# 2. Installa
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh

# 3. Avvia
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### Installa come OpenClaw Skill

```bash
clawhub install openclaw-guardian
```

---

<a name="español"></a>
## 🇪🇸 Español

> Un proceso watchdog autónomo que mantiene tu gateway de [OpenClaw](https://openclaw.ai) funcionando las 24 horas del día — con reparación automática, reversión basada en Git y alertas opcionales de Discord.

### Características

- **Monitoreo automático** — comprueba el estado del gateway cada 30 segundos
- **Reparación automática** — ejecuta `openclaw doctor --fix` en caso de fallo (hasta 3 intentos)
- **Reversión automática** — restaura el workspace al último commit Git estable si la reparación falla
- **Instantáneas diarias** — copia de seguridad Git automática diaria del workspace
- **Alertas de Discord** — notificaciones webhook opcionales para fallos y recuperaciones

### Inicio rápido

```bash
# 1. Inicializar repositorio Git
cd ~/.openclaw/workspace
git init && git add -A && git commit -m "initial"

# 2. Instalar
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh

# 3. Iniciar
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### Instalar como OpenClaw Skill

```bash
clawhub install openclaw-guardian
```

---

## License

MIT © [LeoYeAI](https://github.com/LeoYeAI)
