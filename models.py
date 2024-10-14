import datetime

from typing import Optional, List
from database import Base
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str] = mapped_column(String(150))

    tasks: Mapped[Optional[List['Task']]] = relationship('Task', back_populates='user')

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_info: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    datetime_to_do: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped['int'] = mapped_column(ForeignKey('users.id'))

    user: Mapped['User'] = relationship('User', back_populates='tasks')