# Helpdesk Application

A full-stack helpdesk ticketing system with email integration, built with FastAPI (backend) and Angular (frontend).

## Project Overview

This application provides a comprehensive helpdesk system for organizations to manage IT support tickets. It includes:

- User authentication with role-based access control
- Ticket creation and management
- Automated email notifications
- Kanban dashboard for support staff
- Audit trail for all ticket changes
- Responsive web interface

## Architecture

- **Backend**: Python FastAPI with MongoDB
- **Frontend**: Angular 17 (standalone components)
- **Database**: MongoDB
- **Email Service**: SendGrid API
- **Authentication**: JWT tokens

## Features

### Must-Have Features (Implemented)
- ✅ User registration and authentication
- ✅ Ticket submission with category and priority
- ✅ Automated email notifications on ticket creation/assignment/status change
- ✅ Role-based access control (End User, Support Staff, Administrator)
- ✅ Kanban dashboard for support staff
- ✅ Audit trail for ticket changes
- ✅ Basic reporting/dashboard statistics

### User Roles

1. **End User**: Can create tickets and view their own tickets
2. **Support Staff**: Can view all tickets, update status, assign tickets, and use Kanban view
3. **Administrator**: Full access including user management

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB (local or cloud instance)
- SendGrid API key (optional, for email notifications)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

5. Update `.env` with your configuration:
   - Set `MONGODB_URL` to your MongoDB connection string
   - Set `SECRET_KEY` to a secure random string
   - Set `SENDGRID_API_KEY` if you want email notifications (optional)
   - Set `FROM_EMAIL` to your sender email address

6. Start the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:4200`

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Create Ticket**: End users can create tickets with title, description, category, and priority
3. **View Tickets**: All users can view their tickets; support staff can view all tickets
4. **Manage Tickets**: Support staff can update ticket status, assign tickets, and add resolution notes
5. **Kanban View**: Support staff can use the Kanban board to visualize ticket workflow
6. **Dashboard**: View statistics and quick actions

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

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/kanban` - Get Kanban view data

### Users
- `GET /api/users` - List all users (admin only)
- `GET /api/users/support-staff` - List support staff
- `PATCH /api/users/{id}` - Update user (admin only)

## Email Notifications

The system sends automated emails for:
- Ticket creation (to user)
- Ticket assignment (to support staff)
- Status updates (to user)
- Ticket closure (to user)

Email notifications require a SendGrid API key. If not configured, emails will be logged to console instead.

## Development

### Backend Development
- Uses FastAPI with async/await
- MongoDB with Motor (async driver)
- JWT authentication
- Pydantic models for validation

### Frontend Development
- Angular 17 with standalone components
- TypeScript
- RxJS for reactive programming
- HTTP interceptors for authentication

## Testing

To test the application:

1. Start MongoDB
2. Start the backend server
3. Start the frontend server
4. Register a new user
5. Create a ticket
6. Login as support staff (or change user role in database)
7. View and manage tickets

## Deployment

### Backend Deployment (Render.com)
1. Connect your repository to Render
2. Set environment variables
3. Deploy as a web service
4. Use MongoDB Atlas for database

### Frontend Deployment
1. Build the application: `npm run build`
2. Deploy the `dist/helpdesk` folder to a static hosting service
3. Update `environment.ts` with production API URL

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── security.py
│   │   │   └── email.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── ticket.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── tickets.py
│   │   │   ├── users.py
│   │   │   └── dashboard.py
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   ├── guards/
│   │   │   └── interceptors/
│   │   └── environments/
│   ├── package.json
│   └── README.md
└── README.md
```

## License

This project is part of a university coursework submission.

## Author

Joseph Mc Cusker
Student ID: B00885401
Course: COM668 Computing Project

