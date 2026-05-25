/**
 * Microsoft Entra ID JWT Validation for Cloudflare Workers
 *
 * IMPORTANT: MSAL.js does NOT work in Cloudflare Workers because it relies on
 * browser/Node.js APIs. Use the jose library for token validation instead.
 *
 * This module provides:
 * - JWT validation using Azure AD's public keys (JWKS)
 * - Proper JWKS endpoint discovery (Azure uses non-standard path)
 * - Caching to avoid fetching keys on every request
 * - Multi-tenant support
 */

import * as jose from "jose";

/**
 * Decoded token payload from Microsoft Entra ID
 */
export interface EntraTokenPayload {
  /** Audience - your application's client ID or API URI */
  aud: string;
  /** Issuer - https://login.microsoftonline.com/{tenant}/v2.0 */
  iss: string;
  /** Subject - unique identifier for the user */
  sub: string;
  /** Object ID - user's Azure AD object ID */
  oid: string;
  /** Tenant ID - the Azure AD tenant */
  tid: string;
  /** User's email (may be preferred_username) */
  preferred_username: string;
  /** Display name */
  name: string;
  /** Email address (if available) */
  email?: string;
  /** App roles assigned to the user */
  roles?: string[];
  /** Scopes granted (space-separated string) */
  scp?: string;
  /** Issued at timestamp */
  iat: number;
  /** Expiration timestamp */
  exp: number;
  /** Not before timestamp */
  nbf: number;
}

/**
 * Environment bindings required for token validation
 */
export interface AuthEnv {
  /** Azure AD tenant ID (GUID) */
  AZURE_TENANT_ID: string;
  /** Azure AD application (client) ID (GUID) */
  AZURE_CLIENT_ID: string;
}

// JWKS cache to avoid fetching on every request
interface JWKSCache {
  jwks: jose.JWTVerifyGetKey;
  fetchedAt: number;
}

const jwksCache = new Map<string, JWKSCache>();
const JWKS_CACHE_DURATION = 3600000; // 1 hour in milliseconds

/**
 * Fetches the JWKS for a given Azure AD tenant.
 *
 * CRITICAL: Azure AD does NOT serve JWKS at the standard
 * .well-known/jwks.json path. You must first fetch the
 * OpenID configuration to get the correct jwks_uri.
 */
async function getJWKS(tenantId: string): Promise<jose.JWTVerifyGetKey> {
  const now = Date.now();
  const cached = jwksCache.get(tenantId);

  // Return cached JWKS if still valid
  if (cached && now - cached.fetchedAt < JWKS_CACHE_DURATION) {
    return cached.jwks;
  }

  // Fetch OpenID configuration to get JWKS URI
  // This is the CORRECT way to discover Azure AD's JWKS endpoint
  const configUrl = `https://login.microsoftonline.com/${tenantId}/v2.0/.well-known/openid-configuration`;

  const configResponse = await fetch(configUrl);
  if (!configResponse.ok) {
    throw new Error(
      `Failed to fetch OpenID configuration: ${configResponse.status}`
    );
  }

  const config = (await configResponse.json()) as { jwks_uri: string };

  // Create remote JWKS using the discovered URI
  const jwks = jose.createRemoteJWKSet(new URL(config.jwks_uri));

  // Cache for future requests
  jwksCache.set(tenantId, { jwks, fetchedAt: now });

  return jwks;
}

/**
 * Validates a Microsoft Entra ID JWT token.
 *
 * @param token - The JWT token (without "Bearer " prefix)
 * @param env - Environment bindings with Azure configuration
 * @returns Decoded token payload if valid, null if invalid
 *
 * Usage:
 * ```typescript
 * const authHeader = request.headers.get("Authorization");
 * if (!authHeader?.startsWith("Bearer ")) {
 *   return new Response("Unauthorized", { status: 401 });
 * }
 *
 * const token = authHeader.slice(7);
 * const user = await validateEntraToken(token, env);
 *
 * if (!user) {
 *   return new Response("Invalid token", { status: 401 });
 * }
 *
 * // Token is valid, user contains the decoded claims
 * console.log(`User: ${user.name} (${user.preferred_username})`);
 * ```
 */
