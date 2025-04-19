from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.models import User
from app.schemas.email_template import EmailTemplate, EmailTemplateCreate, EmailTemplateUpdate
from app.schemas.generated_email import GeneratedEmail, GeneratedEmailCreate
from app.api import deps
from app.services.email_generator import EmailGenerator

router = APIRouter()
email_generator = EmailGenerator()


@router.get("/", response_model=List[EmailTemplate])
def read_templates(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve templates.
    """
    templates = crud.email_template.get_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return templates


@router.post("/", response_model=EmailTemplate)
def create_template(
    *,
    db: Session = Depends(deps.get_db),
    template_in: EmailTemplateCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new template.
    """
    template = crud.email_template.create_with_owner(
        db=db, obj_in=template_in, owner_id=current_user.id
    )
    return template


@router.put("/{template_id}", response_model=EmailTemplate)
def update_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    template_in: EmailTemplateUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a template.
    """
    template = crud.email_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    template = crud.email_template.update(db=db, db_obj=template, obj_in=template_in)
    return template


@router.get("/{template_id}", response_model=EmailTemplate)
def read_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get template by ID.
    """
    template = crud.email_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not template.is_public and template.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return template


@router.delete("/{template_id}", response_model=EmailTemplate)
def delete_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a template.
    """
    template = crud.email_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    template = crud.email_template.remove(db=db, id=template_id)
    return template


@router.get("/public/", response_model=List[EmailTemplate])
def read_public_templates(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve public templates.
    """
    templates = crud.email_template.get_public_templates(db, skip=skip, limit=limit)
    return templates


@router.get("/figma/{file_key}", response_model=EmailTemplate)
def read_template_by_figma(
    *,
    db: Session = Depends(deps.get_db),
    file_key: str,
    node_id: str = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get template by Figma file key and optionally node ID.
    """
    template = crud.email_template.get_by_figma_file(
        db, figma_file_key=file_key, figma_node_id=node_id
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not template.is_public and template.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return template


@router.post("/{template_id}/generate", response_model=GeneratedEmail)
def generate_email(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    data: Dict[str, Any],
    preview: bool = False,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate an email from a template.
    
    Args:
        template_id: ID of the template to use
        data: Dictionary of data to inject into the template
        preview: Whether to generate a preview version
        current_user: The authenticated user
        
    Returns:
        The generated email content
    """
    # Get the template
    template = crud.email_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not template.is_public and template.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    try:
        # Generate the email
        html_content = email_generator.generate_email(
            template=template,
            data=data,
            preview=preview
        )
        
        # Create the generated email record
        generated_email = crud.generated_email.create_with_template(
            db=db,
            obj_in=GeneratedEmailCreate(
                html_content=html_content,
                template_id=template_id,
                data=data
            ),
            owner_id=current_user.id
        )
        
        return generated_email
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating email") 