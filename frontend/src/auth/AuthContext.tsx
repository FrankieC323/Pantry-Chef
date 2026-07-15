import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { authApi, type StaffUser } from "@/api/auth";
import { authToken } from "@/api/client";

interface AuthContextValue {
  user: StaffUser | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<StaffUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // On load, if a token is already stored (previous session, same
    // browser), validate it against /api/auth/me rather than trusting it
    // blindly -- it may have expired since the last visit.
    const existing = authToken.get();
    if (!existing) {
      setIsLoading(false);
      return;
    }
    authApi
      .me()
      .then(setUser)
      .catch(() => authToken.clear())
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (username: string, password: string) => {
    const token = await authApi.login(username, password);
    authToken.set(token.access_token);
    const me = await authApi.me();
    setUser(me);
  };

  const register = async (username: string, password: string) => {
    await authApi.register(username, password);
    await login(username, password);
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
