# 🧠 OpenClaw Master Skills

<div align="center">

<a href="https://myclaw.ai">
  <img src="https://img.shields.io/badge/Powered%20by-MyClaw.ai-blue?style=for-the-badge" alt="Powered by MyClaw.ai" />
</a>
<img src="https://img.shields.io/badge/Updated-Weekly-green?style=for-the-badge" alt="Weekly Updates" />
<img src="https://img.shields.io/badge/Skills-Curated-orange?style=for-the-badge" alt="Curated" />

**A curated collection of the best OpenClaw skills from around the web.**
Reviewed, tested, and updated every week by the [MyClaw.ai](https://myclaw.ai) team.

[Browse Skills](#-skill-index) · [Submit a Skill](#-submit-a-skill) · [Weekly Updates](#-weekly-updates) · [Install Guide](#-how-to-install)

</div>

---

## 🤖 What is This?

[OpenClaw](https://openclaw.ai) agents are powered by **Skills** — modular packages that teach your AI how to do specific tasks. This repo is the community's best collection, hand-curated from:

- [ClaWHub](https://clawhub.ai) — the official skill registry
- GitHub repos tagged `openclaw-skill`
- Community submissions via Issues
- MyClaw.ai's internal production skill library

Every skill in this collection has been **reviewed for quality, tested for correctness, and is kept up to date**.

> 🌐 **Want a fully-managed AI agent?** Try [MyClaw.ai](https://myclaw.ai)

---

## 📦 Skill Index

| Skill | Description | Category | Source | Added |
|---|---|---|---|---|
| [openclaw-guardian](skills/openclaw-guardian/) | 🛡️ Gateway watchdog with auto-repair & git rollback | DevOps | [GitHub](https://github.com/LeoYeAI/openclaw-guardian) | 2026-03-02 |

> More skills added every week. [Submit yours →](#-submit-a-skill)

---

## 🚀 How to Install

### Install a single skill

```bash
# Via ClaWHub CLI
clawhub install <skill-name>

# Or clone this repo and copy manually
git clone https://github.com/LeoYeAI/openclaw-master-skills.git
cp -r openclaw-master-skills/skills/<skill-name> ~/.openclaw/workspace/skills/
```

### Install all skills at once

```bash
git clone https://github.com/LeoYeAI/openclaw-master-skills.git
cp -r openclaw-master-skills/skills/. ~/.openclaw/workspace/skills/
```

### Stay up to date

```bash
cd openclaw-master-skills
git pull
cp -r skills/. ~/.openclaw/workspace/skills/
```

---

## 📬 Submit a Skill

Have a skill you'd like to share? There are two ways:

### Option 1: GitHub Issue (easiest)

[Open a "Submit Skill" issue](../../issues/new?template=submit-skill.md) and fill in the template. We'll review and add it within a week.

### Option 2: Pull Request

1. Fork this repo
2. Add your skill folder under `skills/<your-skill-name>/`
3. Make sure it has a valid `SKILL.md` with frontmatter
4. Open a PR with a brief description

**Review criteria:**
- ✅ Valid `SKILL.md` with `name` and `description`
- ✅ Clear, useful purpose
- ✅ No hardcoded credentials or personal data
- ✅ Works on a standard OpenClaw setup

---

## 📅 Weekly Updates

We publish a weekly digest every **Monday** summarizing:
- New skills added
- Skills updated
- Community highlights

See [CHANGELOG.md](CHANGELOG.md) for the full history.

---

## 📁 Repo Structure

```
openclaw-master-skills/
├── skills/                    # ✅ Curated, ready-to-use skills
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
├── pending/                   # 🔍 Skills under review
├── scripts/
│   └── collect.sh             # Weekly collection & sync script
├── CHANGELOG.md               # Weekly update log
└── README.md
```

---

## 🔍 How We Collect Skills

Every week, our collection script:

1. **Scans ClaWHub** for newly published/updated skills
2. **Scans GitHub** for repos tagged `openclaw-skill`
3. **Reviews community submissions** from Issues
4. **Tests and validates** each skill
5. **Merges approved skills** into `skills/` and publishes the weekly digest

Want to automate collection for your own fork? See [scripts/collect.sh](scripts/collect.sh).

---

## 🌟 Categories

| Category | Description |
|---|---|
| `devops` | Deployment, monitoring, infrastructure |
| `productivity` | Calendar, email, task management |
| `coding` | Code generation, review, debugging |
| `data` | Database, analytics, data processing |
| `communication` | Messaging, notifications, social |
| `media` | Image, video, audio processing |
| `finance` | Budgeting, trading, accounting |
| `research` | Web search, summarization, knowledge |

---

## License

All skills retain their original licenses. This collection is MIT licensed.

© [MyClaw.ai](https://myclaw.ai) — Making AI agents accessible to everyone.
