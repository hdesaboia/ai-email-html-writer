import pytest
from sqlalchemy.orm import Session
from app.crud.crud_email_template import crud_email_template
from app.crud.crud_generated_email import crud_generated_email
from app.schemas.email_template import EmailTemplateCreate
from app.schemas.generated_email import GeneratedEmailCreate
from app.services.email_generator import EmailGenerator


@pytest.fixture
def email_generator():
    return EmailGenerator()


def test_full_email_generation_flow(db: Session, email_generator):
    """Test the complete flow from template creation to email generation and storage."""
    # 1. Create a template
    template_data = {
        "name": "Test Integration Template",
        "html_content": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                .container { max-width: 600px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{{ title }}</h1>
                <p>{{ content }}</p>
            </div>
        </body>
        </html>
        """,
        "is_public": True
    }
    
    template_in = EmailTemplateCreate(**template_data)
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=template_in,
        owner_id=1
    )
    
    # 2. Generate an email
    email_data = {
        "title": "Integration Test Email",
        "content": "This is a test of the full email generation flow."
    }
    
    html_content = email_generator.generate_email(
        template=template,
        data=email_data
    )
    
    # 3. Store the generated email
    generated_email_in = GeneratedEmailCreate(
        html_content=html_content,
        template_id=template.id,
        data=email_data
    )
    
    generated_email = crud_generated_email.create_with_template(
        db=db,
        obj_in=generated_email_in,
        owner_id=1
    )
    
    # 4. Verify the stored email
    stored_email = crud_generated_email.get(db=db, id=generated_email.id)
    assert stored_email
    assert stored_email.html_content == html_content
    assert stored_email.template_id == template.id
    assert stored_email.owner_id == 1
    assert stored_email.data == email_data


def test_concurrent_email_generation(db: Session, email_generator):
    """Test concurrent email generation and storage."""
    import threading
    import time
    
    # Create a template
    template_data = {
        "name": "Concurrent Test Template",
        "html_content": "<html><body>{{ content }}</body></html>",
        "is_public": True
    }
    
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(**template_data),
        owner_id=1
    )
    
    # Function to generate and store an email
    def generate_and_store_email(email_id):
        data = {"content": f"Test content {email_id}"}
        html_content = email_generator.generate_email(
            template=template,
            data=data
        )
        
        generated_email_in = GeneratedEmailCreate(
            html_content=html_content,
            template_id=template.id,
            data=data
        )
        
        crud_generated_email.create_with_template(
            db=db,
            obj_in=generated_email_in,
            owner_id=1
        )
    
    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(
            target=generate_and_store_email,
            args=(i,)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify all emails were created
    emails = crud_generated_email.get_multi(db=db, skip=0, limit=100)
    assert len(emails) >= 5
    
    # Verify each email has unique content
    contents = set()
    for email in emails:
        if email.template_id == template.id:
            contents.add(email.data["content"])
    
    assert len(contents) >= 5


def test_error_handling_integration(db: Session, email_generator):
    """Test error handling across the email generation flow."""
    # 1. Test with invalid template
    with pytest.raises(ValueError):
        email_generator.generate_email(
            template=None,
            data={"content": "test"}
        )
    
    # 2. Test with invalid data
    template_data = {
        "name": "Error Test Template",
        "html_content": "<html><body>{{ content }}</body></html>",
        "is_public": True
    }
    
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(**template_data),
        owner_id=1
    )
    
    with pytest.raises(ValueError):
        email_generator.generate_email(
            template=template,
            data={}  # Missing required content
        )
    
    # 3. Test with invalid storage
    with pytest.raises(Exception):
        crud_generated_email.create_with_template(
            db=db,
            obj_in=GeneratedEmailCreate(
                html_content="<html></html>",
                template_id=999999,  # Non-existent template
                data={}
            ),
            owner_id=1
        ) 