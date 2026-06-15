import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { getErrorMessage } from "../services/api";

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await register(name, email, password);
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
          <p className="eyebrow">Novo capitulo</p>
          <h1>Crie seu perfil e entre em clubes que tratam leitura como experiencia compartilhada.</h1>
          <p className="auth-lead">
            Cadastre-se para acompanhar livros do clube, participar dos encontros e registrar comentarios que ficam no
            historico do grupo.
          </p>

          <div className="auth-highlights">
            <article className="auth-highlight-card">
              <strong>Curadoria</strong>
              <span>Veja o que esta em leitura, o que vem depois e o que ja marcou o clube.</span>
            </article>
            <article className="auth-highlight-card">
              <strong>Participacao</strong>
              <span>Confirme presenca, acompanhe membros e contribua com anotacoes.</span>
            </article>
            <article className="auth-highlight-card">
              <strong>Continuidade</strong>
              <span>Mantenha o contexto dos encontros acessivel para todo o grupo.</span>
            </article>
          </div>
        </section>

        <section className="auth-panel">
          <div className="auth-panel-head">
            <img className="auth-logo" src="/images/logo-header.png" alt="LendoJuntos" />
            <div>
              <p className="eyebrow">Cadastro</p>
              <h2>Criar conta</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <label>
              Nome
              <input type="text" value={name} onChange={(event) => setName(event.target.value)} required />
            </label>

            <label>
              E-mail
              <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            </label>

            <label>
              Senha
              <input
                type="password"
                minLength={6}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </label>

            {error && <p className="feedback error">{error}</p>}

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Cadastrando..." : "Criar conta"}
            </button>
          </form>

          <p className="auth-switch">
            Ja tem conta? <Link to="/">Voltar para login</Link>
          </p>
        </section>
      </section>
    </main>
  );
}
