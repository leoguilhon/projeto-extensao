import { useEffect, useState } from "react";
import type { FormEvent, KeyboardEvent, MouseEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { AutoResizeTextarea } from "../components/AutoResizeTextarea";
import { bookService, clubService, getErrorMessage } from "../services/api";
import type { Book, ClubRole, Comment, Meeting, ReadingStatus } from "../types";
import { formatMeetingDateTime, getMeetingDetailsPath, isInteractiveElementTarget } from "../utils/meetings";

const statusLabel: Record<ReadingStatus, string> = {
  planejado: "Planejado",
  em_leitura: "Em leitura",
  concluido: "Concluído",
};

export function BookDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
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
    const content = comment.trim();
    if (!content) return;
    setFeedback("");

    try {
      const newComment = await bookService.addComment(id, content);
      setComments((current) => [...current, newComment]);
      setComment("");
      setFeedback("Comentário publicado no livro.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  async function handleToggleLike() {
    if (!book) return;
    setFeedback("");

    try {
      const updatedBook = book.liked_by_current_user ? await bookService.unlike(book.id) : await bookService.like(book.id);
      setBook(updatedBook);
      setFeedback(updatedBook.liked_by_current_user ? "Livro curtido." : "Like removido do livro.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  function handleMeetingCardClick(event: MouseEvent<HTMLElement>, meetingDetailsPath: string) {
    if (isInteractiveElementTarget(event.target)) return;
    navigate(meetingDetailsPath);
  }

  function handleMeetingCardKeyDown(event: KeyboardEvent<HTMLElement>, meetingDetailsPath: string) {
    if (event.target !== event.currentTarget) return;
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    navigate(meetingDetailsPath);
  }

  if (isLoading) {
    return <main className="shell">Carregando livro...</main>;
  }

  if (!book) {
    return <main className="shell">{feedback || "Livro não encontrado."}</main>;
  }

  return (
    <main className="shell narrow">
      <section className="page-heading page-heading-with-actions">
        <div>
          <p className="eyebrow">{statusLabel[book.status]}</p>
          <div className="page-heading-row">
            <h1>{book.title}</h1>
            <div className="inline-actions">
              <div className="like-control">
                <button
                  aria-label={book.liked_by_current_user ? "Remover like do livro" : "Curtir livro"}
                  className={`like-toggle ${book.liked_by_current_user ? "active" : ""}`}
                  title={book.liked_by_current_user ? "Remover like" : "Curtir"}
                  type="button"
                  onClick={handleToggleLike}
                >
                  {book.liked_by_current_user ? "♥" : "♡"}
                </button>
                <span>{book.like_count}</span>
              </div>
              <Link className="button-link secondary" to={`/clubs/${book.club_id}`}>
                Voltar ao clube
              </Link>
            </div>
          </div>
          <p>{book.author}</p>
          <div className="resource-meta">
            {book.liked_by_current_user && <span>Curtido por você</span>}
          </div>
        </div>
      </section>

      <section className="stack-layout">
        {clubRole === "admin" && (
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
        )}

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
                <article
                  className="list-card clickable-card"
                  key={meeting.id}
                  role="link"
                  tabIndex={0}
                  onClick={(event) => handleMeetingCardClick(event, getMeetingDetailsPath(meeting.club_id, meeting.id))}
                  onKeyDown={(event) => handleMeetingCardKeyDown(event, getMeetingDetailsPath(meeting.club_id, meeting.id))}
                >
                  <div>
                    <h3>{meeting.title}</h3>
                    <p>{formatMeetingDateTime(meeting.scheduled_for)}</p>
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
                    <span>{formatMeetingDateTime(item.created_at)}</span>
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
              <AutoResizeTextarea
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
