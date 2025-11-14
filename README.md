# Token Usage Dashboard

A secure, interactive dashboard for authenticated users to visualize and analyze their token consumption over time. The dashboard features responsive, accessible charts with selectable timeframes, detailed breakdowns, strict access controls, and audit logging. Built with Streamlit (frontend), FastAPI (backend), and PostgreSQL.

---

## Features

- **Interactive Token Usage Charts**: Visualize your token consumption over time with responsive, accessible Plotly charts.
- **Timeframe & Date Range Filters**: Select daily, weekly, monthly, or custom date ranges.
- **Detailed Activity Breakdowns**: Hover/click for per-activity token usage details.
- **Strict RBAC & Security**: Only authenticated users can view their own data; all data is transmitted securely (TLS).
- **Audit Logging**: All dashboard access and data retrieval are logged for compliance.
- **Performance**: Charts render within 2 seconds, even for large datasets.
- **Accessibility**: Fully WCAG 2.1 AA compliant UI.

---

## Architecture

- **Frontend**: Streamlit + Plotly + Streamlit Components
- **Backend**: FastAPI (REST API), SQLAlchemy ORM
- **Database**: PostgreSQL (time-series optimized)
- **Authentication**: JWT (python-jose), RBAC (streamlit-authenticator)
- **Audit Logging**: Loguru
- **Containerization**: Docker

---

## Quickstart

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 13+

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/token-usage-dashboard.git
cd token-usage-dashboard
```

### 2. Environment Configuration

Create a `.env` file (see `.env.example`) with your secrets and DB connection info.

### 3. Build and Run with Docker

```bash
docker build --target backend -t token-usage-backend .
docker build --target frontend -t token-usage-frontend .
# Or use docker-compose for multi-service orchestration (recommended)
docker-compose up
```

### 4. Database Migration

Run the migration to create the `token_usage` table:

```bash
docker exec -it <postgres_container> psql -U <user> -d <db> -f backend/db/migrations/2024_create_token_usage_table.sql
```

### 5. Access the Dashboard

- **Frontend**: [http://localhost:8501](http://localhost:8501)
- **Backend API**: [https://localhost:8000/docs](https://localhost:8000/docs)

---

## Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Backend (FastAPI)

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

---

## Testing

### Backend

```bash
pytest backend/tests/
```

### Frontend

```bash
pytest frontend/tests/
```

---

## Security & Compliance

- All endpoints require JWT authentication and RBAC.
- All data transmissions are encrypted (TLS).
- Dashboard access and data retrieval are logged (Loguru).
- No user can access or view other users’ token data.
- Charts and UI meet WCAG 2.1 AA accessibility standards.

---

## API Documentation

- OpenAPI/Swagger: [backend/docs/openapi.yaml](backend/docs/openapi.yaml)
- Live docs: [https://localhost:8000/docs](https://localhost:8000/docs)

---

## Project Structure

```
.
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── middleware/
│   ├── models/
│   ├── db/
│   ├── docs/
│   └── tests/
├── frontend/
│   ├── app.py
│   ├── components/
│   ├── api/
│   ├── auth/
│   └── tests/
├── Dockerfile
├── requirements.txt
├── README.md
└── ...
```

---

## Accessibility

- All interactive elements are keyboard-accessible.
- Charts and UI use ARIA attributes and semantic HTML.
- Color contrast and focus indicators meet WCAG 2.1 AA.

---

## License

[MIT License](LICENSE)

---

## Maintainers

- [Your Name](mailto:your.email@example.com)
- [Your Organization](https://your-org.com)

---

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Plotly](https://plotly.com/python/)
- [Loguru](https://github.com/Delgan/loguru)
- [python-jose](https://python-jose.readthedocs.io/)
- [streamlit-authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)

---