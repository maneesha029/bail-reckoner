from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    JSON,
    String,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Offense(Base):
    __tablename__ = "offenses"
    act = Column(String, primary_key=True)
    section = Column(String, primary_key=True)
    offense_category = Column(String, nullable=False)
    is_compoundable = Column(Boolean, default=False)
    max_sentence_months = Column(Integer, nullable=False)

    cases = relationship(
        "CaseRecord",
        secondary="case_offenses",
        back_populates="offense_records",
    )


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
    charges = Column(JSON, nullable=False, default=list)
    version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    offense_records = relationship(
        "Offense",
        secondary="case_offenses",
        back_populates="cases",
        lazy="selectin",
    )


case_offenses = Table(
    "case_offenses",
    Base.metadata,
    Column("case_id", String, ForeignKey("cases.case_id", ondelete="CASCADE"), primary_key=True),
    Column("offense_act", String, primary_key=True),
    Column("offense_section", String, primary_key=True),
    ForeignKeyConstraint(
        ["offense_act", "offense_section"],
        ["offenses.act", "offenses.section"],
        ondelete="RESTRICT",
    ),
)
