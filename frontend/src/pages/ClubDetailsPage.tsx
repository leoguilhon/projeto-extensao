import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { Modal } from "../components/Modal";
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
  const [club, setClub] = useState<Club | null>(null);
  const [members, setMembers] = useState<ClubMember[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [history, setHistory] = useState<ReadingHistoryItem[]>([]);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<ReadingStatus>("planejado");
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(() => new Date().toISOString());
  const [isBookModalOpen, setIsBookModalOpen] = useState(false);

  const isAdmin = club?.current_user_role === "admin";
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
          {isAdmin && (
            <button type="button" onClick={() => setIsBookModalOpen(true)}>
              Cadastrar livro
            </button>
          )}
          <Link className="button-link secondary" to="/dashboard">
            Voltar
          </Link>
          <Link className="button-link" to={`/clubs/${club.id}/meetings`}>
            Ver encontros
          </Link>
        </div>
      </section>

      {feedback && <p className="feedback page-feedback">{feedback}</p>}

      <section className="stats-row">
        <div>
          <span>Participantes</span>
          <strong>{club.member_count}</strong>
        </div>
        <div>
          <span>Livros cadastrados</span>
          <strong>{books.length}</strong>
        </div>
        <div>
          <span>Encontros planejados</span>
          <strong>{meetings.length}</strong>
        </div>
        <div>
          <span>Perfil no clube</span>
          <strong>{club.current_user_role === "admin" ? "Admin" : "Membro"}</strong>
        </div>
      </section>

      <section className="content-grid">
        <section className="panel">
          <h2>Livro atual</h2>
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

        <section className="panel">
          <h2>Próximo encontro</h2>
          {nextMeeting ? (
            <article className="compact-card">
              <h3>{nextMeeting.title}</h3>
              <p>{formatDate(nextMeeting.scheduled_for)}</p>
              <span className="meta-label">{nextMeeting.location || "Local a definir"}</span>
              {nextMeeting.book_id && (
                <Link to={`/books/${nextMeeting.book_id}`}>Livro relacionado: {nextMeeting.book_title}</Link>
              )}
            </article>
          ) : (
            <div className="empty-state">
              <p>Nenhum encontro cadastrado.</p>
              <span>{isAdmin ? "Planeje o primeiro encontro do clube." : "Acompanhe aqui quando o próximo encontro for criado."}</span>
            </div>
          )}
        </section>

        <section className="panel">
          <h2>Membros</h2>
          <div className="item-list compact">
            {members.map((member) => (
              <div className="member-row" key={member.user_id}>
                <span>{member.name}</span>
                <strong>{member.role === "admin" ? "Admin" : "Membro"}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel wide-panel">
          <div className="section-header">
            <div>
              <h2>Livros do clube</h2>
              <p>Acompanhe leituras em andamento, planejadas e concluídas.</p>
            </div>
            {isAdmin && (
              <button type="button" onClick={() => setIsBookModalOpen(true)}>
                Cadastrar livro
              </button>
            )}
          </div>
          {books.length ? (
            <div className="item-list">
              {books.map((book) => (
                <article className="list-card" key={book.id}>
                  <div>
                    <h3>{book.title}</h3>
                    <p>{book.author}</p>
                    <span>{statusLabel[book.status]}</span>
                  </div>
                  <Link className="button-link secondary" to={`/books/${book.id}`}>
                    Detalhes
                  </Link>
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

        <section className="panel wide-panel">
          <div className="section-header">
            <div>
              <h2>Histórico de leituras</h2>
              <p>Registros das obras já concluídas pelo grupo.</p>
            </div>
          </div>
          {history.length ? (
            <div className="item-list">
              {history.map((item) => (
                <article className="list-card" key={item.book_id}>
                  <div>
                    <h3>{item.title}</h3>
                    <p>{item.author}</p>
                    <span>Concluído em {new Date(item.finished_at).toLocaleDateString("pt-BR")}</span>
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
    </main>
  );
}
