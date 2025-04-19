import pytest
import time
import psutil
import os
from sqlalchemy.orm import Session
from app.crud.crud_email_template import crud_email_template
from app.crud.crud_generated_email import crud_generated_email
from app.schemas.email_template import EmailTemplateCreate
from app.schemas.generated_email import GeneratedEmailCreate
from app.services.email_generator import EmailGenerator


@pytest.fixture
def email_generator():
    return EmailGenerator()


@pytest.fixture
def large_template():
    # Create a template with many repeated sections
    repeated_section = """
        <div class="product">
            <h3>{{ product.name }}</h3>
            <p>{{ product.description }}</p>
            <p>Price: ${{ product.price }}</p>
        </div>
    """
    return EmailTemplateCreate(
        name="Large Performance Template",
        html_content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                .container {{ max-width: 600px; margin: 0 auto; }}
                .product {{ margin: 10px; padding: 10px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Product Catalog</h1>
                {"".join([repeated_section for _ in range(1000)])}
            </div>
        </body>
        </html>
        """,
        is_public=True
    )


def test_generation_performance(db: Session, email_generator, large_template):
    """Test the performance of email generation with a large template."""
    # Create the template
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=large_template,
        owner_id=1
    )
    
    # Create test data
    products = [
        {
            "name": f"Product {i}",
            "description": f"Description for product {i}",
            "price": f"{i}.99"
        }
        for i in range(1000)
    ]
    
    data = {"products": products}
    
    # Measure memory before
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Generate email and measure time
    start_time = time.time()
    html_content = email_generator.generate_email(
        template=template,
        data=data
    )
    end_time = time.time()
    
    # Measure memory after
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = final_memory - initial_memory
    
    # Assertions
    assert end_time - start_time < 5.0  # Should complete within 5 seconds
    assert memory_used < 100  # Should use less than 100MB of additional memory
    assert len(html_content) > 0
    assert len(html_content) < 5000000  # Less than 5MB


def test_bulk_generation_performance(db: Session, email_generator):
    """Test the performance of generating multiple emails."""
    # Create a simple template
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(
            name="Bulk Test Template",
            html_content="<html><body>{{ content }}</body></html>",
            is_public=True
        ),
        owner_id=1
    )
    
    # Generate 100 emails
    start_time = time.time()
    for i in range(100):
        data = {"content": f"Test content {i}"}
        html_content = email_generator.generate_email(
            template=template,
            data=data
        )
        
        # Store the email
        crud_generated_email.create_with_template(
            db=db,
            obj_in=GeneratedEmailCreate(
                html_content=html_content,
                template_id=template.id,
                data=data
            ),
            owner_id=1
        )
    
    end_time = time.time()
    
    # Assertions
    assert end_time - start_time < 30.0  # Should complete within 30 seconds
    
    # Verify all emails were created
    emails = crud_generated_email.get_multi(db=db, skip=0, limit=200)
    assert len(emails) >= 100


def test_database_query_performance(db: Session):
    """Test the performance of database queries for generated emails."""
    # Create a template
    template = crud_email_template.create_with_owner(
        db=db,
        obj_in=EmailTemplateCreate(
            name="Query Test Template",
            html_content="<html><body>{{ content }}</body></html>",
            is_public=True
        ),
        owner_id=1
    )
    
    # Create 1000 emails
    for i in range(1000):
        crud_generated_email.create_with_template(
            db=db,
            obj_in=GeneratedEmailCreate(
                html_content=f"<html><body>Test {i}</body></html>",
                template_id=template.id,
                data={"content": f"Test {i}"}
            ),
            owner_id=1
        )
    
    # Test query performance
    start_time = time.time()
    emails = crud_generated_email.get_multi(db=db, skip=0, limit=1000)
    end_time = time.time()
    
    # Assertions
    assert end_time - start_time < 1.0  # Should complete within 1 second
    assert len(emails) == 1000
    
    # Test filtered query performance
    start_time = time.time()
    filtered_emails = crud_generated_email.get_by_template(
        db=db,
        template_id=template.id,
        skip=0,
        limit=1000
    )
    end_time = time.time()
    
    assert end_time - start_time < 1.0  # Should complete within 1 second
    assert len(filtered_emails) == 1000 