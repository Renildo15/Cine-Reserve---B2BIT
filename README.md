# CineReserve API

Sistema de reservas de cinema com API REST built com Django e Django REST Framework.

## Índice

- [Stack](#stack)
- [Quick Start](#quick-start)
- [Configuração](#configuração)
- [API Endpoints](#api-endpoints)
- [Modelos](#modelos)
- [Tarefas Assíncronas](#tarefas-assíncronas)
- [Rate Limiting](#rate-limiting)
- [Segurança](#segurança)
- [Testes](#testes)
- [CI/CD](#cicd)
- [Docker](#docker)

## Stack

| Tecnologia | Descrição |
|-----------|-----------|
| Django 6.0 | Framework web |
| Django REST Framework | API REST |
| PostgreSQL 15 | Banco de dados |
| Redis 7 | Cache e broker Celery |
| Celery | Tarefas assíncronas |
| JWT | Autenticação |

## Quick Start

### Docker (Recomendado)

```bash
# Clonar repositório
git clone <repo-url>
cd CineReserve

# Subir containers
docker-compose up --build

# Acessar API
# http://localhost:8000
# http://localhost:8000/api/swagger/ (Swagger UI)
```

### Sem Docker

```bash
# Clonar e entrar no diretório
cd CineReserve

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependências
poetry install

# Configurar ambiente
cp .env.example .env
# Edite .env com suas configurações

# Migrar banco
python manage.py migrate

# Criar superusuário (opcional)
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

## Configuração

### Variáveis de Ambiente

```env
# Django
SECRET_KEY=sua-chave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=cine_reserve
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua_senha
DEFAULT_FROM_EMAIL=noreply@cinereserve.com
```

## API Endpoints

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/users/register` | Registrar usuário |
| POST | `/api/login/` | Login (retorna JWT) |
| POST | `/api/token/refresh/` | Renovar token |

### Filmes

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/api/movies/` | - | Listar filmes disponíveis |

### Sessões

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/api/sessions/<movie_id>/sessions/` | - | Listar sessões do filme |
| GET | `/api/sessions/<session_id>/seats/` | - | Ver mapa de assentos |

### Reservas

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| POST | `/api/sessions/<session_id>/reserve/` | JWT | Reservar assento |
| POST | `/api/sessions/<session_id>/checkout/` | JWT | Finalizar compra |

### Usuário

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/api/users/me/tickers/` | JWT | Meus ingressos futuros |
| GET | `/api/users/me/tickers/history/` | JWT | Histórico de ingressos |

### Documentação

| Endpoint | Descrição |
|----------|-----------|
| `/api/swagger/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI JSON |

## Modelos

### Movie
```
- title: string (max 255)
- description: text
- duration: integer (minutos)
- rating: string (G, PG, PG-13, R, NC-17, NR)
- is_available: boolean
- created_at: datetime
```

### Room
```
- name: string (max 100)
- total_rows: integer
- seats_per_row: integer
```

### Seat
```
- room: FK(Room)
- row: string (A-Z)
- number: integer
- unique_together: [room, row, number]
```

### Session
```
- movie: FK(Movie)
- room: FK(Room)
- start_time: datetime
- is_available: boolean
```

### Ticket
```
- user: FK(User)
- session: FK(Session)
- seat: FK(Seat)
- code: UUID (único)
- purchased_at: datetime
```

### SeatLock (Redis)
```
- key: lock:session:{session_id}:seat:{seat_id}
- value: user_id
- ttl: 600 segundos (10 min)
```

## Tarefas Assíncronas

### Celery Tasks

| Task | Descrição | Schedule |
|------|-----------|----------|
| `release_expired_seat_locks` | Libera locks expirados no Redis | A cada 60s |
| `send_ticket_confirmation` | Envia email de confirmação | Sob demanda |
| `cleanup_old_tickets` | Remove ingressos de sessões antigas | Daily |

### Comandos

```bash
# Worker (processa tasks)
celery -A cine_reserve worker -l info

# Beat (scheduler)
celery -A cine_reserve beat -l info
```

## Rate Limiting

Throttling configurado no DRF:

| Scope | Limite | Aplicação |
|-------|--------|-----------|
| `anon` | 100/min | Usuários anônimos |
| `user` | 1000/min | Usuários autenticados |
| `login` | 5/min | Endpoint de login |
| `register` | 3/min | Registro de usuários |
| `reserve` | 10/min | Reserva de assentos |

## Segurança

### Implementado
- JWT Authentication
- Rate Limiting (throttling)
- Input Validation (serializers)
- SQL Injection Prevention (Django ORM)
- CSRF Protection (middleware)
- XSS Protection
- Secure Cookies

### Headers de Segurança
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
```

## Testes

```bash
# Todos os testes
python manage.py test

# Por app
python manage.py test movie_app
python manage.py test user_app
python manage.py test session_app
python manage.py test room_app

# Com coverage
coverage run manage.py test
coverage report
```

### Apps Testados
- **movie_app**: 11 testes
- **user_app**: 15 testes
- **session_app**: 27 testes
- **room_app**: 12 testes
- **Total**: 65 testes

## CI/CD

GitHub Actions executa automaticamente:

1. **Testes** - PostgreSQL + Redis + Django tests
2. **Lint** - black + isort

### Secrets Necessários (opcional)
```
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

## Docker

### Serviços

| Serviço | Porta | Descrição |
|--------|-------|-----------|
| web | 8000 | Django app |
| db | 5432 | PostgreSQL |
| redis | 6379 | Redis |
| celery_worker | - | Worker Celery |
| celery_beat | - | Scheduler Celery |

### Comandos

```bash
# Desenvolvimento
docker-compose up --build

#后台运行
docker-compose up -d

# Parar
docker-compose down

# Rebuild
docker-compose up --build --force-recreate
```

### Estrutura de diretórios

```
CineReserve/
├── cine_reserve/          # Config Django
│   ├── settings.py
│   ├── celery.py
│   └── urls.py
├── movie_app/             # App filmes
├── user_app/              # App usuários
├── room_app/              # App salas
├── session_app/           # App sessões/reservas
│   ├── tasks.py          # Celery tasks
│   └── throttling.py     # Rate limits
├── helpers/               # Funções auxiliares
├── .github/workflows/     # CI/CD
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## API Usage Examples

### Registrar usuário
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user@test.com","password":"Pass123!","password2":"Pass123!"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"Pass123!"}'
```

### Reservar assento
```bash
curl -X POST http://localhost:8000/api/sessions/1/reserve/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"seat_id": 1}'
```

### Finalizar compra
```bash
curl -X POST http://localhost:8000/api/sessions/1/checkout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"seat_id": 1}'
```

## Licença

MIT License
