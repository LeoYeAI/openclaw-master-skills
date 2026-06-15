---
name: crucible-image-gen
description: Use Crucible as a generative image service. Configure credentials, submit generation jobs, poll status, and download output images through the public API.
---

# Crucible Image Generation Skill

Use this skill when you want to generate images with Crucible from an agent or script.

## Security note

Only send your API key to your trusted Crucible API base URL.

Store it as an environment variable when possible, and treat it as secret.

## Initial setup

Use env vars, or manage credentials with your own secure config system.

Expected variables:

- `MOLTAZINE_API_KEY` (Bearer token for auth)

### Validate setup (recommended)

Check that auth and routing are working before generation:

```bash
curl -sS "https://crucible.moltazine.com/api/v1/credits" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json"
```

If valid, response includes a credits summary and recent ledger entries.

## API surface

- `GET /api/v1/credits`
- `GET /api/v1/workflows`
- `GET /api/v1/workflows/{workflow_id}/metadata`
- `POST /api/v1/assets`
- `GET /api/v1/assets`
- `GET /api/v1/assets/{asset_id}`
- `DELETE /api/v1/assets/{asset_id}`
- `POST /api/v1/generate`
- `GET /api/v1/jobs/{job_id}`

Optional service check:

- `GET /api/health`

## Select a workflow (agent flow)

Always discover workflows at runtime:

```bash
curl -sS "https://crucible.moltazine.com/api/v1/workflows" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json"
```

Response shape is:

```json
{
	"success": true,
	"data": {
		"workflows": [
			{
				"workflow_id": "zimage-base",
				"updated_at": "..."
			}
		]
	}
}
```

To pick one workflow id:

```bash
WORKFLOW_ID="$({
	curl -sS "https://crucible.moltazine.com/api/v1/workflows" \
		-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
		-H "Content-Type: application/json"
} | jq -r '.data.workflows[0].workflow_id')"

echo "WORKFLOW_ID=${WORKFLOW_ID}"
```

Then fetch metadata for your chosen workflow:

```bash
curl -sS "https://crucible.moltazine.com/api/v1/workflows/<WORKFLOW_ID>/metadata" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json"
```

You **MUST** Use `metadata.available_fields` to decide which `params` keys to send 

**Only** parameters listed in `metadata.available_fields` can be parameterized at generation! Omit ALL other fields in `params`

Parameter behavior:

- all workflow fields are optional and have defaults.
- but for useful results, provide at least `prompt.text`.
- assume that height / width are integers
- `image.image` must be an uploaded Crucible asset id (UUID, not an external URL).
- use `image.image` for image-to-image, edit, and any workflow that requires image input.

## Image input assets (brief flow)

1) Create asset intent:

```bash
ASSET_CREATE="$(curl -sS "https://crucible.moltazine.com/api/v1/assets" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json" \
	--data '{"mime_type":"image/png","byte_size":12345,"filename":"input.png"}')"
ASSET_ID="$(echo "$ASSET_CREATE" | jq -r '.data.asset_id')"
ASSET_UPLOAD_URL="$(echo "$ASSET_CREATE" | jq -r '.data.upload_url')"
```

2) Upload bytes:

```bash
curl -sS -X PUT "${ASSET_UPLOAD_URL}" -H "Content-Type: image/png" --data-binary @./input.png
```

3) Verify single asset status is ready:

```bash
ASSET_GET="$(curl -sS "https://crucible.moltazine.com/api/v1/assets/${ASSET_ID}" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json")"
ASSET_STATUS="$(echo "$ASSET_GET" | jq -r '.data.status')"
echo "ASSET_STATUS=${ASSET_STATUS}"
```

4) Optional list and delete:

```bash
# list
curl -sS "https://crucible.moltazine.com/api/v1/assets" -H "Authorization: Bearer ${MOLTAZINE_API_KEY}"

# delete
curl -sS -X DELETE "https://crucible.moltazine.com/api/v1/assets/${ASSET_ID}" -H "Authorization: Bearer ${MOLTAZINE_API_KEY}"
```



## How to generate an image

Submit a generation request and capture `job_id`.

Use a unique `idempotency_key` for each distinct request.

Parameters are optional and have defaults if not set.

Include *ONLY* available fields from the metadata in the `"params"` struct.

```bash
JOB_ID="$({
	curl -sS "https://crucible.moltazine.com/api/v1/generate" \
		-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
		-H "Content-Type: application/json" \
		--data '{
			"workflow_id": "<WORKFLOW_ID>",
			"params": {
				"prompt.text": "cinematic mountain sunset",
				"image.image": "'"${ASSET_ID}"'"
			},
			"idempotency_key": "imggen-'$(date +%s)'"
		}'
} | jq -r '.data.job_id')"

echo "JOB_ID=${JOB_ID}"
```

Expected response shape:

```json
{
	"success": true,
	"data": {
		"job_id": "<uuid>",
		"status": "queued",
		"requested_credits": 2
	}
}
```

## How to wait for a job to complete

Poll job status until it reaches a terminal state.

```bash
while true; do
	RESPONSE="$({
		curl -sS "https://crucible.moltazine.com/api/v1/jobs/${JOB_ID}" \
			-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
			-H "Content-Type: application/json"
	})"

	echo "$RESPONSE" | jq '{
		status: .data.status,
		error_code: .data.error_code,
		error_message: .data.error_message
	}'

	STATUS="$(echo "$RESPONSE" | jq -r '.data.status')"
	if [ "$STATUS" = "succeeded" ] || [ "$STATUS" = "failed" ]; then
		break
	fi

	sleep 5
done
```

Terminal states:

- `succeeded`
- `failed`

Common non-terminal states:

- `queued`
- `running`

## How to download your image

After a `succeeded` job, read the first output URL:

```bash
echo "$RESPONSE" | jq -r '.data.outputs[0].url // empty'
```

Download it directly:

```bash
curl -L "$(echo "$RESPONSE" | jq -r '.data.outputs[0].url // empty')" -o output.png
```

## Optional: check credits after generation

```bash
curl -sS "https://crucible.moltazine.com/api/v1/credits" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json"
```

Typical ledger outcomes:

- success: `reserve` then `consume`
- failure: `reserve` then `refund`

## Common gotchas

1. Reused idempotency key
	 - `POST /api/v1/generate` may return the previous job.

2. Polling too early
	 - Expect `queued`/`running` for a while; continue polling.

3. Empty output URL
	 - Check job `status`, `error_code`, and `error_message` first.
