from datetime import datetime, timedelta, timezone

from app.db.memory import store
from app.services.books import create_book
from app.services.clubs import create_club
from app.services.comments import create_comment
from app.services.meetings import create_meeting
from app.services.users import create_user


def seed_data() -> None:
    if store.users:
        return

    ana = create_user("Ana Martins", "ana@lendojuntos.test", "123456", "Organizadora de clubes de leitura contemporânea.")
    bia = create_user("Beatriz Lima", "bia@lendojuntos.test", "123456", "Participante interessada em romances clássicos.")
    clube = create_club(
        "Clube Literário Primavera",
        "Grupo voltado a leituras mensais, encontros virtuais e registro das discussões mais importantes.",
        ana["id"],
    )
    store.club_members[clube["id"]][bia["id"]] = "membro"

    orgulho = create_book(
        clube["id"],
        "Orgulho e Preconceito",
        "Jane Austen",
        "Leitura atual do clube, com foco nos debates sobre relações sociais e costumes.",
        "em_leitura",
        ana["id"],
    )
    capitaes = create_book(
        clube["id"],
        "Capitães da Areia",
        "Jorge Amado",
        "Leitura concluída e registrada no histórico do grupo.",
        "concluido",
        ana["id"],
    )

    encontro_atual = create_meeting(
        clube["id"],
        "Debate de abertura do livro do mês",
        datetime.now(timezone.utc) + timedelta(days=4),
        "Sala virtual do clube",
        "Alinhamento da leitura, divisão dos capítulos iniciais e coleta de primeiras impressões.",
        ana["id"],
        orgulho["id"],
    )
    create_meeting(
        clube["id"],
        "Fechamento de Capitães da Areia",
        datetime.now(timezone.utc) - timedelta(days=9),
        "Encontro presencial no café da biblioteca",
        "Encerramento da leitura concluída com registro dos principais aprendizados do grupo.",
        ana["id"],
        capitaes["id"],
    )

    create_comment(
        clube["id"],
        bia["id"],
        "Gostei da escolha do livro do mês. A abertura já rende uma conversa boa sobre expectativas.",
        book_id=orgulho["id"],
    )
    create_comment(
        clube["id"],
        ana["id"],
        "Vamos usar este encontro para combinar o ritmo de leitura e fechar a dinâmica dos comentários.",
        meeting_id=encontro_atual["id"],
    )
