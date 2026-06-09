# Quick Start Guide

## Prerequisites

1. **Python 3.8+** - Install from [python.org](https://www.python.org/downloads/)
2. **Node.js 18+** - Install from [nodejs.org](https://nodejs.org/)
3. **MongoDB** - Install locally (MongoDB Community Server + optional MongoDB Compass app)

## Step-by-Step Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Create virtual environment (Mac/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
# Windows PowerShell:
Copy-Item .env.example .env

# Mac/Linux:
cp .env.example .env

# Edit .env file and update:
# - MONGODB_URL (default: mongodb://localhost:27017)
# - SECRET_KEY (generate a random string)
# - SENDGRID_API_KEY (optional, for email notifications)

# Start MongoDB (if running locally)
# Windows: mongod
# Mac/Linux: mongod or brew services start mongodb-community

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:4200

### 3. First Use

1. Open http://localhost:4200 in your browser
2. Click "Register" to create a new account
3. After registration, you'll be logged in automatically
4. Create your first ticket!

### 4. Testing Different Roles

To test support staff or administrator features:

1. Register a user normally (defaults to "end_user")
2. Connect to MongoDB and update the user's role:
   ```javascript
   // In MongoDB shell or Compass
   use helpdesk_db
   db.users.updateOne(
     { email: "your-email@example.com" },
     { $set: { role: "support_staff" } }
   )
   ```
3. Logout and login again to see the new role

Or create a support staff user directly via the API:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "support@example.com",
    "full_name": "Support Staff",
    "password": "password123",
    "role": "support_staff"
  }'
```

## Troubleshooting

### Backend Issues

- **MongoDB connection error**: Make sure MongoDB is running
- **Import errors**: Make sure virtual environment is activated
- **Port already in use**: Change port in uvicorn command: `--port 8001`

### Frontend Issues

- **Module not found**: Run `npm install` again
- **CORS errors**: Make sure backend is running and CORS is configured
- **API connection failed**: Check that backend is running on port 8000

### Email Notifications

If you don't have a SendGrid API key:
- The application will still work
- Email notifications will be logged to console instead
- To enable emails, get a free SendGrid account and add API key to `.env`

## Next Steps

- Read the full README.md for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Check the project structure in the README files

