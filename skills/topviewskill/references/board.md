# Board Module

Manage boards that organize generated results (images, videos, audio). Users can view and edit results on the web via board links.

## When to Use

- **Before first task in a session** -- run `list --default -q` to get the default board ID
- **User wants a new board** -- run `create --name "..."`
- **User wants to browse results** -- run `tasks --board-id <id>`
- **User wants board management** -- list, detail, update, delete

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List boards (paginated). Use `--default` for agent auto-discovery |
| `create` | Create a new board |
| `detail` | Get board details (members, share tokens) |
| `update` | Rename a board |
| `delete` | Delete a board |
| `tasks` | List tasks in a board (with filters) |
| `task-detail` | Get a single task's full details |

## Usage

```bash
python {baseDir}/scripts/board.py <subcommand> [options]
```

## Examples

### Get Default Board ID (Agent Startup)

```bash
BOARD_ID=$(python {baseDir}/scripts/board.py list --default -q)
```

The agent should run this once at session start and reuse the board ID for all tasks.

### List All Boards

```bash
python {baseDir}/scripts/board.py list
```

Output (tab-separated):

```
board_123456    My First Board    5 tasks [default]
board_789012    Campaign Q3       12 tasks
```

### Create a New Board

```bash
python {baseDir}/scripts/board.py create --name "Campaign Q3"
```

Prints the new board ID. Use this when the user explicitly asks for a new board.

### View Board Details

```bash
python {baseDir}/scripts/board.py detail --board-id <boardId>
```

### Rename a Board

```bash
python {baseDir}/scripts/board.py update --board-id <boardId> --name "Campaign Q4"
```

### Delete a Board

```bash
python {baseDir}/scripts/board.py delete --board-id <boardId>
```

### List Tasks in a Board

```bash
python {baseDir}/scripts/board.py tasks --board-id <boardId>
```

With filters:

```bash
python {baseDir}/scripts/board.py tasks --board-id <boardId> \
  --media-type video \
  --sort-field gmtCreate --sort-order desc \
  --page 1 --size 50
```

### Get Task Details

```bash
python {baseDir}/scripts/board.py task-detail --task-id <taskId>
```

Shows full task info including edit link:

```
Task: task_abc123
  boardTaskId: bt_xyz789
  boardId:     board_abc123
  status:      success
  tool:        text2video
  cost:        10 credits
  edit: https://www.topview.ai/board/board_abc123?boardResultId=bt_xyz789
```

## Options

### `list`

| Option | Description |
|--------|-------------|
| `--default` | Print only the default board ID (for agent auto-discovery) |
| `--page N` | Page number (default: 1) |
| `--size N` | Items per page (default: 20) |

### `create`

| Option | Description |
|--------|-------------|
| `--name TEXT` | Board name, max 200 chars (required) |

### `detail`

| Option | Description |
|--------|-------------|
| `--board-id ID` | Board ID (required) |

### `update`

| Option | Description |
|--------|-------------|
| `--board-id ID` | Board ID (required) |
| `--name TEXT` | New name, max 200 chars (required) |

### `delete`

| Option | Description |
|--------|-------------|
| `--board-id ID` | Board ID (required) |

### `tasks`

| Option | Description |
|--------|-------------|
| `--board-id ID` | Board ID (required) |
| `--media-type` | Filter: `image` / `video` |
| `--rating N` | Filter by rating: 0-3 |
| `--tool-category` | Filter by tool category |
| `--tool-type` | Filter by tool type |
| `--sort-field` | Sort: `gmtCreate` / `sortWeight` |
| `--sort-order` | `asc` / `desc` |
| `--page N` | Page number |
| `--size N` | Items per page |

### `task-detail`

| Option | Description |
|--------|-------------|
| `--task-id ID` | Task ID (required) |

### Global

| Option | Description |
|--------|-------------|
| `--json` | Full JSON response |
| `-q, --quiet` | Suppress status messages |

## Board Web URL

View and edit board results at:

```
https://www.topview.ai/board/{boardId}
```

View a specific result:

```
https://www.topview.ai/board/{boardId}?boardResultId={boardTaskId}
```

## Agent Protocol

1. **Session start**: run `board.py list --default -q` to get the default board ID
2. **Pass to all tasks**: add `--board-id <id>` to every generation command
3. **After completion**: show the edit link to the user if `boardTaskId` is in the response
4. **User wants new board**: run `board.py create --name "..."` and use the returned ID
5. **User specifies board**: use the user-provided board ID instead
