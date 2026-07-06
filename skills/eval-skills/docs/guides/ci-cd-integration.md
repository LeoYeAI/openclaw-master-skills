# CI/CD Integration

Use eval-skills as a quality gate in your CI/CD pipeline to prevent Skill degradation.

## GitHub Actions

```yaml
name: Skill Quality Gate

on:
  push:
    paths:
      - 'skills/**'
  pull_request:
    paths:
      - 'skills/**'

jobs:
  eval:
    name: Evaluate Skills
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - run: pnpm install --frozen-lockfile
      - run: pnpm build

      - name: Run Skill Evaluation
        run: |
          eval-skills eval \
            --skills ./skills/ \
            --benchmark coding-easy \
            --exit-on-fail \
            --min-completion 0.8 \
            --format json markdown \
            --output-dir ./eval-reports

      - name: Upload Evaluation Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-reports
          path: ./eval-reports/
```

## Key Options for CI

### `--exit-on-fail`

Returns exit code 1 if any Skill falls below the completion rate threshold. This blocks the pipeline.

```bash
eval-skills eval \
  --skills ./skills/ \
  --benchmark my-benchmark \
  --exit-on-fail \
  --min-completion 0.8   # Skills must achieve >= 80%
```

### `--json` Output

For machine-readable output in CI logs:

```bash
eval-skills eval --skills ./skills/ --benchmark coding-easy --json
```

### Regression Detection with `report diff`

Compare current results against a baseline:

```bash
# Store baseline (e.g., from main branch)
eval-skills eval --skills ./skills/ --benchmark coding-easy --format json --output-dir ./baseline

# Run on PR branch
eval-skills eval --skills ./skills/ --benchmark coding-easy --format json --output-dir ./current

# Generate diff
eval-skills report diff ./baseline/eval-result-*.json ./current/eval-result-*.json
```

## Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Eval Skills') {
            steps {
                sh '''
                    eval-skills eval \
                        --skills ./skills/ \
                        --benchmark coding-easy \
                        --exit-on-fail \
                        --min-completion 0.8 \
                        --format json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
                }
            }
        }
    }
}
```

## Exit Codes

| Code | Meaning |
|:---|:---|
| 0 | All Skills passed the threshold |
| 1 | One or more Skills below threshold (with `--exit-on-fail`) |
| 1 | Configuration or runtime error |

## Tips

1. **Pin benchmark versions** — use a specific benchmark file, not just an ID
2. **Set reasonable thresholds** — start with 0.7 and increase as Skills improve
3. **Archive reports** — keep evaluation history for trend analysis
4. **Run on Skill changes only** — use path filters to avoid unnecessary runs
5. **Use `--dry-run` first** — validate config before running full evaluation
