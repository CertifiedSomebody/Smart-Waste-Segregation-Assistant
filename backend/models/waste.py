"""
Smart Waste Segregation System - Waste Model
Production-ready SQLAlchemy model for tracking waste classification
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Enum,
    JSON,
    Index,
    Text
)
from sqlalchemy.dialects.postgresql import UUID

from backend.database.db import Base

# ----------------------------
# Waste Categories
# ----------------------------
WASTE_TYPES = ("biodegradable", "non_biodegradable", "hazardous")

WASTE_CATEGORIES = (
    "organic",
    "plastic",
    "metal",
    "glass",
    "paper",
    "e_waste",
    "others"
)

# ----------------------------
# Waste Model
# ----------------------------
class WasteRecord(Base):
    __tablename__ = "waste_records"

    # ----------------------------
    # Primary Identity
    # ----------------------------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ----------------------------
    # Waste Details
    # ----------------------------
    waste_name = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)

    waste_type = Column(
        Enum(*WASTE_TYPES, name="waste_type_enum"),
        nullable=True,
        index=True
    )

    category = Column(
        Enum(*WASTE_CATEGORIES, name="waste_category_enum"),
        nullable=True,
        index=True
    )

    # ----------------------------
    # AI / Detection Info
    # ----------------------------
    classification_confidence = Column(String(10), nullable=True)
    model_prediction = Column(String(100), nullable=True)

    image_path = Column(String(255), nullable=True)  # optional image input

    # Flexible storage for AI results / logs
    ai_metadata = Column(JSON, nullable=True)

    # ----------------------------
    # Disposal Info
    # ----------------------------
    disposal_instructions = Column(Text, nullable=True)
    recycling_info = Column(Text, nullable=True)

    is_recyclable = Column(Boolean, default=False, index=True)
    is_hazardous = Column(Boolean, default=False, index=True)

    # ----------------------------
    # System Fields
    # ----------------------------
    is_active = Column(Boolean, default=True, index=True)
    is_deleted = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ----------------------------
    # Indexes
    # ----------------------------
    __table_args__ = (
        Index("idx_waste_category", "category"),
        Index("idx_waste_type", "waste_type"),
    )

    # ----------------------------
    # Utility Methods
    # ----------------------------
    def soft_delete(self):
        self.is_deleted = True
        self.is_active = False

    def to_dict(self):
        return {
            "id": str(self.id),
            "waste_name": self.waste_name,
            "description": self.description,
            "waste_type": self.waste_type,
            "category": self.category,
            "classification_confidence": self.classification_confidence,
            "model_prediction": self.model_prediction,
            "image_path": self.image_path,
            "ai_metadata": self.ai_metadata,
            "disposal_instructions": self.disposal_instructions,
            "recycling_info": self.recycling_info,
            "is_recyclable": self.is_recyclable,
            "is_hazardous": self.is_hazardous,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    # ----------------------------
    # Representation
    # ----------------------------
    def __repr__(self):
        return f"<WasteRecord {self.waste_name or 'Unknown'} | {self.id}>"