from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_mongo_connection, connect_to_mongo
from app.routers import auth, dashboard, notifications, tickets, users

app = FastAPI(title="Helpdesk API", version="1.0.0")

# CORS: allow simple HTML frontend (e.g. simple_frontend at 5500)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.on_event("startup")
async def on_startup() -> None:
  await connect_to_mongo()


@app.on_event("shutdown")
async def on_shutdown() -> None:
  await close_mongo_connection()


@app.get("/")
async def root():
  return {"message": "Helpdesk API is running"}


@app.get("/api/health")
async def health():
  return {"status": "healthy"}

