from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from . import config

# Database URL
DATABASE_URL = f"postgresql://{config.settings.database_user}:{config.settings.database_password}@{config.settings.database_host}:{config.settings.database_port}/{config.settings.database_name}"

# Create engine
engine = create_engine(DATABASE_URL)

# Create base class
Base = declarative_base()

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Post model
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Boolean, default=True)
    rating = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

#User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)    

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
