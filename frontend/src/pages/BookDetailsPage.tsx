import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { bookService, getErrorMessage } from "../services/api";
import type { Book, ReadingStatus } from "../types";

const statusLabel: Record<ReadingStatus, string> = {
  planejado: "Planejado",
  em_leitura: "Em leitura",
  concluido: "Concluído",
};

export function BookDetailsPage() {
  const { id } = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    bookService
      .get(id)
      .then(setBook)
      .catch((err) => setFeedback(getErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, [id]);

  async function handleStatusChange(status: ReadingStatus) {
    if (!id) return;
    setFeedback("");
    try {
      setBook(await bookService.updateStatus(id, status));
      setFeedback("Situação da leitura atualizada.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  if (isLoading) {
    return <main className="shell">Carregando livro...</main>;
  }

  if (!book) {
    return <main className="shell">{feedback || "Livro não encontrado."}</main>;
  }

  return (
    <main className="shell narrow">
      <section className="page-heading">
        <div>
          <p className="eyebrow">{statusLabel[book.status]}</p>
          <h1>{book.title}</h1>
          <p>{book.author}</p>
        </div>
        <Link className="button-link secondary" to={`/clubs/${book.club_id}`}>
          Voltar ao clube
        </Link>
      </section>

      <section className="panel">
        <h2>Detalhes da leitura</h2>
        <p>{book.description || "Sem descrição cadastrada."}</p>
        {book.finished_at && <p>Leitura concluída em {new Date(book.finished_at).toLocaleDateString("pt-BR")}.</p>}

        <div className="segmented-control" aria-label="Situação da leitura">
          {(["planejado", "em_leitura", "concluido"] as ReadingStatus[]).map((status) => (
            <button
              className={book.status === status ? "active" : ""}
              key={status}
              type="button"
              onClick={() => handleStatusChange(status)}
            >
              {statusLabel[status]}
            </button>
          ))}
        </div>

        {feedback && <p className="feedback">{feedback}</p>}
      </section>
    </main>
  );
}
