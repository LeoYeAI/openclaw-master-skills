# Errors and Retry Strategy

## Task state lifecycle

States (typical order): `created` → `queueing` → `preparation` → `scheduling` → `processing` → **success** or **failed** (or `canceled`).

Only **success** and **failed** are terminal. Do not treat other states as completion.

---

## When state is failed

- **err_code** (string): Server-defined error code. Present in GET task response.
- **err_msg** (string): Human-readable message when available (e.g. in full task object).

Report to the user that the task failed and, if available, the reason (err_code and/or err_msg). Do not return a video URL.

---

## Query task status/result

There is **no wait mode**: after submit you get task_id; the caller queries when needed. Use **GET** `/vidu/v1/tasks/{task_id}` (or **get_task_result.py** \<task_id\>) to get current state and, when success, video URL(s). GET is read-only and safe to retry.

---

## Network and client errors

- **4xx on submit**: Check body (type, input.prompts, settings) and token. Do not retry same body blindly; fix and resubmit.
- **5xx or connection error on submit**: Retry with backoff (e.g. 1s, 2s, 4s) up to 3 times. If all fail, report network/server error to the user.
- **5xx or connection error on upload (CreateUpload / PUT / FinishUpload)**: Retry the failing step. For PUT, ensure you resend the same image and headers.
- **Timeout on GET task**: Retry once or twice; if still failing, report that the result could not be fetched and suggest retrying later.

---

## Summary for the agent

- Treat only **success** / **failed** / **canceled** as terminal.
- On **failed**: return err_code/err_msg to the user, no video link.
- No built-in wait: submit returns task_id; caller uses GET task (or get_task_result.py) to query status/result when needed.
- On submit or upload client/network errors: retry with backoff a few times; then report clearly to the user.
