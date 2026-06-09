from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, tickets, users, dashboard
from app.database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Helpdesk API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Allow any origin so we can use a simple static HTML frontend
    # served from a different port or tool (e.g. Live Server).
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()


@app.get("/")
async def root():
    return {"message": "Helpdesk API is running"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

