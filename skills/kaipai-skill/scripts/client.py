import json
import os
import tempfile
import requests
from pathlib import Path
from urllib.parse import urlencode
from ai import api
from sign_sdk import sign
import config as app_config


def _load_env_file():
    """
    Load environment variables from a .env file.
    Search order: 1) directory containing client.py  2) current working directory
    """
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        env_path = Path.cwd() / '.env'

    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if key and key not in os.environ:
                        os.environ[key] = value


_load_env_file()


def _wapi_meta_code_value(meta_code):
    """
    Normalize meta.code for comparisons (int). Unparseable non-zero codes become -1.
    Treat missing / 0 / "0" as success (0).
    """
    if meta_code is None:
        return 0
    if meta_code == 0 or meta_code == "0":
        return 0
    try:
        return int(meta_code)
    except (TypeError, ValueError):
        return -1


class WapiApiError(RuntimeError):
    """HTTP 200 but WAPI meta.code != 0."""

    def __init__(self, code: int, msg: str, raw: dict, *, original_code=None):
        self.code = code
        self.original_code = original_code if original_code is not None else code
        self.msg = msg or "Request failed"
        self.raw = raw if isinstance(raw, dict) else {}
        detail = json.dumps(self.raw, ensure_ascii=False)
        super().__init__(f"[{self.original_code}] {self.msg} | API response: {detail}")


class ConsumeDeniedError(WapiApiError):
    """Non-zero meta from POST /skill/consume.json (quota / permission)."""


class WapiClient:
    """Signed HTTP client for the skill WAPI gateway (see config.WAPI_ENDPOINT)."""

    def __init__(self, ak, sk):
        """
        :param ak: Access Key
        :param sk: Secret Key
        """
        self.ak = ak
        self.sk = sk
        self.endpoint = app_config.WAPI_ENDPOINT

    def request(self, path, method="GET", params=None, body=None):
        """
        Send a signed request to the configured WAPI host (HTTPS).

        :return: Parsed JSON under the top-level ``response`` field
        :raises WapiApiError: on HTTP 200 with meta.code != 0
        :raises RuntimeError: on HTTP errors and transport failures
        """
        query_string = urlencode(params) if params else ""
        uri = f"https://{self.endpoint}{path}"
        if query_string:
            uri = f"{uri}?{query_string}"

        try:
            import config as app_config
            signer = sign.Signer(self.ak, self.sk)
            headers = {
                # sign.HeaderHost: self.endpoint,
                "User-Agent": getattr(app_config, "USER_AGENT", "action-web-skill-v1.2.1"),
            }

            body_str = ""
            if body:
                headers["Content-Type"] = "application/json"
                body_str = json.dumps(body)

            signed_request = signer.sign(uri, method, headers, body_str)

            session = requests.Session()
            resp = session.send(signed_request, timeout=10)

            if resp.status_code == 200:
                data = json.loads(resp.content)

                meta = data.get("meta") or {}
                raw_code = meta.get("code", 0)
                norm = _wapi_meta_code_value(raw_code)

                if norm != 0:
                    msg = meta.get("msg", "Request failed")
                    raise WapiApiError(
                        norm, msg, data, original_code=raw_code
                    )

                return data.get("response", {})
            else:
                raise RuntimeError(
                    f"Request failed: HTTP {resp.status_code} | body: {resp.text}"
                )
        except (RuntimeError, WapiApiError):
            raise
        except Exception as e:
            raise RuntimeError(f"Request error: {e}")


