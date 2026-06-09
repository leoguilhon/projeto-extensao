from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="LendoJuntos API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ReadingStatus = Literal["planejado", "em_leitura", "concluido"]
ClubRole = Literal["admin", "membro"]


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=80)


class UserLogin(BaseModel):
    email: str = Field(min_length=5, max_length=120)
    password: str


class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    bio: str = ""


class UserUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    bio: str = Field(default="", max_length=240)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class ClubCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=8, max_length=500)


class ClubPublic(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: str
    member_count: int
    current_user_role: ClubRole | None = None
    is_member: bool = False


class ClubMemberPublic(BaseModel):
    user_id: int
    name: str
    role: ClubRole


class BookCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    author: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    status: ReadingStatus = "planejado"


class BookStatusUpdate(BaseModel):
    status: ReadingStatus


class BookPublic(BaseModel):
    id: int
    club_id: int
    title: str
    author: str
    description: str = ""
    status: ReadingStatus
    added_by: int
    created_at: str
    finished_at: str | None = None


class ReadingHistoryItem(BaseModel):
    club_id: int
    club_name: str
    book_id: int
    title: str
    author: str
    finished_at: str


class MeetingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    scheduled_for: datetime
    location: str = Field(default="", max_length=120)
    agenda: str = Field(default="", max_length=500)
    book_id: int | None = None


class MeetingPublic(BaseModel):
    id: int
    club_id: int
    title: str
    scheduled_for: str
    location: str = ""
    agenda: str = ""
    book_id: int | None = None
    book_title: str | None = None
    created_by: int
    created_at: str
    comment_count: int = 0


class CommentCreate(BaseModel):
    content: str = Field(min_length=2, max_length=500)


class CommentPublic(BaseModel):
    id: int
    club_id: int
    user_id: int
    user_name: str
    content: str
    created_at: str
    book_id: int | None = None
    meeting_id: int | None = None


users: dict[int, dict] = {}
clubs: dict[int, dict] = {}
club_members: dict[int, dict[int, ClubRole]] = {}
books: dict[int, dict] = {}
meetings: dict[int, dict] = {}
comments: dict[int, dict] = {}
tokens: dict[str, int] = {}

next_user_id = 1
next_club_id = 1
next_book_id = 1
next_meeting_id = 1
next_comment_id = 1


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def to_user_public(user: dict) -> UserPublic:
    return UserPublic(id=user["id"], name=user["name"], email=user["email"], bio=user.get("bio", ""))


def to_club_public(club: dict, current_user_id: int | None = None) -> ClubPublic:
    members = club_members.get(club["id"], {})
    role = members.get(current_user_id) if current_user_id else None
    return ClubPublic(
        id=club["id"],
        name=club["name"],
        description=club["description"],
        owner_id=club["owner_id"],
        created_at=club["created_at"],
        member_count=len(members),
        current_user_role=role,
        is_member=current_user_id in members if current_user_id else False,
    )


def to_book_public(book: dict) -> BookPublic:
    return BookPublic(**book)


def to_meeting_public(meeting: dict) -> MeetingPublic:
    linked_book = books.get(meeting["book_id"]) if meeting.get("book_id") else None
    return MeetingPublic(
        **meeting,
        book_title=linked_book["title"] if linked_book else None,
        comment_count=sum(1 for comment in comments.values() if comment.get("meeting_id") == meeting["id"]),
    )


def to_comment_public(comment: dict) -> CommentPublic:
    return CommentPublic(
        **comment,
        user_name=users[comment["user_id"]]["name"],
    )


def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de acesso ausente.")

    token = authorization.split(" ", 1)[1]
    user_id = tokens.get(token)
    if not user_id or user_id not in users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de acesso inválido.")

    return users[user_id]


def require_member(club_id: int, user: dict) -> ClubRole:
    role = club_members.get(club_id, {}).get(user["id"])
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não participa deste clube.")
    return role


def require_admin(club_id: int, user: dict) -> None:
    if require_member(club_id, user) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação permitida apenas para administradores.",
        )


