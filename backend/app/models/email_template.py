from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class EmailTemplate(Base):
    """Email template model for storing HTML email templates.
    
    Attributes:
        id: Primary key
        name: Name of the template
        description: Optional description of the template
        html_content: The actual HTML content of the template
        owner_id: ID of the user who owns this template
        is_public: Whether the template is publicly available
        created_at: Timestamp when the template was created
        updated_at: Timestamp when the template was last updated
        figma_url: Optional URL to the Figma design this template is based on
        figma_file_key: Optional Figma file key for API access
        figma_node_id: Optional Figma node ID for specific component
    """
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    html_content = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    figma_url = Column(String)
    figma_file_key = Column(String)
    figma_node_id = Column(String)

    # Relationships
    owner = relationship("User", back_populates="email_templates")
    generated_emails = relationship("GeneratedEmail", back_populates="template") 