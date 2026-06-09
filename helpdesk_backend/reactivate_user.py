"""
One-off script: set is_active=True for a user by email.
Run from helpdesk_backend: python reactivate_user.py test@test.com
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "helpdesk_db")

def main():
    email = sys.argv[1] if len(sys.argv) > 1 else "test@test.com"
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    result = db.users.update_one(
        {"email": email},
        {"$set": {"is_active": True}}
    )
    if result.modified_count:
        print(f"Reactivated user: {email}")
    elif result.matched_count:
        print(f"User {email} was already active.")
    else:
        print(f"No user found with email: {email}")
    client.close()

if __name__ == "__main__":
    main()
