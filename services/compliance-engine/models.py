from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ProceduralRequirement(Base):
    __tablename__ = "procedural_requirements"
    id = Column(String, primary_key=True)
    offense_category = Column(String, nullable=False)
    bond_type = Column(String, nullable=False)
    estimated_fine_amount_inr = Column(Integer)
    required_documents = Column(String)  # comma-separated for simplicity
    procedural_steps = Column(String)  # JSON-encoded list of {step_number, description}
    governing_sections = Column(String)


class BondWaiverFlag(Base):
    __tablename__ = "bond_waiver_flags"
    case_id = Column(String, primary_key=True)
    is_flagged = Column(Boolean, default=False)
    confidence = Column(String)
    reasoning = Column(String)


class DiscretionAssessment(Base):
    __tablename__ = "discretion_assessments"
    case_id = Column(String, primary_key=True)
    flight_risk_band = Column(String, nullable=False)
    flight_risk_score = Column(Integer, nullable=False)
    witness_influence_band = Column(String, nullable=False)
    witness_influence_score = Column(Integer, nullable=False)
    factors_present = Column(String)  # comma-separated, both categories combined
