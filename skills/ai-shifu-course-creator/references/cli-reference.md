# CLI Reference

All commands use `{skillDir}/scripts/shifu-cli.py`. Prefix every call with:

```bash
python3 {skillDir}/scripts/shifu-cli.py <command>
```

## Authentication

Run login once — the token persists in `{skillDir}/.env` for subsequent commands:

```bash
# Step 1: Send SMS verification code
login --phone 13800138000 --region cn

# Step 2: Complete login with the code
login --phone 13800138000 --region cn --sms-code 123456
```

Region options: `cn` (maps to `https://app.ai-shifu.cn`) or `global` (maps to `https://app.ai-shifu.com`). You can also use `--base-url` to override the URL directly.

Alternatively, set environment variables or CLI flags:
- `--base-url` or `SHIFU_BASE_URL` in `.env`
- `--token` or `SHIFU_TOKEN` in `.env`

### Agent Login Flow

When no valid token is available, guide the user through login:

1. Ask the user to choose their region:
   - 1: China mainland
   - 2: Non-China-mainland
2. **If the user chooses non-China-mainland**: CLI login is not supported for this region. Tell the user to log in manually at `https://app.ai-shifu.com`, copy their token from the browser, and set it via `--token` or by adding `SHIFU_TOKEN=<token>` and `SHIFU_BASE_URL=https://app.ai-shifu.com` to `{skillDir}/.env`. Then stop — do not proceed with the SMS flow.
3. **If the user chooses China mainland**: continue with the SMS login flow below.
4. Ask for their registered phone number.
5. Send SMS code:
   `python3 {skillDir}/scripts/shifu-cli.py login --phone <phone> --region cn`
6. Ask the user for the verification code they received.
7. Complete login:
   `python3 {skillDir}/scripts/shifu-cli.py login --phone <phone> --region cn --sms-code <code>`
8. Token is automatically saved — proceed with the requested operation.

Always use CLI commands. Never make raw HTTP/API calls directly.

## Query Commands

```bash
list                                          # List all courses
show <shifu_bid>                              # Show course details + outline tree
show <shifu_bid> <outline_bid>                # Read a lesson's MDF content
history <shifu_bid> <outline_bid>             # MDF revision history
export <shifu_bid> [-o file.json]             # Export course as JSON
```

## Create Commands

```bash
create --name "Title" [--description "Desc"]
add-chapter <shifu_bid> --name "Chapter Name"
add-lesson <shifu_bid> --name "Name" --mdf-file lesson.md --parent-bid <chapter_bid>
```

## Update Commands

```bash
update-meta <shifu_bid> [--name "..."] [--description "..."] [--system-prompt-file prompt.md]
update-lesson <shifu_bid> <outline_bid> --mdf-file lesson.md    # Uses optimistic locking
rename-lesson <shifu_bid> <outline_bid> --name "New Name"
reorder <shifu_bid> --order bid1,bid2,bid3
```

`update-lesson` fetches the current revision before saving. If another user modified the lesson since you last read it, the server returns a conflict.

## Delete Commands

```bash
delete-lesson <shifu_bid> <outline_bid>
```

## Bulk Import

```bash
# Flat JSON import
import <shifu_bid> --json-file course.json
import --new --json-file course.json

# One-step build + import from course directory
import <shifu_bid> --course-dir ./course-a/ [--title "..."] [--chapter-name "..."]
import --new --course-dir ./course-a/ [--title "..."] [--chapter-name "..."]

# Local build only (offline, generates shifu-import.json)
build --course-dir ./course-a/ [-o shifu-import.json] [--title "..."] [--chapter-name "..."]
```

The `build` command works entirely offline — it reads local MDF files and produces `shifu-import.json` without any network calls. The `import --course-dir` option combines build + import in one step.

Build behavior:
- **Course title** resolution order: `--title` CLI arg -> first heading in `README.md` -> directory name
- **Chapter structure**: if `structure.json` exists, generates multi-chapter structure per its definition; otherwise creates a single chapter (named via `--chapter-name` or defaults to course title) containing all `lesson-*.md` files in sorted order
- **Lesson title** resolution order: `title` field in `structure.json` -> `lesson_title: ...` line in MDF content -> filename derived (e.g., `lesson-01.md` -> "Lesson 01")

## State Management

```bash
publish <shifu_bid>       # Publish course (makes it live)
archive <shifu_bid>       # Archive course
unarchive <shifu_bid>     # Restore archived course
```
