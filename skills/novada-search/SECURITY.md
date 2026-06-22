# SECURITY NOTES (novada-search v1.0.7)

## Data Flow

Query payloads are sent only to:
- `https://scraperapi.novada.com/search`

No hidden secondary endpoints are used by the core request path.

## API Key Handling

- Credential name: `NOVADA_API_KEY`
- Used only to authenticate Novada API requests.
- Not persisted by this package.
- Not intentionally logged by default output.

Resolution order:
1. `--api-key`
2. `NOVADA_API_KEY` environment variable
3. Local `.env` in current working directory

## What this project does NOT do

- No shell execution (`subprocess`, `os.system`, etc.)
- No scanning of `~/.ssh`, cloud credentials, or unrelated home directories
- No writes outside package scope during normal operation

## Runtime Safety Recommendations

- Run in sandbox for first validation.
- Use least-privilege env setup.
- Keep network permissions constrained to declared endpoint.

## Vulnerability Reporting

Please report security issues to: `security@novada.com`
