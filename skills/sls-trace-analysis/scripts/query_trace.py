# -*- coding: utf-8 -*-
"""
SLS + ARMS 联合问题定位脚本
- SLS：查业务日志（多 LogStore 并发）
- ARMS：查调用链（Span 树 + 异常信息）
- 输出：合并的调用链 + 日志 + 根因摘要

用法：
  python query_trace.py --trace-id <ID>
  python query_trace.py --trace-id <ID> --minutes 60
  python query_trace.py --trace-id <ID> --start "2024-01-15 14:00:00" --end "2024-01-15 15:00:00"
  python query_trace.py --trace-id <ID> --skip-sls      # 只查 ARMS
  python query_trace.py --trace-id <ID> --skip-arms     # 只查 SLS
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# 依赖检查
# ---------------------------------------------------------------------------
missing_deps = []
try:
    from aliyun.log import LogClient, GetLogsRequest
except ImportError:
    missing_deps.append("aliyun-log-python-sdk")

try:
    from alibabacloud_arms20190808 import client as arms_client
    from alibabacloud_arms20190808 import models as arms_models
    from alibabacloud_tea_openapi import models as openapi_models
    HAS_ARMS_SDK = True
except ImportError:
    HAS_ARMS_SDK = False
    # ARMS 也可以用 HTTP 直接调用，不强依赖 SDK

import re
import urllib.request
import urllib.error
import urllib.parse
import hmac
import hashlib
import base64
import time as time_module

if missing_deps:
    print(json.dumps({
        "error": "缺少依赖：{}".format(", ".join(missing_deps)),
        "fix": "pip install {} -i https://mirrors.aliyun.com/pypi/simple".format(
            " ".join(missing_deps))
    }, ensure_ascii=False))
    sys.exit(1)


# ---------------------------------------------------------------------------
# 从 openclaw.json 加载 env 字段作为环境变量的后备来源
# ---------------------------------------------------------------------------
_openclaw_env_cache = None

def _load_openclaw_env():
    global _openclaw_env_cache
    if _openclaw_env_cache is not None:
        return _openclaw_env_cache
    _openclaw_env_cache = {}
    config_path = os.path.join(os.path.expanduser("~"), ".openclaw", "openclaw.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # env vars 可能在多个位置：plugins.env.vars / env.vars / env
        for path_fn in [
            lambda d: d.get("plugins", {}).get("env", {}).get("vars", {}),
            lambda d: d.get("env", {}).get("vars", {}),
            lambda d: d.get("env", {}),
        ]:
            found = path_fn(data)
            if found and isinstance(found, dict):
                _openclaw_env_cache = found
                break
    except Exception:
        pass
    return _openclaw_env_cache

def get_env(key, default=None):
    """优先读 os.environ，找不到则从 openclaw.json 的 env 字段读。"""
    val = os.environ.get(key)
    if val:
        return val
    return _load_openclaw_env().get(key, default)


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
def get_config(logstores_override=None, skip_sls=False, skip_arms=False):
    cfg = {
        "skip_sls":  skip_sls,
        "skip_arms": skip_arms,
    }

    # SLS 配置
    if not skip_sls:
        sls_required = ["SLS_ENDPOINT", "SLS_ACCESS_KEY_ID",
                        "SLS_ACCESS_KEY_SECRET", "SLS_PROJECT", "SLS_LOGSTORE"]
        missing = [k for k in sls_required if not get_env(k)]
        if missing:
            print(json.dumps({
                "error": "SLS 缺少环境变量：{}".format(", ".join(missing)),
                "fix": "请在 openclaw.json 的 env 字段中配置，或加 --skip-sls 跳过"
            }, ensure_ascii=False))
            sys.exit(1)
        raw_stores = logstores_override or get_env("SLS_LOGSTORE")
        cfg["sls"] = {
            "endpoint":    get_env("SLS_ENDPOINT"),
            "ak_id":       get_env("SLS_ACCESS_KEY_ID"),
            "ak_secret":   get_env("SLS_ACCESS_KEY_SECRET"),
            "project":     get_env("SLS_PROJECT"),
            "logstores":   [s.strip() for s in raw_stores.split(",") if s.strip()],
            "trace_field": get_env("SLS_TRACE_FIELD", "traceId"),
        }

    # ARMS 配置
    if not skip_arms:
        arms_required = ["ARMS_ACCESS_KEY_ID", "ARMS_ACCESS_KEY_SECRET", "ARMS_REGION_ID"]
        missing = [k for k in arms_required if not get_env(k)]
        if missing:
            print(json.dumps({
                "error": "ARMS 缺少环境变量：{}".format(", ".join(missing)),
                "fix": "请在 openclaw.json 的 env 字段中配置，或加 --skip-arms 跳过"
            }, ensure_ascii=False))
            sys.exit(1)
        cfg["arms"] = {
            "ak_id":     get_env("ARMS_ACCESS_KEY_ID"),
            "ak_secret": get_env("ARMS_ACCESS_KEY_SECRET"),
            "region_id": get_env("ARMS_REGION_ID"),
        }

    return cfg


# ---------------------------------------------------------------------------
# SLS 查询（多 LogStore 并发）
# ---------------------------------------------------------------------------
def _query_one_logstore(client, project, store, query, from_ts, to_ts):
    try:
        req = GetLogsRequest(project=project, logstore=store,
                             fromTime=from_ts, toTime=to_ts,
                             query=query, line=200, offset=0, reverse=False)
        resp = client.get_logs(req)
        logs = [dict(l.get_contents()) for l in resp.get_logs()]
        return store, logs, None
    except Exception as e:
        err_msg = str(e)
        err_code = getattr(e, "get_error_code", lambda: "")()
        err_detail = getattr(e, "get_error_message", lambda: "")()
        full_err = "{} {} {}".format(err_msg, err_code, err_detail)

        # 全文搜索也失败时，降级为 * 通配 + 客户端过滤
        sys.stderr.write("  ⚠️ [{}] 查询失败({}), 尝试通配查询...\n".format(
            store, err_code or err_msg[:60]))
        sys.stderr.flush()
        try:
            req2 = GetLogsRequest(project=project, logstore=store,
                                  fromTime=from_ts, toTime=to_ts,
                                  query="*", line=200, offset=0, reverse=False)
            resp2 = client.get_logs(req2)
            logs2 = [dict(l.get_contents()) for l in resp2.get_logs()]
            search_values = _extract_search_values(query)
            if search_values and logs2:
                logs2 = _client_filter(logs2, search_values)
            if logs2:
                return store, logs2, None
            return store, [], "全文查询失败, 通配查询未匹配到数据。原始错误: {}".format(full_err[:100])
        except Exception as e2:
            return store, [], "全文查询失败: {} | 通配查询也失败: {}".format(
                full_err[:80], str(e2)[:80])


def _extract_search_values(query):
    """从查询语句中提取所有搜索值（双引号内的内容）"""
    import re as _re
    values = _re.findall(r'"([^"]+)"', query)
    seen = set()
    unique = []
    for v in values:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


def _client_filter(logs, search_values):
    """客户端过滤：日志中至少包含一个搜索值"""
    filtered = []
    for log in logs:
        log_text = " ".join(str(v) for v in log.values())
        if any(val in log_text for val in search_values):
            filtered.append(log)
    return filtered

def build_sls_query(trace_field, trace_id=None, wusid=None, path=None):
    """
    构建 SLS 查询语句。默认使用全文搜索，不依赖任何字段索引。

    查询策略（全文搜索，无需配置字段索引）：
      trace_id → "xxx"           32位十六进制，全文搜索足够精确
      wusid    → "xxx"           数字 ID，全文匹配
      path     → "xxx"           请求路径，全文匹配
      多条件   → "a" AND "b"    AND 连接确保同时命中
    """
    conditions = []
    if trace_id:
        conditions.append('"{}"'.format(trace_id))
    if wusid:
        conditions.append('"{}"'.format(str(wusid)))
    if path:
        conditions.append('"{}"'.format(path))
    if not conditions:
        return None
    return " AND ".join(conditions)


# SLS 日志中可能存放 trace_id 的字段名
_SLS_TRACE_FIELDS = ["data.trace_id", "trace_id", "traceId", "TraceId", "data.traceId"]

# SLS 日志中可能存放 wusid (wechat_user_space_id) 的字段名（按优先级排列）
_SLS_WUSID_FIELDS = [
    "wechat_user_space_id",
    "data.wechat_user_space_id",
    "promoter_wechat_user_space_id",
    "data.promoter_wechat_user_space_id",
    "wusid",
    "data.wusid",
]


def build_sls_wusid_queries(wusid, path=None):
    """
    为 wusid (wechat_user_space_id) 生成多种查询策略（按优先级排列），逐一尝试直到有结果。

    策略优先级：
      1. 字段精确查询（OR 连接所有可能的字段名，需要字段索引）
      2. SLS Analytics WHERE 过滤（不依赖字段索引，精准匹配）
      3. 全文搜索（依赖全文索引，数字可能被跳过）
      4. 通配 + 客户端过滤（兜底，最慢但最通用）
    """
    wusid_str = str(wusid).strip()
    queries = []

    # 策略 1：字段精确查询（需字段索引）
    field_conditions = " OR ".join(
        '{}: "{}"'.format(f, wusid_str) for f in _SLS_WUSID_FIELDS
    )
    if path:
        field_conditions = "({}) AND \"{}\"".format(field_conditions, path)
    queries.append(("field_query", field_conditions))

    # 策略 2：SLS Analytics WHERE（不依赖索引，用 SQL 过滤）
    # 每个字段用 cast 保证数字字段也能比较
    where_clauses = " OR ".join(
        "cast({} as varchar) = '{}'".format(f.replace(".", "_"), wusid_str)
        for f in _SLS_WUSID_FIELDS
    )
    analytics_query = "* | select * where {}".format(where_clauses)
    if path:
        analytics_query = '"{}" | select * where {}'.format(path, where_clauses)
    queries.append(("analytics", analytics_query))

    # 策略 3：全文搜索（数字 ID 在某些索引配置下无法命中）
    fulltext = '"{}"'.format(wusid_str)
    if path:
        fulltext = '{} AND "{}"'.format(fulltext, path)
    queries.append(("fulltext", fulltext))

    # 策略 4：通配查询（由 query_sls_by_wusid 做客户端过滤）
    queries.append(("wildcard", "*"))

    return queries


def query_sls_by_wusid(cfg, wusid, from_ts, to_ts, path=None):
    """
    多策略查询 SLS：逐一尝试不同查询方式，直到找到包含 wusid 的日志。
    返回与 query_sls() 相同格式的结果。
    """
    queries = build_sls_wusid_queries(wusid, path=path)
    wusid_str = str(wusid).strip()

    for strategy_name, query in queries:
        sys.stderr.write("  🔍 尝试策略 [{}]: {}\n".format(
            strategy_name, query[:160]))
        sys.stderr.flush()

        try:
            if strategy_name == "wildcard":
                # 通配兜底：逐页翻页查询 + 客户端过滤
                sls_result = _query_sls_wildcard_paged(cfg, wusid_str, from_ts, to_ts)
            else:
                sls_result = query_sls(cfg, query, from_ts, to_ts)
        except Exception as e:
            sys.stderr.write("  ⚠️ 策略 [{}] 查询异常: {}\n".format(
                strategy_name, str(e)[:100]))
            sys.stderr.flush()
            continue

        if sls_result and sls_result["total"] > 0:
            sys.stderr.write("  ✅ 策略 [{}] 命中 {} 条日志\n".format(
                strategy_name, sls_result["total"]))
            sys.stderr.flush()
            return sls_result

        sys.stderr.write("  ○ 策略 [{}] 无数据，尝试下一策略\n".format(strategy_name))
        sys.stderr.flush()

    # 全部策略均无结果
    sys.stderr.write("  ⚠️ 所有策略均未找到 wusid={} 的日志\n".format(wusid_str))
    sys.stderr.flush()
    return None


def _query_sls_wildcard_paged(cfg, wusid_str, from_ts, to_ts,
                               page_size=200, max_pages=5):
    """
    通配 `*` 翻页查询 + 客户端过滤，最多翻 max_pages 页，
    每页过滤出包含 wusid_str 的日志，找到足够结果即停止翻页。
    返回与 query_sls() 相同格式的结果。
    """
    sc = cfg["sls"]
    client = LogClient(sc["endpoint"], sc["ak_id"], sc["ak_secret"])

    store_stats = []
    failed = []
    logs_by_store = {s: [] for s in sc["logstores"]}

    for store in sc["logstores"]:
        matched = []
        for page in range(max_pages):
            offset = page * page_size
            try:
                req = GetLogsRequest(
                    project=sc["project"], logstore=store,
                    fromTime=from_ts, toTime=to_ts,
                    query="*", line=page_size, offset=offset, reverse=False)
                resp = client.get_logs(req)
                raw_logs = [dict(l.get_contents()) for l in resp.get_logs()]
            except Exception as e:
                failed.append(store)
                sys.stderr.write("    ⚠️ [{}] page={} 失败: {}\n".format(
                    store, page, str(e)[:60]))
                sys.stderr.flush()
                break

            if not raw_logs:
                break  # 该 logstore 已无更多日志

            for log in raw_logs:
                log_text = " ".join(str(v) for v in log.values())
                if wusid_str in log_text:
                    matched.append(log)

            sys.stderr.write("    [{}] page={} 扫描 {} 条，命中 {}\n".format(
                store, page, len(raw_logs), len(matched)))
            sys.stderr.flush()

            # 该页不足一页说明已到末尾，无需继续翻页
            if len(raw_logs) < page_size:
                break

        logs_by_store[store] = matched
        store_stats.append({
            "logstore": store,
            "count": len(matched),
            "status": "ok" if matched else "empty",
        })

    return _build_sls_result(sc["logstores"], logs_by_store, store_stats, failed)



def extract_trace_ids(sls_result):
    """从 SLS 查询结果中提取所有不重复的 trace_id，按出现顺序保序。"""
    seen = set()
    ids  = []
    for log in sls_result.get("all_logs", []):
        raw = log.get("raw", {})
        for field in _SLS_TRACE_FIELDS:
            val = str(raw.get(field, "")).strip()
            if val and val not in ("", "null", "None") and val not in seen:
                seen.add(val)
                ids.append(val)
    return ids


def build_trace_summary(sls_result):
    """
    按 trace_id 汇总 SLS 日志，返回有序列表：
    [ {"trace_id", "first_time", "service", "path", "response_code", "response_msg", "has_error", "log_count"} ]
    """
    summary = {}   # trace_id -> info dict
    order   = []   # 保持首次出现顺序

    for log in sls_result.get("all_logs", []):
        raw = log.get("raw", {})
        tid = None
        for field in _SLS_TRACE_FIELDS:
            v = str(raw.get(field, "")).strip()
            if v and v not in ("", "null", "None"):
                tid = v
                break
        if not tid:
            continue

        if tid not in summary:
            # 解析 data.request / data.response（JSON 字符串）
            path = ""
            code = ""
            msg  = ""
            req_str  = raw.get("data.request", "")
            resp_str = raw.get("data.response", "")
            try:
                req_obj = json.loads(req_str)
                path    = req_obj.get("path", "")
            except Exception:
                pass
            try:
                resp_obj = json.loads(resp_str)
                code     = str(resp_obj.get("code", ""))
                msg      = str(resp_obj.get("msg", ""))
            except Exception:
                pass

            summary[tid] = {
                "trace_id":      tid,
                "first_time":    log.get("time", ""),
                "service":       log.get("service", ""),
                "path":          path,
                "response_code": code,
                "response_msg":  msg,
                "has_error":     False,
                "log_count":     0,
            }
            order.append(tid)

        info = summary[tid]
        info["log_count"] += 1
        if log.get("level") in ("ERROR", "FATAL", "PANIC", "CRITICAL"):
            info["has_error"] = True

    return [summary[tid] for tid in order]


def prompt_trace_selection(trace_summaries):
    """
    向用户展示 trace_id 列表（写入 stderr），读取用户输入，返回选中的 trace_id 列表。
    直接回车 → 选择第一条；输入 all → 全选；输入编号（逗号分隔）→ 选中对应条目。
    """
    stderr = sys.stderr

    stderr.write("\n")
    stderr.write("┌─ 找到以下 TraceID，请选择要深入分析的调用链 " + "─" * 20 + "\n")
    stderr.write("│\n")
    for i, info in enumerate(trace_summaries, 1):
        status = "❌ ERROR" if info["has_error"] else "✅ OK"
        code   = "  code={}".format(info["response_code"]) if info["response_code"] else ""
        rmsg   = "  {}".format(info["response_msg"][:30]) if info["response_msg"] else ""
        path   = info["path"] or "-"
        stderr.write("│  [{:>2}] {}  [{}]  {}  {}{}{}  ({} 条日志)\n".format(
            i,
            info["first_time"],
            info["service"],
            path[:60],
            status,
            code,
            rmsg,
            info["log_count"],
        ))
    stderr.write("│\n")
    stderr.write("└─ 输入编号（逗号分隔），回车选第 1 条，输入 all 全选：")
    stderr.flush()

    try:
        raw = input()
    except (EOFError, KeyboardInterrupt):
        stderr.write("\n已取消\n")
        sys.exit(0)

    raw = raw.strip()
    if not raw:
        return [trace_summaries[0]["trace_id"]]
    if raw.lower() == "all":
        return [t["trace_id"] for t in trace_summaries]

    selected = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            idx = int(token) - 1
            if 0 <= idx < len(trace_summaries):
                selected.append(trace_summaries[idx]["trace_id"])
            else:
                sys.stderr.write("⚠️  编号 {} 超出范围，已忽略\n".format(token))
        except ValueError:
            sys.stderr.write("⚠️  无效输入 '{}' 已忽略\n".format(token))
    if not selected:
        sys.stderr.write("未选中任何 TraceID，退出\n")
        sys.exit(0)
    return selected


_SLS_TIMEOUT = 30  # 单个 logstore 查询超时（秒）

def query_sls(cfg, query, from_ts, to_ts):
    sc = cfg["sls"]
    client = LogClient(sc["endpoint"], sc["ak_id"], sc["ak_secret"])

    sys.stderr.write("⏳ SLS 查询中（{} 个 logstore）...\n".format(len(sc["logstores"])))
    sys.stderr.flush()

    logs_by_store = {s: [] for s in sc["logstores"]}
    store_stats = []
    failed = []

    with ThreadPoolExecutor(max_workers=min(5, len(sc["logstores"]))) as ex:
        futures = {
            ex.submit(_query_one_logstore, client, sc["project"], s, query, from_ts, to_ts): s
            for s in sc["logstores"]
        }
        for f in as_completed(futures, timeout=_SLS_TIMEOUT + 5):
            try:
                store, raw_logs, err = f.result(timeout=_SLS_TIMEOUT)
            except Exception as e:
                store = futures[f]
                raw_logs, err = [], "查询超时（{}s）".format(_SLS_TIMEOUT)
            logs_by_store[store] = raw_logs
            stat = {"logstore": store, "count": len(raw_logs),
                    "status": "error" if err else ("ok" if raw_logs else "empty")}
            if err:
                stat["error"] = err
                failed.append(store)
            store_stats.append(stat)
            sys.stderr.write("  ✓ {} → {} 条{}\n".format(
                store, len(raw_logs), " (⚠️ {})".format(err) if err else ""))
            sys.stderr.flush()

    store_stats.sort(key=lambda x: x["logstore"])
    return _build_sls_result(sc["logstores"], logs_by_store, store_stats, failed)


# ---------------------------------------------------------------------------
# SLS 日志解析公用函数（供 query_sls / _query_sls_wildcard_paged 共用）
# ---------------------------------------------------------------------------
_LEVEL_F = ["data.level", "level", "log_level", "severity", "lvl"]
_MSG_F   = ["data.msg", "message", "msg", "content", "log"]
_FILE_F  = ["data.caller", "caller", "file", "source", "location"]
_SVC_F   = ["data.log_source", "_container_name_", "service", "app",
            "application", "server_name"]


def _pick(d, keys):
    for k in keys:
        if d.get(k): return d[k]
    return ""


def _fmt_ts(s):
    try:
        ts = int(s)
        if ts > 1_000_000_000_000: ts //= 1000
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return s


def _build_sls_result(logstores, logs_by_store, store_stats, failed):
    """
    将各 logstore 的原始 log 字典列表解析为统一格式，返回 query_sls 标准结构。
    """
    all_logs = []
    logs_by_store_parsed = {}
    for store in logstores:
        parsed = []
        for raw in logs_by_store.get(store, []):
            svc = _pick(raw, _SVC_F) or store
            entry = {
                "time":     _fmt_ts(raw.get("__time__", "")),
                "level":    _pick(raw, _LEVEL_F).upper(),
                "logstore": store,
                "service":  svc,
                "file":     _pick(raw, _FILE_F),
                "message":  _pick(raw, _MSG_F),
                "raw":      {k: v for k, v in raw.items()
                             if not k.startswith("__")},
            }
            parsed.append(entry)
        logs_by_store_parsed[store] = parsed
        all_logs.extend(parsed)

    all_logs.sort(key=lambda x: x["time"])
    error_logs = [l for l in all_logs
                  if l["level"] in ("ERROR", "FATAL", "PANIC", "CRITICAL")]

    return {
        "store_stats":      store_stats,
        "failed_logstores": failed,
        "logs_by_logstore": logs_by_store_parsed,
        "all_logs":         all_logs,
        "error_logs":       error_logs,
        "total":            len(all_logs),
        "error_count":      len(error_logs),
    }


# ---------------------------------------------------------------------------
# ARMS 查询 - GetTrace API（HTTP 签名方式，不依赖 SDK）
# ---------------------------------------------------------------------------
def _arms_sign(ak_secret, string_to_sign):
    h = hmac.new(ak_secret.encode("utf-8"),
                 string_to_sign.encode("utf-8"), hashlib.sha1)
    return base64.b64encode(h.digest()).decode("utf-8")

def query_arms(cfg, trace_id, from_ts_ms, to_ts_ms):
    """
    调用 ARMS GetTrace API，返回 Span 列表
    文档：https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/api-arms-2019-08-08-gettrace-apps
    """
    sys.stderr.write("⏳ ARMS 查询中（trace_id={}）...\n".format(trace_id[:16]))
    sys.stderr.flush()
    ac = cfg["arms"]

    # 优先用 alibabacloud SDK，若没装则用 HTTP 直接调用
    if HAS_ARMS_SDK:
        return _query_arms_sdk(ac, trace_id, from_ts_ms, to_ts_ms)
    else:
        return _query_arms_http(ac, trace_id, from_ts_ms, to_ts_ms)

def _query_arms_sdk(ac, trace_id, from_ts_ms, to_ts_ms):
    config = openapi_models.Config(
        access_key_id=ac["ak_id"],
        access_key_secret=ac["ak_secret"],
        region_id=ac["region_id"],
    )
    client = arms_client.Client(config)
    req = arms_models.GetTraceRequest(
        trace_id=trace_id,
        region_id=ac["region_id"],
        start_time=from_ts_ms,
        end_time=to_ts_ms,
    )
    resp = client.get_trace(req)
    spans_raw = resp.body.spans or []
    return _parse_spans(spans_raw, use_sdk=True)

def _query_arms_http(ac, trace_id, from_ts_ms, to_ts_ms):
    """
    不依赖 SDK，用标准 HTTP + 签名方式调用 ARMS API
    """
    endpoint = "arms.{}.aliyuncs.com".format(ac["region_id"])
    now_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    nonce = str(int(time_module.time() * 1000))

    params = {
        "Action":           "GetTrace",
        "Version":          "2019-08-08",
        "Format":           "JSON",
        "AccessKeyId":      ac["ak_id"],
        "SignatureMethod":  "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce":   nonce,
        "Timestamp":        now_utc,
        "TraceID":          trace_id,
        "RegionId":         ac["region_id"],
        "StartTime":        str(from_ts_ms),
        "EndTime":          str(to_ts_ms),
    }

    # 构建签名
    sorted_params = sorted(params.items())
    canonicalized = "&".join(
        "{}={}".format(
            urllib.parse.quote(k, safe=""),
            urllib.parse.quote(str(v), safe="")
        ) for k, v in sorted_params
    )
    string_to_sign = "GET&{}&{}".format(
        urllib.parse.quote("/", safe=""),
        urllib.parse.quote(canonicalized, safe="")
    )
    signature = _arms_sign(ac["ak_secret"] + "&", string_to_sign)
    params["Signature"] = signature

    url = "https://{}/?{}".format(endpoint, urllib.parse.urlencode(params))
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    spans_raw = data.get("Spans", [])
    return _parse_spans(spans_raw, use_sdk=False)

def _parse_spans(spans_raw, use_sdk=False):
    """统一解析 Span，不论来自 SDK 还是 HTTP"""
    RPC_TYPE_MAP = {
        0: "HTTP", 25: "HTTP_CLIENT", 60: "MySQL", 61: "MySQL",
        70: "Redis", 72: "Elasticsearch", 13: "MQ_Client", 252: "MQ",
        23: "Kafka_Client", 256: "Kafka", 7: "Dubbo_Client", 8: "Dubbo",
        9: "gRPC", 40: "Local", 41: "Async", 98: "UserMethod",
        100: "Root", -2: "Frontend", -3: "App",
    }

    def get(obj, key):
        if use_sdk:
            return getattr(obj, _snake(key), None)
        return obj.get(key)

    def _snake(s):
        # CamelCase -> snake_case
        return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

    def fmt_ts(ts):
        try:
            ts = int(ts)
            if ts > 1_000_000_000_000: ts //= 1000
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        except: return str(ts)

    spans = []
    for s in spans_raw:
        tags = {}
        tag_list = get(s, "TagEntryList") or []
        for t in tag_list:
            k = get(t, "Key") or ""
            v = get(t, "Value") or ""
            tags[k] = v

        rpc_type_num = get(s, "RpcType")
        try: rpc_type_num = int(rpc_type_num)
        except: rpc_type_num = -1

        # 提取异常 ID 和完整堆栈（LogEventList）
        exception_id = get(s, "ExceptionId") or tags.get("exception.id") or ""
        log_events = get(s, "LogEventList") or []
        stack_traces = []
        for evt in log_events:
            evt_tags = {}
            evt_tag_list = (get(evt, "TagEntryList") if not use_sdk
                           else getattr(evt, "tag_entry_list", None)) or []
            for t in evt_tag_list:
                k = get(t, "Key") if not use_sdk else getattr(t, "key", "")
                v = get(t, "Value") if not use_sdk else getattr(t, "value", "")
                evt_tags[k or ""] = v or ""
            stack_trace = evt_tags.get("stack", "") or evt_tags.get("error.stack", "")
            if stack_trace:
                stack_traces.append(stack_trace)

        # 完整堆栈：优先 LogEventList，其次 tags 中的 stack 字段
        full_stack = "\n".join(stack_traces) if stack_traces else (
            tags.get("stack") or tags.get("error.stack") or "")

        span = {
            "span_id":       get(s, "SpanId") or "",
            "parent_span_id":get(s, "ParentSpanId") or "",
            "trace_id":      get(s, "TraceID") or "",
            "service":       get(s, "ServiceName") or "",
            "operation":     get(s, "OperationName") or "",
            "ip":            get(s, "ServiceIp") or "",
            "rpc_type":      RPC_TYPE_MAP.get(rpc_type_num, str(rpc_type_num)),
            "rpc_type_num":  rpc_type_num,
            "duration_ms":   int(get(s, "Duration") or 0),
            "result_code":   get(s, "ResultCode") or "0",
            "timestamp":     fmt_ts(get(s, "Timestamp") or 0),
            "rpc_id":        get(s, "RpcId") or "",
            "have_stack":    bool(get(s, "HaveStack")),
            "exception_id":  str(exception_id) if exception_id else "",
            "full_stack":    full_stack,
            "tags":          tags,
            "is_error":      str(get(s, "ResultCode") or "0") not in ("0", "200"),
        }
        spans.append(span)

    return spans


# ---------------------------------------------------------------------------
# ARMS GetStack API - 获取方法级完整堆栈
# ---------------------------------------------------------------------------
def query_arms_stack(cfg, trace_id, rpc_id, pid=None, start_time=None, end_time=None):
    """
    调用 ARMS GetStack API，获取指定 Span 的方法级堆栈。
    文档：https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/api-arms-2019-08-08-getstack-apps
    返回堆栈信息列表或空列表。
    """
    ac = cfg["arms"]
    sys.stderr.write("⏳ ARMS GetStack 查询中（rpc_id={}）...\n".format(rpc_id))
    sys.stderr.flush()

    if HAS_ARMS_SDK:
        return _query_stack_sdk(ac, trace_id, rpc_id, pid, start_time, end_time)
    else:
        return _query_stack_http(ac, trace_id, rpc_id, pid, start_time, end_time)


def _query_stack_sdk(ac, trace_id, rpc_id, pid=None, start_time=None, end_time=None):
    config = openapi_models.Config(
        access_key_id=ac["ak_id"],
        access_key_secret=ac["ak_secret"],
        region_id=ac["region_id"],
    )
    client = arms_client.Client(config)
    req_params = {
        "trace_id": trace_id,
        "region_id": ac["region_id"],
        "rpc_id": rpc_id,
    }
    if pid:
        req_params["pid"] = pid
    if start_time:
        req_params["start_time"] = start_time
    if end_time:
        req_params["end_time"] = end_time
    req = arms_models.GetStackRequest(**req_params)
    resp = client.get_stack(req)
    stack_info = resp.body.stack_info or []
    return _parse_stack_info(stack_info, use_sdk=True)


def _query_stack_http(ac, trace_id, rpc_id, pid=None, start_time=None, end_time=None):
    endpoint = "arms.{}.aliyuncs.com".format(ac["region_id"])
    now_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    nonce = str(int(time_module.time() * 1000))

    params = {
        "Action":           "GetStack",
        "Version":          "2019-08-08",
        "Format":           "JSON",
        "AccessKeyId":      ac["ak_id"],
        "SignatureMethod":  "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce":   nonce,
        "Timestamp":        now_utc,
        "TraceID":          trace_id,
        "RegionId":         ac["region_id"],
        "RpcID":            rpc_id,
    }
    if pid:
        params["Pid"] = pid
    if start_time:
        params["StartTime"] = str(start_time)
    if end_time:
        params["EndTime"] = str(end_time)

    sorted_params = sorted(params.items())
    canonicalized = "&".join(
        "{}={}".format(
            urllib.parse.quote(k, safe=""),
            urllib.parse.quote(str(v), safe="")
        ) for k, v in sorted_params
    )
    string_to_sign = "GET&{}&{}".format(
        urllib.parse.quote("/", safe=""),
        urllib.parse.quote(canonicalized, safe="")
    )
    signature = _arms_sign(ac["ak_secret"] + "&", string_to_sign)
    params["Signature"] = signature

    url = "https://{}/?{}".format(endpoint, urllib.parse.urlencode(params))
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        stack_info = data.get("StackInfo", [])
        return _parse_stack_info(stack_info, use_sdk=False)
    except Exception as e:
        sys.stderr.write("⚠️ GetStack 查询失败: {}\n".format(e))
        sys.stderr.flush()
        return []


def _parse_stack_info(stack_info_raw, use_sdk=False):
    """解析 GetStack API 返回的方法级堆栈"""
    result = []
    for item in stack_info_raw:
        if use_sdk:
            entry = {
                "api":          getattr(item, "api", "") or "",
                "service_name": getattr(item, "service_name", "") or "",
                "duration":     getattr(item, "duration", 0) or 0,
                "rpc_id":       getattr(item, "rpc_id", "") or "",
                "exception":    getattr(item, "exception", "") or "",
                "line":         getattr(item, "line", 0) or 0,
                "start_time":   getattr(item, "start_time", 0) or 0,
            }
            ext_info = getattr(item, "ext_info", None)
            if ext_info:
                entry["ext_info"] = {
                    "type": getattr(ext_info, "type", "") or "",
                    "info": getattr(ext_info, "info", "") or "",
                }
        else:
            entry = {
                "api":          item.get("Api", ""),
                "service_name": item.get("ServiceName", ""),
                "duration":     item.get("Duration", 0),
                "rpc_id":       item.get("RpcId", ""),
                "exception":    item.get("Exception", ""),
                "line":         item.get("Line", 0),
                "start_time":   item.get("StartTime", 0),
            }
            ext_info = item.get("ExtInfo")
            if ext_info:
                entry["ext_info"] = {
                    "type": ext_info.get("Type", ""),
                    "info": ext_info.get("Info", ""),
                }
        result.append(entry)
    return result


def format_stack_detail(stack_entries):
    """将 GetStack 返回的堆栈格式化为可读文本"""
    if not stack_entries:
        return ""
    lines = []
    for i, e in enumerate(stack_entries):
        line = "  [{:>2}] {}".format(i + 1, e["api"])
        if e["service_name"]:
            line += " (服务: {})".format(e["service_name"])
        if e["duration"]:
            line += " {}ms".format(e["duration"])
        if e["line"]:
            line += " L{}".format(e["line"])
        lines.append(line)
        if e.get("exception"):
            lines.append("       ⚡ 异常: {}".format(e["exception"]))
        if e.get("ext_info") and e["ext_info"].get("info"):
            lines.append("       📎 {}".format(e["ext_info"]["info"]))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 调用链树构建
# ---------------------------------------------------------------------------
def build_call_tree(spans):
    """
    根据 ParentSpanId 构建树，输出带缩进的调用链文本
    """
    if not spans:
        return [], "（无 Span 数据）"

    # 找根节点（无 parent 或 parent 不在列表中）
    span_ids = {s["span_id"] for s in spans}
    roots = [s for s in spans
             if not s["parent_span_id"] or s["parent_span_id"] not in span_ids]

    # 按 rpc_id 排序更准确（0 < 0.1 < 0.1.1 ...）
    def rpc_sort_key(s):
        try:
            return [int(x) for x in s["rpc_id"].split(".")]
        except:
            return [0]

    spans_sorted = sorted(spans, key=rpc_sort_key)

    # 构建 parent -> children 映射
    children_map = {}
    for s in spans_sorted:
        pid = s["parent_span_id"]
        children_map.setdefault(pid, []).append(s)

    lines = []
    error_spans = []

    def walk(span, depth=0):
        indent = "  " * depth
        connector = "└─ " if depth > 0 else "● "
        status = "❌" if span["is_error"] else "✅"
        slow   = " ⚠️慢" if span["duration_ms"] > 1000 else ""
        line = "{}{}[{}] {} → {} {}ms {}{}".format(
            indent, connector,
            span["service"],
            span["rpc_type"],
            span["operation"],
            span["duration_ms"],
            status,
            slow,
        )
        if span["ip"]:
            line += "  (ip:{})".format(span["ip"])
        lines.append(line)

        if span["is_error"]:
            error_spans.append(span)
            err_msg = span["tags"].get("error.message") or span["tags"].get("exception.message", "")
            if err_msg:
                lines.append("{}    ⚡ 错误: {}".format(indent, err_msg))
            if span.get("exception_id"):
                lines.append("{}    🔗 异常ID: {}".format(indent, span["exception_id"]))
            if span.get("full_stack"):
                # 堆栈完整输出，按行缩进
                for stack_line in span["full_stack"].split("\n")[:50]:
                    lines.append("{}      {}".format(indent, stack_line))

        # 递归子节点
        for child in children_map.get(span["span_id"], []):
            walk(child, depth + 1)

    for root in (roots if roots else spans_sorted[:1]):
        walk(root)

    tree_text = "\n".join(lines)
    return error_spans, tree_text


# ---------------------------------------------------------------------------
# 根因分析 + 排查建议
# ---------------------------------------------------------------------------
def analyze_root_cause(sls_result, arms_result, call_chain):
    """
    综合 SLS 日志 + ARMS 调用链推断根本原因，给出排查建议。
    返回 {"root_cause": str, "findings": [...], "suggestions": [...]}
    """
    findings    = []
    suggestions = []
    root_cause  = "未能确定根本原因，请查看下方 findings"

    error_spans = []
    slow_spans  = []
    if arms_result:
        error_spans = arms_result.get("error_spans", [])
        slow_spans  = [s for s in arms_result.get("spans", []) if s["duration_ms"] > 1000]

    # ---- 1. 找调用链最深层异常 Span（通常是根因发起点）----
    if error_spans:
        def rpc_depth(s):
            try:    return len(s["rpc_id"].split("."))
            except: return 0

        deepest  = max(error_spans, key=rpc_depth)
        tags     = deepest.get("tags", {})
        err_msg  = (tags.get("error.message") or tags.get("exception.message")
                    or tags.get("exception.type") or "")
        exc_type = tags.get("exception.type") or tags.get("error.kind") or ""
        exc_id   = deepest.get("exception_id") or ""
        stack    = deepest.get("full_stack") or tags.get("stack") or tags.get("error.stack") or ""

        root_cause = "[{}] {}.{} 发生异常（rpc_id={}）".format(
            deepest["service"], deepest["rpc_type"],
            deepest["operation"], deepest["rpc_id"])
        if err_msg:
            root_cause += "：{}".format(err_msg)

        findings.append("调用链根因 Span: rpc_id={}, 服务={}, 操作={}, 耗时={}ms, 结果码={}".format(
            deepest["rpc_id"], deepest["service"], deepest["operation"],
            deepest["duration_ms"], deepest["result_code"]))
        if exc_id:
            findings.append("异常 ID: {}".format(exc_id))
        if exc_type:
            findings.append("异常类型: {}".format(exc_type))
        if stack:
            findings.append("完整堆栈:\n{}".format(stack))

        # 按错误关键词给出定向建议
        text = (err_msg + " " + exc_type).lower()
        if "timeout" in text or "timed out" in text or "read timeout" in text:
            suggestions.append("超时错误：检查下游服务 {} 的响应时间，增大调用方超时配置，或优化慢 SQL/接口".format(
                deepest["service"]))
        if "connection refused" in text or "connection reset" in text or "econnrefused" in text:
            suggestions.append("连接拒绝/重置：确认目标服务 {} 是否正常运行，检查端口/防火墙/K8s Service 配置".format(
                deepest["service"]))
        if "nullpointer" in text or "null pointer" in text or "npe" in text:
            suggestions.append("空指针异常：检查 {} 中 {} 方法的入参/返回值完整性，增加 null 保护".format(
                deepest["service"], deepest["operation"]))
        if "outofmemory" in text or "out of memory" in text or "gc overhead" in text:
            suggestions.append("内存溢出：检查 {} 的 JVM Heap 设置，排查内存泄漏（堆 dump 分析）".format(
                deepest["service"]))
        if "sql" in text or "jdbc" in text or "duplicate entry" in text or "deadlock" in text:
            suggestions.append("数据库错误：检查 SQL 语句、连接池配置、表锁/死锁情况，以及数据一致性")
        if "403" in err_msg or "401" in err_msg or "unauthorized" in text or "permission" in text or "access denied" in text:
            suggestions.append("鉴权/权限错误：检查 AK/SK 有效性、RAM 授权策略、Token 是否过期")
        if "429" in err_msg or "too many requests" in text or "throttl" in text or "rate limit" in text:
            suggestions.append("限流错误：检查 QPS 配额上限，接入方添加退避重试，或申请提升配额")
        if "500" in deepest["result_code"] or "internal server error" in text:
            suggestions.append("服务端内部错误：查看 {} 的完整异常堆栈日志，定位业务代码异常".format(deepest["service"]))
        if "classnotfound" in text or "nosuchmethod" in text or "nosuchfield" in text:
            suggestions.append("类/方法/字段不存在：检查依赖版本兼容性，是否有 JAR 包冲突或未正确打包")

    # ---- 2. 分析慢 Span ----
    if slow_spans:
        slowest = max(slow_spans, key=lambda s: s["duration_ms"])
        findings.append("最慢调用: [{}] {} → {} ({}ms)".format(
            slowest["service"], slowest["rpc_type"], slowest["operation"], slowest["duration_ms"]))
        if slowest["rpc_type"] in ("MySQL", "Redis", "Elasticsearch"):
            suggestions.append("慢{}调用 {}ms：检查索引/缓存命中率，定位慢查询语句".format(
                slowest["rpc_type"], slowest["duration_ms"]))
        elif not error_spans:
            suggestions.append("最慢节点 [{}] {}ms：建议 profiling 分析性能热点，考虑异步/缓存优化".format(
                slowest["service"], slowest["duration_ms"]))

    # ---- 3. 分析 SLS 错误日志 ----
    if sls_result:
        sls_errors = sls_result.get("error_logs", [])
        if sls_errors:
            store_counts = {}
            for el in sls_errors:
                store_counts[el["logstore"]] = store_counts.get(el["logstore"], 0) + 1
            findings.append("SLS ERROR 日志分布: " +
                            ", ".join("[{}:{} 条]".format(k, v) for k, v in store_counts.items()))

            # 与 ARMS 错误服务关联
            if error_spans:
                err_svcs    = {s["service"] for s in error_spans}
                err_stores  = {l["logstore"] for l in sls_errors}
                findings.append("ARMS 异常服务: {} | 有 ERROR 的 LogStore: {}".format(
                    "、".join(sorted(err_svcs)), "、".join(sorted(err_stores))))

            # 第一条错误日志作为佐证
            first = sls_errors[0]
            findings.append("首条 ERROR 日志: [{}] {} {} {}".format(
                first["logstore"], first["time"],
                first["file"] or "", first["message"][:150]))

            if not error_spans:
                root_cause = "SLS 发现 ERROR 日志，但 ARMS 未采样到异常 Span，请重点查看日志"
                suggestions.append("ARMS 未采样此链路，建议开启全量采样或手动标记，同时逐条分析 ERROR 日志")
        elif error_spans:
            findings.append("SLS 日志无 ERROR 级别记录，错误可能仅由 ARMS 采样到")

    # ---- 4. 无任何异常时的提示 ----
    if not error_spans and not (sls_result and sls_result.get("error_logs")):
        if call_chain and call_chain.get("total_spans", 0) > 0:
            root_cause = "调用链和日志均无明显异常"
            suggestions.append("若仍有问题：1) 检查业务逻辑错误码（非 HTTP 500 的业务 code）；"
                                "2) 扩大查询时间范围；3) 确认 TraceID 是否完整传递到所有下游")
        else:
            root_cause = "未查到调用链数据，可能未被 ARMS 采样"
            suggestions.append("确认 ARMS Agent 已接入目标服务；检查采样率配置；确认 TraceID 格式是否正确")

    if not suggestions:
        suggestions.append("建议结合完整日志堆栈与业务代码进一步分析")

    return {
        "root_cause":  root_cause,
        "findings":    findings,
        "suggestions": suggestions,
    }


# ---------------------------------------------------------------------------
# 自然语言时间解析
# ---------------------------------------------------------------------------
_DURATION_UNITS = {
    # 中文
    "分钟": 1, "分": 1,
    "小时": 60, "时": 60,
    "天": 1440, "日": 1440,
    "周": 10080, "星期": 10080,
    "月": 43200,
    # 英文缩写
    "m": 1, "min": 1, "mins": 1,
    "h": 60, "hr": 60, "hrs": 60, "hour": 60, "hours": 60,
    "d": 1440, "day": 1440, "days": 1440,
    "w": 10080, "week": 10080, "weeks": 10080,
    "M": 43200, "month": 43200, "months": 43200,
}

def parse_duration(text):
    """
    将自然语言时间转换为分钟数。
    支持格式：1周, 2天, 1个月, 半小时, 30m, 6h, 3d, 1w, 1.5天 等
    返回 int 分钟数，解析失败返回 None。
    """
    text = text.strip()
    # 去掉 "个" 字（"1个月" → "1月"）
    text = text.replace("个", "")

    # 特殊词
    if text in ("半小时", "半个小时"):
        return 30
    if text in ("半天"):
        return 720

    # 尝试匹配 "数字+单位" 模式
    m = re.match(r'^(\d+(?:\.\d+)?)\s*(.+)$', text)
    if m:
        num = float(m.group(1))
        unit = m.group(2).strip()
        if unit in _DURATION_UNITS:
            return int(num * _DURATION_UNITS[unit])

    # 纯数字视为分钟
    try:
        return int(float(text))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 主函数
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SLS + ARMS 联合问题定位")
    # 查询入口：至少提供一个
    parser.add_argument("--trace-id",  dest="trace_id",
                        help="调用链 TraceID")
    parser.add_argument("--wusid", "--wechat-user-space-id", dest="wusid",
                        help="微信用户空间ID (wechat_user_space_id / promoter_wechat_user_space_id)")
    parser.add_argument("--path", dest="path",
                        help="请求路径 (data.request.path)，支持精确或前缀匹配")
    # 时间 & 范围
    parser.add_argument("--minutes",   type=int, default=None,
                        help="查询最近 N 分钟（与 --duration 二选一）")
    parser.add_argument("--duration",  type=str, default=None,
                        help="自然语言时间范围，如：1小时/2天/1周/1星期/1个月/30m/6h/3d")
    parser.add_argument("--start",     help="2024-01-15 14:00:00")
    parser.add_argument("--end",       help="2024-01-15 15:00:00")
    parser.add_argument("--logstores", help="临时覆盖 SLS_LOGSTORE")
    parser.add_argument("--skip-sls",       action="store_true", help="跳过 SLS 查询")
    parser.add_argument("--skip-arms",      action="store_true", help="跳过 ARMS 查询")
    parser.add_argument("--no-interactive", action="store_true",
                        help="非交互模式：发现多 TraceID 时自动选第一条，不等待用户输入")
    args = parser.parse_args()

    # 参数校验：
    #   - 提供了 trace_id → 直接分析，wusid/path 作为附加 SLS 过滤条件
    #   - 未提供 trace_id → wusid 必填（用于先检索 SLS 再让用户选择 TraceID）
    if not args.trace_id and not args.wusid and not args.path:
        parser.error("未指定 --trace-id 时，--wusid 或 --path 至少需要提供一个")

    # 时间范围：--duration 优先，其次 --minutes，默认 1 周
    if args.duration:
        minutes = parse_duration(args.duration)
        if minutes is None:
            parser.error("无法识别时间格式 '{}'，示例：1小时, 2天, 1周, 1星期, 1个月, 30m, 6h, 3d".format(
                args.duration))
    elif args.minutes is not None:
        minutes = args.minutes
    else:
        minutes = 10080  # 默认 1 周

    now = datetime.now()
    if args.start and args.end:
        from_dt = datetime.strptime(args.start, "%Y-%m-%d %H:%M:%S")
        to_dt   = datetime.strptime(args.end,   "%Y-%m-%d %H:%M:%S")
    else:
        to_dt   = now
        from_dt = now - timedelta(minutes=minutes)

    from_ts_s  = int(from_dt.timestamp())
    to_ts_s    = int(to_dt.timestamp())
    from_ts_ms = from_ts_s * 1000
    to_ts_ms   = to_ts_s   * 1000

    cfg = get_config(
        logstores_override=args.logstores,
        skip_sls=args.skip_sls,
        skip_arms=args.skip_arms,
    )

    trace_id = args.trace_id.strip() if args.trace_id else None
    wusid    = args.wusid.strip()    if args.wusid    else None
    path     = args.path.strip()     if args.path     else None

    result = {
        "query": {
            "trace_id": trace_id,
            "wusid":    wusid,
            "path":     path,
        },
        "time_range": "{} ~ {}".format(
            from_dt.strftime("%Y-%m-%d %H:%M:%S"),
            to_dt.strftime("%Y-%m-%d %H:%M:%S"),
        ),
        "discovered_traces": None,
        "sls":               None,
        "arms":              None,
        "call_chain":        None,
        "analysis":          None,
        "summary":           "",
    }

    sls_result  = None
    arms_spans       = []
    errors_info      = []
    all_arms_results = {}
    arms_trace_ids   = []   # 在模式 A 中由 trace_id 直接确定，模式 B 中从 SLS 发现

    # ---- 模式 A（有 trace_id）：SLS 和 ARMS 并行查询，大幅提速 ----
    sys.stderr.write("🚀 开始查询（时间范围：{}）\n".format(result["time_range"]))
    sys.stderr.flush()
    if trace_id:
        sls_query = None
        if not args.skip_sls:
            sls_query = build_sls_query(
                cfg["sls"]["trace_field"] if not args.skip_sls else "traceId",
                trace_id=trace_id, wusid=wusid, path=path)

        with ThreadPoolExecutor(max_workers=2) as ex:
            sls_future = None
            arms_future = None

            if sls_query:
                sls_future = ex.submit(query_sls, cfg, sls_query, from_ts_s, to_ts_s)
            if not args.skip_arms:
                arms_future = ex.submit(query_arms, cfg, trace_id, from_ts_ms, to_ts_ms)

            if sls_future:
                try:
                    sls_result = sls_future.result()
                    result["sls"] = sls_result
                except Exception as e:
                    errors_info.append("SLS 查询失败: {}".format(e))

            if arms_future:
                try:
                    spans = arms_future.result()
                    all_arms_results[trace_id] = spans
                    arms_spans.extend(spans)
                except Exception as e:
                    errors_info.append("ARMS 查询失败: {}".format(e))

    # ---- 模式 B（无 trace_id）：先查 SLS，再查 ARMS ----
    else:
        if not args.skip_sls:
            # 当 wusid 是主要查询条件时，使用多策略查询
            if wusid:
                sys.stderr.write("🔎 通过 wusid={} 多策略检索 SLS 日志...\n".format(wusid))
                sys.stderr.flush()
                try:
                    sls_result = query_sls_by_wusid(cfg, wusid, from_ts_s, to_ts_s, path=path)
                    result["sls"] = sls_result
                except Exception as e:
                    errors_info.append("SLS 查询失败: {}".format(e))
            else:
                sls_query = build_sls_query(
                    cfg["sls"]["trace_field"] if not args.skip_sls else "traceId",
                    trace_id=None, wusid=wusid, path=path)
                if sls_query:
                    try:
                        sls_result = query_sls(cfg, sls_query, from_ts_s, to_ts_s)
                        result["sls"] = sls_result
                    except Exception as e:
                        errors_info.append("SLS 查询失败: {}".format(e))

        # 从 SLS 结果中发现 trace_id
        arms_trace_ids = []
        if not args.skip_arms and sls_result:
            trace_summaries = build_trace_summary(sls_result)
            if trace_summaries:
                result["discovered_traces"] = trace_summaries
                if args.no_interactive:
                    arms_trace_ids = [trace_summaries[0]["trace_id"]]
                else:
                    arms_trace_ids = prompt_trace_selection(trace_summaries)
            else:
                errors_info.append("SLS 日志中未找到 trace_id 字段，跳过 ARMS 查询")

        if arms_trace_ids:
            with ThreadPoolExecutor(max_workers=min(3, len(arms_trace_ids))) as ex:
                fut_map = {
                    ex.submit(query_arms, cfg, tid, from_ts_ms, to_ts_ms): tid
                    for tid in arms_trace_ids
                }
                for fut in as_completed(fut_map):
                    tid = fut_map[fut]
                    try:
                        spans = fut.result()
                        all_arms_results[tid] = spans
                        arms_spans.extend(spans)
                    except Exception as e:
                        errors_info.append("ARMS 查询失败 (trace_id={}): {}".format(tid, e))

    if arms_spans:
        all_error_spans = [s for s in arms_spans if s["is_error"]]
        result["arms"] = {
            "status":            "ok",
            "queried_trace_ids": arms_trace_ids,
            "span_count":        len(arms_spans),
            "spans":             arms_spans,
            "error_spans":       all_error_spans,
            "per_trace":         {
                tid: {
                    "span_count":  len(spans),
                    "error_spans": [s for s in spans if s["is_error"]],
                }
                for tid, spans in all_arms_results.items()
            },
        }
    else:
        result["arms"] = {
            "status":            "no_data",
            "message":           "ARMS 未采样到此 TraceID 的调用链",
            "queried_trace_ids": arms_trace_ids,
            "span_count":        0,
            "spans":             [],
            "error_spans":       [],
        }

    # ---- 构建调用链树 ----
    if arms_spans:
        error_spans, tree_text = build_call_tree(arms_spans)
        result["call_chain"] = {
            "tree":              tree_text,
            "error_spans":       error_spans,
            "total_spans":       len(arms_spans),
            "error_count":       len(error_spans),
            "services":          list(dict.fromkeys(s["service"] for s in arms_spans)),
            "total_duration_ms": max((s["duration_ms"] for s in arms_spans), default=0),
        }
    else:
        # ARMS 无数据时也要给出明确状态，防止 AI 跳过 ARMS 段
        arms_status = "ARMS 未采样到此 TraceID 的调用链"
        if args.skip_arms:
            arms_status = "用户跳过 ARMS 查询（--skip-arms）"
        elif any("ARMS" in e for e in errors_info):
            arms_status = "ARMS 查询失败: " + next(
                (e for e in errors_info if "ARMS" in e), "未知错误")
        result["call_chain"] = {
            "tree":              "⚠️ " + arms_status,
            "error_spans":       [],
            "total_spans":       0,
            "error_count":       0,
            "services":          [],
            "total_duration_ms": 0,
            "status":            arms_status,
        }

    # ---- 用 GetStack API 获取 error span 的方法级堆栈 ----
    stack_details = {}
    if arms_spans and not args.skip_arms:
        error_spans_for_stack = [s for s in arms_spans if s["is_error"]]
        # 最多查 5 个 error span 的堆栈，避免过多 API 调用
        for es in error_spans_for_stack[:5]:
            tid = es.get("trace_id") or trace_id
            rid = es.get("rpc_id")
            if not tid or not rid:
                continue
            try:
                stack_entries = query_arms_stack(
                    cfg, tid, rid,
                    pid=es["tags"].get("appName") or es["tags"].get("pid"),
                    start_time=from_ts_ms,
                    end_time=to_ts_ms,
                )
                if stack_entries:
                    key = "{}:{}".format(tid, rid)
                    stack_details[key] = {
                        "trace_id":      tid,
                        "rpc_id":        rid,
                        "service":       es["service"],
                        "operation":     es["operation"],
                        "exception_id":  es.get("exception_id", ""),
                        "stack_entries": stack_entries,
                        "formatted":     format_stack_detail(stack_entries),
                    }
            except Exception as e:
                errors_info.append("GetStack 失败 (rpc_id={}): {}".format(rid, e))

    result["stack_details"] = stack_details if stack_details else None

    # ---- 检查是否完全无数据 ----
    sls_total = sls_result["total"] if sls_result else 0
    arms_total = len(arms_spans)
    no_data = (sls_total == 0 and arms_total == 0)
    result["no_data"] = no_data
    result["current_minutes"] = minutes

    # ---- 根因分析 ----
    analysis = analyze_root_cause(sls_result, result.get("arms"), result.get("call_chain"))
    if no_data:
        # 根据当前已查范围，建议下一步扩大到多少
        if minutes < 10080:
            next_hint = "--duration \"1周\""
        elif minutes < 43200:
            next_hint = "--duration \"1个月\""
        else:
            next_hint = "确认 TraceID 是否正确"
        analysis["suggestions"].insert(0,
            "当前时间范围 ({}) 内 SLS 和 ARMS 均无数据，建议扩大时间范围重新查询（{}）".format(
                result["time_range"], next_hint))
    result["analysis"] = analysis

    # ---- 生成综合摘要 ----
    summary_lines = []
    summary_lines.append("=" * 60)
    if trace_id:
        summary_lines.append("TraceID:  {}".format(trace_id))
    if wusid:
        summary_lines.append("WSUID:    {}".format(wusid))
    if path:
        summary_lines.append("Path:     {}".format(path))
    if arms_trace_ids and not trace_id:
        summary_lines.append("发现 TraceID: {}".format(", ".join(arms_trace_ids)))
    summary_lines.append("时间范围: {}".format(result["time_range"]))
    summary_lines.append("=" * 60)

    # 根因结论（置顶）
    summary_lines.append("\n【根本原因】")
    summary_lines.append("  " + analysis["root_cause"])

    # 关键发现
    if analysis["findings"]:
        summary_lines.append("\n【关键发现】")
        for f in analysis["findings"]:
            summary_lines.append("  • " + f)

    # 排查建议
    if analysis["suggestions"]:
        summary_lines.append("\n【排查建议】")
        for i, s in enumerate(analysis["suggestions"], 1):
            summary_lines.append("  {}. {}".format(i, s))

    # ARMS 调用链详情（多 trace_id 时逐一展示）
    if result["call_chain"]:
        cc = result["call_chain"]
        summary_lines.append("\n【ARMS 调用链】涉及 {} 个服务，共 {} 个 Span，总耗时 {}ms".format(
            len(cc["services"]), cc["total_spans"], cc["total_duration_ms"]))
        summary_lines.append("涉及服务：{}".format("、".join(cc["services"])))
        if cc["error_count"]:
            summary_lines.append("❌ 发现 {} 个异常 Span：".format(cc["error_count"]))
            for es in cc["error_spans"]:
                err_msg = (es["tags"].get("error.message")
                           or es["tags"].get("exception.message", "无详细信息"))
                summary_lines.append("   [{}] {} → {} | {}".format(
                    es["service"], es["rpc_type"], es["operation"], err_msg[:100]))
        # 多 trace 时分段展示
        if len(arms_trace_ids) > 1:
            for tid, spans in all_arms_results.items():
                if not spans:
                    continue
                _, tree_text_i = build_call_tree(spans)
                summary_lines.append("\n── TraceID: {} ──".format(tid))
                summary_lines.append(tree_text_i)
        else:
            summary_lines.append("\n调用链路图：")
            summary_lines.append(cc["tree"])
    elif not args.skip_arms:
        if arms_trace_ids:
            summary_lines.append("\n【ARMS 调用链】查询了 {} 个 TraceID，均无数据".format(
                len(arms_trace_ids)))
        else:
            summary_lines.append("\n【ARMS 调用链】未查到数据（TraceID 可能未被 ARMS 采样）")

    # GetStack 方法级堆栈详情
    if stack_details:
        summary_lines.append("\n【方法级堆栈详情（GetStack）】")
        for key, detail in stack_details.items():
            summary_lines.append("\n── [{}] {} → {} ──".format(
                detail["service"], detail["operation"],
                "异常ID: {}".format(detail["exception_id"]) if detail["exception_id"] else "rpc_id: {}".format(detail["rpc_id"])))
            summary_lines.append(detail["formatted"])

    # SLS 日志摘要
    if sls_result:
        summary_lines.append("\n【SLS 日志】")
        for stat in sls_result["store_stats"]:
            flag = {"ok": "✅", "empty": "○", "error": "❌"}.get(stat["status"], "?")
            summary_lines.append("  {} [{}] {} 条".format(
                flag, stat["logstore"], stat["count"]))
        if sls_result["error_logs"]:
            summary_lines.append("\n❌ ERROR 日志 ({} 条)：".format(sls_result["error_count"]))
            for el in sls_result["error_logs"][:5]:
                summary_lines.append("  [{}] {} | {} | {}".format(
                    el["logstore"], el["time"], el["file"] or "-", el["message"][:120]))
    elif not args.skip_sls:
        summary_lines.append("\n【SLS 日志】未查到数据")

    if errors_info:
        summary_lines.append("\n⚠️ 查询警告：")
        for e in errors_info:
            summary_lines.append("  " + e)

    result["summary"] = "\n".join(summary_lines)

    # Windows UTF-8 输出
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
