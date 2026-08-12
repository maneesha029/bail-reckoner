from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Offense(Base):
    __tablename__ = "offenses"
    id = Column(String, primary_key=True)
    act = Column(String, nullable=False)
    section = Column(String, nullable=False)
    offense_category = Column(String, nullable=False)
    is_compoundable = Column(Boolean, default=False)
    max_sentence_months = Column(Integer, nullable=False)


class CaseRecord(Base):
    __tablename__ = "cases"
    case_id = Column(String, primary_key=True)
    prisoner_id = Column(String, nullable=False)
    custody_start_date = Column(DateTime, nullable=False)
    is_first_time_offender = Column(Boolean, default=False)
    state = Column(String)
    district = Column(String)
    case_stage = Column(String, default="under_trial")
    has_legal_aid = Column(Boolean, default=False)
