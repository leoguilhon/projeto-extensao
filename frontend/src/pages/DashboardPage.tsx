import { Link } from "react-router-dom";

export function DashboardPage() {
  return (
    <main>
      <h1>Meus Clubes</h1>

      <ul>
        <li>
          <Link to="/clubs/1">Clube Literário Primavera</Link>
        </li>
        <li>
          <Link to="/clubs/2">Clube Página Aberta</Link>
        </li>
      </ul>

      <p>
        <Link to="/profile">Ir para perfil</Link>
      </p>
    </main>
  );
}