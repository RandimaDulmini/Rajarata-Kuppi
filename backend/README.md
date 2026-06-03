# Rajarata Kuppi Backend

FastAPI backend for the Rajarata Kuppi frontend.

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@rajaratakuppi.lk | admin123 |
| Student | student@rajaratakuppi.lk | student123 |

## Run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

The first run creates `rajarata_kuppi.db` and seeds sample data.

## Main API features

- Auth: register, login, current user
- Student profile: read/update profile
- Departments and modules
- Student resources: notes, PPTs, tutorials, videos, past papers
- File upload for admin users
- GPA calculator and GPA history
- Forum posts and replies
- Notifications and mark-as-read
- Support contact messages
- Home stats
