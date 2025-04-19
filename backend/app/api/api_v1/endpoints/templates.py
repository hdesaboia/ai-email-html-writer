from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.EmailTemplate])
def read_templates(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve templates.
    """
    templates = crud.email_template.get_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return templates


@router.post("/", response_model=schemas.EmailTemplate)
def create_template(
    *,
    db: Session = Depends(deps.get_db),
    template_in: schemas.EmailTemplateCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new template.
    """
    template = crud.email_template.create_with_owner(
        db=db, obj_in=template_in, owner_id=current_user.id
    )
    return template


@router.put("/{template_id}", response_model=schemas.EmailTemplate)
def update_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    template_in: schemas.EmailTemplateUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
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


@router.get("/{template_id}", response_model=schemas.EmailTemplate)
def read_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
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


@router.delete("/{template_id}", response_model=schemas.EmailTemplate)
def delete_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
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


@router.get("/public/", response_model=List[schemas.EmailTemplate])
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


@router.get("/figma/{file_key}", response_model=schemas.EmailTemplate)
def read_template_by_figma(
    *,
    db: Session = Depends(deps.get_db),
    file_key: str,
    node_id: str = None,
    current_user: models.User = Depends(deps.get_current_active_user),
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