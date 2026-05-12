import { useState } from "react";
import type { FormEvent } from "react";
import { useAuth } from "../contexts/AuthContext";
import { authService, getErrorMessage } from "../services/api";

export function ProfilePage() {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.name ?? "");
  const [bio, setBio] = useState(user?.bio ?? "");
  const [feedback, setFeedback] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback("");

    try {
      const updatedUser = await authService.updateProfile(name, bio);
      updateUser(updatedUser);
      setFeedback("Perfil atualizado.");
    } catch (err) {
      setFeedback(getErrorMessage(err));
    }
  }

  return (
    <main className="shell narrow">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Minha conta</p>
          <h1>Perfil</h1>
          <p>{user?.email}</p>
        </div>
      </section>

      <form className="panel" onSubmit={handleSubmit}>
        <label>
          Nome
          <input value={name} onChange={(event) => setName(event.target.value)} required />
        </label>
        <label>
          Bio
          <textarea value={bio} onChange={(event) => setBio(event.target.value)} />
        </label>
        <button type="submit">Salvar perfil</button>
        {feedback && <p className="feedback">{feedback}</p>}
      </form>
    </main>
  );
}
