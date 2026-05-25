/**
 * MSAL Provider Setup for React Applications
 *
 * This file should be imported in your main.tsx or App.tsx.
 * CRITICAL: MSAL instance must be created OUTSIDE the component tree
 * to prevent re-instantiation on re-renders.
 */

import React, { useEffect, useState } from "react";
import {
  PublicClientApplication,
  EventType,
  EventMessage,
  AuthenticationResult,
  InteractionStatus,
} from "@azure/msal-browser";
import { MsalProvider, useMsal } from "@azure/msal-react";
import { msalConfig } from "./msal-config";

// CRITICAL: Create MSAL instance outside component tree
// This prevents re-initialization on every render
export const msalInstance = new PublicClientApplication(msalConfig);

/**
 * Initialize MSAL and set up event handlers
 * Call this before rendering your app
 */
export async function initializeMsal(): Promise<void> {
  await msalInstance.initialize();

  // Handle redirect response if coming back from login
  try {
    const response = await msalInstance.handleRedirectPromise();
    if (response) {
      msalInstance.setActiveAccount(response.account);
    }
  } catch (error) {
    console.error("Error handling redirect:", error);
  }

  // Set active account if one exists
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    // If multiple accounts, you might want to let user choose
    // For now, use the first one
    msalInstance.setActiveAccount(accounts[0]);
  }

  // Listen for sign-in success to set active account
  msalInstance.addEventCallback((event: EventMessage) => {
    if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
      const result = event.payload as AuthenticationResult;
      msalInstance.setActiveAccount(result.account);
    }

    if (event.eventType === EventType.LOGOUT_SUCCESS) {
      msalInstance.setActiveAccount(null);
    }
  });
}

/**
 * Props for the auth provider wrapper
 */
interface AuthProviderProps {
  children: React.ReactNode;
  loadingComponent?: React.ReactNode;
}

/**
 * Auth Provider Component
 *
 * Wraps your app with MsalProvider and handles initialization.
 * Shows a loading state while MSAL initializes.
 *
 * Usage in main.tsx:
 * ```tsx
 * import { AuthProvider } from "./auth/msal-provider";
 *
 * ReactDOM.createRoot(document.getElementById("root")!).render(
 *   <React.StrictMode>
 *     <AuthProvider>
 *       <App />
 *     </AuthProvider>
 *   </React.StrictMode>
 * );
 * ```
 */
export function AuthProvider({
  children,
  loadingComponent = <DefaultLoadingComponent />,
}: AuthProviderProps) {
  const [isInitialized, setIsInitialized] = useState(false);
  const [initError, setInitError] = useState<Error | null>(null);

  useEffect(() => {
    initializeMsal()
      .then(() => setIsInitialized(true))
      .catch((error) => {
        console.error("Failed to initialize MSAL:", error);
        setInitError(error);
      });
  }, []);

  if (initError) {
    return (
      <div style={{ padding: "20px", color: "red" }}>
        <h2>Authentication Error</h2>
        <p>Failed to initialize authentication: {initError.message}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!isInitialized) {
    return <>{loadingComponent}</>;
  }

  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>;
}

/**
 * Default loading component shown during MSAL initialization
 */
function DefaultLoadingComponent() {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <div style={{ textAlign: "center" }}>
        <div
          style={{
            width: "40px",
            height: "40px",
            border: "3px solid #f3f3f3",
            borderTop: "3px solid #0078d4",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
            margin: "0 auto 16px",
          }}
        />
        <p style={{ color: "#666" }}>Initializing authentication...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
}

/**
 * Hook to check if MSAL is currently processing an interaction
 * Useful to prevent calling interactive APIs while another is in progress
 */
export function useAuthInProgress(): boolean {
  const { inProgress } = useMsal();
  return inProgress !== InteractionStatus.None;
}
