# OpenClaw Setup

Use this skill with two required runtime configs only:

1. `base_url`
   Example: `https://your-blog.example.com`
2. `api_key`
   Value from POETIZE admin API settings

The skill does not need an admin cookie or browser session.
It calls the existing POETIZE API feature directly.
Use `{baseDir}` in commands so the installed skill can run from any OpenClaw workspace location.

## 中文说明

- 这是一个给 POETIZE 博客使用的 OpenClaw skill，通过站点已经提供的 `/api/api/*` 接口完成文章和运营动作。
- 专为 `awesome-poetize-open` 这个开源分支设计，以区别于原版项目。
- 只有 `awesome-poetize-open` 才完全兼容这个 skill，原版 POETIZE 不要直接接入。
- 运行时只需要两个关键值：站点域名 `base_url` 和后台生成的 `api_key`。
- 推荐在发布前先跑一次只读 smoke test，确认 OpenClaw、域名配置和 API 权限都正常。

## 安装方式一：让 OpenClaw 按提示词帮你安装（最推荐）

这个方式会**优先走安装方式二**，也就是优先使用 `ClawHub` 安装；如果技能暂未发布、`ClawHub` 搜索不到，或者遇到 `ClawHub` 限流，再自动回退到**安装方式三**，也就是克隆项目后手动安装。

可以直接把下面这段提示词发给 OpenClaw：

```text
请先检查是否已安装 ClawHub CLI。

若未安装，请根据 OpenClaw 官方 ClawHub 文档先安装 ClawHub CLI，然后尝试安装技能 `awesome-poetize-open-blog-automation`。

若已安装，则直接尝试安装技能 `awesome-poetize-open-blog-automation`。

如果该技能尚未发布、在 ClawHub 中搜索不到，或者遇到 ClawHub 限流，请改为克隆项目 `https://github.com/LeapYa/awesome-poetize-open.git`，然后按手动安装方式把 `openclaw-skills/poetize-blog-automation` 复制到 OpenClaw 的 `skills/` 目录中完成安装。

安装目标默认使用 OpenClaw 的 `~/.openclaw/workspace/skills/` 目录，配置默认写入 `~/.openclaw/openclaw.json`。
```

## 安装方式二：使用 OpenClaw 安装

如果该 skill 已经发布到公开注册表，默认可在 OpenClaw 的 `~/.openclaw/workspace/` 目录执行：

```bash
cd ~/.openclaw/workspace
clawhub install awesome-poetize-open-blog-automation
```

安装完成后，OpenClaw 仍然使用内部 `skillKey`：

- `poetize-blog-automation`

## 安装方式三：手动安装

推荐做法：默认把整个 skill 目录复制到 OpenClaw 的 `~/.openclaw/workspace/skills/` 目录中：

```text
~/.openclaw/workspace/
  skills/
    poetize-blog-automation/
      SKILL.md
      agents/
      references/
      scripts/
```

如果你自定义过 OpenClaw 的 workspace，就把它放到你自己的 `skills/` 目录中。

If the skill is already inside OpenClaw's normal `skills/` directory, you do not need any `skills.load.extraDirs` config.

`skills.load.extraDirs` only means: "also scan this extra filesystem directory for skills."
It is optional and is mainly useful when you want OpenClaw to read skills directly from this repository without copying them into the OpenClaw workspace first.

## Public Registry Position

- ClawHub is a public registry. Anyone can see the skill listing and install it after you publish it.
- Publish this skill as an integration for the open-source awesome-poetize-open.
- Recommended public slug: `awesome-poetize-open-blog-automation`.
- Before publishing, re-check that no real API keys, private domains, personal file paths, or draft content remain inside the skill bundle.
- Keep the repository link and the applicable AGPL attribution visible in the public listing or linked source repository.

## ClawHub Publish And Install

Publish from the repository root:

```bash
clawhub publish ./openclaw-skills/poetize-blog-automation --slug awesome-poetize-open-blog-automation --name "POETIZE 博客自动化" --version 1.0.0 --tags latest
```

Install from an OpenClaw workspace after publishing:

```bash
clawhub install awesome-poetize-open-blog-automation
```

After install, OpenClaw still uses the skill's internal `skillKey`:

- `poetize-blog-automation`

## Future Updates

To keep future upgrades smooth, keep these identifiers stable:

- `slug`: `awesome-poetize-open-blog-automation`
- folder name: `poetize-blog-automation`
- `skillKey`: `poetize-blog-automation`

When publishing updates, bump only the skill version and keep the same `slug`.

Publish a new version:

```bash
clawhub publish ./openclaw-skills/poetize-blog-automation --slug awesome-poetize-open-blog-automation --name "POETIZE 博客自动化" --version 1.0.1 --tags latest
```

Update one installed skill:

```bash
cd ~/.openclaw/workspace
clawhub update awesome-poetize-open-blog-automation
```

Update all installed skills:

```bash
cd ~/.openclaw/workspace
clawhub update --all
```

Update to a specific version:

```bash
cd ~/.openclaw/workspace
clawhub update awesome-poetize-open-blog-automation --version 1.0.1
```

Force overwrite a locally modified installed skill:

```bash
cd ~/.openclaw/workspace
clawhub update awesome-poetize-open-blog-automation --force
```

For manual installs, replace `~/.openclaw/workspace/skills/poetize-blog-automation/` with the newer folder contents and keep the existing `~/.openclaw/openclaw.json`.

## Required Runtime Values

- `base_url`
- `api_key`

When wiring this into OpenClaw, map those values to `POETIZE_BASE_URL` and `POETIZE_API_KEY`.

## Version Requirement

- This skill is intended for the open-source `awesome-poetize-open`.
- Do not connect it to the original POETIZE project.

## Base URL Rules

- Production: set `POETIZE_BASE_URL` to the public nginx origin, for example `https://blog.example.com`.
- Actual API request path = `${POETIZE_BASE_URL}/api/api/...`.
- Do not append `/api` inside `POETIZE_BASE_URL` itself. The bundled scripts already do that.
- Fault tolerance: if the provided URL accidentally ends with `/api` or `/api/`, the bundled scripts will trim that trailing suffix automatically.
- If POETIZE's API IP whitelist is enabled, add the OpenClaw server egress IP (or CIDR) to the whitelist before running this skill.

