import { Link, useParams } from "react-router-dom";

export function MeetingsPage() {
  const { id } = useParams();

  return (
    <main className="shell narrow">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Encontros</p>
          <h1>Encontros do Clube</h1>
          <p>O módulo de encontros está previsto para a semana 13 do cronograma.</p>
        </div>
        <Link className="button-link secondary" to={`/clubs/${id}`}>
          Voltar ao clube
        </Link>
      </section>
    </main>
  );
}
