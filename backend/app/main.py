from fastapi import FastAPI

app = FastAPI(title="LendoJuntos API")

@app.get("/")
def read_root():
    return {"message": "API do LendoJuntos rodando com sucesso"}