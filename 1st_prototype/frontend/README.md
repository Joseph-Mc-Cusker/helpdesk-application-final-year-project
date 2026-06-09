# Helpdesk Frontend

Angular frontend for the Helpdesk application.

## Setup

1. Install Node.js and npm if not already installed.

2. Install dependencies:
```bash
npm install
```

3. Make sure the backend API is running on `http://localhost:8000` (or update `src/environments/environment.ts`).

4. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:4200`

## Features

- User authentication (login/register)
- Role-based access control
- Dashboard with statistics
- Ticket creation and management
- Kanban board view for support staff
- Admin panel (administrator only)
- Responsive design

## User Roles

- **End User**: Can create tickets and view their own tickets
- **Support Staff**: Can view all tickets, update status, and use Kanban view
- **Administrator**: Full access including user management

## Project Structure

- `src/app/components/` - Angular components
- `src/app/services/` - Services for API communication
- `src/app/guards/` - Route guards for authentication and authorization
- `src/app/interceptors/` - HTTP interceptors for adding auth tokens

