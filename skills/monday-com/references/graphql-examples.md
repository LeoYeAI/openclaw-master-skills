# GraphQL API Examples

Full query and mutation examples for the monday.com GraphQL API.

**Endpoint:** `POST https://api.monday.com/v2`
**Headers:** `Authorization: <your-token>`, `Content-Type: application/json`, `API-Version: 2024-10`

## Queries

### List Boards

```graphql
{ boards(limit: 25, order_by: used_at) { id name board_folder_id state workspace { id name } } }
```

### Get Board with Items

```graphql
{ boards(ids: [BOARD_ID]) { id name columns { id title type settings_str } groups { id title } items_page(limit: 50) { cursor items { id name group { id title } column_values { id text type value } } } } }
```

### Search Items by Column Value

```graphql
{ items_page_by_column_values(board_id: BOARD_ID, limit: 50, columns: [{column_id: "status", column_values: ["Working on it"]}]) { cursor items { id name column_values { id text } } } }
```

### Get Activity Logs

```graphql
{ boards(ids: [BOARD_ID]) { activity_logs(limit: 50) { id event data entity account_id created_at user_id } } }
```

With date range:
```graphql
{ boards(ids: [BOARD_ID]) { activity_logs(limit: 50, from: "2026-03-03T00:00:00Z", to: "2026-03-10T00:00:00Z") { id event data entity created_at user_id } } }
```

Common event values: `update_column_value`, `create_pulse` (item created), `delete_pulse`, `create_update`, `move_pulse` (item moved between groups).

### Get User Info

```graphql
{ me { id name email account { id name slug } } }
```

### List Workspaces

```graphql
{ workspaces { id name kind } }
```

## Mutations

### Create Board

```graphql
mutation { create_board(board_name: "Project Alpha", board_kind: public, workspace_id: WORKSPACE_ID) { id } }
```

Board kinds: `public`, `private`, `share`.

### Create Item

```graphql
mutation { create_item(board_id: BOARD_ID, group_id: "GROUP_ID", item_name: "New Task", column_values: "{\"status\": {\"label\": \"Working on it\"}, \"date\": {\"date\": \"2026-03-15\"}}") { id } }
```

### Update Column Values

```graphql
mutation { change_multiple_column_values(board_id: BOARD_ID, item_id: ITEM_ID, column_values: "{\"status\": {\"label\": \"Done\"}, \"person\": {\"personsAndTeams\": [{\"id\": USER_ID, \"kind\": \"person\"}]}}") { id } }
```

Always prefer `change_multiple_column_values` over `change_column_value` for efficiency.

### Create Group

```graphql
mutation { create_group(board_id: BOARD_ID, group_name: "Sprint 3", group_color: "#00CA72") { id } }
```

### Add Update (Comment)

```graphql
mutation { create_update(item_id: ITEM_ID, body: "Completed the review. Ready for QA.") { id } }
```

### Create Subitem

```graphql
mutation { create_subitem(parent_item_id: ITEM_ID, item_name: "Subtask: Write tests") { id board { id } } }
```

### Move Item to Group

```graphql
mutation { move_item_to_group(item_id: ITEM_ID, group_id: "GROUP_ID") { id } }
```

### Delete Item

```graphql
mutation { delete_item(item_id: ITEM_ID) { id } }
```

### Create Webhook

```graphql
mutation { create_webhook(board_id: BOARD_ID, url: "https://your-endpoint.com/webhook", event: change_column_value) { id } }
```

Events: `change_column_value`, `change_status_column_value`, `create_item`, `delete_item`, `change_name`, `create_update`, `change_subitem_column_value`, `create_subitem`.

## File Uploads

File uploads use the `/v2/file` endpoint with multipart POST (not the standard JSON body).

### Upload File to Item Column

```graphql
mutation ($file: File!) { add_file_to_column(item_id: ITEM_ID, column_id: "files", file: $file) { id name url } }
```

> The column must be a "Files" type column. Max file size: 500MB.

### Upload File to Update

```graphql
mutation ($file: File!) { add_file_to_update(update_id: UPDATE_ID, file: $file) { id name url } }
```

## Pagination

```graphql
# First page
{ boards(ids: [BOARD_ID]) { items_page(limit: 200) { cursor items { id name } } } }

# Next pages
{ next_items_page(limit: 200, cursor: "CURSOR_VALUE") { cursor items { id name } } }
```

Recommended page size: 200. Max: 500. Cursors expire after 60 minutes.
