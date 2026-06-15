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

    seed_users = [
        ("Ana Martins", "ana@lendojuntos.test", "Organizadora de clubes de leitura contemporânea."),
        ("Beatriz Lima", "bia@lendojuntos.test", "Participante interessada em romances clássicos."),
        ("Caio Ferreira", "caio@lendojuntos.test", "Leitor de ficção científica e fantasia."),
        ("Daniela Souza", "daniela@lendojuntos.test", "Gosta de literatura brasileira e debates em grupo."),
        ("Eduardo Nunes", "eduardo@lendojuntos.test", "Acompanha leituras históricas e biografias."),
        ("Fernanda Rocha", "fernanda@lendojuntos.test", "Interessada em romances contemporâneos."),
        ("Gabriel Costa", "gabriel@lendojuntos.test", "Leitor frequente de clássicos e ensaios."),
        ("Helena Barros", "helena@lendojuntos.test", "Participa de encontros literários virtuais."),
        ("Igor Almeida", "igor@lendojuntos.test", "Gosta de discutir personagens e adaptação de obras."),
        ("Juliana Castro", "juliana@lendojuntos.test", "Leitora de poesia, contos e literatura latino-americana."),
        ("Karen Oliveira", "karen@lendojuntos.test", "Explora clubes para encontrar novas leituras."),
        ("Lucas Pereira", "lucas@lendojuntos.test", "Prefere ficção policial e narrativas curtas."),
        ("Mariana Gomes", "mariana@lendojuntos.test", "Acompanha metas pessoais de leitura."),
        ("Nicolas Ribeiro", "nicolas@lendojuntos.test", "Curioso por livros de tecnologia e sociedade."),
        ("Olivia Mendes", "olivia@lendojuntos.test", "Gosta de comentar leituras capítulo a capítulo."),
        ("Paulo Henrique", "paulo@lendojuntos.test", "Leitor de não ficção e divulgação científica."),
        ("Renata Dias", "renata@lendojuntos.test", "Interessada em literatura de autoria feminina."),
        ("Sofia Martins", "sofia@lendojuntos.test", "Busca clubes para manter constância de leitura."),
        ("Thiago Lopes", "thiago@lendojuntos.test", "Gosta de registrar impressões sobre livros."),
        ("Vivian Cardoso", "vivian@lendojuntos.test", "Participa de discussões sobre clássicos modernos."),
    ]
    users = [create_user(name, email, "123456", bio) for name, email, bio in seed_users]
    ana = users[0]
    bia = users[1]
    clube = create_club(
        "Clube Literário Primavera",
        "Grupo voltado a leituras mensais, encontros virtuais e registro das discussões mais importantes.",
        ana["id"],
    )
    for member in users[1:10]:
        store.club_members[clube["id"]][member["id"]] = "membro"

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
