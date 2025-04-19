import pytest
from bs4 import BeautifulSoup
from app.services.email_generator import EmailGenerator
from app.models.email_template import EmailTemplate
import time


@pytest.fixture
def email_generator():
    return EmailGenerator()


@pytest.fixture
def sample_template():
    return EmailTemplate(
        id=1,
        name="Test Template",
        html_content="""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                .container { max-width: 600px; margin: 0 auto; }
                .header { background-color: #f5f5f5; padding: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ title }}</h1>
                </div>
                <div class="content">
                    <p>{{ content }}</p>
                    <img src="{{ image_url }}" alt="Sample Image" style="max-width: 100%;">
                </div>
            </div>
        </body>
        </html>
        """,
        owner_id=1,
        is_public=True
    )


@pytest.fixture
def complex_template():
    return EmailTemplate(
        id=2,
        name="Complex Template",
        html_content="""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                .container { max-width: 600px; margin: 0 auto; }
                .header { background-color: #f5f5f5; padding: 20px; }
                .product { margin: 10px; padding: 10px; border: 1px solid #ddd; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ user.name }}'s Order</h1>
                    <p>Order #{{ order.id }}</p>
                </div>
                <div class="content">
                    {% if order.items %}
                        <h2>Your Items:</h2>
                        {% for item in order.items %}
                            <div class="product">
                                <h3>{{ item.name }}</h3>
                                <p>Price: ${{ item.price }}</p>
                                <p>Quantity: {{ item.quantity }}</p>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p>No items in this order.</p>
                    {% endif %}
                </div>
            </div>
        </body>
        </html>
        """,
        owner_id=1,
        is_public=True
    )


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
    return EmailTemplate(
        id=3,
        name="Large Template",
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
                {"".join([repeated_section for _ in range(100)])}
            </div>
        </body>
        </html>
        """,
        owner_id=1,
        is_public=True
    )


def test_generate_email_basic(email_generator, sample_template):
    """Test basic email generation with a simple template."""
    data = {
        "title": "Test Email",
        "content": "This is a test email content.",
        "image_url": "https://example.com/image.jpg"
    }
    
    html_content = email_generator.generate_email(
        template=sample_template,
        data=data
    )
    
    # Basic validation
    assert html_content
    assert "Test Email" in html_content
    assert "This is a test email content" in html_content
    assert "https://example.com/image.jpg" in html_content
    
    # Check if HTML is valid
    soup = BeautifulSoup(html_content, 'html.parser')
    assert soup.find('html')
    assert soup.find('body')
    assert soup.find('div', class_='container')


def test_generate_email_preview(email_generator, sample_template):
    """Test email generation in preview mode."""
    data = {
        "title": "Preview Test",
        "content": "This is a preview test.",
        "image_url": "https://example.com/preview.jpg"
    }
    
    html_content = email_generator.generate_email(
        template=sample_template,
        data=data,
        preview=True
    )
    
    # Check for preview-specific modifications
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.find('body')
    assert body
    assert 'border: 2px dashed #ccc' in body.get('style', '')
    
    # Check for preview header
    header = soup.find('div', string='Email Preview')
    assert header
    assert 'background: #f5f5f5' in header.get('style', '')


def test_generate_email_validation(email_generator, sample_template):
    """Test email validation during generation."""
    # Test with missing required data
    with pytest.raises(ValueError):
        email_generator.generate_email(
            template=sample_template,
            data={}  # Missing required fields
        )
    
    # Test with invalid HTML
    invalid_template = EmailTemplate(
        id=2,
        name="Invalid Template",
        html_content="<div>No body tag</div>",
        owner_id=1,
        is_public=True
    )
    
    with pytest.raises(ValueError):
        email_generator.generate_email(
            template=invalid_template,
            data={"title": "Test"}
        )


def test_generate_email_optimization(email_generator, sample_template):
    """Test email-specific optimizations."""
    data = {
        "title": "Optimization Test",
        "content": "Testing optimizations",
        "image_url": "/relative/path/image.jpg"
    }
    
    html_content = email_generator.generate_email(
        template=sample_template,
        data=data
    )
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for email-specific CSS
    style = soup.find('style')
    assert style
    assert 'margin: 0' in style.string
    assert 'padding: 0' in style.string
    
    # Check for image optimizations
    img = soup.find('img')
    assert img
    assert 'border: 0' in img.get('style', '')
    assert 'height: auto' in img.get('style', '')
    
    # Check for URL conversion
    assert 'https://example.com/relative/path/image.jpg' in html_content


def test_generate_email_with_special_characters(email_generator, sample_template):
    """Test email generation with special characters in data."""
    data = {
        "title": "Special & Characters <Test>",
        "content": "Testing & < > ' \" characters",
        "image_url": "https://example.com/image.jpg"
    }
    
    html_content = email_generator.generate_email(
        template=sample_template,
        data=data
    )
    
    # Check that special characters are properly escaped
    assert "Special &amp; Characters &lt;Test&gt;" in html_content
    assert "Testing &amp; &lt; &gt; &#x27; &quot; characters" in html_content


def test_generate_email_with_nested_variables(email_generator, complex_template):
    """Test email generation with nested template variables."""
    data = {
        "user": {
            "name": "John Doe"
        },
        "order": {
            "id": "12345",
            "items": [
                {
                    "name": "Product 1",
                    "price": "19.99",
                    "quantity": 2
                },
                {
                    "name": "Product 2",
                    "price": "29.99",
                    "quantity": 1
                }
            ]
        }
    }
    
    html_content = email_generator.generate_email(
        template=complex_template,
        data=data
    )
    
    # Check nested variable rendering
    assert "John Doe's Order" in html_content
    assert "Order #12345" in html_content
    assert "Product 1" in html_content
    assert "$19.99" in html_content
    assert "Quantity: 2" in html_content


def test_generate_email_with_conditional_content(email_generator, complex_template):
    """Test email generation with conditional content."""
    # Test with items
    data_with_items = {
        "user": {"name": "Test User"},
        "order": {
            "id": "123",
            "items": [{"name": "Test Item", "price": "10.00", "quantity": 1}]
        }
    }
    
    html_with_items = email_generator.generate_email(
        template=complex_template,
        data=data_with_items
    )
    assert "Your Items:" in html_with_items
    assert "Test Item" in html_with_items
    
    # Test without items
    data_without_items = {
        "user": {"name": "Test User"},
        "order": {"id": "123", "items": []}
    }
    
    html_without_items = email_generator.generate_email(
        template=complex_template,
        data=data_without_items
    )
    assert "No items in this order." in html_without_items


def test_generate_email_with_repeated_sections(email_generator, large_template):
    """Test email generation with repeated sections."""
    # Create test data with 100 products
    products = [
        {
            "name": f"Product {i}",
            "description": f"Description for product {i}",
            "price": f"{i}.99"
        }
        for i in range(100)
    ]
    
    data = {"products": products}
    
    html_content = email_generator.generate_email(
        template=large_template,
        data=data
    )
    
    # Check that all products are rendered
    for i in range(100):
        assert f"Product {i}" in html_content
        assert f"Description for product {i}" in html_content
        assert f"${i}.99" in html_content


def test_generate_email_performance(email_generator, large_template):
    """Test performance of email generation with large templates."""
    # Create test data with 100 products
    products = [
        {
            "name": f"Product {i}",
            "description": f"Description for product {i}",
            "price": f"{i}.99"
        }
        for i in range(100)
    ]
    
    data = {"products": products}
    
    # Measure generation time
    start_time = time.time()
    html_content = email_generator.generate_email(
        template=large_template,
        data=data
    )
    end_time = time.time()
    
    # Assert that generation time is reasonable (less than 1 second)
    assert end_time - start_time < 1.0
    
    # Verify content length is reasonable
    assert len(html_content) > 0
    assert len(html_content) < 1000000  # Less than 1MB


def test_generate_email_with_email_client_quirks(email_generator, sample_template):
    """Test email generation with email client-specific quirks."""
    data = {
        "title": "Email Client Test",
        "content": "Testing email client quirks",
        "image_url": "https://example.com/image.jpg"
    }
    
    html_content = email_generator.generate_email(
        template=sample_template,
        data=data
    )
    
    # Check for email client-specific optimizations
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for Outlook-specific fixes
    assert 'mso-table-lspace:0pt' in html_content
    assert 'mso-table-rspace:0pt' in html_content
    
    # Check for Gmail-specific fixes
    assert 'display:block' in html_content
    assert 'min-width:100%' in html_content
    
    # Check for mobile-specific optimizations
    assert 'width=device-width' in html_content
    assert 'initial-scale=1.0' in html_content 