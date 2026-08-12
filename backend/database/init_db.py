"""
Run this once before starting the app:

python database/init_db.py
"""

from database.session import Base, engine
from database import models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database initialized: triora.db")