def get_club_or_404(club_id: int) -> dict:
    club = clubs.get(club_id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado.")
    return club


def get_book_or_404(book_id: int) -> dict:
    book = books.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
    return book


def get_meeting_or_404(meeting_id: int) -> dict:
    meeting = meetings.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encontro não encontrado.")
    return meeting


def ensure_book_belongs_to_club(book_id: int, club_id: int) -> dict:
    book = get_book_or_404(book_id)
    if book["club_id"] != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O livro informado não pertence a este clube.",
        )
    return book


def ensure_single_current_book(club_id: int, active_book_id: int) -> None:
    for book in books.values():
        if book["club_id"] == club_id and book["id"] != active_book_id and book["status"] == "em_leitura":
            book["status"] = "planejado"
            book["finished_at"] = None


def sorted_club_books(club_id: int) -> list[dict]:
    status_order = {"em_leitura": 0, "planejado": 1, "concluido": 2}
    return sorted(
        (book for book in books.values() if book["club_id"] == club_id),
        key=lambda item: (status_order[item["status"]], item["created_at"]),
    )


def create_user(name: str, email: str, password: str, bio: str = "") -> dict:
    global next_user_id
    user = {
        "id": next_user_id,
        "name": name,
        "email": email.lower(),
        "password_hash": hash_password(password),
        "bio": bio,
    }
    users[user["id"]] = user
    next_user_id += 1
    return user


def create_club(name: str, description: str, owner_id: int) -> dict:
    global next_club_id
    club = {
        "id": next_club_id,
        "name": name,
        "description": description,
        "owner_id": owner_id,
        "created_at": now_iso(),
    }
    clubs[club["id"]] = club
    club_members[club["id"]] = {owner_id: "admin"}
    next_club_id += 1
    return club


def create_book(club_id: int, title: str, author: str, description: str, status_value: ReadingStatus, added_by: int) -> dict:
    global next_book_id
    book = {
        "id": next_book_id,
        "club_id": club_id,
        "title": title,
        "author": author,
        "description": description,
        "status": status_value,
        "added_by": added_by,
        "created_at": now_iso(),
        "finished_at": now_iso() if status_value == "concluido" else None,
    }
    books[book["id"]] = book
    next_book_id += 1
    if status_value == "em_leitura":
        ensure_single_current_book(club_id, book["id"])
    return book


def create_meeting(
    club_id: int,
    title: str,
    scheduled_for: str,
    location: str,
    agenda: str,
    created_by: int,
    book_id: int | None = None,
) -> dict:
    global next_meeting_id
    meeting = {
        "id": next_meeting_id,
        "club_id": club_id,
        "title": title,
        "scheduled_for": scheduled_for,
        "location": location,
        "agenda": agenda,
        "book_id": book_id,
        "created_by": created_by,
        "created_at": now_iso(),
    }
    meetings[meeting["id"]] = meeting
    next_meeting_id += 1
    return meeting


def create_comment(
    club_id: int,
    user_id: int,
    content: str,
    *,
    book_id: int | None = None,
    meeting_id: int | None = None,
) -> dict:
    global next_comment_id
    comment = {
        "id": next_comment_id,
        "club_id": club_id,
        "user_id": user_id,
        "content": content,
        "created_at": now_iso(),
        "book_id": book_id,
        "meeting_id": meeting_id,
    }
    comments[comment["id"]] = comment
    next_comment_id += 1
    return comment


