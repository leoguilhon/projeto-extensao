import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { authService } from "../services/api";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  updateUser: (user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem("lendojuntos:token"));
  const [user, setUser] = useState<User | null>(() => {
    const storedUser = localStorage.getItem("lendojuntos:user");
    return storedUser ? JSON.parse(storedUser) : null;
  });
  const [isLoading, setIsLoading] = useState(Boolean(token));

  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }

    authService
      .me()
      .then((profile) => {
        setUser(profile);
        localStorage.setItem("lendojuntos:user", JSON.stringify(profile));
      })
      .catch(() => {
        localStorage.removeItem("lendojuntos:token");
        localStorage.removeItem("lendojuntos:user");
        setToken(null);
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, [token]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isLoading,
      async login(email, password) {
        const response = await authService.login(email, password);
        localStorage.setItem("lendojuntos:token", response.access_token);
        localStorage.setItem("lendojuntos:user", JSON.stringify(response.user));
        setToken(response.access_token);
        setUser(response.user);
      },
      async register(name, email, password) {
        const response = await authService.register(name, email, password);
        localStorage.setItem("lendojuntos:token", response.access_token);
        localStorage.setItem("lendojuntos:user", JSON.stringify(response.user));
        setToken(response.access_token);
        setUser(response.user);
      },
      updateUser(updatedUser) {
        setUser(updatedUser);
        localStorage.setItem("lendojuntos:user", JSON.stringify(updatedUser));
      },
      logout() {
        localStorage.removeItem("lendojuntos:token");
        localStorage.removeItem("lendojuntos:user");
        setToken(null);
        setUser(null);
      },
    }),
    [isLoading, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return context;
}
