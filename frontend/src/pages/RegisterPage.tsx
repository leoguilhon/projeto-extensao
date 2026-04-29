import { Link, useNavigate } from "react-router-dom";

export function RegisterPage() {
  const navigate = useNavigate();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    navigate("/");
  }

  return (
    <main>
      <h1>Cadastro</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <input type="text" placeholder="Nome" />
        </div>

        <div>
          <input type="email" placeholder="E-mail" />
        </div>

        <div>
          <input type="password" placeholder="Senha" />
        </div>

        <button type="submit">Cadastrar</button>
      </form>

      <p>
        Já tem conta? <Link to="/">Voltar para login</Link>
      </p>
    </main>
  );
}