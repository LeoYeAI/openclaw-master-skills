# Todoist Routing Reference

**App name:** `todoist`
**Base URL proxied:** `api.todoist.com`

## API Path Pattern

```
/todoist/rest/v2/{resource}
```

## Common Endpoints

### List Projects
```bash
GET /todoist/rest/v2/projects
```

### Get Project
```bash
GET /todoist/rest/v2/projects/{id}
```

### Create Project
```bash
POST /todoist/rest/v2/projects
Content-Type: application/json

{
  "name": "My Project",
  "color": "blue"
}
```

### Update Project
```bash
POST /todoist/rest/v2/projects/{id}
Content-Type: application/json

{
  "name": "Updated Name"
}
```

### Delete Project
```bash
DELETE /todoist/rest/v2/projects/{id}
```

### List Tasks
```bash
GET /todoist/rest/v2/tasks
GET /todoist/rest/v2/tasks?project_id={project_id}
GET /todoist/rest/v2/tasks?filter={filter}
```

### Get Task
```bash
GET /todoist/rest/v2/tasks/{id}
```

### Create Task
```bash
POST /todoist/rest/v2/tasks
Content-Type: application/json

{
  "content": "Buy groceries",
  "priority": 2,
  "due_string": "tomorrow"
}
```

### Update Task
```bash
POST /todoist/rest/v2/tasks/{id}
Content-Type: application/json

{
  "content": "Updated content",
  "priority": 4
}
```

### Close Task (Complete)
```bash
POST /todoist/rest/v2/tasks/{id}/close
```

### Reopen Task
```bash
POST /todoist/rest/v2/tasks/{id}/reopen
```

### Delete Task
```bash
DELETE /todoist/rest/v2/tasks/{id}
```

### List Sections
```bash
GET /todoist/rest/v2/sections
GET /todoist/rest/v2/sections?project_id={project_id}
```

### Create Section
```bash
POST /todoist/rest/v2/sections
Content-Type: application/json

{
  "name": "In Progress",
  "project_id": "123456"
}
```

### Delete Section
```bash
DELETE /todoist/rest/v2/sections/{id}
```

### List Labels
```bash
GET /todoist/rest/v2/labels
```

### Create Label
```bash
POST /todoist/rest/v2/labels
Content-Type: application/json

{
  "name": "urgent",
  "color": "red"
}
```

### Delete Label
```bash
DELETE /todoist/rest/v2/labels/{id}
```

### List Comments
```bash
GET /todoist/rest/v2/comments?task_id={task_id}
GET /todoist/rest/v2/comments?project_id={project_id}
```

### Create Comment
```bash
POST /todoist/rest/v2/comments
Content-Type: application/json

{
  "task_id": "123456",
  "content": "This is a comment"
}
```

### Delete Comment
```bash
DELETE /todoist/rest/v2/comments/{id}
```

## Notes

- Task and Project IDs are strings
- Priority values: 1 (normal) to 4 (urgent)
- Use only one due date format per request: `due_string`, `due_date`, or `due_datetime`
- Comments require either `task_id` or `project_id`
- Close/reopen/delete operations return 204 No Content

## Resources

- [Todoist REST API v2 Documentation](https://developer.todoist.com/rest/v2)
- [Todoist Filter Syntax](https://todoist.com/help/articles/introduction-to-filters)
