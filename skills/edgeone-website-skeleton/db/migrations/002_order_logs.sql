-- 订单状态机审计日志表
-- Phase 3 P2-2 实现
-- 执行时机：订单状态机上线前

-- 1. 状态变更审计日志表
CREATE TABLE IF NOT EXISTS order_status_logs (
  id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id     BIGINT UNSIGNED NOT NULL COMMENT '订单 ID',
  from_status  VARCHAR(32) DEFAULT NULL COMMENT '变更前状态',
  to_status    VARCHAR(32) NOT NULL COMMENT '变更后状态',
  operator     BIGINT UNSIGNED DEFAULT NULL COMMENT '操作者 ID（NULL=系统）',
  reason       VARCHAR(255) DEFAULT NULL COMMENT '变更原因',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  INDEX idx_logs_order (order_id),
  INDEX idx_logs_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单状态变更审计日志';

-- 2. orders 表新增 version 字段（如果还没有）
-- 注意：MySQL 不支持 IF NOT EXISTS ADD COLUMN，需要先检查
-- ALTER TABLE orders ADD COLUMN IF NOT EXISTS version INT UNSIGNED DEFAULT 1;

-- 建议执行：
ALTER TABLE orders
  ADD COLUMN IF NOT EXISTS version INT UNSIGNED DEFAULT 1 COMMENT '乐观锁版本号';

-- 3. orders 表新增物流字段（发货时填写）
ALTER TABLE orders
  ADD COLUMN IF NOT EXISTS express_company VARCHAR(64) DEFAULT NULL COMMENT '快递公司',
  ADD COLUMN IF NOT EXISTS express_no VARCHAR(64) DEFAULT NULL COMMENT '运单号';

-- 4. 给 version 加索引（高并发乐观锁）
ALTER TABLE orders ADD INDEX idx_orders_version (version);
