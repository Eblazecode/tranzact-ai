export const SESSION_STORAGE_KEY = "transacai_session";
export const ACCESS_TOKEN_STORAGE_KEY = "transacai_access_token";

export type AuthSession = {
  userName: string;
  email: string;
  createdAt: string;
  accessToken?: string;
};

export function getSession(): AuthSession | null {
  if (typeof window === "undefined") return null;

  const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as AuthSession;
    if (!parsed.userName || !parsed.email || !parsed.createdAt) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  const session = getSession();
  return session !== null && Boolean(session.accessToken);
}

export function canUseBrowserSession() {
  return typeof window !== "undefined";
}

export function createSession(userName: string, email: string, accessToken?: string) {
  if (typeof window === "undefined") return;

  const session: AuthSession = {
    userName,
    email,
    createdAt: new Date().toISOString(),
    accessToken,
  };

  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
  if (accessToken) {
    window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, accessToken);
  } else {
    window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
  }
}

export function clearSession() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(SESSION_STORAGE_KEY);
  window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function updateSessionUserName(userName: string) {
  if (typeof window === "undefined") return;

  const session = getSession();
  if (!session) return;

  window.localStorage.setItem(
    SESSION_STORAGE_KEY,
    JSON.stringify({
      ...session,
      userName,
    }),
  );
}

export function getCurrentUserName() {
  return getSession()?.userName ?? "Dashboard User";
}

export function getAccessToken() {
  return getSession()?.accessToken ?? null;
}
