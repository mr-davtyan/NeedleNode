import os
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, ForeignKey, Table, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DATABASE_URL = "sqlite:///embroidery.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
