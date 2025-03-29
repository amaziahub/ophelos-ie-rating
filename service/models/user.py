from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from service.db import Base


class UserDB(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    statements = relationship("StatementDB", back_populates="user")
