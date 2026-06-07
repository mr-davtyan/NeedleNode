import os
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, ForeignKey, Table, Column, Integer, String, Float, DateTime, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///embroidery.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 15})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in str(DATABASE_URL):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Junction table for many-to-many relationship
file_tag = Table(
    "file_tag",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("files.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(default=False, server_default="0")
    is_main: Mapped[bool] = mapped_column(default=False, server_default="0")
    
    files: Mapped[List["File"]] = relationship(
        secondary=file_tag, back_populates="tags"
    )

class File(Base):
    __tablename__ = "files"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    path: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    is_starred: Mapped[bool] = mapped_column(default=False, server_default="0")
    
    # Embroidery specific metadata
    width: Mapped[float | None] = mapped_column(Float, nullable=True)  # in mm or pixels
    height: Mapped[float | None] = mapped_column(Float, nullable=True) # in mm or pixels
    stitches: Mapped[int | None] = mapped_column(Integer, nullable=True)
    colors: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Paths for caching
    thumbnail_path: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    tags: Mapped[List[Tag]] = relationship(
        secondary=file_tag, back_populates="files"
    )

class SystemState(Base):
    __tablename__ = "system_state"
    
    key: Mapped[str] = mapped_column(String, primary_key=True) # 'scan' or 'import'
    is_active: Mapped[bool] = mapped_column(default=False)
    processed: Mapped[int] = mapped_column(default=0)
    total: Mapped[int] = mapped_column(default=0)
    current_file: Mapped[str] = mapped_column(default="")
    stop_requested: Mapped[bool] = mapped_column(default=False)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

def init_db(session: Session = None):
    Base.metadata.create_all(bind=engine)
    
    # Initialize state rows if missing
    db = session if session else SessionLocal()
    try:
        for key in ['scan', 'import']:
            existing = db.query(SystemState).filter(SystemState.key == key).first()
            if not existing:
                db.add(SystemState(key=key, last_heartbeat=datetime.utcnow()))
        db.commit()
    finally:
        if not session:
            db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
