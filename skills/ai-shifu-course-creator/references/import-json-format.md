# Import JSON Format

The `build` command generates a `shifu-import.json` file that can be imported to the AI-Shifu platform.

## Schema

```json
{
  "version": "1.0",
  "shifu": {
    "shifu_bid": "<UUID>",
    "title": "Course Title",
    "description": "Description",
    "keywords": "keywords",
    "llm": "",
    "llm_temperature": 0,
    "llm_system_prompt": "<content from system-prompt.md>",
    "ask_enabled_status": 5101,
    "price": 0.0
  },
  "outline_items": [
    {
      "outline_item_bid": "<UUID>",
      "title": "Lesson Title",
      "type": 401,
      "parent_bid": "",
      "position": "0",
      "content": "<MDF content>"
    }
  ],
  "structure": { "bid": "<shifu_bid>", "type": "shifu", "children": [] }
}
```

## Key Fields

- `llm_system_prompt`: Course-level AI role definition (from `system-prompt.md`)
- `type: 401`: Regular lesson node
- `parent_bid`: Empty string = chapter (top-level container); non-empty = lesson (child node with MDF content). Use `add-chapter` to create chapters, then pass the chapter BID as `--parent-bid` when creating lessons
- `content`: The MDF prompt content (this is the core teaching material)
- `ask_enabled_status: 5101`: Enables learner questions
