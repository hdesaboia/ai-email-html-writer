from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class GeneratedEmail(Base):
    html_content = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("emailtemplate.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="generated_emails")
    template = relationship("EmailTemplate", back_populates="generated_emails") 