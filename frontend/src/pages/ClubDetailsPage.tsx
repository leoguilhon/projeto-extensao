import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { bookService, clubService, getErrorMessage } from "../services/api";
import type { Book, Club, ClubMember, ReadingHistoryItem, ReadingStatus } from "../types";

const statusLabel: Record<ReadingStatus, string> = {
  planejado: "Planejado",
  em_leitura: "Em leitura",
  concluido: "Concluído",
};

export function ClubDetailsPage() {
  const { id } = useParams();
  const [club, setClub] = useState<Club | null>(null);
  const [members, setMembers] = useState<ClubMember[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [history, setHistory] = useState<ReadingHistoryItem[]>([]);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<ReadingStatus>("planejado");
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const isAdmin = club?.current_user_role === "admin";
  const currentBook = useMemo(() => books.find((book) => book.status === "em_leitura"), [books]);

  async function loadClub() {
    if (!id) return;
    setIsLoading(true);
    setFeedback("");
    try {
      const [clubData, memberData, bookData, historyData] = await Promise.all([
        clubService.get(id),
        clubService.members(id),
        bookService.listByClub(id),
        bookService.history(id),
      ]);
      setClub(clubData);
      setMembers(memberData);
      setBooks(bookData);
      setHistory(historyData);
    } catch (err) {
      setFeedback(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadClub();
  }, [id]);

  async function handleCreateBook(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!id) return;
    setFeedback("");

    try {
      const book = await bookService.create(id, { title, author, description, status });
      setBooks((current) => [book, ...current]);
      setTitle("");
      setAuthor("");
      setDescription("");
      setStatus("planejado");
      setFeedback("Livro cadastrado no clube.");
      if (book.status === "concluido") {
        setHistory(await bookService.history(id));
      }
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
        <Link className="button-link secondary" to="/dashboard">
          Voltar
        </Link>
      </section>

      {feedback && <p className="feedback">{feedback}</p>}

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
              <Link to={`/books/${currentBook.id}`}>Ver detalhes</Link>
            </article>
          ) : (
            <p>Nenhum livro marcado como leitura atual.</p>
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

        {isAdmin && (
          <form className="panel" onSubmit={handleCreateBook}>
            <h2>Cadastrar livro</h2>
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
            <button type="submit">Cadastrar livro</button>
          </form>
        )}

        <section className="panel wide-panel">
          <h2>Livros do clube</h2>
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
        </section>

        <section className="panel wide-panel">
          <h2>Histórico de leituras</h2>
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
            <p>Ainda não há livros concluídos neste clube.</p>
          )}
        </section>
      </section>
    </main>
  );
}