def seed_data() -> None:
    if users:
        return

    ana = create_user("Ana Martins", "ana@lendojuntos.test", "123456", "Organizadora de clubes de leitura contemporânea.")
    bia = create_user("Beatriz Lima", "bia@lendojuntos.test", "123456", "Participante interessada em romances clássicos.")
    clube = create_club(
        "Clube Literário Primavera",
        "Grupo voltado a leituras mensais, encontros virtuais e registro das discussões mais importantes.",
        ana["id"],
    )
    club_members[clube["id"]][bia["id"]] = "membro"

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
        normalize_datetime(datetime.now(timezone.utc) + timedelta(days=4)),
        "Sala virtual do clube",
        "Alinhamento da leitura, divisão dos capítulos iniciais e coleta de primeiras impressões.",
        ana["id"],
        orgulho["id"],
    )
    create_meeting(
        clube["id"],
        "Fechamento de Capitães da Areia",
        normalize_datetime(datetime.now(timezone.utc) - timedelta(days=9)),
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


seed_data()


@app.get("/")
def read_root():
    return {"message": "API do LendoJuntos rodando com sucesso"}


@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate):
    if any(user["email"] == payload.email.lower() for user in users.values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado.")

    user = create_user(payload.name, payload.email, payload.password)
    token = str(uuid4())
    tokens[token] = user["id"]
    return AuthResponse(access_token=token, user=to_user_public(user))


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: UserLogin):
    password_hash = hash_password(payload.password)
    user = next((item for item in users.values() if item["email"] == payload.email.lower()), None)
    if not user or user["password_hash"] != password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos.")

    token = str(uuid4())
    tokens[token] = user["id"]
    return AuthResponse(access_token=token, user=to_user_public(user))


@app.get("/users/me", response_model=UserPublic)
def get_profile(user: dict = Depends(current_user)):
    return to_user_public(user)


@app.put("/users/me", response_model=UserPublic)
def update_profile(payload: UserUpdate, user: dict = Depends(current_user)):
    user["name"] = payload.name
    user["bio"] = payload.bio
    return to_user_public(user)


@app.get("/clubs", response_model=list[ClubPublic])
def list_clubs(user: dict = Depends(current_user)):
    ordered_clubs = sorted(clubs.values(), key=lambda item: item["created_at"], reverse=True)
    return [to_club_public(club, user["id"]) for club in ordered_clubs]


@app.post("/clubs", response_model=ClubPublic, status_code=status.HTTP_201_CREATED)
def add_club(payload: ClubCreate, user: dict = Depends(current_user)):
    club = create_club(payload.name, payload.description, user["id"])
    return to_club_public(club, user["id"])


@app.get("/clubs/{club_id}", response_model=ClubPublic)
def get_club(club_id: int, user: dict = Depends(current_user)):
    club = get_club_or_404(club_id)
    return to_club_public(club, user["id"])


@app.post("/clubs/{club_id}/join", response_model=ClubPublic)
def join_club(club_id: int, user: dict = Depends(current_user)):
    club = get_club_or_404(club_id)
    members = club_members.setdefault(club_id, {})
    if user["id"] in members:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já participa deste clube.")
    members[user["id"]] = "membro"
    return to_club_public(club, user["id"])


@app.get("/clubs/{club_id}/members", response_model=list[ClubMemberPublic])
def list_members(club_id: int, user: dict = Depends(current_user)):
    get_club_or_404(club_id)
    require_member(club_id, user)
    return [
        ClubMemberPublic(user_id=member_id, name=users[member_id]["name"], role=role)
        for member_id, role in sorted(
            club_members.get(club_id, {}).items(),
            key=lambda item: (0 if item[1] == "admin" else 1, users[item[0]]["name"].lower()),
        )
    ]


@app.get("/clubs/{club_id}/books", response_model=list[BookPublic])
def list_books(club_id: int, user: dict = Depends(current_user)):
    get_club_or_404(club_id)
    require_member(club_id, user)
    return [to_book_public(book) for book in sorted_club_books(club_id)]


@app.post("/clubs/{club_id}/books", response_model=BookPublic, status_code=status.HTTP_201_CREATED)
def add_book(club_id: int, payload: BookCreate, user: dict = Depends(current_user)):
    get_club_or_404(club_id)
    require_admin(club_id, user)
    book = create_book(club_id, payload.title, payload.author, payload.description, payload.status, user["id"])
    return to_book_public(book)


