from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/")
def read_root():
    return {"message": "API do LendoJuntos rodando com sucesso"}
