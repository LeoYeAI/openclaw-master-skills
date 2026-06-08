# Basic troubleshooting (deploy-time and startup)

Use this when a deploy fails, the service crashes on start, or health checks time out.
Keep fixes minimal and redeploy after each change.

## 1) Classify the failure

- **Build failure**: errors in build logs, missing dependencies, build command issues.
- **Startup failure**: app exits quickly, crashes, or cannot bind to `$PORT`.
- **Runtime/health failure**: service is live but health checks fail or 5xx errors.

## 2) Quick checks by class

**Build failure**
- Confirm the build command is correct for the runtime.
- Ensure required dependencies are present in `package.json`, `requirements.txt`, etc.
- Check for missing build-time env vars.

**Startup failure**
- Confirm the start command and working directory.
- Ensure port binding is `0.0.0.0:$PORT`.
- Check for missing runtime env vars (secrets, DB URLs).

**Runtime/health failure**
- Verify the health endpoint path and response.
- Confirm the app is actually listening on `$PORT`.
- Check database connectivity and migrations.

## 3) Common fixes

- **Port**: App must listen on `0.0.0.0` and the port from the `PORT` environment variable.
- **Secrets**: All env vars marked `sync: false` must be set in the Render Dashboard.
- **Database**: Ensure `fromDatabase.name` matches a database in the same Blueprint; run migrations in `preDeployCommand` if needed.

## 4) If still blocked

Gather the latest build logs and runtime error logs from the Dashboard (or API). Check [Render docs](https://render.com/docs) and the Blueprint spec for your service type and runtime.
