# Rajarata Kuppi Full Stack Project

This project has two separate parts:

```text
rajarata_kuppi_fullstack/
├── frontend/
└── backend/
```

## 1. Start the FastAPI backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger API docs:

```text
http://127.0.0.1:8000/docs
```

## 2. Start the frontend

Open another terminal:

```bash
cd frontend
python -m http.server 5500
```

Frontend:

```text
http://127.0.0.1:5500
```

## Demo login

Admin:

```text
admin@rajaratakuppi.lk
admin123
```

Student:

```text
student@rajaratakuppi.lk
student123
```

## Important

This is a development-ready project. Before real deployment, change `SECRET_KEY`, configure a production database, protect admin routes properly, and store uploaded files in a safer storage service.
