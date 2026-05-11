export enum Severity {
  SAFE = 'SAFE',
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export enum Action {
  ALLOW = 'allow',
  LOG = 'log',
  WARN = 'warn',
  BLOCK = 'block',
  BLOCK_NOTIFY = 'block_notify'
}

export interface SecurityPattern {
  id: string;
  category: string;
  subcategory?: string;
  pattern: string | RegExp;
  severity: Severity;
  language: 'en' | 'ko' | 'ja' | 'zh' | 'all';
  description: string;
  examples: string[];
  falsePositiveRisk: 'low' | 'medium' | 'high';
  enabled: boolean;
  tags: string[];
}

export interface Finding {
  module: string;
  pattern: SecurityPattern;
  matchedText: string;
  severity: Severity;
  metadata?: Record<string, any>;
}

export interface ValidationResult {
  severity: Severity;
  action: Action;
  findings: Finding[];
  fingerprint: string;
  timestamp: Date;
  normalizedText?: string;
  recommendations: string[];
}

export interface SecurityConfig {
  enabled: boolean;
  sensitivity: 'paranoid' | 'strict' | 'medium' | 'permissive';
  owner_ids: string[];
  modules: ModuleConfigs;
  actions: Record<Severity, Action>;
  rate_limit: RateLimitConfig;
  notifications: NotificationConfig;
  logging: LoggingConfig;
  database: DatabaseConfig;
  earlyExitOnCritical?: boolean;
  cacheSize?: number;
  cacheTtlMs?: number;
}

export interface ModuleConfigs {
  prompt_injection: ModuleConfig;
  command_validator: ModuleConfig;
  url_validator: ModuleConfig;
  path_validator: ModuleConfig;
  secret_detector: ModuleConfig;
  content_scanner: ModuleConfig;
  injection_validator: ModuleConfig;
  exfiltration_detector: ModuleConfig;
  code_execution_detector: ModuleConfig;
  serialization_detector: ModuleConfig;
}

export interface ModuleConfig {
  enabled: boolean;
  sensitivity?: 'paranoid' | 'strict' | 'medium' | 'permissive';
  [key: string]: any;
}

export interface RateLimitConfig {
  enabled: boolean;
  max_requests_per_minute: number;
  lockout_threshold: number;
}

export interface NotificationConfig {
  enabled: boolean;
  channels: {
    webhook?: { enabled: boolean; url: string };
    slack?: { enabled: boolean; webhook_url: string };
    discord?: { enabled: boolean; webhook_url: string };
    email?: { enabled: boolean; smtp_config: any };
  };
  severity_threshold: Severity;
}

export interface LoggingConfig {
  enabled: boolean;
  level: 'debug' | 'info' | 'warn' | 'error';
  file: string;
  rotation: 'daily' | 'weekly' | 'monthly';
  retention_days: number;
}

export interface DatabaseConfig {
  path: string;
  analytics_enabled: boolean;
  retention_days: number;
}
