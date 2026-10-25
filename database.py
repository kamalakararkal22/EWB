from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Define the SQLite database URL
# "sqlite:///./students.db" creates a local database file named students.db in the current directory
DATABASE_URL = "sqlite:///./students.db"

# 2. Create the SQLAlchemy Engine
# SQLite requires "check_same_thread": False when used with FastAPI
# because FastAPI can handle requests across multiple threads for the same connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. Create a SessionLocal factory
# Each instance of SessionLocal will be a distinct database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 4. Create the Declarative Base class
# Our database models in models.py will inherit from this Base class
Base = declarative_base()


# 5. Dependency for FastAPI endpoints
# This function creates a fresh database session for each incoming request,
# yields it to the route function, and guarantees it closes when the request finishes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
