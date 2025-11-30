# embedded-systems-fuzzy-project
Repositório dedicado ao projeto "Sistema de Controle Fuzzy MISO para Refrigeração em Centros de Dados" da disciplina de Sistemas Embarcados (C213))

Como executar o projeto:
Utilizando UV (recomendado):
    pip install uv
    uv sync

Executando a API:
    uv run uvicorn app.main:app --reload
    A API ficará disponível em http://127.0.0.1:8000

Estrutura do projeto:
app/
 ├── api/
 │    ├── endpoints.py
 │    └── schemas.py
 ├── controllers/
 │    ├── fuzzy_controller.py
 │    ├── physical_model.py
 │    └── simulation.py
 ├── core/
 │    └── config.py
 └── main.py

Colaboradores:
Murilo de Oliveira Domingos Figueiredo
Petterson Ikaro Bento de Souza
