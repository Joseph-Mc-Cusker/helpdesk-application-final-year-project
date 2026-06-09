# Helpdesk Backend (New Project)

FastAPI backend for the Helpdesk ticketing system, rewritten in a clean project structure.

## Features

- User registration and login with JWT
- Roles: `end_user`, `support_staff`, `administrator`
- Ticket creation, listing, detail, and status updates
- Ticket history / audit trail
- Dashboard statistics per user
- **Email notifications**: End users are emailed when their ticket is **resolved** (and on other status changes). Uses SendGrid when configured.

## Project Structure

```text
helpdesk_backend/
  app/
    __init__.py
    main.py
    database.py
    core/
      security.py
      email.py
    models/
      user.py
      ticket.py
    routers/
      __init__.py
      auth.py
      tickets.py
      users.py
      dashboard.py
  requirements.txt
  .env.example
  README.md
```

## Setup

From `helpdesk_backend`:

```powershell
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

Copy-Item .env.example .env
```

Then edit `.env`:

- `MONGODB_URL=mongodb://localhost:27017`
- `DATABASE_NAME=helpdesk_db`
- `SECRET_KEY=` set to a long random string
- For **resolved-ticket email notifications** to end users, set:
  - `SENDGRID_API_KEY` – your SendGrid API key
  - `FROM_EMAIL` – sender address (e.g. `noreply@yourdomain.com`)
  - If these are not set, the app logs the email to the console instead of sending.

## Run

```powershell
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

## Frontend

You can use any frontend that calls these endpoints (e.g. the `simple_frontend` folder in `Com668`):

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/tickets`
- `GET /api/tickets`
- `GET /api/tickets/{id}`
- `PATCH /api/tickets/{id}`
- `GET /api/tickets/{id}/history`
- `GET /api/dashboard/stats`
- `GET /api/users` (admin)
- `GET /api/users/support-staff`
- `PATCH /api/users/{id}` (admin)

