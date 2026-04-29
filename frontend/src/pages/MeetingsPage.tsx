import { Link } from "react-router-dom";

export function MeetingsPage() {
  return (
    <main>
      <h1>Encontros do Clube</h1>
      <p>Próximo encontro: 25/04 às 19h</p>

      <p>
        <Link to="/clubs/1">Voltar ao clube</Link>
      </p>
    </main>
  );
}