@app.get("/books/{book_id}", response_model=BookPublic)
def get_book(book_id: int, user: dict = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_member(book["club_id"], user)
    return to_book_public(book)


@app.patch("/books/{book_id}/status", response_model=BookPublic)
def update_book_status(book_id: int, payload: BookStatusUpdate, user: dict = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_admin(book["club_id"], user)
    book["status"] = payload.status
    book["finished_at"] = now_iso() if payload.status == "concluido" else None
    if payload.status == "em_leitura":
        ensure_single_current_book(book["club_id"], book["id"])
    return to_book_public(book)


@app.get("/books/{book_id}/comments", response_model=list[CommentPublic])
def list_book_comments(book_id: int, user: dict = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_member(book["club_id"], user)
    return [
        to_comment_public(comment)
        for comment in sorted(
            (item for item in comments.values() if item.get("book_id") == book_id),
            key=lambda item: item["created_at"],
        )
    ]


@app.post("/books/{book_id}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
def add_book_comment(book_id: int, payload: CommentCreate, user: dict = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_member(book["club_id"], user)
    comment = create_comment(book["club_id"], user["id"], payload.content, book_id=book_id)
    return to_comment_public(comment)


@app.get("/books/{book_id}/meetings", response_model=list[MeetingPublic])
def list_book_meetings(book_id: int, user: dict = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_member(book["club_id"], user)
    return [
        to_meeting_public(meeting)
        for meeting in sorted(
            (item for item in meetings.values() if item.get("book_id") == book_id),
            key=lambda item: item["scheduled_for"],
        )
    ]


@app.get("/clubs/{club_id}/meetings", response_model=list[MeetingPublic])
def list_meetings(club_id: int, user: dict = Depends(current_user)):
    get_club_or_404(club_id)
    require_member(club_id, user)
    return [
        to_meeting_public(meeting)
        for meeting in sorted(
            (item for item in meetings.values() if item["club_id"] == club_id),
            key=lambda item: item["scheduled_for"],
        )
    ]


@app.post("/clubs/{club_id}/meetings", response_model=MeetingPublic, status_code=status.HTTP_201_CREATED)
def add_meeting(club_id: int, payload: MeetingCreate, user: dict = Depends(current_user)):
    get_club_or_404(club_id)
    require_admin(club_id, user)
    if payload.book_id is not None:
        ensure_book_belongs_to_club(payload.book_id, club_id)
    meeting = create_meeting(
        club_id,
        payload.title,
        normalize_datetime(payload.scheduled_for),
        payload.location,
        payload.agenda,
        user["id"],
        payload.book_id,
    )
    return to_meeting_public(meeting)


@app.get("/meetings/{meeting_id}/comments", response_model=list[CommentPublic])
def list_meeting_comments(meeting_id: int, user: dict = Depends(current_user)):
    meeting = get_meeting_or_404(meeting_id)
    require_member(meeting["club_id"], user)
    return [
        to_comment_public(comment)
        for comment in sorted(
            (item for item in comments.values() if item.get("meeting_id") == meeting_id),
            key=lambda item: item["created_at"],
        )
    ]


@app.post("/meetings/{meeting_id}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
def add_meeting_comment(meeting_id: int, payload: CommentCreate, user: dict = Depends(current_user)):
    meeting = get_meeting_or_404(meeting_id)
    require_member(meeting["club_id"], user)
    comment = create_comment(meeting["club_id"], user["id"], payload.content, meeting_id=meeting_id)
    return to_comment_public(comment)


@app.get("/clubs/{club_id}/reading-history", response_model=list[ReadingHistoryItem])
def club_reading_history(club_id: int, user: dict = Depends(current_user)):
    club = get_club_or_404(club_id)
    require_member(club_id, user)
    return [
        ReadingHistoryItem(
            club_id=club_id,
            club_name=club["name"],
            book_id=book["id"],
            title=book["title"],
            author=book["author"],
            finished_at=book["finished_at"],
        )
        for book in sorted_club_books(club_id)
        if book["status"] == "concluido" and book["finished_at"]
    ]
