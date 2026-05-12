import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function ProtectedRoute() {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return <main className="shell">Carregando...</main>;
  }

  return token ? <Outlet /> : <Navigate to="/" replace />;
}
