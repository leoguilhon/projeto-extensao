import { Link } from "react-router-dom";

export function BookDetailsPage() {
  return (
    <main>
      <h1>Livro Atual</h1>
      <p>Título: Orgulho e Preconceito</p>
      <p>Autor: Jane Austen</p>
      <p>Comentários em breve...</p>

      <p>
        <Link to="/clubs/1">Voltar ao clube</Link>
      </p>
    </main>
  );
}