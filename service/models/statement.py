from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime, timezone

from sqlalchemy.orm import relationship

from service.db import Base


class StatementDB(Base):
    __tablename__ = "statement"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    report_date = Column(DateTime, default=datetime.now(timezone.utc))

    # one to many -> user:statements
    user = relationship("UserDB", back_populates="statements")
    # one to many -> statement:incomes
    incomes = relationship("IncomeDB", back_populates="statement",
                           lazy="selectin", cascade="all, delete-orphan")

    # one to many -> statement:expenditure
    expenditures = relationship("ExpenditureDB", back_populates="statement",
                                lazy="selectin",
                                cascade="all, delete-orphan")
