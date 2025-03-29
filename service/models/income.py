from sqlalchemy import Column, Integer, String, Float, ForeignKey

from service.db import Base


class IncomeDB(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    statement_id = Column(Integer, ForeignKey("statement.id"), nullable=True)
