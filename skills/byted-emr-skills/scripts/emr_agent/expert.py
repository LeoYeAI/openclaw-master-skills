# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # 添加父目录
from pathlib import Path
from scripts.client.tmp_file_manager import _get_tmp_dir

from scripts.client.volc_open_api_client import request, stream_request
from scripts.config import load_emr_skill_config

skill_cfg = load_emr_skill_config()


def _call_api(action: str, body, timeout=30):
    region = skill_cfg.region
    return request(
        "emr",
        action,
        "2025-10-15",
        region,
        f"emr.{region}.volcengineapi.com",
        "POST",
        {},
        body,
        timeout=timeout,
    )
    # api_client = _get_volc_api_client()
    # header_params = {
    #     'Accept': api_client.select_header_accept(['application/json']),
    #     'Content-Type': api_client.select_header_content_type(['application/json']),
    #     'Connection': 'close',
    #     'Accept-Encoding': 'identity'
    # }
    # auth_settings = ['volcengineSign']
    # return api_client.call_api(
    #     f'/{action}/2025-10-15/emr/post/application_json/', 'POST',
    #     {},
    #     [],
    #     header_params,
    #     body=body,
    #     post_params=[],
    #     files={},
    #     response_type=response_type,
    #     auth_settings=auth_settings,
    #     async_req=False,
    #     _return_http_data_only=True,
    #     _preload_content=True,
    #     _request_timeout=timeout,
    #     collection_formats={}
    # )

def _stream_call_api(action: str, body, timeout=30):
    task_id = ""
    result_events = []
    region = skill_cfg.region
    run_finished = False
    try:
        for event in stream_request(
            "emr",
            action,
            "2025-10-15",
            region,
            f"emr.{region}.volcengineapi.com",
            "POST",
            {},
            body,
            timeout=timeout,
            headers={'Accept': 'text/event-stream'},
        ):
            if not task_id:
                header = event.get_response_header()
                task_id = header["X-Task-Id"]
            if not event.get_event_data().startswith('data:'):
                continue
            result_events.append(event.get_event_data())

            if "RUN_FINISHED" in event.get_event_data():
                run_finished = True
    except Exception as ex:
        if run_finished:
            print("agent run success")
            return "\n".join(result_events)
        result_events = []
        # 失败的尝试一次断点续传
        if not task_id:
            raise ex
        for event in stream_request(
            "emr",
            action,
            "2025-10-15",
            region,
            f"emr.{region}.volcengineapi.com",
            "POST",
            {},
            body,
            timeout=timeout,
            headers={
                'Accept': 'text/event-stream',
                'X-Resume-Task-Id': task_id,
                'X-Resume-From-Index': '0'
            },
        ):
            if not task_id:
                header = event.get_response_header()
                task_id = header["X-Task-Id"]
            if not event.get_event_data().startswith('data:'):
                continue
            result_events.append(event.get_event_data())
    return "\n".join(result_events)


def _parse_and_format(raw):
    if isinstance(raw, bytes):
        text = raw.decode('utf-8', errors='ignore')
    else:
        text = str(raw)
    chat_id = None
    report_id = None
    parts = []

    text_content = ""
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if not s.startswith('data:'):
            continue
        payload = s[len('data:'):].strip()
        try:
            evt = json.loads(payload)
        except Exception:
            continue
        if not chat_id:
            chat_id = evt.get('threadId')
        match evt.get('type'):
            case 'ARTIFACT_CONTENT':
                report_id = evt.get('delta', {}).get('id')
            case 'STEP_STARTED':
                parts.append(f"\n========{evt.get('title', '')}========\n")
            case 'TEXT_MESSAGE_CONTENT':
                text_content += evt.get('delta')
            case 'TEXT_MESSAGE_END':
                parts.append(text_content)
                text_content = ""

    meta = "========meta========\n"
    if report_id:
        meta += f"report-id: {report_id}\n"
    if chat_id:
        meta += f"chat-id: {chat_id}\n"
    return "\n".join([meta] + parts).strip()

def _staging_file_name(output_dir: str, file_id: str) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{file_id}.staging"

def _final_file_name(output_dir: str, file_id: str) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{file_id}.txt"

def _chat(question: str, chat_id: str = None):
    if not chat_id:
        resp = _call_api("CreateChat", {"Verbose": False})
        chat_id = resp.get("Result",{}).get("ChatId")
    file_id = str(os.getpid())
    print(f"pid: {file_id}")
    output_dir = _get_tmp_dir()
    staging_file_name = _staging_file_name(output_dir, file_id)
    final_file_name = _final_file_name(output_dir, file_id)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    try:
        with open(staging_file_name, 'w', encoding='utf-8') as f:
            f.write("")
            f.flush()

        res = _stream_call_api(
            action="ChatCompletions",
            body={"Content": question, "ChatId": chat_id, "Verbose": False},
            timeout=600
        )
        formatted = _parse_and_format(res)
        print(formatted)
        with open(staging_file_name, 'w', encoding='utf-8') as f:
            f.write(formatted)
        os.replace(staging_file_name, final_file_name)
    except Exception as e:
        err = f"SessionID: {chat_id or '无'}\n请求失败: {str(e)}"
        try:
            with open(staging_file_name, 'w', encoding='utf-8') as f:
                f.write(err)
            os.replace(staging_file_name, final_file_name)
        except Exception:
            pass

def _get_result(file_id: str):
    output_dir = _get_tmp_dir()
    staging_file_name = _staging_file_name(output_dir, file_id)
    final_file_name = _final_file_name(output_dir, file_id)
    if staging_file_name.exists():
        print("still running, please fetch result later.")
    elif final_file_name.exists():
        result = ""
        with open(final_file_name, 'r', encoding='utf-8') as f:
            result = f.readlines()
        final_file_name.unlink(missing_ok=True)
        print(result)
    else:
        print("result not found.")


def _main():
    parser = argparse.ArgumentParser(prog="expert.py")
    parser.add_argument("--question", required=False)
    parser.add_argument("--chat-id", required=False)
    parser.add_argument("--get-result", required=False)
    args = parser.parse_args()
    if args.get_result:
        _get_result(args.get_result)
    elif args.question:
        _chat(args.question, args.chat_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    _main()