## Recommended Working Flow

1. Install the skill into OpenClaw's normal `skills/` directory.
2. Start or reload OpenClaw with that config.
3. When the user provides images, save them as local files near the Markdown draft and reference them with relative Markdown paths.
4. Run a read-only smoke test.
5. Only then use publish, update, hide, or SEO write actions.

Generate a standalone config file:

```bash
python {baseDir}/scripts/render_openclaw_config.py --output openclaw.poetize.local.json --api-key "replace-with-poetize-api-key"
```

Merge into an existing OpenClaw config:

```bash
python {baseDir}/scripts/render_openclaw_config.py --existing-config "<path-to-existing-openclaw-config>" --output openclaw.poetize.merged.json --api-key "replace-with-poetize-api-key"
```

Run a read-only smoke test against the public nginx/domain origin:

```bash
python {baseDir}/scripts/openclaw_smoke_test.py --base-url "https://your-blog.example.com" --api-key "replace-with-poetize-api-key"
```

## Local Image Intake

The skill does not need a separate image API contract from OpenClaw.
The practical contract is:

1. OpenClaw writes the Markdown draft to disk.
2. OpenClaw saves each user-provided image as a local file in the same workspace, for example `./assets/photo-1.png`.
3. The Markdown references those files, for example `![配图](./assets/photo-1.png)`.
4. `publish_post.py` uploads each local image through the existing `POST /api/resource/upload` endpoint.
5. The script rewrites the Markdown image target to the returned URL before publishing the article.

This means the skill "gets the image" from the local filesystem, not from an extra unpublished remote API.

## Recommended `openclaw.json` Wiring

Because `SKILL.md` now declares `skillKey`, `primaryEnv`, and required env vars, you can wire it like this:

```json
{
  "skills": {
    "entries": {
      "poetize-blog-automation": {
        "enabled": true,
        "apiKey": "replace-with-poetize-api-key",
        "env": {
          "POETIZE_BASE_URL": "https://your-blog.example.com"
        }
      }
    }
  }
}
```

`apiKey` is mapped to the skill's `primaryEnv`, so it becomes `POETIZE_API_KEY`.
Extra env vars still go into `skills.entries.<skillKey>.env`.

## Optional Repo-Direct Loading

Use this only if you do not want to copy the skill into OpenClaw's normal `skills/` directory.
Replace the example path below with the absolute path to your own cloned repository.

```json
{
  "skills": {
    "load": {
      "extraDirs": [
        "<absolute-path-to-your-repo>/openclaw-skills"
      ],
      "watch": true,
      "watchDebounceMs": 250
    },
    "entries": {
      "poetize-blog-automation": {
        "enabled": true,
        "apiKey": "replace-with-poetize-api-key",
        "env": {
          "POETIZE_BASE_URL": "https://your-blog.example.com"
        }
      }
    }
  }
}
```

Meaning of this block:

- `extraDirs`: tell OpenClaw to scan one more directory for skills
- `watch`: reload when files in that directory change
- `watchDebounceMs`: delay reload slightly to avoid reloading on every tiny file event

## Expected Tool Contract

OpenClaw should provide these values to the skill runtime:

- `POETIZE_BASE_URL={{base_url}}`
- `POETIZE_API_KEY={{api_key}}`

Then invoke:

```bash
python {baseDir}/scripts/publish_post.py --markdown-file article.md --brief-file article-brief.json --publish --wait
```

## Installation Notes

- Enable API in POETIZE admin first
- Copy the API key from the API settings page
- Install this skill folder into OpenClaw's normal `skills/` directory
- Use `skills.load.extraDirs` only when you intentionally want repo-direct loading
- Bind `base_url` and `api_key` as install-time or runtime variables
- In production, prefer the public nginx/domain origin such as `https://your-blog.example.com`
- Remember that the final request path is `${POETIZE_BASE_URL}/api/api/...`
- Create `article-brief.json` from `{baseDir}/assets/article-brief.template.json` before mutating actions
- Run `python {baseDir}/scripts/openclaw_smoke_test.py ...` before the first real write action
- Generate a strategy brief JSON before any mutating command
- No extra OpenClaw secrets are required unless your deployment adds them separately
- If you use OpenClaw sandboxing, make sure those env vars are allowed into the sandbox too

## What OpenClaw Can Do After Wiring

- Generate a full article from a topic
- Create a strategy brief before publish, update, or hide actions
- Upload a local cover image
- Start an async create or update task
- Poll task status until publish completes
- Return `articleId` and `articleUrl` to the caller
