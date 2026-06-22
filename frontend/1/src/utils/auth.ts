const TOKEN_KEY = 'PULSEFORGE_JWT';
const USER_KEY = 'PULSEFORGE_USER';

export interface AuthUser {
  id: number;
  full_name: string;
  email: string;
  role: 'organizer' | 'reviewer' | 'participant';
  organization?: string | null;
  reviewer_id?: number | null;
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function setStoredUser(user: AuthUser): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function roleToActiveRole(role: string): 'organizer' | 'reviewer' | 'participant' | 'login' {
  if (role === 'organizer' || role === 'admin') return 'organizer';
  if (role === 'reviewer') return 'reviewer';
  if (role === 'participant') return 'participant';
  return 'login';
}

export function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function logoutAuth(): void {
  clearAuth();
}
