import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { bookService, clubService, getErrorMessage } from "../services/api";
import type { Book, ClubRole, Comment, Meeting, ReadingStatus } from "../types";

const statusLabel: Record<ReadingStatus, string> = {
  planejado: "Planejado",
  em_leitura: "Em leitura",
  concluido: "Concluído",
};

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

export function BookDetailsPage() {
  const { id } = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [clubRole, setClubRole] = useState<ClubRole | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [comment, setComment] = useState("");
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const bookId = id;
    let isMounted = true;

    async function loadBookDetails() {
      try {
        const bookData = await bookService.get(bookId);
        const [clubData, commentData, meetingData] = await Promise.all([
          clubService.get(bookData.club_id),
          bookService.comments(bookId),
          bookService.meetings(bookId),
        ]);
        if (!isMounted) return;
        setBook(bookData);
        setClubRole(clubData.current_user_role);
        setComments(commentData);
        setMeetings(meetingData);
      } catch (err) {
        if (isMounted) {
          setFeedback(getErrorMessage(err));
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadBookDetails();

    return () => {
      isMounted = false;
    };
  }, [id]);

  async function handleStatusChange(status: ReadingStatus) {
    if (!id || clubRole !== "admin") return;
    setFeedback("");
    try {
      setBook(await bookService.updateStatus(id, status));
      setFeedback("Situação da leitura atualizada.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  async function handleAddComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!id) return;
    setFeedback("");

    try {
      const newComment = await bookService.addComment(id, comment);
      setComments((current) => [...current, newComment]);
      setComment("");
      setFeedback("Comentário publicado no livro.");
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

      <section className="stack-layout">
        <section className="panel">
          <h2>Detalhes da leitura</h2>
          <p>{book.description || "Sem descrição cadastrada."}</p>
          {book.finished_at && <p>Leitura concluída em {new Date(book.finished_at).toLocaleDateString("pt-BR")}.</p>}

          {clubRole === "admin" ? (
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
          ) : (
            <div className="notice-box">
              Apenas administradores do clube podem alterar o status da leitura.
            </div>
          )}

          {feedback && <p className="feedback">{feedback}</p>}
        </section>

        <section className="panel">
          <div className="section-header">
            <div>
              <h2>Encontros relacionados</h2>
              <p>Discussões e reuniões vinculadas a esta leitura.</p>
            </div>
            <Link className="button-link secondary" to={`/clubs/${book.club_id}/meetings`}>
              Abrir encontros
            </Link>
          </div>
          {meetings.length ? (
            <div className="item-list">
              {meetings.map((meeting) => (
                <article className="list-card" key={meeting.id}>
                  <div>
                    <h3>{meeting.title}</h3>
                    <p>{formatDateTime(meeting.scheduled_for)}</p>
                    <span>{meeting.location || "Local a definir"}</span>
                  </div>
                  <strong className="comment-count">{meeting.comment_count} comentário(s)</strong>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Este livro ainda não possui encontros vinculados.</p>
              <span>Os encontros aparecerão aqui quando forem planejados pelo clube.</span>
            </div>
          )}
        </section>

        <section className="panel">
          <div className="section-header">
            <div>
              <h2>Comentários do livro</h2>
              <p>Espaço simples para registrar impressões do clube sobre a leitura.</p>
            </div>
          </div>

          {comments.length ? (
            <div className="comment-list">
              {comments.map((item) => (
                <article className="comment-card" key={item.id}>
                  <div className="comment-meta">
                    <strong>{item.user_name}</strong>
                    <span>{formatDateTime(item.created_at)}</span>
                  </div>
                  <p>{item.content}</p>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Ainda não há comentários sobre este livro.</p>
              <span>Publique a primeira observação para iniciar a discussão.</span>
            </div>
          )}

          <form className="comment-form" onSubmit={handleAddComment}>
            <label>
              Novo comentário
              <textarea
                value={comment}
                onChange={(event) => setComment(event.target.value)}
                placeholder="Compartilhe um ponto da leitura para o clube discutir."
                required
              />
            </label>
            <button type="submit">Publicar comentário</button>
          </form>
        </section>
      </section>
    </main>
  );
}
