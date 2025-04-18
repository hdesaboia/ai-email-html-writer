from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class EmailTemplate(Base):
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    html_content = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="email_templates")
    generated_emails = relationship("GeneratedEmail", back_populates="template") 