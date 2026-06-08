#!/usr/bin/env python3
"""
AlphaPai Research CLI
=====================
Alpha派投研 API 命令行工具。

用法：
  python alphapai_client.py config --set-key YOUR_KEY
  python alphapai_client.py qa --question "贵州茅台2024年经营情况？"
  python alphapai_client.py recall --query "茅台市值" --type comment,qa --start 2025-01-01

模块用法（供其他脚本导入）：
  from alphapai_client import AlphaPaiClient, load_config
  client = AlphaPaiClient(load_config())
  result = client.qa_text("问题")
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import requests

# ============================================================
# 配置管理
# ============================================================

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"
)


def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> Optional[Dict]:
    """加载API配置，返回 {"api_key": "...", "base_url": "..."} 或 None"""
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    if not config.get("api_key"):
        return None
    config.setdefault("base_url", "https://open-api.rabyte.cn")
    return config


def save_config(
    api_key: str,
    base_url: str = "https://open-api.rabyte.cn",
    config_path: str = DEFAULT_CONFIG_PATH,
) -> Dict:
    """保存API配置到 config.json"""
    config = {"api_key": api_key, "base_url": base_url}
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return config


# ============================================================
# API Client（可单独导入使用）
# ============================================================


class AlphaPaiClient:
    """AlphaPai Open API 客户端"""

    def __init__(self, config: Dict):
        self.base_url = config["base_url"].rstrip("/")
        self.headers = {
            "app-agent": config["api_key"],
            "Content-Type": "application/json",
        }

    def _post(self, endpoint: str, payload: Dict, stream: bool = False) -> Any:
        """通用POST请求。stream=True时返回原始Response，False时返回解析后的JSON。"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(
            url,
            headers=self.headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            stream=stream,
        )
        response.raise_for_status()
        return response if stream else response.json()

    @staticmethod
    def parse_sse(response) -> Dict:
        """解析SSE流式响应，返回 {"answer": str, "references": list}"""
        buffer, answer, references = "", "", []
        for chunk in response.iter_content(chunk_size=4096):
            if not chunk:
                continue
            buffer += chunk.decode("utf-8", errors="replace")
            while "\n\n" in buffer:
                event, buffer = buffer.split("\n\n", 1)
                event = event.strip()
                if not event.startswith("data: "):
                    continue
                line = event[6:].strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        d = data.get("data", data)
                        if d.get("answer"):
                            answer += d["answer"]
                        if d.get("references"):
                            references.extend(d["references"])
                except json.JSONDecodeError:
                    continue
        return {"answer": answer, "references": references}

    def qa_text(
        self,
        question: str,
        context: Optional[List[str]] = None,
        mode: str = "Flash",
        is_stream: bool = False,
        is_auto_route: bool = False,
        is_web_search: bool = False,
        is_deep_reasoning: bool = False,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        question_id: Optional[str] = None,
    ) -> Dict:
        """投研知识问答接口。is_stream=True时内部解析SSE并返回聚合结果。"""
        payload = {
            "question": question,
            "mode": mode,
            "isStream": is_stream,
            "isAutoRoute": is_auto_route,
            "userInfo": {
                "userCode": "001010",
                "userName": "rabyte",
                "roleName": "基金经理",
                "roleCode": 5,
            },
        }
        if context:
            payload["context"] = context
        if is_web_search:
            payload["isWebSearch"] = True
        if is_deep_reasoning:
            payload["isDeepReasoning"] = True
        if start_time:
            payload["requestSelectStartTime"] = start_time
        if end_time:
            payload["requestSelectEndTime"] = end_time
        if question_id:
            payload["questionId"] = question_id

        if is_stream:
            return self.parse_sse(
                self._post("/alpha/open-api/v1/paipai/qa-text", payload, stream=True)
            )
        return self._post("/alpha/open-api/v1/paipai/qa-text", payload)

    def recall_data(
        self,
        query: str,
        is_cut_off: bool = True,
        recall_type: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict:
        """获取问题召回数据"""
        payload = {"query": query, "isCutOff": is_cut_off}
        if recall_type:
            payload["recallType"] = recall_type
        else:
            payload["recallType"] = []
        if start_time:
            payload["startTime"] = start_time
        if end_time:
            payload["endTime"] = end_time
        return self._post("/alpha/open-api/v1/paipai/recall-data", payload)

    def stock_agent(
        self,
        question: str,
        agent_mode: int,
        stock: Optional[Dict] = None,
        template: int = 0,
        template_text: str = "",
        report_type: Optional[str] = None,
        stock_report_id: Optional[str] = None,
        stock_report_title: Optional[str] = None,
        stock_report_period: Optional[str] = None,
        template_concern: Optional[str] = None,
        request_select_start_time: Optional[str] = None,
        request_select_end_time: Optional[str] = None,
        input_industry: Optional[str] = None,
        report_date: Optional[str] = None,
        fund_type: Optional[str] = None,
        if_annual: Optional[int] = None,
        stock_list: Optional[List[Dict]] = None,
        picture_color: Optional[List[str]] = None,
        picture_style: Optional[str] = None,
        source: Optional[int] = None,
        language: Optional[str] = None,
        only_answer: Optional[bool] = None,
    ) -> Dict:
        """Alpha派投研Agent接口（公司一页纸、业绩点评、调研大纲等），SSE 流式请求。"""
        payload: Dict = {
            "question": question,
            "agentMode": agent_mode,
            "template": template,
            "templateText": template_text,
        }
        if stock:
            payload["stock"] = stock
        if report_type:
            payload["reportType"] = report_type
        if stock_report_id:
            payload["stockReportId"] = stock_report_id
        if stock_report_title:
            payload["stockReportTitle"] = stock_report_title
        if stock_report_period:
            payload["stockReportPeriod"] = stock_report_period
        if template_concern:
            payload["templateConcern"] = template_concern
        if request_select_start_time:
            payload["requestSelectStartTime"] = request_select_start_time
        if request_select_end_time:
            payload["requestSelectEndTime"] = request_select_end_time
        if input_industry:
            payload["inputIndustry"] = input_industry
        if report_date:
            payload["reportDate"] = report_date
        if fund_type:
            payload["fundType"] = fund_type
        if if_annual is not None:
            payload["ifAnnual"] = if_annual
        if stock_list:
            payload["stockList"] = stock_list
        if picture_color:
            payload["pictureColor"] = picture_color
        if picture_style:
            payload["pictureStyle"] = picture_style
        if source is not None:
            payload["source"] = source
        if language:
            payload["language"] = language
        if only_answer is not None:
            payload["onlyAnswer"] = only_answer
        return self.parse_sse(
            self._post("/alpha/open-api/v1/paipai/stock/agent", payload, stream=True)
        )

    def stock_report(self, code: str) -> Dict:
        """获取某个股票的公告列表（上市公司在交易所公开的公告）"""
        return self._post("/alpha/open-api/v1/paipai/stock/report", {"code": code})

    def search_image(
        self,
        query_text: str,
        files_range: Optional[List[str]] = None,
        topk: int = 50,
        recall_mode: str = "both",
        use_llm_rank: bool = False,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict:
        """搜图表：从研报/公告中搜索相关图片和表格"""
        payload: Dict = {
            "queryText": query_text,
            "topk": topk,
            "recallMode": recall_mode,
            "useLlmRank": use_llm_rank,
        }
        if files_range:
            payload["filesRange"] = files_range
        if start_date:
            payload["startDate"] = start_date
        if end_date:
            payload["endDate"] = end_date
        return self._post("/alpha/open-api/v1/paipai/search-image", payload)


# ============================================================
# 输出格式化
# ============================================================

_TYPE_LABEL = {
    "comment": "机构点评",
    "vps": "基金定期报告",
    "report": "内资研报",
    "foreign_report": "外资研报",
    "wechat_public_article": "公众号",
    "ann": "公司公告",
    "roadShow": "路演纪要",
    "roadShow_ir": "上市公司披露投关纪要",
    "roadShow_us": "美股纪要",
    "table": "公告/研报表格",
    "image": "研报图片",
    "edb": "EDB数据库",
}


def _type_label(type_val: str) -> str:
    return _TYPE_LABEL.get(type_val, type_val)


def _require_success(result: Dict):
    """检查响应码，非成功则打印错误并退出"""
    if result.get("code") != 200000:
        print(
            f"[错误] code={result.get('code')} message={result.get('message')}",
            file=sys.stderr,
        )
        sys.exit(1)


def format_qa(result: Dict) -> str:
    # parse_sse returns {"answer": ..., "references": [...]} directly (no code wrapper)
    if "answer" in result:
        answer = result.get("answer", "（无回答）")
        references = result.get("references", [])
    else:
        _require_success(result)
        data = result.get("data", {})
        answer = data.get("answer", "（无回答）")
        references = data.get("references", [])

    lines = ["[回答]", answer]
    if references:
        lines.append(f"\n[引用来源 {len(references)} 条]")
        for i, ref in enumerate(references, 1):
            date = f" ({ref.get('publishDate', '')})" if ref.get("publishDate") else ""
            lines.append(
                f"  {i}. [{_type_label(ref.get('type', ''))}] {ref.get('title', '')}{date}"
            )
    return "\n".join(lines)


def format_recall(result: Dict) -> str:
    _require_success(result)
    items = result.get("data", [])
    lines = [f"[召回数据 {len(items)} 条]\n"]
    for i, item in enumerate(items, 1):
        item_type = item.get("type", "")
        context_info = item.get("contextInfo", "")
        lines.append(f"#{i} [{_type_label(item_type)}]")
        lines.append(f"  {context_info}")
        if item_type == "qa":
            if item.get("contextText"):
                lines.append(f"  Q: {item['contextText']}")
            if item.get("answer"):
                text = item["answer"]
                lines.append(f"  A: {text[:300]}{'...' if len(text) > 300 else ''}")
        elif item.get("chunks"):
            text = item["chunks"][0]
            lines.append(f"  {text[:300]}{'...' if len(text) > 300 else ''}")
        lines.append("")
    return "\n".join(lines)


def format_agent(result: Dict) -> str:
    if "answer" in result:
        answer = result.get("answer", "（无回答）")
        references = result.get("references", [])
    else:
        _require_success(result)
        data = result.get("data", {})
        answer = data.get("answer", "（无回答）")
        references = data.get("references", [])
    lines = ["[Agent 回答]", answer]
    if references:
        lines.append(f"\n[引用来源 {len(references)} 条]")
        for i, ref in enumerate(references, 1):
            date = f" ({ref.get('publishDate', '')})" if ref.get("publishDate") else ""
            lines.append(
                f"  {i}. [{_type_label(ref.get('type', ''))}] {ref.get('title', '')}{date}"
            )
    return "\n".join(lines)


def format_report(result: Dict) -> str:
    _require_success(result)
    items = result.get("data", [])
    if not items:
        return "[公告列表] 未找到相关公告"
    lines = [f"[公告列表 {len(items)} 条]\n"]
    for i, item in enumerate(items, 1):
        lines.append(
            f"#{i} [{item.get('reportType', '')}] {item.get('stockReportTitle', '')}"
        )
        lines.append(
            f"   期间: {item.get('reportPeriod', '')}  ID: {item.get('stockReportId', '')}"
        )
        lines.append("")
    return "\n".join(lines)


def format_image(result: Dict) -> str:
    _require_success(result)
    items = result.get("data", [])
    if not items:
        return "[图表搜索] 未找到相关图表"
    lines = [f"[图表搜索 {len(items)} 条]\n"]
    for i, item in enumerate(items, 1):
        lines.append(f"#{i} {item.get('articleTitle', '')}")
        caption = ", ".join(item.get("captionList") or [])
        if caption:
            lines.append(f"   说明: {caption}")
        lines.append(
            f"   来源: {item.get('source', '')}  日期: {item.get('publishDate', '')}"
        )
        if item.get("imageUrl"):
            lines.append(f"   图片: {item['imageUrl']}")
        lines.append("")
    return "\n".join(lines)


# ============================================================
# CLI 子命令
# ============================================================


def cmd_config(args):
    config_path = DEFAULT_CONFIG_PATH
    if args.set_key or args.set_url:
        config = load_config(config_path) or {}
        if args.set_key:
            config["api_key"] = args.set_key
        if args.set_url:
            config["base_url"] = args.set_url
        config.setdefault("base_url", "https://open-api.rabyte.cn")
        save_config(config["api_key"], config["base_url"], config_path)
        key = config["api_key"]
        masked = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
        print(f"配置已保存: api_key={masked}  base_url={config['base_url']}")
        print(f"路径: {config_path}")
    elif args.show:
        config = load_config(config_path)
        if not config:
            print(
                "未找到配置，请先运行: python alphapai_client.py config --set-key YOUR_KEY"
            )
            sys.exit(1)
        key = config["api_key"]
        masked = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
        print(f"api_key : {masked}")
        print(f"base_url: {config['base_url']}")
        print(f"路径    : {config_path}")
    else:
        print(
            "用法: python alphapai_client.py config --show | --set-key KEY [--set-url URL]"
        )


def cmd_qa(args):
    config = load_config()
    if not config:
        print(
            "[错误] 未找到配置，请先运行: python alphapai_client.py config --set-key YOUR_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    client = AlphaPaiClient(config)
    result = client.qa_text(
        question=args.question,
        context=args.context or None,
        mode=args.mode,
        is_stream=True,
        is_web_search=args.web_search,
        is_deep_reasoning=args.deep_reasoning,
        start_time=args.start,
        end_time=args.end,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_qa(result))


def cmd_recall(args):
    config = load_config()
    if not config:
        print(
            "[错误] 未找到配置，请先运行: python alphapai_client.py config --set-key YOUR_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    client = AlphaPaiClient(config)
    recall_type = [t.strip() for t in args.type.split(",")] if args.type else []

    result = client.recall_data(
        query=args.query,
        is_cut_off=not args.no_cutoff,
        recall_type=recall_type,
        start_time=args.start,
        end_time=args.end,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_recall(result))


def _parse_stock(s: str) -> Dict:
    """解析 CODE:NAME 格式的股票参数"""
    parts = s.split(":", 1)
    return {"code": parts[0], "name": parts[1] if len(parts) == 2 else ""}


def cmd_agent(args):
    config = load_config()
    if not config:
        print(
            "[错误] 未找到配置，请先运行: python alphapai_client.py config --set-key YOUR_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    client = AlphaPaiClient(config)
    stock = _parse_stock(args.stock) if args.stock else None
    stock_list = [_parse_stock(s) for s in args.stock_list] if args.stock_list else None

    # modes 5/8/9 have template fixed at 1 per API spec
    template = 1 if args.mode in (5, 8, 9) else args.template

    result = client.stock_agent(
        question=args.question,
        agent_mode=args.mode,
        stock=stock,
        template=template,
        template_text=args.template_text or "",
        report_type=args.report_type,
        stock_report_id=args.report_id,
        stock_report_title=args.report_title,
        stock_report_period=args.report_period,
        template_concern=args.concern,
        request_select_start_time=args.start,
        request_select_end_time=args.end,
        input_industry=args.industry,
        report_date=args.report_date,
        fund_type=args.fund_type,
        if_annual=args.if_annual,
        stock_list=stock_list,
        picture_color=args.picture_color,
        picture_style=args.picture_style,
        source=args.source,
        language=args.language,
        only_answer=True if args.only_answer else None,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_agent(result))


def cmd_report(args):
    config = load_config()
    if not config:
        print(
            "[错误] 未找到配置，请先运行: python alphapai_client.py config --set-key YOUR_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    client = AlphaPaiClient(config)
    result = client.stock_report(code=args.code)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))


def cmd_image(args):
    config = load_config()
    if not config:
        print(
            "[错误] 未找到配置，请先运行: python alphapai_client.py config --set-key YOUR_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    client = AlphaPaiClient(config)
    result = client.search_image(
        query_text=args.query,
        files_range=args.files_range,
        topk=args.topk,
        recall_mode=args.recall_mode,
        use_llm_rank=args.llm_rank,
        start_date=args.start,
        end_date=args.end,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_image(result))


# ============================================================
# CLI 入口
# ============================================================


def main():
    parser = argparse.ArgumentParser(
        prog="alphapai_client.py",
        description="AlphaPai Research CLI — Alpha派投研API命令行工具",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- config ---
    p_cfg = sub.add_parser("config", help="查看或设置API配置")
    p_cfg.add_argument("--show", action="store_true", help="显示当前配置")
    p_cfg.add_argument("--set-key", metavar="KEY", help="设置api_key")
    p_cfg.add_argument(
        "--set-url",
        metavar="URL",
        help="设置base_url（默认 https://open-api.rabyte.cn）",
    )

    # --- qa ---
    p_qa = sub.add_parser("qa", help="投研知识问答")
    p_qa.add_argument("--question", "-q", required=True, help="问题内容")
    p_qa.add_argument(
        "--mode",
        default="Flash",
        choices=["Flash", "Think"],
        help="问答模式: Flash=简单搜索问答，一问一搜一答（默认）; Think=Wide Search，一问多搜一答",
    )
    p_qa.add_argument(
        "--context",
        "-c",
        nargs="+",
        metavar="MSG",
        help="多轮对话上下文，按顺序传入历史消息列表",
    )
    p_qa.add_argument("--web-search", action="store_true", help="开启联网搜索")
    p_qa.add_argument("--deep-reasoning", action="store_true", help="开启深度推理")
    p_qa.add_argument("--start", metavar="YYYY-MM-DD", help="数据筛选开始日期")
    p_qa.add_argument("--end", metavar="YYYY-MM-DD", help="数据筛选结束日期")
    p_qa.add_argument("--json", action="store_true", help="输出原始JSON（供程序解析）")

    # --- recall ---
    p_rc = sub.add_parser("recall", help="获取问题召回的底层数据")
    p_rc.add_argument("--query", "-q", required=True, help="查询问题")
    p_rc.add_argument(
        "--type",
        "-t",
        metavar="TYPES",
        help="数据类型，逗号分隔，如 comment,qa,report（不传则全类型）",
    )
    p_rc.add_argument(
        "--no-cutoff",
        action="store_true",
        help="返回截断前完整内容（默认截断，与送入大模型的数据一致）",
    )
    p_rc.add_argument("--start", metavar="YYYY-MM-DD", help="数据筛选开始日期")
    p_rc.add_argument("--end", metavar="YYYY-MM-DD", help="数据筛选结束日期")
    p_rc.add_argument("--json", action="store_true", help="输出原始JSON（供程序解析）")

    # --- agent ---
    p_ag = sub.add_parser(
        "agent", help="股票 Agent（公司一页纸、业绩点评、调研大纲等）"
    )
    p_ag.add_argument(
        "--mode",
        "-m",
        type=int,
        required=True,
        help="Agent模式: 1=业绩点评 2=公司一页纸 3=调研大纲 5=主题选股 "
        "7=投资逻辑 8=可比公司 9=观点Challenge 11=行业一页纸 "
        "12=个股选基 13=主题选基 15=画图",
    )
    p_ag.add_argument("--question", "-q", required=True, help="问题内容")
    p_ag.add_argument(
        "--stock",
        metavar="CODE:NAME",
        help="股票信息，格式 CODE:NAME，如 300014.SZ:亿纬锂能",
    )
    p_ag.add_argument(
        "--template",
        type=int,
        default=0,
        help="模版类型: 0=alpha派模板(默认) 1=用户模板",
    )
    p_ag.add_argument(
        "--template-text", metavar="TEXT", help="用户模版正文（template=1时需传）"
    )
    p_ag.add_argument(
        "--report-type", metavar="TYPE", help="报告类型（业绩点评必填），如: 季报"
    )
    p_ag.add_argument("--report-id", metavar="ID", help="公告ID（业绩点评必填）")
    p_ag.add_argument(
        "--report-title", metavar="TITLE", help="报告标题（业绩点评必填）"
    )
    p_ag.add_argument(
        "--report-period",
        metavar="PERIOD",
        help="报告期（业绩点评必填），如: 2025年一季报",
    )
    p_ag.add_argument(
        "--concern", metavar="TEXT", help="用户关注内容（业绩点评/观点Challenge选填）"
    )
    p_ag.add_argument(
        "--industry", metavar="NAME", help="行业信息（行业一页纸必填），如: 白酒"
    )
    p_ag.add_argument(
        "--report-date",
        metavar="DATE",
        help="报告期（个股选基/主题选基必填），如: 2025-09-30",
    )
    p_ag.add_argument(
        "--fund-type",
        metavar="TYPE",
        help="基金类型（个股选基/主题选基必填）: 全部|主动|指数|ETF",
    )
    p_ag.add_argument(
        "--if-annual", type=int, choices=[0, 1], help="是否年报: 0=否 1=是"
    )
    p_ag.add_argument(
        "--stock-list",
        nargs="+",
        metavar="CODE:NAME",
        help="股票列表（个股选基必填），如: 601231.SH:环旭电子 300308.SZ:中际旭创",
    )
    p_ag.add_argument(
        "--picture-color",
        nargs="+",
        metavar="HEX",
        help="图片颜色HEX值（画图必填），如: 2A66F6 A5A8AF",
    )
    p_ag.add_argument(
        "--picture-style",
        metavar="STYLE",
        help="图片风格（画图必填）: PPT风格|科普风格",
    )
    p_ag.add_argument(
        "--source",
        type=int,
        choices=[0, 1],
        help="画图样式: 0=仅图片(默认) 1=图文",
    )
    p_ag.add_argument(
        "--language", metavar="LANG", help="语言（美股公司一页纸可选）: 中文|英文"
    )
    p_ag.add_argument(
        "--only-answer",
        action="store_true",
        help="仅返回最终答案（mode 7 投资逻辑可选）",
    )
    p_ag.add_argument("--start", metavar="YYYY-MM-DD", help="数据开始日期")
    p_ag.add_argument("--end", metavar="YYYY-MM-DD", help="数据结束日期")
    p_ag.add_argument("--json", action="store_true", help="输出原始JSON（供程序解析）")

    # --- report ---
    p_rp = sub.add_parser("report", help="获取股票公告列表（供业绩点评查询公告ID）")
    p_rp.add_argument("--code", "-c", required=True, help="股票编码，如 603380.SH")
    p_rp.add_argument("--json", action="store_true", help="输出原始JSON（供程序解析）")

    # --- image ---
    p_img = sub.add_parser("image", help="搜图表（从研报/公告中搜索图片和表格）")
    p_img.add_argument("--query", "-q", required=True, help="搜索内容")
    p_img.add_argument(
        "--files-range",
        nargs="+",
        metavar="CODE",
        help="来源类型代码列表，可选值: 3=内资研报 8=外资研报 6=公告 9=三方研报",
    )
    p_img.add_argument("--topk", type=int, default=50, help="返回数量(1-100，默认50)")
    p_img.add_argument(
        "--recall-mode",
        default="both",
        choices=["both", "vector_only", "es_only"],
        help="召回模式（默认both）",
    )
    p_img.add_argument("--llm-rank", action="store_true", help="使用LLM重排序")
    p_img.add_argument("--start", metavar="YYYY-MM-DD", help="开始日期")
    p_img.add_argument("--end", metavar="YYYY-MM-DD", help="结束日期")
    p_img.add_argument("--json", action="store_true", help="输出原始JSON（供程序解析）")

    args = parser.parse_args()
    {
        "config": cmd_config,
        "qa": cmd_qa,
        "recall": cmd_recall,
        "agent": cmd_agent,
        "report": cmd_report,
        "image": cmd_image,
    }[args.command](args)


if __name__ == "__main__":
    main()
