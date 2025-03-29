from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from service.db import Base


class ExpenditureDB(Base):
    __tablename__ = "expenditure"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    statement_id = Column(Integer, ForeignKey("statement.id"), nullable=True)

    # one to many -> statement:expenditures
    statement = relationship("StatementDB", back_populates="expenditures")
