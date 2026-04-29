import { Link, useNavigate } from "react-router-dom";

export function LoginPage() {
  const navigate = useNavigate();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    navigate("/dashboard");
  }

  return (
    <main>
      <h1>LendoJuntos</h1>
      <h2>Login</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <input type="email" placeholder="E-mail" />
        </div>

        <div>
          <input type="password" placeholder="Senha" />
        </div>

        <button type="submit">Entrar</button>
      </form>

      <p>
        Não tem conta? <Link to="/register">Criar conta</Link>
      </p>
    </main>
  );
}