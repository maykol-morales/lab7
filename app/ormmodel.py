from app.sqlite import Base, engine
from sqlalchemy import Column, Integer, String

class PaperORM(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

Base.metadata.create_all(bind=engine)