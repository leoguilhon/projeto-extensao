import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import { clubService, getErrorMessage } from "../services/api";
import type { Club } from "../types";

export function DashboardPage() {
  const [clubs, setClubs] = useState<Club[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadClubs() {
    setIsLoading(true);
    try {
      setClubs(await clubService.list());
    } catch (err) {
      setFeedback(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadClubs();
  }, []);

  async function handleCreateClub(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback("");

    try {
      const club = await clubService.create(name, description);
      setClubs((current) => [club, ...current]);
      setName("");
      setDescription("");
      setFeedback("Clube criado com sucesso.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  async function handleJoinClub(clubId: number) {
    setFeedback("");
    try {
      const updatedClub = await clubService.join(clubId);
      setClubs((current) => current.map((club) => (club.id === clubId ? updatedClub : club)));
      setFeedback("Ingresso no clube realizado.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  return (
    <main className="shell">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Área dos clubes</p>
          <h1>Meus Clubes</h1>
          <p>Crie clubes, visualize grupos disponíveis e acompanhe sua participação.</p>
        </div>
      </section>

      <section className="content-grid">
        <form className="panel" onSubmit={handleCreateClub}>
          <h2>Criar clube</h2>
          <label>
            Nome do clube
            <input value={name} onChange={(event) => setName(event.target.value)} required />
          </label>
          <label>
            Descrição
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} required />
          </label>
          <button type="submit">Criar clube</button>
          {feedback && <p className="feedback">{feedback}</p>}
        </form>

        <section className="panel wide-panel">
          <h2>Clubes disponíveis</h2>
          {isLoading ? (
            <p>Carregando clubes...</p>
          ) : (
            <div className="item-list">
              {clubs.map((club) => (
                <article className="list-card" key={club.id}>
                  <div>
                    <h3>{club.name}</h3>
                    <p>{club.description}</p>
                    <span>{club.member_count} participante(s)</span>
                  </div>
                  <div className="actions">
                    {club.is_member ? (
                      <Link className="button-link" to={`/clubs/${club.id}`}>
                        Abrir
                      </Link>
                    ) : (
                      <button type="button" onClick={() => handleJoinClub(club.id)}>
                        Ingressar
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
