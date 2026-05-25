/**
 * Protected Route Components for MSAL React
 *
 * Provides components to protect routes that require authentication.
 * Handles loading states, authentication checks, and automatic login redirects.
 */

import React from "react";
import {
  useMsal,
  useIsAuthenticated,
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
} from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { loginRequest } from "./msal-config";

interface ProtectedRouteProps {
  children: React.ReactNode;
  /** Component to show while checking auth status */
  loadingComponent?: React.ReactNode;
  /** Component to show for unauthenticated users (instead of auto-redirect) */
  fallback?: React.ReactNode;
  /** If true, automatically redirect to login. If false, show fallback */
  autoRedirect?: boolean;
}

/**
 * Protected Route Component
 *
 * Wraps content that should only be visible to authenticated users.
 * By default, automatically redirects unauthenticated users to login.
 *
 * Usage:
 * ```tsx
 * <ProtectedRoute>
 *   <DashboardPage />
 * </ProtectedRoute>
 * ```
 *
 * With custom fallback:
 * ```tsx
 * <ProtectedRoute
 *   autoRedirect={false}
 *   fallback={<LoginPrompt />}
 * >
 *   <DashboardPage />
 * </ProtectedRoute>
 * ```
 */
export function ProtectedRoute({
  children,
  loadingComponent = <DefaultLoadingComponent />,
  fallback,
  autoRedirect = true,
}: ProtectedRouteProps) {
  const { instance, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  // Wait for MSAL to finish any in-progress operations
  // This prevents race conditions with redirect handling
  if (inProgress !== InteractionStatus.None) {
    return <>{loadingComponent}</>;
  }

  // User is authenticated, render protected content
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // User is not authenticated
  if (autoRedirect) {
    // Trigger login redirect
    // Using loginRedirect instead of loginPopup for better mobile support
    instance.loginRedirect(loginRequest).catch((error) => {
      console.error("Login redirect failed:", error);
    });

    return <>{loadingComponent}</>;
  }

  // Show fallback for unauthenticated users
  return <>{fallback || <DefaultUnauthenticatedComponent />}</>;
}

/**
 * Alternative approach using MSAL's built-in templates
 *
 * This is simpler but less flexible than ProtectedRoute.
 * Use for straightforward protected/public content switching.
 *
 * Usage:
 * ```tsx
 * <AuthenticatedContent fallback={<LoginButton />}>
 *   <UserProfile />
 * </AuthenticatedContent>
 * ```
 */
export function AuthenticatedContent({
  children,
  fallback,
}: {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  return (
    <>
      <AuthenticatedTemplate>{children}</AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        {fallback || <DefaultUnauthenticatedComponent />}
      </UnauthenticatedTemplate>
    </>
  );
}

/**
 * Login Button Component
 *
 * Triggers login flow when clicked.
 */
export function LoginButton({
  children = "Sign in with Microsoft",
  className,
  style,
}: {
  children?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}) {
  const { instance, inProgress } = useMsal();
  const isLoading = inProgress !== InteractionStatus.None;

  const handleLogin = () => {
    if (isLoading) return;
    instance.loginRedirect(loginRequest).catch((error) => {
      console.error("Login failed:", error);
    });
  };

  return (
    <button
      onClick={handleLogin}
      disabled={isLoading}
      className={className}
      style={{
        padding: "10px 20px",
        backgroundColor: "#0078d4",
        color: "white",
        border: "none",
        borderRadius: "4px",
        cursor: isLoading ? "wait" : "pointer",
        opacity: isLoading ? 0.7 : 1,
        display: "inline-flex",
        alignItems: "center",
        gap: "8px",
        fontFamily: "system-ui, sans-serif",
        fontSize: "14px",
        ...style,
      }}
    >
      {/* Microsoft logo */}
      <svg width="16" height="16" viewBox="0 0 21 21" fill="currentColor">
        <rect x="1" y="1" width="9" height="9" />
        <rect x="11" y="1" width="9" height="9" />
        <rect x="1" y="11" width="9" height="9" />
        <rect x="11" y="11" width="9" height="9" />
      </svg>
      {isLoading ? "Signing in..." : children}
    </button>
  );
}

/**
 * Logout Button Component
 */
export function LogoutButton({
  children = "Sign out",
  className,
  style,
}: {
  children?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}) {
  const { instance, inProgress } = useMsal();
  const isLoading = inProgress !== InteractionStatus.None;

  const handleLogout = () => {
    if (isLoading) return;
    instance.logoutRedirect().catch((error) => {
      console.error("Logout failed:", error);
    });
  };

  return (
    <button
      onClick={handleLogout}
      disabled={isLoading}
      className={className}
      style={{
        padding: "8px 16px",
        backgroundColor: "transparent",
        color: "#666",
        border: "1px solid #ddd",
        borderRadius: "4px",
        cursor: isLoading ? "wait" : "pointer",
        fontFamily: "system-ui, sans-serif",
        fontSize: "14px",
        ...style,
      }}
    >
      {isLoading ? "Signing out..." : children}
    </button>
  );
}

/**
 * User Info Component
 *
 * Displays the currently signed-in user's information.
 */
export function UserInfo() {
  const { accounts } = useMsal();
  const account = accounts[0];

  if (!account) {
    return null;
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <div
        style={{
          width: "32px",
          height: "32px",
          borderRadius: "50%",
          backgroundColor: "#0078d4",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "14px",
          fontWeight: 500,
        }}
      >
        {account.name?.charAt(0).toUpperCase() || "U"}
      </div>
      <div>
        <div style={{ fontWeight: 500 }}>{account.name}</div>
        <div style={{ fontSize: "12px", color: "#666" }}>
          {account.username}
        </div>
      </div>
    </div>
  );
}

// Default components
function DefaultLoadingComponent() {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100%",
        minHeight: "200px",
      }}
    >
      <p style={{ color: "#666", fontFamily: "system-ui, sans-serif" }}>
        Loading...
      </p>
    </div>
  );
}

function DefaultUnauthenticatedComponent() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100%",
        minHeight: "300px",
        gap: "16px",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h2 style={{ margin: 0 }}>Sign in required</h2>
      <p style={{ color: "#666", margin: 0 }}>
        Please sign in to access this content.
      </p>
      <LoginButton />
    </div>
  );
}
