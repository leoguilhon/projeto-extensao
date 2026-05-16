from datetime import datetime, timezone
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


users: dict[int, dict] = {}
clubs: dict[int, dict] = {}
club_members: dict[int, dict[int, ClubRole]] = {}
books: dict[int, dict] = {}
tokens: dict[str, int] = {}

next_user_id = 1
next_club_id = 1
next_book_id = 1


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ação permitida apenas para administradores.")


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
    finished_at = now_iso() if status_value == "concluido" else None
    book = {
        "id": next_book_id,
        "club_id": club_id,
        "title": title,
        "author": author,
        "description": description,
        "status": status_value,
        "added_by": added_by,
        "created_at": now_iso(),
        "finished_at": finished_at,
    }
    books[book["id"]] = book
    next_book_id += 1
    return book


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
    create_book(
        clube["id"],
        "Orgulho e Preconceito",
        "Jane Austen",
        "Leitura atual do clube, com foco nos debates sobre relações sociais e costumes.",
        "em_leitura",
        ana["id"],
    )
    create_book(
        clube["id"],
        "Capitães da Areia",
        "Jorge Amado",
        "Leitura concluída e registrada no histórico do grupo.",
        "concluido",
        ana["id"],
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
    return [to_club_public(club, user["id"]) for club in clubs.values()]


@app.post("/clubs", response_model=ClubPublic, status_code=status.HTTP_201_CREATED)
def add_club(payload: ClubCreate, user: dict = Depends(current_user)):
    club = create_club(payload.name, payload.description, user["id"])
    return to_club_public(club, user["id"])


@app.get("/clubs/{club_id}", response_model=ClubPublic)
def get_club(club_id: int, user: dict = Depends(current_user)):
    club = clubs.get(club_id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado.")
    return to_club_public(club, user["id"])


@app.post("/clubs/{club_id}/join", response_model=ClubPublic)
def join_club(club_id: int, user: dict = Depends(current_user)):
    club = clubs.get(club_id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado.")
    club_members.setdefault(club_id, {})[user["id"]] = "membro"
    return to_club_public(club, user["id"])


@app.get("/clubs/{club_id}/members", response_model=list[ClubMemberPublic])
def list_members(club_id: int, user: dict = Depends(current_user)):
    if club_id not in clubs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado.")
    require_member(club_id, user)
    return [
        ClubMemberPublic(user_id=member_id, name=users[member_id]["name"], role=role)
        for member_id, role in club_members.get(club_id, {}).items()
    ]


@app.get("/clubs/{club_id}/books", response_model=list[BookPublic])
def list_books(club_id: int, user: dict = Depends(current_user)):
    if club_id not in clubs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado.")
    require_member(club_id, user)
    return [to_book_public(book) for book in books.values() if book["club_id"] == club_id]


@app.post("/clubs/{club_id}/books", response_model=BookPublic, status_code=status.HTTP_201_CREATED)
def add_book(club_id: int, payload: BookCreate, user: dict = Depends(current_user)):
    if club_id not in clubs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado.")
    require_admin(club_id, user)
    book = create_book(club_id, payload.title, payload.author, payload.description, payload.status, user["id"])
    return to_book_public(book)


@app.get("/books/{book_id}", response_model=BookPublic)
def get_book(book_id: int, user: dict = Depends(current_user)):
    book = books.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
    require_member(book["club_id"], user)
    return to_book_public(book)


@app.patch("/books/{book_id}/status", response_model=BookPublic)
def update_book_status(book_id: int, payload: BookStatusUpdate, user: dict = Depends(current_user)):
    book = books.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
    require_admin(book["club_id"], user)
    book["status"] = payload.status
    book["finished_at"] = now_iso() if payload.status == "concluido" else None
    return to_book_public(book)


@app.get("/clubs/{club_id}/reading-history", response_model=list[ReadingHistoryItem])
def club_reading_history(club_id: int, user: dict = Depends(current_user)):
    club = clubs.get(club_id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado.")
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
        for book in books.values()
        if book["club_id"] == club_id and book["status"] == "concluido" and book["finished_at"]
    ]
