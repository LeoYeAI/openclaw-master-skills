-- 数据库管理员初始化脚本
-- 自动创建常用数据表及索引

-- 1. 三维模型表（已在 roadflow 中创建）
CREATE TABLE IF NOT EXISTS models (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL UNIQUE,
    file_path VARCHAR(255) NOT NULL,
    file_size BIGINT DEFAULT 0,
    author_name VARCHAR(100),
    description TEXT,
    tags JSONB DEFAULT '[]',
    version DECIMAL(2,1) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE models IS '三维模型信息表，存储模型文件元数据';
COMMENT ON COLUMN models.id IS '自增主键（BIGINT）';
COMMENT ON COLUMN models.model_name IS '模型名称（唯一标识）';
COMMENT ON COLUMN models.file_path IS '模型文件存储路径/文件名';
COMMENT ON COLUMN models.file_size IS '文件大小（字节）';
COMMENT ON COLUMN models.author_name IS '模型创建者姓名';
COMMENT ON COLUMN models.description IS '模型详细描述信息';
COMMENT ON COLUMN models.tags IS '模型标签数组（JSONB 格式）';
COMMENT ON COLUMN models.version IS '模型版本号（如 1.0、2.3）';
COMMENT ON COLUMN models.is_active IS '是否启用该模型记录';
COMMENT ON COLUMN models.created_at IS '记录创建时间戳';
COMMENT ON COLUMN models.updated_at IS '最后更新时间戳';

CREATE UNIQUE INDEX IF NOT EXISTS idx_models_name ON models(model_name);
CREATE INDEX IF NOT EXISTS idx_models_path ON models(file_path);

-- 2. 报销单表（待插入 rf_form）
-- （此处预留表单生成逻辑，由 form-builder 脚本处理）