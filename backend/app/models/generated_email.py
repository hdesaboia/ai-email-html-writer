from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class GeneratedEmail(Base):
    """Model for storing generated emails.
    
    Attributes:
        html_content: The generated HTML content
        template_id: ID of the template used
        owner_id: ID of the user who generated the email
        data: JSON data used to generate the email
        created_at: Timestamp when the email was generated
    """
    __tablename__ = "generated_emails"

    html_content = Column(Text, nullable=False)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    template = relationship("EmailTemplate", back_populates="generated_emails")
    owner = relationship("User", back_populates="generated_emails") 