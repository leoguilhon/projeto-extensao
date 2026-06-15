import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ActionMenu } from "../components/ActionMenu";
import { Modal } from "../components/Modal";
import { useAuth } from "../contexts/AuthContext";
import { bookService, clubService, getErrorMessage, meetingService } from "../services/api";
import type { Book, Club, ClubMember, Meeting, ReadingHistoryItem, ReadingStatus } from "../types";

const statusLabel: Record<ReadingStatus, string> = {
  planejado: "Planejado",
  em_leitura: "Em leitura",
  concluido: "Concluído",
};

function formatDate(value: string) {
  return new Date(value).toLocaleString("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

export function ClubDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [club, setClub] = useState<Club | null>(null);
  const [members, setMembers] = useState<ClubMember[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [history, setHistory] = useState<ReadingHistoryItem[]>([]);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [description, setDescription] = useState("");
  const [clubNameDraft, setClubNameDraft] = useState("");
  const [clubDescriptionDraft, setClubDescriptionDraft] = useState("");
  const [status, setStatus] = useState<ReadingStatus>("planejado");
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(() => new Date().toISOString());
  const [isBookModalOpen, setIsBookModalOpen] = useState(false);
  const [isEditClubModalOpen, setIsEditClubModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLeaveModalOpen, setIsLeaveModalOpen] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  const isAdmin = club?.current_user_role === "admin";
  const canEditClub = Boolean(club && user && club.owner_id === user.id);
  const canDeleteClub = Boolean(club && user && club.owner_id === user.id);
  const canLeaveClub = Boolean(club && user && club.is_member && club.owner_id !== user.id);
  const currentBook = useMemo(() => books.find((book) => book.status === "em_leitura"), [books]);
  const nextMeeting = useMemo(
    () => meetings.find((meeting) => meeting.scheduled_for >= currentTime) ?? meetings[0] ?? null,
    [currentTime, meetings],
  );

  useEffect(() => {
    if (!id) return;
    const clubId = id;
    let isMounted = true;

    async function loadClub() {
      try {
        const [clubData, memberData, bookData, meetingData, historyData] = await Promise.all([
          clubService.get(clubId),
          clubService.members(clubId),
          bookService.listByClub(clubId),
          meetingService.listByClub(clubId),
          bookService.history(clubId),
        ]);
        if (!isMounted) return;
        setClub(clubData);
        setClubNameDraft(clubData.name);
        setClubDescriptionDraft(clubData.description);
        setMembers(memberData);
        setBooks(bookData);
        setMeetings(meetingData);
        setHistory(historyData);
        setCurrentTime(new Date().toISOString());
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

    void loadClub();

    return () => {
      isMounted = false;
    };
  }, [id]);

  async function handleCreateBook(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!id) return;
    setFeedback("");

    try {
      await bookService.create(id, { title, author, description, status });
      const [updatedBooks, updatedHistory] = await Promise.all([bookService.listByClub(id), bookService.history(id)]);
      setBooks(updatedBooks);
      setHistory(updatedHistory);
      setTitle("");
      setAuthor("");
      setDescription("");
      setStatus("planejado");
      setFeedback("Livro cadastrado no clube.");
      setIsBookModalOpen(false);
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  async function handleUpdateClub(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!club) return;
    setFeedback("");

    try {
      const updatedClub = await clubService.update(club.id, {
        name: clubNameDraft,
        description: clubDescriptionDraft,
      });
      setClub(updatedClub);
      setClubNameDraft(updatedClub.name);
      setClubDescriptionDraft(updatedClub.description);
      setFeedback("Clube atualizado.");
      setIsEditClubModalOpen(false);
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  async function handleDeleteClub() {
    if (!id) return;
    setFeedback("");
    setIsDeleting(true);

    try {
      await clubService.remove(id);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setFeedback(getErrorMessage(err));
      setIsDeleteModalOpen(false);
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleLeaveClub() {
    if (!id) return;
    setFeedback("");
    setIsLeaving(true);

    try {
      await clubService.leave(id);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setFeedback(getErrorMessage(err));
      setIsLeaveModalOpen(false);
    } finally {
      setIsLeaving(false);
    }
  }

  async function handleToggleFavorite() {
    if (!club) return;
    setFeedback("");

    try {
      const updatedClub = club.is_favorite ? await clubService.unfavorite(club.id) : await clubService.favorite(club.id);
      setClub(updatedClub);
      setFeedback(updatedClub.is_favorite ? "Clube favoritado." : "Clube removido dos favoritos.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  async function handleToggleBookLike(book: Book) {
    setFeedback("");

    try {
      const updatedBook = book.liked_by_current_user ? await bookService.unlike(book.id) : await bookService.like(book.id);
      setBooks((current) => current.map((item) => (item.id === book.id ? updatedBook : item)));
      setFeedback(updatedBook.liked_by_current_user ? "Livro curtido." : "Like removido do livro.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  if (isLoading) {
    return <main className="shell">Carregando clube...</main>;
  }

  if (!club) {
    return <main className="shell">{feedback || "Clube não encontrado."}</main>;
  }

  return (
    <main className="shell">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Clube de leitura</p>
          <h1>{club.name}</h1>
          <p>{club.description}</p>
        </div>
        <div className="inline-actions">
          <button
            aria-label={club.is_favorite ? "Remover clube dos favoritos" : "Favoritar clube"}
            className={`favorite-toggle ${club.is_favorite ? "active" : ""}`}
            title={club.is_favorite ? "Remover favorito" : "Favoritar"}
            type="button"
            onClick={handleToggleFavorite}
          >
            {club.is_favorite ? "★" : "☆"}
          </button>
          <ActionMenu>
            <Link className="button-link" to={`/clubs/${club.id}/meetings`}>
              📍 Ver encontros
            </Link>
            {isAdmin && (
              <button type="button" onClick={() => setIsBookModalOpen(true)}>
                📚 Cadastrar livro
              </button>
            )}
            {canEditClub && (
              <button type="button" onClick={() => setIsEditClubModalOpen(true)}>
                ✏️ Editar clube
              </button>
            )}
            <Link className="button-link secondary" to="/dashboard">
              ↩️ Voltar
            </Link>
            {canLeaveClub && (
              <button className="danger-button" type="button" onClick={() => setIsLeaveModalOpen(true)}>
                🚪 Sair do clube
              </button>
            )}
            {canDeleteClub && (
              <button className="danger-button" type="button" onClick={() => setIsDeleteModalOpen(true)}>
                🗑️ Excluir clube
              </button>
            )}
          </ActionMenu>
        </div>
      </section>

      {feedback && <p className="feedback page-feedback">{feedback}</p>}

      <section className="content-grid workspace-grid">
        <section className="workspace-panel club-summary-panel">
          <h2>📚 Livro atual</h2>
          {currentBook ? (
            <article className="compact-card">
              <h3>{currentBook.title}</h3>
              <p>{currentBook.author}</p>
              <span className="meta-label">{statusLabel[currentBook.status]}</span>
              <Link to={`/books/${currentBook.id}`}>Ver detalhes</Link>
            </article>
          ) : (
            <div className="empty-state">
              <p>Nenhum livro marcado como leitura atual.</p>
              <span>Cadastre um livro ou atualize o status de uma leitura existente.</span>
            </div>
          )}
        </section>

        <section className="workspace-panel club-summary-panel">
          <h2>📍 Próximo encontro</h2>
          {nextMeeting ? (
            <article className="compact-card">
              <h3>{nextMeeting.title}</h3>
              <p>{formatDate(nextMeeting.scheduled_for)}</p>
              <span className="meta-label">{nextMeeting.location || "Local a definir"}</span>
              {nextMeeting.book_id && (
                <Link to={`/books/${nextMeeting.book_id}`}>{nextMeeting.book_title}</Link>
              )}
            </article>
          ) : (
            <div className="empty-state">
              <p>Nenhum encontro cadastrado.</p>
              <span>{isAdmin ? "Planeje o primeiro encontro do clube." : "Acompanhe aqui quando o próximo encontro for criado."}</span>
            </div>
          )}
        </section>

        <section className="workspace-panel club-summary-panel members-panel">
          <h2>👤 Membros</h2>
          <div className="item-list compact scroll-list">
            {members.map((member) => (
              <div className="member-row" key={member.user_id}>
                <span>{member.name}</span>
                <strong>{member.role === "admin" ? "Admin" : "Membro"}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="workspace-panel wide-panel">
          <div className="section-header compact">
            <div>
              <h2>📚 Livros do clube</h2>
              <p>Acompanhe leituras em andamento, planejadas e concluídas.</p>
            </div>
          </div>
          {books.length ? (
            <div className="item-list scroll-list long-list">
              {books.map((book) => (
                <article className="resource-card" key={book.id}>
                  <div className="resource-main">
                    <h3>{book.title}</h3>
                    <p>{book.author}</p>
                    <div className="resource-meta">
                      <span>{statusLabel[book.status]}</span>
                    </div>
                  </div>
                  <div className="card-actions">
                    <div className="like-control">
                      <button
                        aria-label={book.liked_by_current_user ? "Remover like do livro" : "Curtir livro"}
                        className={`like-toggle ${book.liked_by_current_user ? "active" : ""}`}
                        title={book.liked_by_current_user ? "Remover like" : "Curtir"}
                        type="button"
                        onClick={() => handleToggleBookLike(book)}
                      >
                        {book.liked_by_current_user ? "♥" : "♡"}
                      </button>
                      <span>{book.like_count}</span>
                    </div>
                    <Link className="button-link" to={`/books/${book.id}`}>
                      Detalhes
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Este clube ainda não possui livros cadastrados.</p>
              <span>{isAdmin ? "Use o botão Cadastrar livro para registrar a primeira leitura." : "Aguarde um administrador publicar a primeira obra."}</span>
            </div>
          )}
        </section>

        <section className="workspace-panel wide-panel">
          <div className="section-header compact">
            <div>
              <h2>✅ Histórico de leituras</h2>
              <p>Registros das obras já concluídas pelo grupo.</p>
            </div>
          </div>
          {history.length ? (
            <div className="item-list scroll-list long-list">
              {history.map((item) => (
                <article className="resource-card" key={item.book_id}>
                  <div className="resource-main">
                    <h3>{item.title}</h3>
                    <p>{item.author}</p>
                    <div className="resource-meta">
                      <span>Concluído em {new Date(item.finished_at).toLocaleDateString("pt-BR")}</span>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Ainda não há livros concluídos neste clube.</p>
              <span>Assim que uma leitura for finalizada, ela aparecerá automaticamente aqui.</span>
            </div>
          )}
        </section>
      </section>

      <Modal title="Cadastrar livro" isOpen={isBookModalOpen} onClose={() => setIsBookModalOpen(false)}>
        <form onSubmit={handleCreateBook}>
          <label>
            Título
            <input value={title} onChange={(event) => setTitle(event.target.value)} required />
          </label>
          <label>
            Autor
            <input value={author} onChange={(event) => setAuthor(event.target.value)} required />
          </label>
          <label>
            Descrição
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} />
          </label>
          <label>
            Situação
            <select value={status} onChange={(event) => setStatus(event.target.value as ReadingStatus)}>
              <option value="planejado">Planejado</option>
              <option value="em_leitura">Em leitura</option>
              <option value="concluido">Concluído</option>
            </select>
          </label>
          <div className="form-actions">
            <button className="ghost-button" type="button" onClick={() => setIsBookModalOpen(false)}>
              Cancelar
            </button>
            <button type="submit">Cadastrar livro</button>
          </div>
        </form>
      </Modal>

      <Modal title="Editar clube" isOpen={isEditClubModalOpen} onClose={() => setIsEditClubModalOpen(false)}>
        <form onSubmit={handleUpdateClub}>
          <label>
            Título
            <input value={clubNameDraft} onChange={(event) => setClubNameDraft(event.target.value)} required />
          </label>
          <label>
            Descrição
            <textarea
              value={clubDescriptionDraft}
              onChange={(event) => setClubDescriptionDraft(event.target.value)}
              required
            />
          </label>
          <div className="form-actions">
            <button className="ghost-button" type="button" onClick={() => setIsEditClubModalOpen(false)}>
              Cancelar
            </button>
            <button type="submit">Salvar alterações</button>
          </div>
        </form>
      </Modal>

      <Modal title="Excluir clube" isOpen={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)}>
        <div className="confirmation-content">
          <p>
            Esta ação excluirá o clube, seus livros, encontros, comentários e membros. Apenas o criador do clube pode
            fazer isso.
          </p>
          <div className="form-actions">
            <button className="ghost-button" type="button" onClick={() => setIsDeleteModalOpen(false)}>
              Cancelar
            </button>
            <button className="danger-button" type="button" onClick={handleDeleteClub} disabled={isDeleting}>
              {isDeleting ? "Excluindo..." : "Excluir clube"}
            </button>
          </div>
        </div>
      </Modal>

      <Modal title="Sair do clube" isOpen={isLeaveModalOpen} onClose={() => setIsLeaveModalOpen(false)}>
        <div className="confirmation-content">
          <p>Ao sair do clube, você deixará de acessar seus livros, encontros e comentários internos.</p>
          <div className="form-actions">
            <button className="ghost-button" type="button" onClick={() => setIsLeaveModalOpen(false)}>
              Cancelar
            </button>
            <button className="danger-button" type="button" onClick={handleLeaveClub} disabled={isLeaving}>
              {isLeaving ? "Saindo..." : "Sair do clube"}
            </button>
          </div>
        </div>
      </Modal>
    </main>
  );
}
