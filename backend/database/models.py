from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.session import Base


class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    project_duration_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    activities = relationship("ActivityDB", back_populates="project", cascade="all, delete-orphan")
    materials = relationship("MaterialDB", back_populates="project", cascade="all, delete-orphan")
    vendors = relationship("VendorDB", back_populates="project", cascade="all, delete-orphan")


class ActivityDB(Base):
    __tablename__ = "activities"

    # Composite primary key: the same activity id (e.g. "A01") can now exist
    # in many different projects without colliding, since it's only unique
    # WITHIN a project_id, not globally.
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), primary_key=True)

    name = Column(String)
    duration_days = Column(Integer)
    predecessors = Column(String, default="")
    float_days = Column(Integer, nullable=True)

    project = relationship("ProjectDB", back_populates="activities")


class VendorDB(Base):
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), primary_key=True)

    name = Column(String)
    historical_delay_rate = Column(Float, default=0.15)
    jobs_completed = Column(Integer, default=0)
    jobs_delayed = Column(Integer, default=0)

    project = relationship("ProjectDB", back_populates="vendors")


class MaterialDB(Base):
    __tablename__ = "materials"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), primary_key=True)

    name = Column(String)
    activity_id = Column(String)
    vendor_id = Column(String, nullable=True)
    lead_time_days = Column(Integer)
    vendor_reported_status = Column(String, nullable=True)
    manual_p_delay_override = Column(Float, nullable=True)

    p_delay = Column(Float, nullable=True)
    cwrs = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    reason = Column(String, nullable=True)

    project = relationship("ProjectDB", back_populates="materials")


class PhotoEvidenceDB(Base):
    __tablename__ = "photo_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String)
    project_id = Column(String, nullable=True)
    activity_id = Column(String)
    photo_url = Column(String)
    expected_stage = Column(String)
    match_result = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)