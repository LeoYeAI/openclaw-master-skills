import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from scripts.config import build_serverless_client, load_emr_skill_config


def _parse_json(value: Optional[str]) -> Dict[str, Any]:
    if not value:
        return {}
    return json.loads(value)


def _merge_conf(base: Optional[Dict[str, Any]], override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    if base:
        merged.update(base)
    if override:
        merged.update(override)
    return merged


def _add_spark_credential(conf: Dict[str, Any]) -> Dict[str, Any]:
    ak = os.getenv("VOLCENGINE_AK")
    sk = os.getenv("VOLCENGINE_SK")
    if ak:
        conf["serverless.spark.access.key"] = ak
    if sk:
        conf["serverless.spark.secret.key"] = sk
    return conf


def _add_compute_group(conf: Dict[str, Any], compute_group: Optional[str]) -> Dict[str, Any]:
    if compute_group:
        conf["serverless.compute.group.name"] = compute_group
    return conf


def _try_construct(task_cls: Any, attempts: Iterable[Dict[str, Any]]) -> Any:
    last_exc: Optional[BaseException] = None
    for kwargs in attempts:
        try:
            return task_cls(**{k: v for k, v in kwargs.items() if v is not None})
        except TypeError as exc:
            last_exc = exc
    raise RuntimeError(f"构造 task 失败: {task_cls} {last_exc}") from last_exc


def _resolve_task_type(engine: str) -> Any:
    try:
        from serverless.common import TaskTypeEnum  # type: ignore
    except Exception:
        return engine.lower()
    key = engine.upper()
    if hasattr(TaskTypeEnum, key):
        return getattr(TaskTypeEnum, key)
    return engine.lower()


def _submit(task: Any) -> str:
    client = build_serverless_client()
    try:
        try:
            job = client.execute(
                task=task,
                is_sync=False,
            )
        except TypeError:
            job = client.execute(task, is_sync=False)
        job_id = getattr(job, "id", None) or getattr(job, "job_id", None) or str(job)
        return str(job_id)
    finally:
        try:
            client.close()
        except Exception:
            pass


def _ensure_queue(queue: Optional[str]) -> str:
    if queue:
        return queue
    cfg = load_emr_skill_config()
    if cfg.default_queue:
        return cfg.default_queue
    raise RuntimeError("queue 未指定且未配置 EMR_DEFAULT_QUEUE")


def _cmd_sql(args: argparse.Namespace) -> str:
    conf = _merge_conf({}, _parse_json(args.conf))
    conf = _add_compute_group(conf, args.compute_group)
    queue = _ensure_queue(args.queue)

    if args.engine == "spark":
        try:
            from serverless.task import SparkSQLTask  # type: ignore
        except Exception as exc:
            raise RuntimeError("未安装 serverless SDK 或缺少 serverless.task.SparkSQLTask") from exc
        task = _try_construct(
            SparkSQLTask,
            [
                {"name": args.name, "query": args.query, "conf": conf, "queue": queue},
                {"name": args.name, "sql": args.query, "conf": conf, "queue": queue},
            ],
        )
    else:
        try:
            from serverless.task import PrestoSQLTask  # type: ignore
        except Exception as exc:
            raise RuntimeError("未安装 serverless SDK 或缺少 serverless.task.PrestoSQLTask") from exc
        task = _try_construct(
            PrestoSQLTask,
            [
                {"name": args.name, "sql": args.query, "conf": conf, "queue": queue},
                {"name": args.name, "query": args.query, "conf": conf, "queue": queue},
            ],
        )
    return _submit(task)

spark_jar_jobs = [("serverless.task", "SparkJarTask"), ("serverless.task", "JarTask")]

def _cmd_jar(args: argparse.Namespace) -> str:
    conf = _merge_conf({}, _parse_json(args.conf))
    conf = _add_spark_credential(conf)
    conf = _add_compute_group(conf, args.compute_group)
    queue = _ensure_queue(args.queue)

    task_cls = None
    for mod_name, cls_name in spark_jar_jobs:
        try:
            mod = __import__(mod_name, fromlist=[cls_name])
            task_cls = getattr(mod, cls_name)
            break
        except Exception:
            continue
    if task_cls is None:
        raise RuntimeError("未安装 serverless SDK 或缺少 SparkJarTask/JarTask")

    main_args = _parse_json(args.main_args).get("args") if args.main_args else None
    if main_args is None:
        main_args_list: List[str] = []
    elif isinstance(main_args, list):
        main_args_list = [str(x) for x in main_args]
    else:
        raise RuntimeError("--main-args 需要是形如 {\"args\":[...]} 的 JSON")

    depend_jars = _parse_json(args.depend_jars).get("items") if args.depend_jars else []
    files = _parse_json(args.files).get("items") if args.files else []
    archives = _parse_json(args.archives).get("items") if args.archives else []

    task = _try_construct(
        task_cls,
        [
            {
                "name": args.name,
                "jar": args.jar,
                "main_class": args.main_class,
                "main_args": main_args_list,
                "depend_jars": depend_jars,
                "files": files,
                "archives": archives,
                "conf": conf,
                "queue": queue,
            },
            {
                "name": args.name,
                "jar_resource": args.jar,
                "main_class": args.main_class,
                "args": main_args_list,
                "conf": conf,
                "queue": queue,
            },
            {
                "name": args.name,
                "jar": args.jar,
                "main_class": args.main_class,
                "args": main_args_list,
                "conf": conf,
                "queue": queue,
            },
        ],
    )
    return _submit(task)


def _cmd_pyspark(args: argparse.Namespace) -> str:
    conf = _merge_conf({}, _parse_json(args.conf))
    conf = _add_spark_credential(conf)
    conf = _add_compute_group(conf, args.compute_group)
    queue = _ensure_queue(args.queue)

    try:
        from serverless.task import PySparkTask  # type: ignore
    except Exception as exc:
        raise RuntimeError("未安装 serverless SDK 或缺少 serverless.task.PySparkTask") from exc

    script_args = _parse_json(args.args).get("args") if args.args else []
    if not isinstance(script_args, list):
        raise RuntimeError("--args 需要是形如 {\"args\":[...]} 的 JSON")

    pyfiles = _parse_json(args.pyfiles).get("items") if args.pyfiles else []
    depend_jars = _parse_json(args.depend_jars).get("items") if args.depend_jars else []
    files = _parse_json(args.files).get("items") if args.files else []
    archives = _parse_json(args.archives).get("items") if args.archives else []

    task = _try_construct(
        PySparkTask,
        [
            {
                "name": args.name,
                "script": args.script,
                "args": script_args,
                "pyfiles": pyfiles,
                "depend_jars": depend_jars,
                "files": files,
                "archives": archives,
                "conf": conf,
                "queue": queue,
            },
            {
                "name": args.name,
                "python_resource": args.script,
                "args": script_args,
                "pyfiles": pyfiles,
                "conf": conf,
                "queue": queue,
            },
        ],
    )
    return _submit(task)

ray_jobs = [("serverless.task", "RayJobTask"), ("serverless.task", "RayTask")]

def _cmd_ray(args: argparse.Namespace) -> str:
    conf = _merge_conf({}, _parse_json(args.conf))
    conf = _add_compute_group(conf, args.compute_group)
    queue = _ensure_queue(args.queue)

    task_cls = None
    for mod_name, cls_name in ray_jobs:
        try:
            mod = __import__(mod_name, fromlist=[cls_name])
            task_cls = getattr(mod, cls_name)
            break
        except Exception:
            continue
    if task_cls is None:
        raise RuntimeError("未安装 serverless SDK 或缺少 RayJobTask/RayTask")

    runtime_env = _parse_json(args.runtime_env) if args.runtime_env else {}

    task = _try_construct(
        task_cls,
        [
            {
                "name": args.name,
                "entrypoint_cmd": args.entrypoint_cmd,
                "entrypoint_resource": args.entrypoint_resource,
                "head_cpu": args.head_cpu,
                "head_memory": args.head_memory,
                "worker_cpu": args.worker_cpu,
                "worker_memory": args.worker_memory,
                "worker_replicas": args.worker_replicas,
                "runtime_env": runtime_env,
                "conf": conf,
                "queue": queue,
            },
            {
                "name": args.name,
                "entrypoint_cmd": args.entrypoint_cmd,
                "entrypoint_resource": args.entrypoint_resource,
                "conf": conf,
                "queue": queue,
            },
        ],
    )
    return _submit(task)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sql = sub.add_parser("sql")
    p_sql.add_argument("--engine", choices=["spark", "presto"], required=True)
    p_sql.add_argument("--query", required=True)
    p_sql.add_argument("--name", default="sql")
    p_sql.add_argument("--queue")
    p_sql.add_argument("--compute-group", dest="compute_group")
    p_sql.add_argument("--conf")
    p_sql.set_defaults(func=_cmd_sql)

    p_jar = sub.add_parser("jar")
    p_jar.add_argument("--jar", required=True)
    p_jar.add_argument("--main-class", dest="main_class", required=True)
    p_jar.add_argument("--main-args")
    p_jar.add_argument("--depend-jars")
    p_jar.add_argument("--files")
    p_jar.add_argument("--archives")
    p_jar.add_argument("--name", default="jar")
    p_jar.add_argument("--queue")
    p_jar.add_argument("--compute-group", dest="compute_group")
    p_jar.add_argument("--conf")
    p_jar.set_defaults(func=_cmd_jar)

    p_pyspark = sub.add_parser("pyspark")
    p_pyspark.add_argument("--script", required=True)
    p_pyspark.add_argument("--args")
    p_pyspark.add_argument("--pyfiles")
    p_pyspark.add_argument("--depend-jars")
    p_pyspark.add_argument("--files")
    p_pyspark.add_argument("--archives")
    p_pyspark.add_argument("--name", default="pyspark")
    p_pyspark.add_argument("--queue")
    p_pyspark.add_argument("--compute-group", dest="compute_group")
    p_pyspark.add_argument("--conf")
    p_pyspark.set_defaults(func=_cmd_pyspark)

    p_ray = sub.add_parser("ray")
    p_ray.add_argument("--entrypoint-cmd", dest="entrypoint_cmd", required=True)
    p_ray.add_argument("--entrypoint-resource", dest="entrypoint_resource", required=True)
    p_ray.add_argument("--head-cpu", dest="head_cpu")
    p_ray.add_argument("--head-memory", dest="head_memory")
    p_ray.add_argument("--worker-cpu", dest="worker_cpu")
    p_ray.add_argument("--worker-memory", dest="worker_memory")
    p_ray.add_argument("--worker-replicas", dest="worker_replicas", type=int, default=None)
    p_ray.add_argument("--runtime-env", dest="runtime_env")
    p_ray.add_argument("--name", default="ray")
    p_ray.add_argument("--queue")
    p_ray.add_argument("--compute-group", dest="compute_group")
    p_ray.add_argument("--conf")
    p_ray.set_defaults(func=_cmd_ray)

    args = parser.parse_args()
    job_id = args.func(args)
    print(job_id)


if __name__ == "__main__":
    main()
