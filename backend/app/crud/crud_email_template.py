from typing import List, Optional

from app.crud.base import CRUDBase
from app.models.email_template import EmailTemplate
from app.schemas.email_template import EmailTemplateCreate, EmailTemplateUpdate


class CRUDEmailTemplate(CRUDBase[EmailTemplate, EmailTemplateCreate, EmailTemplateUpdate]):
    """CRUD operations for EmailTemplate model.
    
    Inherits from CRUDBase and adds template-specific operations.
    """
    
    def create_with_owner(
        self, db, *, obj_in: EmailTemplateCreate, owner_id: int
    ) -> EmailTemplate:
        """Create a new template with an owner."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_owner(
        self, db, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[EmailTemplate]:
        """Get all templates owned by a specific user."""
        return (
            db.query(self.model)
            .filter(EmailTemplate.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_public_templates(
        self, db, *, skip: int = 0, limit: int = 100
    ) -> List[EmailTemplate]:
        """Get all public templates."""
        return (
            db.query(self.model)
            .filter(EmailTemplate.is_public == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_figma_file(
        self, db, *, figma_file_key: str, figma_node_id: Optional[str] = None
    ) -> Optional[EmailTemplate]:
        """Get template by Figma file key and optionally node ID."""
        query = db.query(self.model).filter(EmailTemplate.figma_file_key == figma_file_key)
        if figma_node_id:
            query = query.filter(EmailTemplate.figma_node_id == figma_node_id)
        return query.first()


crud_email_template = CRUDEmailTemplate(EmailTemplate) 