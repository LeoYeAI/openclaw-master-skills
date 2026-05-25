# Project Generator Usage Examples

## Example 1: E-commerce System

Input:
```
创建一个电商管理系统，包含：
- 商品管理：名称、价格、库存、分类、状态
- 订单管理：订单号、用户、商品列表、总价、状态
- 用户管理：用户名、邮箱、手机号、角色
- 分类管理：名称、父分类、排序
```

Generated Entities:
- Product (商品)
- Order (订单)
- OrderItem (订单项)
- User (用户)
- Category (分类)

## Example 2: Blog System

Input:
```
博客系统，包含：
- 文章：标题、内容、作者、分类、标签、状态、浏览量
- 分类：名称、描述
- 标签：名称
- 评论：内容、作者、文章、父评论
- 用户：用户名、昵称、头像、简介
```

Generated Entities:
- Article (文章)
- Category (分类)
- Tag (标签)
- Comment (评论)
- User (用户)

## Example 3: Task Management

Input:
```
任务管理系统：
- 项目：名称、描述、负责人、开始/结束时间、状态
- 任务：标题、描述、所属项目、执行人、优先级、状态、截止日期
- 标签：名称、颜色
- 用户：用户名、邮箱、角色
```

Generated Entities:
- Project (项目)
- Task (任务)
- Tag (标签)
- User (用户)

## Field Type Mapping

| Java Type | TypeScript Type | Database Type | UI Component |
|-----------|-----------------|---------------|--------------|
| String | string | VARCHAR | Input |
| Text | string | TEXT | Textarea |
| Long | number | BIGINT | InputNumber |
| Integer | number | INT | InputNumber |
| BigDecimal | number | DECIMAL | InputNumber |
| LocalDateTime | string | DATETIME | DatePicker |
| Boolean | boolean | BOOLEAN | Switch |
| Enum | string | VARCHAR | Select |

## Quick Start Template

```python
project_spec = {
    "name": "YourProject",
    "description": "项目描述",
    "entities": [
        {
            "name": "EntityName",
            "fields": [
                {"name": "fieldName", "type": "String", "required": True},
                {"name": "price", "type": "BigDecimal", "required": True},
            ],
            "relationships": [
                {"type": "ManyToOne", "target": "OtherEntity", "field": "other"}
            ]
        }
    ],
    "features": ["auth", "audit", "soft-delete"]
}
```
