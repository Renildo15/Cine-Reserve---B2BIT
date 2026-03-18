# CineReserve API

API REST para sistema de reservas de cinema (teste técnico).

## Stack

- Django 6.0 + DRF
- PostgreSQL 15
- Redis 7
- Docker

## Quick Start

```bash
# Com Docker
docker-compose up --build

# Sem Docker
poetry install
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## API Endpoints

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/api/movies/` | - | Listar filmes |
| GET | `/api/sessions/<id>/sessions/` | - | Listar sessões |
| GET | `/api/sessions/<id>/seats/` | - | Mapa de assentos |
| POST | `/api/sessions/<id>/reserve/` | JWT | Reservar assento |
| POST | `/api/sessions/<id>/checkout/` | JWT | Finalizar compra |
| POST | `/api/users/register` | - | Registrar |
| POST | `/api/login/` | - | Login JWT |
| GET | `/api/users/me/tickers/` | JWT | Meus ingressos |

## Testes

```bash
python manage.py test
```

## CI/CD

GitHub Actions executa:
- Testes automáticos
- Lint (black, isort)
