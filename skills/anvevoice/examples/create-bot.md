# Example: Creating a Bot

## User Prompt
> "Create a new voice bot called 'Product Guide' for my e-commerce site at shop.example.com"

## Agent Action

```json
{
  "tool": "create_bot",
  "arguments": {
    "name": "Product Guide",
    "bot_type": "sales",
    "target_website": "https://shop.example.com",
    "system_prompt": "You are a friendly product guide for shop.example.com. Help visitors find products, answer questions about sizing, shipping, and returns. Be concise and helpful.",
    "welcome_message": "Hi! I'm your product guide. What are you looking for today?",
    "widget_position": "bottom-right",
    "widget_theme": "light"
  }
}
```

## Expected Response

```json
{
  "success": true,
  "data": {
    "bot": {
      "id": "ghi-789",
      "name": "Product Guide",
      "status": "active",
      "bot_type": "sales",
      "target_website": "https://shop.example.com"
    },
    "message": "Bot created successfully"
  }
}
```

## Follow-up: Get Embed Code

```json
{
  "tool": "get_embed_code",
  "arguments": { "bot_id": "ghi-789" }
}
```

## Agent Response
> ✅ Created **Product Guide** for shop.example.com!
>
> Here's the embed code to add to your website:
> ```html
> <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.57.4/dist/umd/supabase.min.js"></script>
> <script src="https://aaxlcyouksuljvmypyhy.supabase.co/functions/v1/voice-assistant-embed-js?embedId=ghi-789&position=bottom-right&theme=light"></script>
> ```
>
> Would you like to add knowledge sources (URLs or FAQ text) to train the bot?
