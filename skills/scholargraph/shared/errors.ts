/**
 * Shared Errors - 自定义错误类
 * 提供结构化的错误处理
 */

/**
 * 应用基础错误类
 */
export class AppError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly retryable: boolean;
  public readonly cause?: Error;

  constructor(
    message: string,
    options: {
      code?: string;
      statusCode?: number;
      retryable?: boolean;
      cause?: Error;
    } = {}
  ) {
    super(message);
    this.name = this.constructor.name;
    this.code = options.code || 'APP_ERROR';
    this.statusCode = options.statusCode || 500;
    this.retryable = options.retryable ?? false;
    this.cause = options.cause;

    // 保持正确的原型链
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

/**
 * API 初始化错误
 */
export class ApiInitializationError extends AppError {
  constructor(message: string, cause?: Error) {
    super(message, {
      code: 'API_INIT_ERROR',
      statusCode: 503,
      retryable: true,
      cause
    });
  }
}

/**
 * API 调用错误
 */
export class ApiCallError extends AppError {
  public readonly endpoint?: string;
  public readonly responseStatus?: number;

  constructor(
    message: string,
    options: {
      endpoint?: string;
      responseStatus?: number;
      retryable?: boolean;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: 'API_CALL_ERROR',
      statusCode: options.responseStatus || 502,
      retryable: options.retryable ?? true,
      cause: options.cause
    });
    this.endpoint = options.endpoint;
    this.responseStatus = options.responseStatus;
  }
}

/**
 * 验证错误
 */
export class ValidationError extends AppError {
  public readonly field?: string;
  public readonly value?: unknown;

  constructor(
    message: string,
    options: {
      field?: string;
      value?: unknown;
    } = {}
  ) {
    super(message, {
      code: 'VALIDATION_ERROR',
      statusCode: 400,
      retryable: false
    });
    this.field = options.field;
    this.value = options.value;
  }
}

/**
 * 解析错误
 */
export class ParseError extends AppError {
  public readonly input?: string;
  public readonly format?: string;

  constructor(
    message: string,
    options: {
      input?: string;
      format?: string;
      cause?: Error;
    } = {}
  ) {
    super(message, {
      code: 'PARSE_ERROR',
      statusCode: 422,
      retryable: false,
      cause: options.cause
    });
    this.input = options.input?.substring(0, 200); // 截断以避免日志过长
    this.format = options.format;
  }
}

/**
 * 超时错误
 */
export class TimeoutError extends AppError {
  public readonly timeoutMs: number;
  public readonly operation?: string;

  constructor(
    message: string,
    options: {
      timeoutMs: number;
      operation?: string;
    }
  ) {
    super(message, {
      code: 'TIMEOUT_ERROR',
      statusCode: 504,
      retryable: true
    });
    this.timeoutMs = options.timeoutMs;
    this.operation = options.operation;
  }
}

/**
 * 配置错误
 */
export class ConfigurationError extends AppError {
  public readonly configKey?: string;

  constructor(message: string, configKey?: string) {
    super(message, {
      code: 'CONFIG_ERROR',
      statusCode: 500,
      retryable: false
    });
    this.configKey = configKey;
  }
}

/**
 * 从未知错误中提取错误消息
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  if (error && typeof error === 'object' && 'message' in error) {
    return String((error as { message: unknown }).message);
  }
  return 'Unknown error occurred';
}

/**
 * 从未知错误中提取错误代码
 */
export function getErrorCode(error: unknown): string {
  if (error instanceof AppError) {
    return error.code;
  }
  if (error && typeof error === 'object' && 'code' in error) {
    return String((error as { code: unknown }).code);
  }
  return 'UNKNOWN_ERROR';
}

/**
 * 判断错误是否可重试
 */
export function isRetryableError(error: unknown): boolean {
  if (error instanceof AppError) {
    return error.retryable;
  }
  // 网络错误通常可重试
  if (error instanceof Error) {
    const retryableMessages = [
      'ECONNRESET',
      'ETIMEDOUT',
      'ECONNREFUSED',
      'ENOTFOUND',
      'network',
      'timeout',
      'rate limit',
      '429',
      '503',
      '504'
    ];
    return retryableMessages.some(msg =>
      error.message.toLowerCase().includes(msg.toLowerCase())
    );
  }
  return false;
}

/**
 * 包装错误为 AppError
 */
export function wrapError(error: unknown, defaultMessage: string = 'An error occurred'): AppError {
  if (error instanceof AppError) {
    return error;
  }
  if (error instanceof Error) {
    return new AppError(error.message || defaultMessage, {
      cause: error,
      retryable: isRetryableError(error)
    });
  }
  return new AppError(getErrorMessage(error) || defaultMessage);
}
