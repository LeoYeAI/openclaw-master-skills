/**
 * SocialVault 核心类型定义
 */

/** 单个 Cookie 条目 */
export interface CookieEntry {
  name: string;
  value: string;
  domain: string;
  path: string;
  expires?: number;
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: "Strict" | "Lax" | "None";
}

/** 认证方式 */
export type AuthMethod = "cookie_paste" | "api_token" | "qrcode";

/** 账号状态 */
export type AccountStatus = "healthy" | "degraded" | "expired" | "unknown";

/** 存储在 vault.enc 中的单个凭证条目（解密后） */
export interface VaultEntry {
  accountId: string;
  authMethod: AuthMethod;
  cookies?: CookieEntry[];
  rawCookieHeader?: string;
  accessToken?: string;
  refreshToken?: string;
  tokenExpiresAt?: string;
  clientId?: string;
  clientSecret?: string;
  updatedAt: string;
}

/** accounts.json 中的单个账号元数据 */
export interface AccountMeta {
  id: string;
  platform: string;
  adapter: string;
  authMethod: AuthMethod;
  displayName: string;
  profileUrl?: string;
  createdAt: string;
  lastValidatedAt: string;
  lastRefreshedAt?: string;
  status: AccountStatus;
  estimatedExpiry?: string;
  fingerprintFile?: string;
  browserProfile?: string;
  tags?: string[];
}

/** accounts.json 文件结构 */
export interface AccountsStore {
  accounts: AccountMeta[];
}

/** 浏览器指纹 */
export interface BrowserFingerprint {
  userAgent: string;
  viewport: { width: number; height: number };
  locale: string;
  timezone: string;
  platform: string;
  deviceScaleFactor: number;
  colorScheme?: "light" | "dark";
  capturedAt: string;
  capturedFrom: "cookie_paste_infer" | "browser_profile" | "manual";
}

/** 适配器 frontmatter 中的认证方式定义 */
export interface AdapterAuthMethod {
  type: AuthMethod;
  priority: number;
  label: string;
}

/** 适配器 frontmatter 中的 session 检查配置 */
export interface SessionCheckConfig {
  method: "api" | "browser";
  endpoint: string;
  success_indicator: string;
}

/** 适配器 frontmatter 结构 */
export interface AdapterFrontmatter {
  platform_id: string;
  platform_name: string;
  auth_methods: AdapterAuthMethod[];
  capabilities: string[];
  cookie_guide?: string;
  session_check: SessionCheckConfig;
  estimated_session_duration_days: number;
  auto_refresh_supported: boolean;
  rate_limits?: Record<string, number>;
}

/** Cookie 解析器识别的输入格式 */
export type CookieFormat = "json_array" | "raw_header" | "netscape";

/** 健康检查结果 */
export interface HealthCheckResult {
  accountId: string;
  platform: string;
  previousStatus: AccountStatus;
  currentStatus: AccountStatus;
  displayName: string;
  checkedAt: string;
  message?: string;
}
