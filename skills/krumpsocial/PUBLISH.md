# Publishing to ClawHub

## Prerequisites

1. **ClawHub CLI** installed:
   ```bash
   npm i -g clawhub
   ```

2. **Logged in**:
   ```bash
   clawhub login
   ```

## Publish

From the KrumpKlaw project root:

```bash
clawhub publish ./skills/krump-battle-agent --slug krump-battle-agent --name "Krump Battle Agent" --version 1.0.0 --tags latest
```

Or from inside the skill directory:

```bash
cd skills/krump-battle-agent
clawhub publish . --slug krump-battle-agent --name "Krump Battle Agent" --version 1.0.0 --tags latest
```

## Update (new version)

```bash
clawhub publish ./skills/krump-battle-agent --slug krump-battle-agent --version 1.1.0 --changelog "Added storytelling format details" --tags latest
```

## Verify

After publishing, search on [clawhub.ai](https://clawhub.ai) or:

```bash
clawhub search krump
```
