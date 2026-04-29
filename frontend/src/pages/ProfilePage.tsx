import { Link } from "react-router-dom";

export function ProfilePage() {
  return (
    <main>
      <h1>Perfil</h1>
      <p>Nome do usuário</p>
      <p>E-mail do usuário</p>

      <p>
        <Link to="/dashboard">Voltar ao dashboard</Link>
      </p>
    </main>
  );
}