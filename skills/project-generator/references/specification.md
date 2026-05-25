# Project Generator Specification Format

## Complete Specification Schema

```json
{
  "projectName": "my-app",
  "description": "Application description",
  "techStack": {
    "backend": "spring-boot",
    "frontend": "vue3",
    "database": "mysql",
    "uiLibrary": "element-plus"
  },
  "features": ["jwt-auth", "audit-log", "soft-delete", "file-upload"],
  "entities": [
    {
      "name": "EntityName",
      "tableName": "table_name",
      "comment": "Entity description",
      "fields": [
        {
          "name": "fieldName",
          "type": "String",
          "length": 255,
          "required": true,
          "unique": false,
          "comment": "Field description",
          "searchable": true
        }
      ],
      "relationships": [
        {
          "type": "OneToMany|ManyToOne|ManyToMany",
          "target": "OtherEntity",
          "field": "fieldName",
          "mappedBy": "mappedField"
        }
      ],
      "operations": ["create", "read", "update", "delete", "list", "search"]
    }
  ],
  "pages": [
    {
      "name": "entity-list",
      "type": "list",
      "entity": "EntityName",
      "features": ["search", "pagination", "export"]
    },
    {
      "name": "entity-form",
      "type": "form",
      "entity": "EntityName",
      "layout": "vertical"
    }
  ]
}
```

## Field Types

### Basic Types
- `String` - 字符串
- `Text` - 长文本
- `Long` - 长整数
- `Integer` - 整数
- `BigDecimal` - 高精度小数
- `LocalDateTime` - 日期时间
- `Boolean` - 布尔值

### Special Types
- `Enum` - 枚举类型
- `Json` - JSON 对象
- `File` - 文件上传
- `Image` - 图片

## Relationship Types

### OneToMany
```json
{
  "type": "OneToMany",
  "target": "OrderItem",
  "field": "items",
  "mappedBy": "order"
}
```

### ManyToOne
```json
{
  "type": "ManyToOne",
  "target": "User",
  "field": "creator"
}
```

### ManyToMany
```json
{
  "type": "ManyToMany",
  "target": "Role",
  "field": "roles"
}
```

## Feature Flags

### Backend Features
- `jwt-auth` - JWT 认证
- `rbac` - 基于角色的权限控制
- `audit-log` - 审计日志
- `soft-delete` - 软删除
- `multi-tenant` - 多租户
- `cache` - Redis 缓存
- `file-upload` - 文件上传
- `excel-export` - Excel 导出

### Frontend Features
- `dark-mode` - 暗黑模式
- `i18n` - 国际化
- `pwa` - PWA 支持
- `responsive` - 响应式设计
