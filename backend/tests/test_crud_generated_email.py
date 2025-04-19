import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.crud.crud_generated_email import crud_generated_email
from app.models.generated_email import GeneratedEmail
from app.schemas.generated_email import GeneratedEmailCreate


@pytest.fixture
def sample_generated_email_data():
    return {
        "html_content": "<html><body>Test email content</body></html>",
        "template_id": 1,
        "data": {"title": "Test Email", "content": "Test content"}
    }


def test_create_generated_email(db: Session, sample_generated_email_data):
    """Test creating a new generated email."""
    email_in = GeneratedEmailCreate(**sample_generated_email_data)
    email = crud_generated_email.create_with_template(
        db=db,
        obj_in=email_in,
        owner_id=1
    )
    
    assert email.id
    assert email.html_content == sample_generated_email_data["html_content"]
    assert email.template_id == sample_generated_email_data["template_id"]
    assert email.owner_id == 1
    assert email.data == sample_generated_email_data["data"]
    assert isinstance(email.created_at, datetime)


def test_get_generated_email(db: Session, sample_generated_email_data):
    """Test retrieving a generated email by ID."""
    # Create a test email
    email_in = GeneratedEmailCreate(**sample_generated_email_data)
    email = crud_generated_email.create_with_template(
        db=db,
        obj_in=email_in,
        owner_id=1
    )
    
    # Retrieve it
    stored_email = crud_generated_email.get(db=db, id=email.id)
    assert stored_email
    assert stored_email.id == email.id
    assert stored_email.html_content == email.html_content


def test_get_multi_generated_emails(db: Session, sample_generated_email_data):
    """Test retrieving multiple generated emails."""
    # Create multiple test emails
    for i in range(3):
        email_in = GeneratedEmailCreate(**sample_generated_email_data)
        crud_generated_email.create_with_template(
            db=db,
            obj_in=email_in,
            owner_id=1
        )
    
    # Retrieve them
    emails = crud_generated_email.get_multi(db=db, skip=0, limit=100)
    assert len(emails) >= 3


def test_get_by_owner(db: Session, sample_generated_email_data):
    """Test retrieving emails by owner."""
    # Create emails for different owners
    for owner_id in [1, 2]:
        email_in = GeneratedEmailCreate(**sample_generated_email_data)
        crud_generated_email.create_with_template(
            db=db,
            obj_in=email_in,
            owner_id=owner_id
        )
    
    # Get emails for owner 1
    emails = crud_generated_email.get_by_owner(
        db=db,
        owner_id=1,
        skip=0,
        limit=100
    )
    assert all(email.owner_id == 1 for email in emails)


def test_get_by_template(db: Session, sample_generated_email_data):
    """Test retrieving emails by template."""
    # Create emails for different templates
    for template_id in [1, 2]:
        email_in = GeneratedEmailCreate(**sample_generated_email_data)
        email_in.template_id = template_id
        crud_generated_email.create_with_template(
            db=db,
            obj_in=email_in,
            owner_id=1
        )
    
    # Get emails for template 1
    emails = crud_generated_email.get_by_template(
        db=db,
        template_id=1,
        skip=0,
        limit=100
    )
    assert all(email.template_id == 1 for email in emails)


def test_remove_generated_email(db: Session, sample_generated_email_data):
    """Test removing a generated email."""
    # Create a test email
    email_in = GeneratedEmailCreate(**sample_generated_email_data)
    email = crud_generated_email.create_with_template(
        db=db,
        obj_in=email_in,
        owner_id=1
    )
    
    # Remove it
    removed_email = crud_generated_email.remove(db=db, id=email.id)
    assert removed_email.id == email.id
    
    # Verify it's gone
    stored_email = crud_generated_email.get(db=db, id=email.id)
    assert not stored_email 