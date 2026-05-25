/**
 * React Hook for Acquiring API Tokens
 *
 * Provides a hook to safely acquire access tokens for calling your backend API.
 * Handles silent token acquisition with automatic fallback to interactive login
 * when tokens expire or need consent.
 */

import { useMsal } from "@azure/msal-react";
import {
  InteractionRequiredAuthError,
  SilentRequest,
} from "@azure/msal-browser";
import { useCallback, useState } from "react";
import { apiRequest } from "./msal-config";

interface UseApiTokenResult {
  /** Get an access token for API calls */
  getAccessToken: () => Promise<string | null>;
  /** Whether a token acquisition is in progress */
  isLoading: boolean;
  /** Any error that occurred during token acquisition */
  error: Error | null;
  /** Clear any stored error */
  clearError: () => void;
}

/**
 * Hook for acquiring access tokens for API calls.
 *
 * Usage:
 * ```tsx
 * function ApiComponent() {
 *   const { getAccessToken, isLoading, error } = useApiToken();
 *
 *   async function fetchData() {
 *     const token = await getAccessToken();
 *     if (!token) return;
 *
 *     const response = await fetch("/api/data", {
 *       headers: {
 *         Authorization: `Bearer ${token}`,
 *       },
 *     });
 *     // handle response...
 *   }
 *
 *   return (
 *     <button onClick={fetchData} disabled={isLoading}>
 *       {isLoading ? "Loading..." : "Fetch Data"}
 *     </button>
 *   );
 * }
 * ```
 */
export function useApiToken(): UseApiTokenResult {
  const { instance, accounts } = useMsal();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const getAccessToken = useCallback(async (): Promise<string | null> => {
    // Check if user is signed in
    if (accounts.length === 0) {
      setError(new Error("No user signed in"));
      return null;
    }

    setIsLoading(true);
    setError(null);

    const request: SilentRequest = {
      ...apiRequest,
      account: accounts[0],
    };

    try {
      // Try silent token acquisition first
      // This uses cached tokens or refresh tokens
      const response = await instance.acquireTokenSilent(request);
      return response.accessToken;
    } catch (err) {
      // Handle interaction required errors
      // These occur when:
      // - Refresh token expired (AADSTS700084 - 24hr limit for SPAs)
      // - Consent needed for new scopes
      // - MFA required
      // - Password changed
      if (err instanceof InteractionRequiredAuthError) {
        try {
          // Fall back to interactive login
          // Using redirect instead of popup for better mobile support
          await instance.acquireTokenRedirect(request);
          // This will redirect, so we won't reach here
          return null;
        } catch (redirectError) {
          const error = new Error(
            `Interactive login failed: ${redirectError}`
          );
          setError(error);
          return null;
        }
      }

      // Other errors (network, configuration, etc.)
      const error =
        err instanceof Error ? err : new Error("Failed to acquire token");
      setError(error);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [instance, accounts]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    getAccessToken,
    isLoading,
    error,
    clearError,
  };
}

/**
 * Higher-order function to create an authenticated fetch wrapper.
 *
 * Usage:
 * ```tsx
 * function MyComponent() {
 *   const { getAccessToken } = useApiToken();
 *   const authFetch = useAuthenticatedFetch(getAccessToken);
 *
 *   async function loadData() {
 *     const response = await authFetch("/api/data");
 *     const data = await response.json();
 *   }
 * }
 * ```
 */
export function useAuthenticatedFetch(
  getAccessToken: () => Promise<string | null>
) {
  return useCallback(
    async (url: string, options: RequestInit = {}): Promise<Response> => {
      const token = await getAccessToken();

      if (!token) {
        throw new Error("Failed to acquire access token");
      }

      const headers = new Headers(options.headers);
      headers.set("Authorization", `Bearer ${token}`);

      return fetch(url, {
        ...options,
        headers,
      });
    },
    [getAccessToken]
  );
}

/**
 * Hook for making authenticated API calls with automatic token handling.
 *
 * Usage:
 * ```tsx
 * function DataComponent() {
 *   const { data, isLoading, error, refetch } = useAuthenticatedQuery<User[]>(
 *     "/api/users"
 *   );
 *
 *   if (isLoading) return <Loading />;
 *   if (error) return <Error message={error.message} />;
 *
 *   return <UserList users={data} />;
 * }
 * ```
 */
export function useAuthenticatedQuery<T>(
  url: string,
  options?: RequestInit
): {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
} {
  const { getAccessToken } = useApiToken();
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [fetchTrigger, setFetchTrigger] = useState(0);

  const refetch = useCallback(() => {
    setFetchTrigger((prev) => prev + 1);
  }, []);

  // Fetch data when component mounts or refetch is called
  useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = await getAccessToken();
      if (!token) {
        throw new Error("Failed to acquire access token");
      }

      const headers = new Headers(options?.headers);
      headers.set("Authorization", `Bearer ${token}`);

      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = (await response.json()) as T;
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch data"));
    } finally {
      setIsLoading(false);
    }
  }, [url, options, getAccessToken, fetchTrigger]);

  return { data, isLoading, error, refetch };
}