class SkillClient:
    """
    High-level client: remote config, quota consume, upload, and task run.

    Example::
        client = SkillClient()
        client.fetch_config()
        result = client.run_task("sod", "/path/to/image.jpg")
    """

    def __init__(self, ak=None, sk=None, region="cn-north-4", oss_region=None, auto_fetch_config=True):
        """
        :param ak: Access Key (default: env ``MT_AK``)
        :param sk: Secret Key (default: env ``MT_SK``)
        :param region: API region, default cn-north-4
        :param oss_region: Optional OSS region override
        :param auto_fetch_config: If True, fetch remote config on init
        """
        self.ak = ak or os.environ.get("MT_AK")
        self.sk = sk or os.environ.get("MT_SK")

        if not self.ak or not self.sk:
            raise ValueError("AK and SK are required via arguments or MT_AK / MT_SK")

        self.wapi = WapiClient(self.ak, self.sk)

        self.api = api.AiApi(self.ak, self.sk, region, oss_region)

        if auto_fetch_config:
            self.fetch_config()

        self._pipeline_trace: list = []

    def fetch_config(self, gid=None, version=None):
        """
        Fetch skill config from wapi and refresh local SDK settings.

        :param gid: Optional group id (uses cached gid if omitted)
        :param version: Client version string (default from config.VERSION)
        """
        if version is None:
            import config as app_config
            version = getattr(app_config, "VERSION", "v1.2.1")

        if not gid:
            cached_gid = self._get_cached_gid()
            if cached_gid:
                gid = cached_gid

        try:
            response = self.wapi.request(
                "/skill/config.json",
                method="POST",
                body={"gid": gid or "", "version": version or ""}
            )
        except RuntimeError as e:
            raise RuntimeError(
                "Failed to fetch skill config (check network, AK/SK, and server). "
                "Detail: " + str(e)
            ) from e

        if response.get("gid"):
            self._cache_gid(response["gid"])

        if response.get("need_update"):
            message = response.get("update_message", "A newer version is available; please update.")
            print(f"[config update] {message}")

        self._update_config_from_response(response)

        return response

    def _get_cached_gid(self):
        """Load gid from local disk cache."""
        cache_file = os.path.expanduser("~/.cache/kaipai/gid.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("gid")
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def _cache_gid(self, gid):
        """Persist gid to local disk cache."""
        cache_file = os.path.expanduser("~/.cache/kaipai/gid.json")
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"gid": gid}, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def _update_config_from_response(self, response):
        """Apply algorithm block from config response to AiApi and INVOKE."""
        if "algorithm" not in response:
            return

        algo = response["algorithm"]

        if "regions" in algo:
            self.api._config["regions"].update(algo["regions"])
            if self.api.region in algo["regions"]:
                self.api.EndPoint = algo["regions"][self.api.region]

        if "token_policy_type" in algo:
            self.api._config["token_policy_type"] = algo["token_policy_type"]

        if "token_policy_types" in algo:
            self.api._config["token_policy_types"] = algo["token_policy_types"]

        if "invoke" in algo:
            import config as app_config
            app_config.INVOKE.update(algo["invoke"])

    def _consume_permission(self, url, task):
        """Call quota/consume API before running a task."""
        gid = self._get_cached_gid()

        try:
            return self.wapi.request(
                "/skill/consume.json",
                method="POST",
                body={"url": url, "task": task, "gid": gid or ""}
            )
        except WapiApiError as e:
            raise ConsumeDeniedError(
                e.code, e.msg, e.raw, original_code=e.original_code
            ) from e

    @staticmethod
    def _preview_media_ref(url) -> str:
        if url is None:
            return ""
        if isinstance(url, str):
            return api.safe_url_preview(url)
        if isinstance(url, dict):
            u = url.get("url") or url.get("uri")
            if u:
                return api.safe_url_preview(str(u))
        try:
            return api.safe_url_preview(json.dumps(url, ensure_ascii=False), max_len=80)
        except (TypeError, ValueError):
            return "<non-serializable>"

    def _fetch_http_input_to_tempfile(self, url: str) -> tuple[str, int]:
        """
        Stream-download URL to a temp file (bounded size). Caller must unlink path.
        """
        preview = api.safe_url_preview(url)
        conn_t = app_config.url_download_connect_timeout()
        read_t = app_config.url_download_read_timeout()
        max_b = app_config.url_download_max_bytes()
        headers = {
            "User-Agent": getattr(app_config, "USER_AGENT", "action-web-skill-v1.2.1"),
        }
        try:
            with requests.get(
                url,
                stream=True,
                timeout=(conn_t, read_t),
                headers=headers,
            ) as resp:
                try:
                    resp.raise_for_status()
                except requests.HTTPError as e:
                    code = getattr(resp, "status_code", "?")
                    raise RuntimeError(
                        f"Input URL HTTP {code} (url={preview}). "
                        "Signed URLs may be expired; shell may have broken the URL at '&' without quotes."
                    ) from e

                fd, path = tempfile.mkstemp(prefix="openclaw_in_", suffix=".bin")
                total = 0
                try:
                    with os.fdopen(fd, "wb") as out:
                        for chunk in resp.iter_content(chunk_size=65536):
                            if not chunk:
                                continue
                            total += len(chunk)
                            if total > max_b:
                                raise RuntimeError(
                                    f"Input URL download exceeds max bytes ({max_b}); url={preview}. "
                                    "Set MT_AI_URL_MAX_BYTES to raise the cap or use a smaller file."
                                )
                            out.write(chunk)
                except Exception:
                    try:
                        os.unlink(path)
                    except OSError:
                        pass
                    raise

                if total == 0:
                    try:
                        os.unlink(path)
                    except OSError:
                        pass
                    raise RuntimeError(
                        f"Input URL returned empty body (url={preview})."
                    )

                return path, total
        except requests.Timeout as e:
            raise RuntimeError(
                f"Input URL download timed out (url={preview}). "
                f"Try MT_AI_URL_READ_TIMEOUT (read={read_t}s, connect={conn_t}s) or "
                f"`kaipai_ai.py resolve-input --url ...` then pass local --input. Detail: {e}"
            ) from e
        except requests.RequestException as e:
            raise RuntimeError(
                f"Input URL download failed (url={preview}): {e}"
            ) from e

    def run_task(self, task_name, image_path, params=None, on_async_submitted=None):
        """
        Upload media (or use remote URL) and run the named algorithm task.

        :param task_name: Preset name from config INVOKE
        :param image_path: Local path or http(s) URL
        :param params: Optional invoke params merged over preset defaults
        :param on_async_submitted: Optional ``callable(task_id: str)`` invoked once
            after the server accepts an async job (status 9) and before status polling.
        """
        self._pipeline_trace = []

        if isinstance(image_path, str) and image_path.startswith(("http://", "https://")):
            preview = api.safe_url_preview(image_path)
            api._progress_log(f"input: download from URL (GET {preview})")
            tmp_path, n = self._fetch_http_input_to_tempfile(image_path)
            try:
                api._progress_log(
                    f"input: download done ({n} bytes) → OSS upload (PutObject)"
                )
                self._pipeline_trace.append(
                    {"step": "download_input", "from_url": preview, "bytes": n}
                )
                url = self.api.getFileUrl(tmp_path)
                self._pipeline_trace.append(
                    {"step": "upload_input", "via": "oss_put_object", "bytes": n}
                )
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        else:
            ip = image_path
            sz = None
            if isinstance(ip, str) and os.path.isfile(ip):
                sz = os.path.getsize(ip)
                api._progress_log(
                    f"input: local file → OSS upload ({os.path.basename(ip)}, {sz} bytes)"
                )
            else:
                api._progress_log("input: local path → OSS upload (PutObject)")
            url = self.api.getFileUrl(image_path)
            self._pipeline_trace.append(
                {
                    "step": "upload_input",
                    "via": "oss_put_object",
                    "path": os.path.basename(ip) if isinstance(ip, str) else str(ip),
                    "bytes": sz,
                }
            )
        if url is None:
            raise RuntimeError("Upload failed")

        ref = self._preview_media_ref(url)
        self._pipeline_trace.append({"step": "media_url_ready", "input_media": ref})
        api._progress_log(f"quota: POST /skill/consume.json task={task_name!r}")
        consume_info = self._consume_permission(url, task_name)
        context = consume_info.get("context", "") if consume_info else ""
        api._progress_log("quota: consume OK → submit algorithm job")

        self._pipeline_trace.append({"step": "consume_quota", "task": task_name})
        self._pipeline_trace.append(
            {"step": "submit_algorithm", "invoke_preset": task_name}
        )

        return self.api.invoke_task(
            task_name, url, params, context, on_async_submitted=on_async_submitted
        )

    def poll_task_status(self, task_id: str):
        """
        Resume status polling for an existing async task (same signing / token policy
        as run-task). Does not upload media or call consume — use the ``task_id`` from
        a previous submit or failure JSON.

        :param task_id: Full task id string from ``data.result.id`` or failure payload
        :return: Same shapes as ``run_task`` (success dict with ``output_urls``, or
            failure dicts with ``skill_status`` / ``error``).
        """
        tid = (task_id or "").strip()
        if not tid:
            raise ValueError("task_id is required")
        self._pipeline_trace = [
            {
                "step": "resume_poll",
                "description": "No input download, OSS upload, or consume; algorithm status GET only",
                "task_id": tid,
            }
        ]
        api._progress_log(
            "query-task: resume polling only (no input download / OSS upload / consume)"
        )
        policy = self.api.getAiStrategy()
        if not policy:
            raise RuntimeError(
                "Failed to load AI token policy (check network, AK/SK, and fetch_config)."
            )
        return self.api.status(tid, policy)
