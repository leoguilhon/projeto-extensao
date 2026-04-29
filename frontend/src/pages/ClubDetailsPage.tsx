import { Link } from "react-router-dom";

export function ClubDetailsPage() {
  return (
    <main>
      <h1>Clube Literário Primavera</h1>
      <p>Descrição do clube.</p>

      <ul>
        <li>
          <Link to="/books/1">Ver livro atual</Link>
        </li>
        <li>
          <Link to="/clubs/1/meetings">Ver encontros</Link>
        </li>
      </ul>

      <p>
        <Link to="/dashboard">Voltar ao dashboard</Link>
      </p>
    </main>
  );
}