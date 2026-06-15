import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ActionMenu } from "../components/ActionMenu";
import { AutoResizeTextarea } from "../components/AutoResizeTextarea";
import { Modal } from "../components/Modal";
import { useAuth } from "../contexts/AuthContext";
import { bookService, clubService, getErrorMessage, meetingService } from "../services/api";
import type { Book, Club, Comment, Meeting, MeetingAttendee } from "../types";
import { formatMeetingDateTime, formatMeetingDay, formatMeetingTime } from "../utils/meetings";

function toDateTimeLocalValue(value: string) {
  const date = new Date(value);
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 16);
}

export function MeetingDetailsPage() {
  const { id, meetingId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [currentTime] = useState(() => new Date().toISOString());
  const [club, setClub] = useState<Club | null>(null);
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [books, setBooks] = useState<Book[]>([]);
  const [attendees, setAttendees] = useState<MeetingAttendee[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [comment, setComment] = useState("");
  const [meetingTitleDraft, setMeetingTitleDraft] = useState("");
  const [meetingScheduledForDraft, setMeetingScheduledForDraft] = useState("");
  const [meetingLocationDraft, setMeetingLocationDraft] = useState("");
  const [meetingAgendaDraft, setMeetingAgendaDraft] = useState("");
  const [meetingBookIdDraft, setMeetingBookIdDraft] = useState("");
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdatingAttendance, setIsUpdatingAttendance] = useState(false);
  const [isEditMeetingModalOpen, setIsEditMeetingModalOpen] = useState(false);
  const [isDeleteMeetingModalOpen, setIsDeleteMeetingModalOpen] = useState(false);
  const [isSavingMeeting, setIsSavingMeeting] = useState(false);
  const [isDeletingMeeting, setIsDeletingMeeting] = useState(false);

  const isAdmin = club?.current_user_role === "admin";
  const isUpcoming = useMemo(() => {
    if (!meeting) return false;
    return meeting.scheduled_for >= currentTime;
  }, [currentTime, meeting]);
  const isAttendanceConfirmed = useMemo(
    () => Boolean(user && attendees.some((attendee) => attendee.user_id === user.id)),
    [attendees, user],
  );

  function syncMeetingDrafts(currentMeeting: Meeting) {
    setMeetingTitleDraft(currentMeeting.title);
    setMeetingScheduledForDraft(toDateTimeLocalValue(currentMeeting.scheduled_for));
    setMeetingLocationDraft(currentMeeting.location);
    setMeetingAgendaDraft(currentMeeting.agenda);
    setMeetingBookIdDraft(currentMeeting.book_id ? String(currentMeeting.book_id) : "");
  }

  useEffect(() => {
    if (!id || !meetingId) return;
    const clubId = id;
    const currentMeetingId = meetingId;
    let isMounted = true;

    async function loadMeetingDetails() {
      try {
        const [clubData, meetingData, bookData, attendeeData, commentData] = await Promise.all([
          clubService.get(clubId),
          meetingService.get(currentMeetingId),
          bookService.listByClub(clubId),
          meetingService.attendees(currentMeetingId),
          meetingService.comments(currentMeetingId),
        ]);

        if (!isMounted) return;

        if (meetingData.club_id !== Number(clubId)) {
          setFeedback("Encontro não encontrado para este clube.");
          return;
        }

        setClub(clubData);
        setMeeting(meetingData);
        setBooks(bookData);
        setAttendees(attendeeData);
        setComments(commentData);
        syncMeetingDrafts(meetingData);
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

    void loadMeetingDetails();

    return () => {
      isMounted = false;
    };
  }, [id, meetingId]);

  function handleOpenEditMeetingModal() {
    if (!meeting) return;
    syncMeetingDrafts(meeting);
    setIsEditMeetingModalOpen(true);
  }

  async function handleUpdateMeeting(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!meeting || !meetingId) return;

    setFeedback("");
    setIsSavingMeeting(true);
    try {
      const updatedMeeting = await meetingService.update(meetingId, {
        title: meetingTitleDraft,
        scheduled_for: new Date(meetingScheduledForDraft).toISOString(),
        location: meetingLocationDraft,
        agenda: meetingAgendaDraft,
        book_id: meetingBookIdDraft ? Number(meetingBookIdDraft) : null,
      });
      setMeeting(updatedMeeting);
      syncMeetingDrafts(updatedMeeting);
      setFeedback("Encontro atualizado.");
      setIsEditMeetingModalOpen(false);
    } catch (err) {
      setFeedback(getErrorMessage(err));
    } finally {
      setIsSavingMeeting(false);
    }
  }

  async function handleDeleteMeeting() {
    if (!meetingId || !club) return;

    setFeedback("");
    setIsDeletingMeeting(true);
    try {
      await meetingService.remove(meetingId);
      navigate(`/clubs/${club.id}/meetings`, { replace: true });
    } catch (err) {
      setFeedback(getErrorMessage(err));
      setIsDeleteMeetingModalOpen(false);
    } finally {
      setIsDeletingMeeting(false);
    }
  }

  async function handleAddComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!meeting || !meetingId) return;

    const content = comment.trim();
    if (!content) return;

    setFeedback("");
    try {
      const createdComment = await meetingService.addComment(meetingId, content);
      setComments((current) => [...current, createdComment]);
      setMeeting((current) => (current ? { ...current, comment_count: current.comment_count + 1 } : current));
      setComment("");
      setFeedback("Comentário publicado no encontro.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  async function handleAttendanceToggle() {
    if (!meetingId || !meeting) return;

    setFeedback("");
    setIsUpdatingAttendance(true);
    try {
      const updatedAttendees = isAttendanceConfirmed
        ? await meetingService.cancelAttendance(meetingId)
        : await meetingService.confirmAttendance(meetingId);
      setAttendees(updatedAttendees);
      setMeeting((current) => (current ? { ...current, attendee_count: updatedAttendees.length } : current));
      setFeedback(isAttendanceConfirmed ? "Confirmação de presença removida." : "Presença confirmada para o encontro.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    } finally {
      setIsUpdatingAttendance(false);
    }
  }

  if (isLoading) {
    return <main className="shell">Carregando encontro...</main>;
  }

  if (!club || !meeting) {
    return <main className="shell">{feedback || "Encontro não encontrado."}</main>;
  }

  return (
    <main className="shell">
      <section className="page-heading page-heading-with-actions">
        <div>
          <p className="eyebrow">Encontro do clube</p>
          <div className="page-heading-row">
            <h1>{meeting.title}</h1>
            <div className="inline-actions">
              <Link className="button-link secondary" to={`/clubs/${club.id}/meetings`}>
                ↩️ Voltar aos encontros
              </Link>
              {isAdmin && (
                <ActionMenu>
                  <button type="button" onClick={handleOpenEditMeetingModal}>
                    ✏️ Editar encontro
                  </button>
                  <button className="danger-button" type="button" onClick={() => setIsDeleteMeetingModalOpen(true)}>
                    🗑️ Apagar encontro
                  </button>
                </ActionMenu>
              )}
            </div>
          </div>
          <p>Detalhes, pauta e registro da conversa do clube {club.name}.</p>
        </div>
      </section>

      {feedback && <p className="feedback page-feedback">{feedback}</p>}

      <section className="stack-layout">
        <section className="workspace-panel focus-panel">
          <article className="meeting-card">
            <div className="meeting-card-header">
              <div>
                <span className="status-pill">{isUpcoming ? "Próximo" : "Realizado"}</span>
                <h2>{meeting.title}</h2>
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
              <span>Criado em {formatMeetingDateTime(meeting.created_at)}</span>
              {meeting.book_id && <Link to={`/books/${meeting.book_id}`}>Livro: {meeting.book_title}</Link>}
            </div>

            <div className="meeting-agenda">
              <h3>Pauta</h3>
              <p>{meeting.agenda || "Sem pauta detalhada cadastrada para este encontro."}</p>
            </div>
          </article>
        </section>

        <section className="workspace-panel">
          <div className="section-header compact">
            <div>
              <h2>👥 Presenças confirmadas</h2>
              <p>Confirme sua participação e veja quem já sinalizou presença no encontro.</p>
            </div>
            <button type="button" onClick={handleAttendanceToggle} disabled={isUpdatingAttendance}>
              {isUpdatingAttendance
                ? "Salvando..."
                : isAttendanceConfirmed
                  ? "Cancelar presença"
                  : "Confirmar presença"}
            </button>
          </div>

          {attendees.length ? (
            <div className="item-list compact">
              {attendees.map((attendee) => (
                <div className="member-row" key={attendee.user_id}>
                  <span>{attendee.name}</span>
                  <strong>{attendee.user_id === user?.id ? "Você" : "Confirmado"}</strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Ninguém confirmou presença ainda.</p>
              <span>Use o botão acima para registrar a primeira confirmação.</span>
            </div>
          )}
        </section>

        <section className="workspace-panel">
          <div className="section-header compact">
            <div>
              <h2>💬 Comentários e registro</h2>
              <p>Use este espaço para registrar decisões, impressões e próximos passos do encontro.</p>
            </div>
            <span className="comment-count">{comments.length} comentário(s)</span>
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
              <p>Sem comentários neste encontro.</p>
              <span>Publique o primeiro registro para manter o histórico da conversa.</span>
            </div>
          )}

          <form className="comment-form" onSubmit={handleAddComment}>
            <label>
              Novo comentário
              <AutoResizeTextarea
                value={comment}
                onChange={(event) => setComment(event.target.value)}
                placeholder="Registre uma decisão, impressão ou encaminhamento do encontro."
                required
              />
            </label>
            <button type="submit">Publicar comentário</button>
          </form>
        </section>
      </section>

      <Modal title="Editar encontro" isOpen={isEditMeetingModalOpen} onClose={() => setIsEditMeetingModalOpen(false)}>
        <form onSubmit={handleUpdateMeeting}>
          <label>
            Título
            <input value={meetingTitleDraft} onChange={(event) => setMeetingTitleDraft(event.target.value)} required />
          </label>
          <label>
            Data e hora
            <input
              type="datetime-local"
              value={meetingScheduledForDraft}
              onChange={(event) => setMeetingScheduledForDraft(event.target.value)}
              required
            />
          </label>
          <label>
            Local
            <input
              value={meetingLocationDraft}
              onChange={(event) => setMeetingLocationDraft(event.target.value)}
              placeholder="Ex.: Google Meet, biblioteca, café"
            />
          </label>
          <label>
            Livro relacionado
            <select value={meetingBookIdDraft} onChange={(event) => setMeetingBookIdDraft(event.target.value)}>
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
              value={meetingAgendaDraft}
              onChange={(event) => setMeetingAgendaDraft(event.target.value)}
              placeholder="Defina os capítulos, decisões ou temas que devem orientar a conversa."
            />
          </label>
          <div className="form-actions">
            <button className="ghost-button" type="button" onClick={() => setIsEditMeetingModalOpen(false)}>
              Cancelar
            </button>
            <button type="submit" disabled={isSavingMeeting}>
              {isSavingMeeting ? "Salvando..." : "Salvar alterações"}
            </button>
          </div>
        </form>
      </Modal>

      <Modal
        title="Apagar encontro"
        isOpen={isDeleteMeetingModalOpen}
        onClose={() => setIsDeleteMeetingModalOpen(false)}
      >
        <div className="confirmation-content">
          <p>Esta ação excluirá o encontro, suas confirmações de presença e todos os comentários vinculados.</p>
          <div className="form-actions">
            <button className="ghost-button" type="button" onClick={() => setIsDeleteMeetingModalOpen(false)}>
              Cancelar
            </button>
            <button className="danger-button" type="button" onClick={handleDeleteMeeting} disabled={isDeletingMeeting}>
              {isDeletingMeeting ? "Apagando..." : "Apagar encontro"}
            </button>
          </div>
        </div>
      </Modal>
    </main>
  );
}
