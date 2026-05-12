import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function AppLayout() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="app-frame">
      <header className="topbar">
        <Link className="brand" to="/dashboard">
          <img src="/images/logo-header.png" alt="LendoJuntos" />
        </Link>
        <nav>
          <NavLink to="/dashboard">Clubes</NavLink>
          <NavLink to="/profile">Perfil</NavLink>
        </nav>
        <div className="user-menu">
          <span>{user?.name}</span>
          <button className="ghost-button" type="button" onClick={handleLogout}>
            Sair
          </button>
        </div>
      </header>
      <Outlet />
    </div>
  );
}
