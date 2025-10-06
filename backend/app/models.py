from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    entity_type = Column(String)
    name = Column(String)
    email = Column(String)
    student_id = Column(String)
    card_id = Column(String)
    device_hash = Column(String)
    department = Column(String)
