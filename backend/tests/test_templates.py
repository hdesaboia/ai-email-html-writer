from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.crud.crud_email_template import crud_email_template
from app.schemas.user import UserCreate
from app.schemas.email_template import EmailTemplateCreate, EmailTemplateUpdate
from app.main import app
from app.core.security import create_access_token
from app.api import deps

client = TestClient(app)

def get_test_db(test_db: Session):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    return override_get_db

def get_test_current_user(user):
    def override_get_current_user():
        return user
    return override_get_current_user

def test_create_template(db: Session) -> None:
    # Create a test user first
    email = "test@example.com"
    password = "testpass123"
    user_in = UserCreate(email=email, password=password)
    user = crud_user.create(db, obj_in=user_in)
    
    # Create template data
    template_in = EmailTemplateCreate(
        name="Test Template",
        description="A test template",
        html_content="<html><body>Test</body></html>",
        is_public=False
    )
    
    # Create template
    template = crud_email_template.create_with_owner(
        db=db, obj_in=template_in, owner_id=user.id
    )
    
    assert template.name == template_in.name
    assert template.description == template_in.description
    assert template.html_content == template_in.html_content
    assert template.owner_id == user.id
    assert template.is_public == template_in.is_public

def test_get_template_by_owner(db: Session) -> None:
    # Create a test user first
    email = "test@example.com"
    password = "testpass123"
    user_in = UserCreate(email=email, password=password)
    user = crud_user.create(db, obj_in=user_in)
    
    # Create template data
    template_in = EmailTemplateCreate(
        name="Test Template",
        description="A test template",
        html_content="<html><body>Test</body></html>",
        is_public=False
    )
    
    # Create template
    template = crud_email_template.create_with_owner(
        db=db, obj_in=template_in, owner_id=user.id
    )
    
    # Get templates by owner
    templates = crud_email_template.get_by_owner(db, owner_id=user.id)
    
    assert len(templates) == 1
    assert templates[0].id == template.id
    assert templates[0].owner_id == user.id

def test_get_public_templates(db: Session) -> None:
    # Create two test users
    user1_in = UserCreate(email="user1@example.com", password="testpass123")
    user2_in = UserCreate(email="user2@example.com", password="testpass123")
    user1 = crud_user.create(db, obj_in=user1_in)
    user2 = crud_user.create(db, obj_in=user2_in)
    
    # Create public and private templates
    public_template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(
            name="Public Template",
            html_content="<html><body>Public</body></html>",
            is_public=True
        ),
        owner_id=user1.id
    )
    
    private_template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(
            name="Private Template",
            html_content="<html><body>Private</body></html>",
            is_public=False
        ),
        owner_id=user2.id
    )
    
    # Get public templates
    public_templates = crud_email_template.get_public_templates(db)
    
    assert len(public_templates) == 1
    assert public_templates[0].id == public_template.id
    assert public_templates[0].is_public is True

def test_update_template(db: Session) -> None:
    # Create a test user
    user_in = UserCreate(email="test@example.com", password="testpass123")
    user = crud_user.create(db, obj_in=user_in)
    
    # Create initial template
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(
            name="Initial Template",
            html_content="<html><body>Initial</body></html>",
            is_public=False
        ),
        owner_id=user.id
    )
    
    # Update template
    update_data = EmailTemplateUpdate(
        name="Updated Template",
        html_content="<html><body>Updated</body></html>",
        is_public=True
    )
    
    updated_template = crud_email_template.update(
        db=db, db_obj=template, obj_in=update_data
    )
    
    assert updated_template.name == update_data.name
    assert updated_template.html_content == update_data.html_content
    assert updated_template.is_public == update_data.is_public

def test_delete_template(db: Session) -> None:
    # Create a test user
    user_in = UserCreate(email="test@example.com", password="testpass123")
    user = crud_user.create(db, obj_in=user_in)
    
    # Create template
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(
            name="To Delete",
            html_content="<html><body>Delete me</body></html>",
            is_public=False
        ),
        owner_id=user.id
    )
    
    # Delete template
    crud_email_template.remove(db=db, id=template.id)
    
    # Try to get deleted template
    deleted_template = crud_email_template.get(db=db, id=template.id)
    assert deleted_template is None

def test_get_template_by_figma(db: Session) -> None:
    # Create a test user
    user_in = UserCreate(email="test@example.com", password="testpass123")
    user = crud_user.create(db, obj_in=user_in)
    
    # Create template with Figma data
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(
            name="Figma Template",
            html_content="<html><body>Figma</body></html>",
            is_public=True,
            figma_file_key="abc123",
            figma_node_id="node123"
        ),
        owner_id=user.id
    )
    
    # Get template by Figma data
    found_template = crud_email_template.get_by_figma_file(
        db, figma_file_key="abc123", figma_node_id="node123"
    )
    
    assert found_template is not None
    assert found_template.id == template.id
    assert found_template.figma_file_key == "abc123"
    assert found_template.figma_node_id == "node123" 