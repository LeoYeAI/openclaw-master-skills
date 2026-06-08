/**
 * middleware.js — Error handling, input sanitization, and validation
 *
 * Three concerns:
 *   1. asyncHandler: wraps route handlers so thrown errors don't crash the process
 *   2. sanitize: strips dangerous content from user/agent input
 *   3. validate: lightweight schema checks for required fields and types
 */

// ══════════════════════════════════════════════════════
// 1. ASYNC ERROR HANDLER
// ══════════════════════════════════════════════════════

/**
 * Wraps an Express route handler so any thrown error (sync or async)
 * is caught and passed to Express's error middleware instead of
 * crashing the process.
 *
 * Usage:
 *   router.get("/foo", asyncHandler((req, res) => { ... }));
 */
export function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

/**
 * Wraps ALL route handlers in an Express Router with asyncHandler.
 * Call this on the router after defining all routes but before exporting.
 *
 * Usage (at the bottom of a route file):
 *   wrapRouter(router);
 *   export default router;
 *
 * This avoids having to wrap each handler individually.
 */
export function wrapRouter(router) {
  const originalRoute = router.route.bind(router);
  router.stack.forEach((layer) => {
    if (layer.route) {
      layer.route.stack.forEach((routeLayer) => {
        const original = routeLayer.handle;
        routeLayer.handle = (req, res, next) => {
          try {
            const result = original(req, res, next);
            // Handle promises (async handlers)
            if (result && typeof result.catch === "function") {
              result.catch(next);
            }
          } catch (err) {
            next(err);
          }
        };
      });
    }
  });
  return router;
}

/**
 * Global error middleware. Mount AFTER all routes in server.js.
 * Logs the full error server-side, sends a safe message to the client.
 */
export function errorMiddleware(err, req, res, _next) {
  const status = err.status || 500;
  const message = status === 500 ? "Internal server error" : err.message;

  console.error(`[ERROR] ${req.method} ${req.path} →`, err.stack || err.message || err);

  res.status(status).json({
    error: message,
    ...(process.env.NODE_ENV !== "production" && { detail: err.message }),
  });
}

/**
 * Creates an error with a status code for use with asyncHandler.
 *   throw httpError(404, "Not found");
 */
export function httpError(status, message) {
  const err = new Error(message);
  err.status = status;
  return err;
}


// ══════════════════════════════════════════════════════
// 2. INPUT SANITIZATION
// ══════════════════════════════════════════════════════

/**
 * HTML entity map for escaping dangerous characters.
 * Prevents stored XSS when content is later rendered in the browser.
 */
const HTML_ENTITIES = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#x27;",
};

const ENTITY_REGEX = /[&<>"']/g;

/**
 * Escapes HTML special characters in a string.
 * Safe for rendering in dangerouslySetInnerHTML contexts.
 */
export function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str.replace(ENTITY_REGEX, (char) => HTML_ENTITIES[char]);
}

/**
 * Strips <script> tags, event handlers, javascript: URLs, and
 * other dangerous patterns from a string. Preserves the text content.
 *
 * This is NOT a full HTML sanitizer — it's a safety net for content
 * that goes through the Markdown renderer or gets stored as-is.
 */
export function stripDangerous(str) {
  if (typeof str !== "string") return str;
  return str
    // Remove <script>...</script> blocks entirely
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    // Remove event handler attributes
    .replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, "")
    .replace(/\s*on\w+\s*=\s*\S+/gi, "")
    // Remove javascript: URLs
    .replace(/javascript\s*:/gi, "")
    // Remove data: URLs with script content
    .replace(/data\s*:\s*text\/html/gi, "")
    // Remove <iframe>, <embed>, <object>, <form> tags
    .replace(/<\s*\/?\s*(iframe|embed|object|form|base|meta|link)\b[^>]*>/gi, "")
    // Remove style attributes that could do expression() injection
    .replace(/style\s*=\s*["'][^"']*expression\s*\([^)]*\)[^"']*["']/gi, "");
}

/**
 * Sanitizes a value for safe database storage and later rendering.
 * - Strings: strips dangerous HTML patterns
 * - Numbers: coerced or returned as-is
 * - Objects/arrays: recursively sanitized
 * - null/undefined: passed through
 */
export function sanitize(value) {
  if (value === null || value === undefined) return value;
  if (typeof value === "string") return stripDangerous(value);
  if (typeof value === "number" || typeof value === "boolean") return value;
  if (Array.isArray(value)) return value.map(sanitize);
  if (typeof value === "object") {
    const clean = {};
    for (const [k, v] of Object.entries(value)) {
      clean[k] = sanitize(v);
    }
    return clean;
  }
  return value;
}

/**
 * Middleware that sanitizes req.body on every request.
 * Mount BEFORE routes in server.js.
 */
export function sanitizeBody(req, res, next) {
  if (req.body && typeof req.body === "object") {
    req.body = sanitize(req.body);
  }
  next();
}


// ══════════════════════════════════════════════════════
// 3. VALIDATION
// ══════════════════════════════════════════════════════

/**
 * Lightweight request body validator.
 *
 * Usage:
 *   const err = validate(req.body, {
 *     title:   { required: true, type: "string", maxLength: 500 },
 *     status:  { type: "string", oneOf: ["active", "draft", "paused"] },
 *     priority:{ type: "string", oneOf: ["critical", "high", "medium", "low"] },
 *   });
 *   if (err) return res.status(400).json({ error: err });
 *
 * Returns null if valid, or a string describing the first error found.
 */
export function validate(body, schema) {
  for (const [field, rules] of Object.entries(schema)) {
    const value = body[field];

    // Required check
    if (rules.required && (value === undefined || value === null || value === "")) {
      return `${field} is required`;
    }

    // Skip further checks if field is absent and not required
    if (value === undefined || value === null) continue;

    // Type check
    if (rules.type && typeof value !== rules.type) {
      return `${field} must be a ${rules.type}`;
    }

    // String length
    if (rules.maxLength && typeof value === "string" && value.length > rules.maxLength) {
      return `${field} must be ${rules.maxLength} characters or fewer`;
    }

    if (rules.minLength && typeof value === "string" && value.length < rules.minLength) {
      return `${field} must be at least ${rules.minLength} characters`;
    }

    // Enum / whitelist
    if (rules.oneOf && !rules.oneOf.includes(value)) {
      return `${field} must be one of: ${rules.oneOf.join(", ")}`;
    }

    // Number range
    if (rules.min !== undefined && typeof value === "number" && value < rules.min) {
      return `${field} must be at least ${rules.min}`;
    }
    if (rules.max !== undefined && typeof value === "number" && value > rules.max) {
      return `${field} must be at most ${rules.max}`;
    }

    // Array check
    if (rules.isArray && !Array.isArray(value)) {
      return `${field} must be an array`;
    }
  }
  return null;
}
