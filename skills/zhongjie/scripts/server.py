#!/usr/bin/env python3
"""
中介哥 Web 应用后端服务。

提供 API 读写客户画像、推荐报告和房源数据，同时托管 Vue 前端构建产物。

用法：
    export PROJECT_ROOT="<项目根目录绝对路径>"

    # 安装依赖（首次）
    pip install fastapi uvicorn

    # 启动服务（同时托管前端 dist）
    python3 skills/zhongjie/scripts/server.py

    # 指定端口
    python3 skills/zhongjie/scripts/server.py --port 3000

    浏览器访问 http://localhost:8000
"""

import argparse
import json
import os
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

SKILL_NAME = "zhongjie"


def find_project_root() -> Path:
    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"])
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "skills" / SKILL_NAME / "SKILL.md").exists():
            return parent
    print("错误：找不到项目根目录。请设置 PROJECT_ROOT 环境变量。", file=sys.stderr)
    sys.exit(1)


def read_env(env_path: Path) -> dict:
    env = {}
    if not env_path.exists():
        return env
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


root = find_project_root()
data_dir = root / ".skills-data" / SKILL_NAME
skill_dir = root / "skills" / SKILL_NAME
dist_dir = skill_dir / "assets" / "dist"

env = read_env(data_dir / ".env")

app = FastAPI(title="中介哥 API", docs_url="/api/docs", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ──────────────────────────────────────────────────────────

class MarkdownBody(BaseModel):
    content: str


# ── API routes ────────────────────────────────────────────────────────────────

@app.get("/api/config")
def get_config():
    return {
        "amapKey": env.get("AMAP_JS_API_KEY", ""),
        "amapSecurityCode": env.get("AMAP_JS_API_SECURITY_CODE", ""),
    }


@app.get("/api/preferences")
def get_preferences():
    path = data_dir / "data" / "preferences.md"
    if not path.exists():
        return {"content": ""}
    return {"content": path.read_text(encoding="utf-8")}


@app.put("/api/preferences")
def save_preferences(body: MarkdownBody):
    path = data_dir / "data" / "preferences.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.content, encoding="utf-8")
    return {"ok": True}


@app.get("/api/research")
def get_research():
    path = data_dir / "data" / "research.md"
    if not path.exists():
        return {"content": ""}
    return {"content": path.read_text(encoding="utf-8")}


@app.put("/api/research")
def save_research(body: MarkdownBody):
    path = data_dir / "data" / "research.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.content, encoding="utf-8")
    return {"ok": True}


@app.get("/api/report")
def get_report():
    path = data_dir / "data" / "report.md"
    if not path.exists():
        return {"content": ""}
    return {"content": path.read_text(encoding="utf-8")}


@app.put("/api/report")
def save_report(body: MarkdownBody):
    path = data_dir / "data" / "report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.content, encoding="utf-8")
    return {"ok": True}


@app.get("/api/properties")
def get_properties():
    path = data_dir / "data" / "properties.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "properties" in data:
        return data["properties"]
    return data


@app.put("/api/properties")
def save_properties(body: dict):
    path = data_dir / "data" / "properties.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    props = body.get("properties", body)
    path.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True}


# ── Static files / SPA fallback ──────────────────────────────────────────────

if dist_dir.exists():
    assets_dir = dist_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static-assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith("api"):
            return HTMLResponse("Not Found", status_code=404)
        file_path = dist_dir / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        index = dist_dir / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return HTMLResponse("Not Found", status_code=404)
else:
    @app.get("/")
    def no_dist():
        return HTMLResponse(
            "<h2>前端未构建</h2>"
            "<p>请先运行：<code>cd webapp && npm run generate</code></p>",
            status_code=200,
        )


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="中介哥 Web 应用后端")
    parser.add_argument("--port", type=int, default=8000, help="监听端口（默认 8000）")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址（默认 127.0.0.1）")
    args = parser.parse_args()

    print(f"🏠 中介哥工作台启动中…")
    print(f"   项目根目录：{root}")
    print(f"   数据目录：  {data_dir}")
    if dist_dir.exists():
        print(f"   前端目录：  {dist_dir}")
    else:
        print(f"   ⚠️  前端未构建，仅提供 API 服务")
    print(f"   访问地址：  http://localhost:{args.port}")
    print()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
