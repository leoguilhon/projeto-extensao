from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time_utils import now_utc
from app.db.models import ClubMembership, User
from app.services.books import create_book
from app.services.clubs import create_club
from app.services.comments import create_comment
from app.services.meetings import create_meeting
from app.services.users import create_user


def seed_data(db: Session) -> None:
    if db.scalar(select(User.id).limit(1)) is not None:
        return

    seed_users = [
        ("Ana Martins", "ana@lendojuntos.test", "Organizadora de clubes de leitura contemporanea."),
        ("Beatriz Lima", "bia@lendojuntos.test", "Participante interessada em romances classicos."),
        ("Caio Ferreira", "caio@lendojuntos.test", "Leitor de ficcao cientifica e fantasia."),
        ("Daniela Souza", "daniela@lendojuntos.test", "Gosta de literatura brasileira e debates em grupo."),
        ("Eduardo Nunes", "eduardo@lendojuntos.test", "Acompanha leituras historicas e biografias."),
        ("Fernanda Rocha", "fernanda@lendojuntos.test", "Interessada em romances contemporaneos."),
        ("Gabriel Costa", "gabriel@lendojuntos.test", "Leitor frequente de classicos e ensaios."),
        ("Helena Barros", "helena@lendojuntos.test", "Participa de encontros literarios virtuais."),
        ("Igor Almeida", "igor@lendojuntos.test", "Gosta de discutir personagens e adaptacao de obras."),
        ("Juliana Castro", "juliana@lendojuntos.test", "Leitora de poesia, contos e literatura latino-americana."),
        ("Karen Oliveira", "karen@lendojuntos.test", "Explora clubes para encontrar novas leituras."),
        ("Lucas Pereira", "lucas@lendojuntos.test", "Prefere ficcao policial e narrativas curtas."),
        ("Mariana Gomes", "mariana@lendojuntos.test", "Acompanha metas pessoais de leitura."),
        ("Nicolas Ribeiro", "nicolas@lendojuntos.test", "Curioso por livros de tecnologia e sociedade."),
        ("Olivia Mendes", "olivia@lendojuntos.test", "Gosta de comentar leituras capitulo a capitulo."),
        ("Paulo Henrique", "paulo@lendojuntos.test", "Leitor de nao ficcao e divulgacao cientifica."),
        ("Renata Dias", "renata@lendojuntos.test", "Interessada em literatura de autoria feminina."),
        ("Sofia Martins", "sofia@lendojuntos.test", "Busca clubes para manter constancia de leitura."),
        ("Thiago Lopes", "thiago@lendojuntos.test", "Gosta de registrar impressoes sobre livros."),
        ("Vivian Cardoso", "vivian@lendojuntos.test", "Participa de discussoes sobre classicos modernos."),
    ]
    users = [create_user(db, name, email, "123456", bio) for name, email, bio in seed_users]
    ana = users[0]
    bia = users[1]
    clube = create_club(
        db,
        "Clube Literario Primavera",
        "Grupo voltado a leituras mensais, encontros virtuais e registro das discussoes mais importantes.",
        ana.id,
    )

    db.add_all([ClubMembership(club_id=clube.id, user_id=member.id, role="membro") for member in users[1:10]])
    db.commit()

    orgulho = create_book(
        db,
        clube.id,
        "Orgulho e Preconceito",
        "Jane Austen",
        "Leitura atual do clube, com foco nos debates sobre relacoes sociais e costumes.",
        "em_leitura",
        ana.id,
    )
    capitaes = create_book(
        db,
        clube.id,
        "Capitaes da Areia",
        "Jorge Amado",
        "Leitura concluida e registrada no historico do grupo.",
        "concluido",
        ana.id,
    )

    encontro_atual = create_meeting(
        db,
        clube.id,
        "Debate de abertura do livro do mes",
        now_utc() + timedelta(days=4),
        "Sala virtual do clube",
        "Alinhamento da leitura, divisao dos capitulos iniciais e coleta de primeiras impressoes.",
        ana.id,
        orgulho.id,
    )
    create_meeting(
        db,
        clube.id,
        "Fechamento de Capitaes da Areia",
        now_utc() - timedelta(days=9),
        "Encontro presencial no cafe da biblioteca",
        "Encerramento da leitura concluida com registro dos principais aprendizados do grupo.",
        ana.id,
        capitaes.id,
    )

    create_comment(
        db,
        clube.id,
        bia.id,
        "Gostei da escolha do livro do mes. A abertura ja rende uma conversa boa sobre expectativas.",
        book_id=orgulho.id,
    )
    create_comment(
        db,
        clube.id,
        ana.id,
        "Vamos usar este encontro para combinar o ritmo de leitura e fechar a dinamica dos comentarios.",
        meeting_id=encontro_atual.id,
    )
