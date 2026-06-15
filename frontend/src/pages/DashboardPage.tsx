import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import { Modal } from "../components/Modal";
import { useAuth } from "../contexts/AuthContext";
import { clubService, getErrorMessage } from "../services/api";
import type { Club } from "../types";

export function DashboardPage() {
  const { user } = useAuth();
  const [clubs, setClubs] = useState<Club[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const orderedClubs = [...clubs].sort((a, b) => Number(b.is_favorite) - Number(a.is_favorite));
  const myClubs = orderedClubs.filter((club) => club.is_member);
  const availableClubs = orderedClubs.filter((club) => !club.is_member);

  useEffect(() => {
    let isMounted = true;

    async function loadClubs() {
      try {
        const clubData = await clubService.list();
        if (isMounted) {
          setClubs(clubData);
        }
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

    void loadClubs();

    return () => {
      isMounted = false;
    };
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
      setIsCreateModalOpen(false);
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

  async function handleToggleFavorite(club: Club) {
    setFeedback("");
    try {
      const updatedClub = club.is_favorite ? await clubService.unfavorite(club.id) : await clubService.favorite(club.id);
      setClubs((current) => current.map((item) => (item.id === club.id ? updatedClub : item)));
      setFeedback(updatedClub.is_favorite ? "Clube favoritado." : "Clube removido dos favoritos.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  return (
    <main className="shell">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Área dos clubes</p>
          <h1>Clubes do livro</h1>
          <p>Crie clubes, visualize grupos disponíveis e acompanhe sua participação.</p>
        </div>
        <div className="inline-actions">
          <button type="button" onClick={() => setIsCreateModalOpen(true)}>
            Criar clube
          </button>
        </div>
      </section>

      {feedback && <p className="feedback page-feedback">{feedback}</p>}

      <section className="list-columns">
        <section className="workspace-panel">
          <div className="section-header compact">
            <div>
              <h2>Meus clubes</h2>
              <p>Grupos em que você participa.</p>
            </div>
          </div>
          {isLoading ? (
            <p>Carregando clubes...</p>
          ) : myClubs.length ? (
            <div className="item-list">
              {myClubs.map((club) => (
                <article className="resource-card" key={club.id}>
                  <div className="resource-main">
                    <h3>{club.name}</h3>
                    <p>{club.description}</p>
                    <div className="resource-meta">
                      <span>{club.member_count} participante(s)</span>
                      {club.is_favorite && <span>Favorito</span>}
                      {club.owner_id === user?.id && <span>Criador</span>}
                    </div>
                  </div>
                  <div className="card-actions">
                    <button
                      aria-label={club.is_favorite ? "Remover clube dos favoritos" : "Favoritar clube"}
                      className={`favorite-toggle ${club.is_favorite ? "active" : ""}`}
                      title={club.is_favorite ? "Remover favorito" : "Favoritar"}
                      type="button"
                      onClick={() => handleToggleFavorite(club)}
                    >
                      {club.is_favorite ? "★" : "☆"}
                    </button>
                    <Link className="button-link" to={`/clubs/${club.id}`}>
                      Abrir
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Você ainda não participa de nenhum clube.</p>
              <span>Crie um clube ou ingresse em um dos grupos disponíveis.</span>
            </div>
          )}
        </section>

        <section className="workspace-panel">
          <div className="section-header compact">
            <div>
              <h2>Clubes disponíveis</h2>
              <p>Grupos abertos para ingresso.</p>
            </div>
          </div>
          {isLoading ? (
            <p>Carregando clubes...</p>
          ) : availableClubs.length ? (
            <div className="item-list">
              {availableClubs.map((club) => (
                <article className="resource-card" key={club.id}>
                  <div className="resource-main">
                    <h3>{club.name}</h3>
                    <p>{club.description}</p>
                    <div className="resource-meta">
                      <span>{club.member_count} participante(s)</span>
                      {club.is_favorite && <span>Favorito</span>}
                    </div>
                  </div>
                  <div className="card-actions">
                    <button
                      aria-label={club.is_favorite ? "Remover clube dos favoritos" : "Favoritar clube"}
                      className={`favorite-toggle ${club.is_favorite ? "active" : ""}`}
                      title={club.is_favorite ? "Remover favorito" : "Favoritar"}
                      type="button"
                      onClick={() => handleToggleFavorite(club)}
                    >
                      {club.is_favorite ? "★" : "☆"}
                    </button>
                    <button type="button" onClick={() => handleJoinClub(club.id)}>
                      Ingressar
                    </button>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Não há clubes disponíveis no momento.</p>
              <span>Todos os clubes cadastrados já fazem parte da sua lista.</span>
            </div>
          )}
        </section>
      </section>

      <Modal title="Criar clube" isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)}>
        <form onSubmit={handleCreateClub}>
          <label>
            Nome do clube
            <input value={name} onChange={(event) => setName(event.target.value)} required />
          </label>
          <label>
            Descrição
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} required />
          </label>
          <div className="form-actions">
            <button className="ghost-button" type="button" onClick={() => setIsCreateModalOpen(false)}>
              Cancelar
            </button>
            <button type="submit">Criar clube</button>
          </div>
        </form>
      </Modal>
    </main>
  );
}
