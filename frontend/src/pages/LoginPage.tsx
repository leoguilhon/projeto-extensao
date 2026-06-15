import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { getErrorMessage } from "../services/api";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("ana@lendojuntos.test");
  const [password, setPassword] = useState("123456");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-stage">
        <section className="auth-story">
          <p className="eyebrow">Leitura com presenca</p>
          <h1>Organize clubes, encontros e conversas sem perder o fio da leitura.</h1>
          <p className="auth-lead">
            Uma interface feita para clubes que querem registrar decisoes, descobrir proximos encontros e manter a memoria
            do grupo viva.
          </p>

          <div className="auth-highlights">
            <article className="auth-highlight-card">
              <strong>Clubes</strong>
              <span>Seu espaco para reunir leitores, livros e responsabilidades.</span>
            </article>
            <article className="auth-highlight-card">
              <strong>Encontros</strong>
              <span>Agenda, pauta e presencas confirmadas no mesmo fluxo.</span>
            </article>
            <article className="auth-highlight-card">
              <strong>Memoria</strong>
              <span>Comentarios e historico acessiveis, sem conversas dispersas.</span>
            </article>
          </div>
        </section>

        <section className="auth-panel">
          <div className="auth-panel-head">
            <img className="auth-logo primary" src="/images/logo-primary.png" alt="LendoJuntos" />
            <div>
              <p className="eyebrow">Acesso ao painel</p>
              <h2>Entrar</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <label>
              E-mail
              <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            </label>

            <label>
              Senha
              <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
            </label>

            {error && <p className="feedback error">{error}</p>}

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Entrando..." : "Entrar na plataforma"}
            </button>
          </form>

          <p className="auth-switch">
            Nao tem conta? <Link to="/register">Criar conta</Link>
          </p>
        </section>
      </section>
    </main>
  );
}
