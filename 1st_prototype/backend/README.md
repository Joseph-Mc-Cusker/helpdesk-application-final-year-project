# Helpdesk Backend API

FastAPI backend for the Helpdesk application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
- `MONGODB_URL`: MongoDB connection string
- `DATABASE_NAME`: Database name
- `SECRET_KEY`: Secret key for JWT tokens
- `SENDGRID_API_KEY`: SendGrid API key for email notifications
- `FROM_EMAIL`: Email address to send from
- `FRONTEND_URL`: Frontend URL for email links

4. Make sure MongoDB is running locally or update `MONGODB_URL` to point to your MongoDB instance.

5. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation is available at `http://localhost:8000/docs`

## Features

- User authentication with JWT
- Role-based access control (End User, Support Staff, Administrator)
- Ticket management (create, update, assign, close)
- Email notifications via SendGrid
- Audit trail for ticket changes
- Dashboard statistics
- Kanban view for support staff

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user info

### Tickets
- `POST /api/tickets` - Create new ticket
- `GET /api/tickets` - List tickets (with filters)
- `GET /api/tickets/{id}` - Get ticket details
- `PATCH /api/tickets/{id}` - Update ticket
- `GET /api/tickets/{id}/history` - Get ticket audit trail

### Users
- `GET /api/users` - List all users (admin only)
- `GET /api/users/support-staff` - List support staff
- `PATCH /api/users/{id}` - Update user (admin only)

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/kanban` - Get Kanban view data