export async function validateEntraToken(
  token: string,
  env: AuthEnv
): Promise<EntraTokenPayload | null> {
  try {
    const jwks = await getJWKS(env.AZURE_TENANT_ID);

    const { payload } = await jose.jwtVerify(token, jwks, {
      // Validate issuer matches expected tenant
      issuer: `https://login.microsoftonline.com/${env.AZURE_TENANT_ID}/v2.0`,

      // Validate audience matches your application
      // Can be client ID or API URI (api://{client_id})
      audience: env.AZURE_CLIENT_ID,
    });

    return payload as unknown as EntraTokenPayload;
  } catch (error) {
    // Log error details for debugging (avoid in production)
    if (error instanceof jose.errors.JWTExpired) {
      console.warn("Token expired");
    } else if (error instanceof jose.errors.JWTClaimValidationFailed) {
      console.warn("Token claim validation failed:", error.message);
    } else {
      console.error("Token validation error:", error);
    }

    return null;
  }
}

/**
 * Validates a token for multi-tenant applications.
 *
 * For multi-tenant apps, the issuer varies based on the user's tenant.
 * This function extracts the tenant from the token and validates accordingly.
 *
 * @param token - The JWT token (without "Bearer " prefix)
 * @param clientId - Your application's client ID
 * @returns Decoded token payload if valid, null if invalid
 */
export async function validateMultiTenantToken(
  token: string,
  clientId: string
): Promise<EntraTokenPayload | null> {
  try {
    // First, decode without verification to get the tenant ID
    const decoded = jose.decodeJwt(token);
    const tenantId = decoded.tid as string;

    if (!tenantId) {
      console.warn("Token missing tenant ID (tid) claim");
      return null;
    }

    // Now validate with the correct tenant's JWKS
    const jwks = await getJWKS(tenantId);

    const { payload } = await jose.jwtVerify(token, jwks, {
      issuer: `https://login.microsoftonline.com/${tenantId}/v2.0`,
      audience: clientId,
    });

    return payload as unknown as EntraTokenPayload;
  } catch (error) {
    console.error("Multi-tenant token validation error:", error);
    return null;
  }
}

/**
 * Middleware pattern for Cloudflare Workers
 *
 * Usage:
 * ```typescript
 * export default {
 *   async fetch(request: Request, env: Env): Promise<Response> {
 *     // Public routes
 *     const url = new URL(request.url);
 *     if (url.pathname === "/" || url.pathname.startsWith("/public")) {
 *       return handlePublicRoute(request, env);
 *     }
 *
 *     // Protected routes
 *     const authResult = await requireAuth(request, env);
 *     if (authResult instanceof Response) {
 *       return authResult; // 401 response
 *     }
 *
 *     // authResult is the validated user
 *     return handleProtectedRoute(request, env, authResult);
 *   },
 * };
 * ```
 */
export async function requireAuth(
  request: Request,
  env: AuthEnv
): Promise<EntraTokenPayload | Response> {
  const authHeader = request.headers.get("Authorization");

  if (!authHeader) {
    return new Response(
      JSON.stringify({ error: "Missing Authorization header" }),
      {
        status: 401,
        headers: {
          "Content-Type": "application/json",
          "WWW-Authenticate": 'Bearer realm="api"',
        },
      }
    );
  }

  if (!authHeader.startsWith("Bearer ")) {
    return new Response(
      JSON.stringify({ error: "Invalid Authorization header format" }),
      {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  const token = authHeader.slice(7);
  const user = await validateEntraToken(token, env);

  if (!user) {
    return new Response(JSON.stringify({ error: "Invalid or expired token" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  return user;
}

/**
 * Check if user has specific roles.
 *
 * App roles must be configured in Azure Portal:
 * App Registration > App roles > Create app role
 *
 * Then assign users/groups to roles:
 * Enterprise applications > Your app > Users and groups
 */
export function hasRole(
  user: EntraTokenPayload,
  requiredRole: string
): boolean {
  return user.roles?.includes(requiredRole) ?? false;
}

/**
 * Check if user has any of the specified roles.
 */
export function hasAnyRole(
  user: EntraTokenPayload,
  roles: string[]
): boolean {
  if (!user.roles) return false;
  return roles.some((role) => user.roles!.includes(role));
}

/**
 * Check if token has specific scopes.
 *
 * Scopes are space-separated in the scp claim.
 */
export function hasScope(
  user: EntraTokenPayload,
  requiredScope: string
): boolean {
  if (!user.scp) return false;
  const scopes = user.scp.split(" ");
  return scopes.includes(requiredScope);
}
