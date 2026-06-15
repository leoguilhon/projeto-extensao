import { useEffect, useMemo, useState } from "react";
import type { FormEvent, KeyboardEvent, MouseEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Modal } from "../components/Modal";
import { bookService, clubService, getErrorMessage, meetingService } from "../services/api";
import type { Book, Club, Meeting } from "../types";
import { formatMeetingDay, formatMeetingTime, getMeetingDetailsPath, isInteractiveElementTarget } from "../utils/meetings";

export function MeetingsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [club, setClub] = useState<Club | null>(null);
  const [books, setBooks] = useState<Book[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [title, setTitle] = useState("");
  const [scheduledFor, setScheduledFor] = useState("");
  const [location, setLocation] = useState("");
  const [agenda, setAgenda] = useState("");
  const [bookId, setBookId] = useState("");
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(() => new Date().toISOString());
  const [isMeetingModalOpen, setIsMeetingModalOpen] = useState(false);

  const isAdmin = club?.current_user_role === "admin";
  const upcomingMeetings = useMemo(
    () =>
      meetings
        .filter((meeting) => meeting.scheduled_for >= currentTime)
        .sort((a, b) => new Date(a.scheduled_for).getTime() - new Date(b.scheduled_for).getTime()),
    [currentTime, meetings],
  );
  const pastMeetings = useMemo(
    () =>
      meetings
        .filter((meeting) => meeting.scheduled_for < currentTime)
        .sort((a, b) => new Date(b.scheduled_for).getTime() - new Date(a.scheduled_for).getTime()),
    [currentTime, meetings],
  );

  useEffect(() => {
    if (!id) return;
    const clubId = id;
    let isMounted = true;

    async function loadMeetingsPage() {
      try {
        const [clubData, bookData, meetingData] = await Promise.all([
          clubService.get(clubId),
          bookService.listByClub(clubId),
          meetingService.listByClub(clubId),
        ]);

        if (!isMounted) return;
        setClub(clubData);
        setBooks(bookData);
        setMeetings(meetingData);
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

    void loadMeetingsPage();

    return () => {
      isMounted = false;
    };
  }, [id]);

  async function handleCreateMeeting(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!id) return;
    setFeedback("");

    try {
      const createdMeeting = await meetingService.create(id, {
        title,
        scheduled_for: new Date(scheduledFor).toISOString(),
        location,
        agenda,
        book_id: bookId ? Number(bookId) : null,
      });
      setMeetings((current) =>
        [...current, createdMeeting].sort((a, b) => new Date(a.scheduled_for).getTime() - new Date(b.scheduled_for).getTime()),
      );
      setCurrentTime(new Date().toISOString());
      setTitle("");
      setScheduledFor("");
      setLocation("");
      setAgenda("");
      setBookId("");
      setFeedback("Encontro criado com sucesso.");
      setIsMeetingModalOpen(false);
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

  function renderMeetingCard(meeting: Meeting) {
    const meetingDetailsPath = getMeetingDetailsPath(meeting.club_id, meeting.id);

    return (
      <article
        className="meeting-card clickable-card"
        key={meeting.id}
        role="link"
        tabIndex={0}
        onClick={(event) => handleMeetingCardClick(event, meetingDetailsPath)}
        onKeyDown={(event) => handleMeetingCardKeyDown(event, meetingDetailsPath)}
      >
        <div className="meeting-card-header">
          <div>
            <span className="status-pill">{meeting.scheduled_for >= currentTime ? "Próximo" : "Realizado"}</span>
            <h3>{meeting.title}</h3>
            <div className="meeting-schedule">
              <span>📅 {formatMeetingDay(meeting.scheduled_for)}</span>
              <span>⏰ {formatMeetingTime(meeting.scheduled_for)}</span>
            </div>
          </div>
          <div className="meeting-card-aside">
            <span className="comment-count">{meeting.attendee_count} presença(s)</span>
            <span className="comment-count">{meeting.comment_count} comentário(s)</span>
          </div>
        </div>

        <div className="meeting-meta">
          <span>📍 {meeting.location || "Local a definir"}</span>
          {meeting.book_id && <Link to={`/books/${meeting.book_id}`}>Livro: {meeting.book_title}</Link>}
        </div>

        <p>{meeting.agenda || "Sem pauta detalhada cadastrada para este encontro."}</p>
      </article>
    );
  }

  if (isLoading) {
    return <main className="shell">Carregando encontros...</main>;
  }

  if (!club) {
    return <main className="shell">{feedback || "Clube não encontrado."}</main>;
  }

  return (
    <main className="shell">
      <section className="page-heading page-heading-with-actions">
        <div>
          <p className="eyebrow">Semana 13</p>
          <div className="page-heading-row">
            <h1>Encontros do {club.name}</h1>
            <div className="inline-actions">
              {isAdmin ? (
                <>
                  <button type="button" onClick={() => setIsMeetingModalOpen(true)}>
                    📍 Criar encontro
                  </button>
                  <Link className="button-link secondary" to={`/clubs/${club.id}`}>
                    ↩️ Voltar ao clube
                  </Link>
                </>
              ) : (
                <Link className="button-link secondary" to={`/clubs/${club.id}`}>
                  Voltar ao clube
                </Link>
              )}
            </div>
          </div>
          <p>Planeje reuniões do clube, vincule livros às conversas e abra cada encontro em uma página exclusiva.</p>
        </div>
      </section>

      {feedback && <p className="feedback page-feedback">{feedback}</p>}

      {!isAdmin && (
        <div className="notice-box page-feedback">
          Apenas administradores do clube podem cadastrar novos encontros. Como membro, você ainda pode acompanhar e comentar as discussões.
        </div>
      )}

      <section className="stack-layout">
        <section className="workspace-panel focus-panel">
          <div className="section-header compact">
            <div>
              <h2>📍 Próximos encontros</h2>
              <p>Organização das próximas leituras e debates do clube.</p>
            </div>
          </div>
          {upcomingMeetings.length ? (
            <div className="item-list">{upcomingMeetings.map(renderMeetingCard)}</div>
          ) : (
            <div className="empty-state">
              <p>Nenhum próximo encontro planejado.</p>
              <span>{isAdmin ? "Use o botão Criar encontro para alinhar a próxima etapa da leitura." : "Aguarde o planejamento do próximo encontro do clube."}</span>
            </div>
          )}
        </section>

        <section className="workspace-panel muted-panel">
          <div className="section-header compact">
            <div>
              <h2>🗓️ Histórico de encontros</h2>
              <p>Registros das conversas já realizadas pelo grupo.</p>
            </div>
          </div>
          {pastMeetings.length ? (
            <div className="item-list">{pastMeetings.map(renderMeetingCard)}</div>
          ) : (
            <div className="empty-state">
              <p>O histórico de encontros ainda está vazio.</p>
              <span>Assim que um encontro passar, ele será mantido aqui como referência do clube.</span>
            </div>
          )}
        </section>
      </section>

      <Modal title="Criar encontro" isOpen={isMeetingModalOpen} onClose={() => setIsMeetingModalOpen(false)}>
        <form onSubmit={handleCreateMeeting}>
          <label>
            Título
            <input value={title} onChange={(event) => setTitle(event.target.value)} required />
          </label>
          <label>
            Data e hora
            <input
              type="datetime-local"
              value={scheduledFor}
              onChange={(event) => setScheduledFor(event.target.value)}
              required
            />
          </label>
          <label>
            Local
            <input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Ex.: Google Meet, biblioteca, café" />
          </label>
          <label>
            Livro relacionado
            <select value={bookId} onChange={(event) => setBookId(event.target.value)}>
              <option value="">Sem vínculo específico</option>
              {books.map((book) => (
                <option key={book.id} value={book.id}>
                  {book.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Pauta
            <textarea
              value={agenda}
              onChange={(event) => setAgenda(event.target.value)}
              placeholder="Defina os capítulos, decisões ou temas que devem orientar a conversa."
            />
          </label>
          <div className="form-actions">
            <button className="ghost-button" type="button" onClick={() => setIsMeetingModalOpen(false)}>
              Cancelar
            </button>
            <button type="submit">Criar encontro</button>
          </div>
        </form>
      </Modal>
    </main>
  );
}
